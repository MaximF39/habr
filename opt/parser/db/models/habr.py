from sqlalchemy import Column, Integer, DateTime, String

from db.models.base import Base


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


class Articles(BaseModel):
    __tablename__ = "parse_habr_articles"

    title = Column(String(length=2000), nullable=False)
    date_published = Column(DateTime(), nullable=False)
    link = Column(String(length=4000), nullable=False)
    link_to_author = Column(String(length=4000), nullable=False)
