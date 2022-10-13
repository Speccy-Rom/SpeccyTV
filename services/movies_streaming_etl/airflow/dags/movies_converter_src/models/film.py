from lib2to3.pytree import convert
from typing import List
from uuid import UUID

from pydantic import BaseModel


class Film(BaseModel):
    "Event for sending notification"
    film_id: UUID
    file_name: str
    reqired_resolutions: List[int]
    source_resolution: int
    source_path: str
    destination_path: str


class Films(BaseModel):
    films: List[Film]


class FilmFile(BaseModel):
    resolution: int
    destination_path: str
    file_name: str
    succeded: bool


class TransformResult(BaseModel):
    film_id: UUID
    film_files: List[FilmFile]


class TransformResults(BaseModel):
    results: List[TransformResult]


class LoaderResults(BaseModel):
    errors: List[str] = []
    loaded_files: int
    updated_movies: int
