from pydantic import Field

from models.base import BaseGetAPIModel
from models.genre import BaseGenre
from models.person import BasePerson


class BaseFilm(BaseGetAPIModel):
    title: str
    rating: float = Field(None, alias='imdb_rating')


class BaseFile(BaseGetAPIModel):
    path: str


class Film(BaseFilm):
    description: str = None
    genre: list[BaseGenre] = None
    actors: list[BasePerson] = None
    writers: list[BasePerson] = None
    directors: list[BasePerson] = None
    high_quality_file: list[BaseFile] = None
    middle_quality_file: list[BaseFile] = None
    low_quality_file: list[BaseFile] = None