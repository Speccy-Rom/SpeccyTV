from datetime import date
from pydantic import BaseModel


class ShortFilm(BaseModel):
    id: str
    title: str
    type: str = None
    rating: float = None


class ShortPerson(BaseModel):
    id: str
    name: str


class Person(ShortPerson):
    roles: list[str] = None
    films: list[ShortFilm] = None


class ShortGenre(BaseModel):
    id: str
    name: str


class Genre(ShortGenre):
    description: str = None


class Film(ShortFilm):
    description: str = None
    creation_date: date = None
    genre: list[ShortGenre] = None
    actors: list[ShortPerson] = None
    writers: list[ShortPerson] = None
    directors: list[ShortPerson] = None