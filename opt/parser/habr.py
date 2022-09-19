from datetime import datetime
from threading import Thread
from time import sleep

import requests
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
        return list(map(lambda el: el["href"], main_titles))

    def _get_soup(self, url) -> BeautifulSoup:
        return BeautifulSoup(self._get_page(url), features="html.parser")

    def _get_page(self, url: str) -> str:
        """ url: url or postfix """
        url = self._get_url(url)
        req = requests.get(url)
        if req.status_code != 200:
            raise requests.exceptions.ConnectionError
        return req.text

    def _get_url(self, url):
        return url if url.startswith(self._prefix_url) else self._prefix_url + url

    def get_info_page(self, url: str) -> dict:
        info = {}
        soup = self._get_soup(url)
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
    _thrWork = None
    _parser = HabrParse()
    _db = DB()

    def start(self):
        if self._isWork:
            return
        self._isWork = True
        self._thrWork = Thread(target=self._work)
        self._thrWork.start()

    def stop(self):
        if not self._isWork:
            return
        self._isWork = False
        self._thrWork.join()
        self._thrWork = None

    def _work(self):
        while self._isWork:
            try:
                urls = self._parser.main_article_urls
                for url in urls:
                    info = self._parser.get_info_page(url=url)
                    exist = self._db.session.query(Articles.id).filter_by(
                        link=info["link"], link_to_author=info["link_to_author"]).first() is not None
                    print("Exist" if exist else "Create", "parse date:", info)
                    if exist is None:
                        self._db.session.add(Articles(**info))
                        self._db.session.commit()
                sleep(10 * 60)
            except BaseException as e:
                print("Ошибка:", e)
