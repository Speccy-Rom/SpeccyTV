from functools import partial

from sqlalchemy import Column, Integer

from db.session import Base


class AbstractModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)


RequiredColumn = partial(Column, nullable=False)
