import asyncio
import time
from datetime import datetime

import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from db import Articles
from db.db import DB
from utils.utils import validation_count


class HabrParse:
    _prefix_url = "https://habr.com"

    @property
    def prefix_url(self):
        return self._prefix_url

    @property
    def main_article_urls(self):
        soup = self._get_soup("/ru/all")
        class_main_article = "tm-article-snippet__title-link"
        main_titles = soup.findAll("a", class_=class_main_article, href=True)
        return list(map(lambda el: self._get_url(el["href"]), main_titles))

    def _get_soup(self, url) -> BeautifulSoup:
        return BeautifulSoup(self._get_page(url), features="html.parser")

    def _get_page(self, url: str) -> str:
        """ url: url or postfix """
        url = self._get_url(url)
        response = requests.get(url)
        if response.status_code != 200:
            raise requests.exceptions.ConnectionError
        return response.text

    def _get_url(self, url):
        return url if url.startswith(self._prefix_url) else self._prefix_url + url

    def get_info_page(self, url: str, html: str = None) -> dict:
        info = {}
        soup = BeautifulSoup(html, features="html.parser") if html is not None else self._get_soup(url)
        title_class = "tm-article-snippet__title tm-article-snippet__title_h1"
        titles = soup.findAll("h1", class_=title_class)

        validation_count(need=1, get=len(titles), add_info="Error titles")
        info["title"] = titles[0].find("span").text
        published_class = "tm-article-snippet__datetime-published"

        data_published = soup.findAll("span", class_=published_class)
        validation_count(need=1, get=len(data_published), add_info="Error published")
        info["date_published"] = datetime.fromisoformat(
            data_published[0].find("time", datetime=True)["datetime"].replace("Z", ""))
        info["link"] = self._get_url(url)
        author_class = "tm-user-info__username"

        data_published = soup.findAll("a", class_=author_class, href=True)
        validation_count(need=1, get=len(data_published), add_info="Error published")
        info["link_to_author"] = self._get_url(data_published[0]["href"])
        return info


class Habr:
    _isWork = False
    _task = None
    _parser = HabrParse()
    _db = DB()

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
            t = time.time()
            urls = self._parser.main_article_urls
            asyncio.create_task(self._work(urls))
            await asyncio.sleep(int(10 * 60 - (time.time() - t)))

    async def async_stop(self):
        if not self._isWork:
            return
        self._isWork = False
        self._task.cancel()
        self._task = None

    async def _fetch_urls(self, urls):
        tasks = []
        async with ClientSession() as session:
            for url in urls:
                task = asyncio.ensure_future(self._get_info_and_append_db(url, session))
                tasks.append(task)
            await asyncio.gather(*tasks)
            self._db.session.commit()

    async def _get_info_and_append_db(self, url, session):
        """ append db without commit """
        async with session.get(url) as response:
            resp = await response.read()
            info = self._parser.get_info_page(url=url, html=resp)
            no_exist = self._db.session.query(Articles.id).filter_by(
                link=info["link"], link_to_author=info["link_to_author"]).first() is None
            print("Create" if no_exist else "Exist", "parse date:", info)
            if no_exist:
                self._db.session.add(Articles(**info))

    async def _work(self, urls):
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self._fetch_urls(urls))
        loop.run_until_complete(future)
