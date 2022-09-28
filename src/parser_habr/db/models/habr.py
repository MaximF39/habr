from sqlalchemy import Column, Integer, DateTime, String

from db.models import Base

__all__ = (
    "Articles",
)


class Articles(Base):
    __tablename__ = "parse_habr_articles"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    title = Column(String(length=2000), nullable=False)
    date_published = Column(DateTime(), nullable=False)
    link = Column(String(length=4000), nullable=False, unique=True)
    link_to_author = Column(String(length=4000), nullable=False, primary_key=True)

    @staticmethod
    def my_save(session, articles):
        for info in articles:
            exist = session.query(Articles.link).filter_by(
                link=info["link"]).first() is not None
            print(("Exist" if exist else "Create"), "parse date:", info)
            if not exist:
                session.add(Articles(**info))
        session.commit()
