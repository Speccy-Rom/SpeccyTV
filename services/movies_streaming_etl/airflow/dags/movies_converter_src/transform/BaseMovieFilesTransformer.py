from abc import ABC, abstractmethod

from movies_converter_src.models.film import Films, TransformResults


class BaseMovieFilesTransformer(ABC):
    def __init__(self, extracted_movies: str):
        self.extracted_movies: Films = Films.parse_raw(extracted_movies)

    @abstractmethod
    def transform_movies(self, *args, **kwargs) -> TransformResults:
        "Main transform|convert func"
        raise NotImplementedError("func transform_movies should have been implemented")
