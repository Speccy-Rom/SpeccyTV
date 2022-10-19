from abc import ABC, abstractmethod

from airflow.utils.log.logging_mixin import LoggingMixin
from movies_converter_src.models.film import LoaderResults, TransformResults


class BaseMovieFilesLoader(ABC):
    def __init__(self, transform_results: str, *args, **kwargs) -> None:

        self.transform_results: TransformResults = TransformResults.parse_raw(transform_results)

    @abstractmethod
    def load(self, *args, **kwargs) -> LoaderResults:
        "Main loader func"
        raise NotImplementedError("func load should have been implemented")
