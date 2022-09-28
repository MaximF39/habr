import asyncio
import os
import time
from abc import ABCMeta, abstractmethod
from asyncio import Task
from datetime import datetime

import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from db.models import Articles
from utils import validation_count


class IParser(metaclass=ABCMeta):
    @property
    @abstractmethod
    def prefix_url(self) -> str:
        ...

    @abstractmethod
    def get_info_page(self, url: str, html: str | bytes) -> dict:
        ...

    @abstractmethod
    def get_urls_to_main_articles(self) -> list:
        ...


class HabrParser(IParser):
    _prefix_url: str = "https://habr.com"

    @property
    def prefix_url(self) -> str:
        return self._prefix_url

    def get_urls_to_main_articles(self) -> list:
        soup = self._get_soup("/ru/all")
        class_main_article = "tm-article-snippet__title-link"
        main_titles = soup.findAll("a", class_=class_main_article, href=True)
        return list(map(lambda el: self._get_url(el["href"]), main_titles))

    def _get_soup(self, url: str) -> BeautifulSoup:
        return BeautifulSoup(self._get_page(url), features="html.parser")

    def _get_page(self, url: str) -> str:
        """ url: url or postfix """
        url = self._get_url(url)
        response = requests.get(url, timeout=120)
        if response.status_code != 200:
            raise requests.exceptions.ConnectionError
        return response.text

    def _get_url(self, url: str) -> str:
        return url if url.startswith(self._prefix_url) else self._prefix_url + url

    def get_info_page(self, url: str, html: str | bytes = None) -> dict:
        info = {}
        soup = BeautifulSoup(html, features="html.parser") if html is not None else self._get_soup(url)

        title_class = "tm-article-snippet__title tm-article-snippet__title_h1"
        titles = soup.findAll("h1", class_=title_class)
        validation_count(need=1, get=len(titles), add_info="Habr parse page error title")
        title = titles[0].find("span").text
        info["title"] = title

        published_class = "tm-article-snippet__datetime-published"
        data_published = soup.findAll("span", class_=published_class)
        validation_count(need=1, get=len(data_published), add_info="Habre parse page error date_published")
        date_published = datetime.fromisoformat(
            data_published[0].find("time", datetime=True)["datetime"].replace("Z", ""))
        info["date_published"] = date_published

        info["link"] = self._get_url(url)

        author_class = "tm-user-info__username"
        links_to_author = soup.findAll("a", class_=author_class, href=True)
        validation_count(need=1, get=len(links_to_author), add_info="Habr parse page error link_to_author")
        link_to_author = self._get_url(links_to_author[0]["href"])
        info["link_to_author"] = link_to_author
        return info


class Habr:
    _is_work: bool = False
    _tasks: {Task, ...}
    _parser: "IParser" = HabrParser()

    def __init__(self, _db):
        self._db = _db
        self._tasks = set()

    @property
    def tasks(self):
        return self._tasks

    @property
    def is_work(self):
        return self._is_work

    async def async_start(self):
        if self._is_work:
            return
        self._is_work = True
        task = asyncio.create_task(self._work_process(), name="_work_process")
        self._tasks.add(task)

    async def async_stop(self):
        if not self._is_work:
            return
        self._is_work = False
        for task in self.tasks:
            await task
        self._tasks.clear()

    async def _fetch_urls(self, urls: list):
        try:
            async with ClientSession() as session:
                tasks = tuple(asyncio.ensure_future(self._get_info_and_append_db(url, session)) for url in urls)
                articles = await asyncio.gather(*tasks)
            Articles.my_save(self._db.session, articles)
        except Exception as e:
            print("Ошибка:", e)

    async def _get_info_and_append_db(self, url: str, session):
        """ append db without commit """
        async with session.get(url) as response:
            html = await response.read()
            try:
                info = self._parser.get_info_page(url=url, html=html)
            except Exception as e:
                print("Ошибка", e)
            return info

    async def _work_process(self):
        while self._is_work:
            start = time.time()
            urls = self._parser.get_urls_to_main_articles()
            task = asyncio.create_task(self._work(urls))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
            end = time.time()
            await asyncio.sleep(float(os.getenv("PARSER_HABR_SECOND")) - (end - start))

    async def _work(self, urls: list):
        await self._fetch_urls(urls)
