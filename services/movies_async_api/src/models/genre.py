from models.base import BaseGetAPIModel


class BaseGenre(BaseGetAPIModel):
    name: str


class Genre(BaseGenre):
    description: str = None
