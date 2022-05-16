from pydantic import Field

from models.base import BaseGetAPIModel


class BasePerson(BaseGetAPIModel):
    name: str = Field(..., alias='full_name')


class BasePersonFilm(BaseGetAPIModel):
    title: str
    rating: float = Field(None, alias='imdb_rating')


class Person(BasePerson):
    roles: list[str] = None
    films: list[BasePersonFilm] = None
