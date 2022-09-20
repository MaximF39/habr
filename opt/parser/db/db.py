import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

from db.models.base import Base
from utils import singleton

load_dotenv()


@singleton
class DB:

    def __init__(self):
        engine = create_engine(f"postgresql+psycopg2://" +
                               os.environ.get("DATABASE_USER") + ":" +
                               os.environ.get("DATABASE_PASSWORD") + "@" +
                               os.environ.get("DATABASE_HOST") + ":" +
                               os.environ.get("DATABASE_PORT") + "/" +
                               os.environ.get("DATABASE_NAME"),
                               pool_pre_ping=True, echo=1)
        Base.metadata.create_all(engine)
        session_factory = sessionmaker(bind=engine)
        self.__session = scoped_session(session_factory)()

    @property
    def session(self):
        return self.__session
