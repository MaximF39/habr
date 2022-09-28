from sqlalchemy import Column, Integer, DateTime, String

from db.models import Base

__all__ = (
    "Articles",
)


class Articles(Base):
    __tablename__ = "parse_habr_articles"

    title = Column(String(length=2000), nullable=False)
    date_published = Column(DateTime(), nullable=False)
    link = Column(String(length=4000), nullable=False, primary_key=True)
    link_to_author = Column(String(length=4000), nullable=False, primary_key=True)
