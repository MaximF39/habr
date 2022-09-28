import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

from db import Articles
from db.models import Base
from utils import singleton

__all__ = (
    "DB",
)

load_dotenv()


@singleton
class _DB:

    def __init__(self):
        engine = create_engine(f"postgresql+psycopg2://" +
                               os.getenv("DATABASE_USER") + ":" +
                               os.getenv("DATABASE_PASSWORD") + "@" +
                               os.getenv("DATABASE_HOST") + ":" +
                               os.getenv("DATABASE_PORT") + "/" +
                               os.getenv("DATABASE_NAME"),
                               pool_pre_ping=True, echo=0)
        Base.metadata.create_all(engine)
        session_factory = sessionmaker(bind=engine)
        self.__session = scoped_session(session_factory)()

    @property
    def session(self):
        return self.__session

    def save_articles(self, articles: list) -> None:
        for info in articles:
            exist = self.session.query(Articles.link).filter_by(
                link=info["link"]).first() is not None
            print(("Exist" if exist else "Create"), "parse date:", info)
            if not exist:
                self.session.add(Articles(**info))
        self.session.commit()


DB = _DB()
