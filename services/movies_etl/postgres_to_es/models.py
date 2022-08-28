from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class ModeETL(Enum):
    FILM_WORK = 'film_work'
    PERSON = 'person'
    GENRE = 'genre'


@dataclass
class ShortFilm:
    id: str
    title: str
    type: str = ''
    rating: float = None


@dataclass
class ShortPerson:
    id: str
    name: str


@dataclass
class ShortFile:
    id: str
    path: str


@dataclass
class Person(ShortPerson):
    roles: List[str] = field(default_factory=list)
    films: List[ShortFilm] = field(default_factory=list)

    def add_role(self, role: str):
        if role not in self.roles:
            self.roles.append(role)

    def add_film(self, film: ShortFilm):
        if film not in self.films:
            self.films.append(film)

    @property
    def as_dict(self):
        return asdict(self)


@dataclass
class ShortGenre:
    id: str
    name: str


@dataclass
class Genre(ShortGenre):
    description: str

    @property
    def as_dict(self):
        return asdict(self)


@dataclass
class Film(ShortFilm):
    description: str = ''
    creation_date: datetime = None
    genre: List[ShortGenre] = field(default_factory=list)
    actors: List[ShortPerson] = field(default_factory=list)
    writers: List[ShortPerson] = field(default_factory=list)
    directors: List[ShortPerson] = field(default_factory=list)
    high_quality_file: List[ShortFile] = field(default_factory=list)
    middle_quality_file: List[ShortFile] = field(default_factory=list)
    low_quality_file: List[ShortFile] = field(default_factory=list)

    def add_genre(self, gen: ShortGenre):
        if gen not in self.genre:
            self.genre.append(gen)

    def add_person(self, person: ShortPerson, role: str):
        if role == 'actor':
            if person not in self.actors:
                self.actors.append(person)
        elif role == 'writer':
            if person not in self.writers:
                self.writers.append(person)
        elif role == 'director':
            if person not in self.directors:
                self.directors.append(person)

    def add_video(self, file: ShortFile, width: int):
        if width:
            if 720 <= width:
                if file not in self.high_quality_file:
                    self.high_quality_file.append(file)
            elif 480 <= width < 720:
                if file not in self.middle_quality_file:
                    self.middle_quality_file.append(file)
            elif width < 480:
                if file not in self.low_quality_file:
                    self.low_quality_file.append(file)

    @property
    def as_dict(self):
        return asdict(self)
