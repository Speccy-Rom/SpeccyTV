from abc import ABC, abstractmethod
from typing import List

from movies_converter_src.core.config.etl import get_config
from movies_converter_src.models.film import Films


class BaseMovieFilesExtractor(ABC):
    def __init__(self):
        self.resolutions: List[int] = get_config().resolutions

    @abstractmethod
    def extract_movies(self, *args, **kwargs) -> Films:
        raise NotImplementedError("func extract_movies should have been implemented")
