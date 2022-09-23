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
from db import DB
from utils import validation_count


class IParser(metaclass=ABCMeta):
    @property
    @abstractmethod
    def prefix_url(self) -> str:
        ...

    @abstractmethod
    def get_info_page(self, url: str, html: str | bytes) -> dict:
        ...

    @property
    @abstractmethod
    def main_article_urls(self) -> list:
        ...


class HabrParser(IParser):
    _prefix_url: str = "https://habr.com"

    @property
    def prefix_url(self) -> str:
        return self._prefix_url

    @property
    def main_article_urls(self) -> list:
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
    _isWork: bool = False
    _task: Task | None = None
    _parser: "IParser" = HabrParser()
    _db: "DB" = DB

    @property
    def task(self):
        return self._task

    @property
    def isWork(self):
        return self._isWork

    async def async_start(self):
        if self._isWork:
            return
        self._isWork = True
        while self._isWork:
            start = time.time()
            urls = self._parser.main_article_urls
            self._task = asyncio.create_task(self._work(urls))
            end = time.time()
            await asyncio.sleep(float(os.getenv("PARSER_HABR_SECOND")) - (end - start))

    async def async_stop(self):
        if not self._isWork:
            return
        self._isWork = False
        self._task.cancel()
        self._task = None

    async def _fetch_urls(self, urls: list):
        try:
            tasks = []
            async with ClientSession() as session:
                for url in urls:
                    task = asyncio.ensure_future(self._get_info_and_append_db(url, session))
                    tasks.append(task)
                await asyncio.gather(*tasks)
                self._db.session.commit()
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
            else:
                no_exist = self._db.session.query(Articles.id).filter_by(
                    link=info["link"], link_to_author=info["link_to_author"]).first() is None
                print("Create" if no_exist else "Exist", "parse date:", info)
                if no_exist:
                    self._db.session.add(Articles(**info))

    async def _work(self, urls: list):
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self._fetch_urls(urls))
        loop.run_until_complete(future)
