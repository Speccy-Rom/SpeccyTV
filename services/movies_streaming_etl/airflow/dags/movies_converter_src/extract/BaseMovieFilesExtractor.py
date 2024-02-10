from abc import ABC, abstractmethod
from typing import List

from movies_converter_src.core.config.etl import get_config
from movies_converter_src.models.film import Films


class BaseMovieFilesExtractor(ABC):
    """
    A base class for extracting movie files.

    ...

    Attributes
    ----------
    resolutions : List[int]
        a list of resolutions for the movie files

    Methods
    -------
    extract_movies(*args, **kwargs):
        Abstract method for extracting movie files. Must be implemented by subclasses.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the BaseMovieFilesExtractor object.

        Attributes
        ----------
        resolutions : List[int]
            a list of resolutions for the movie files, fetched from the configuration
        """
        self.resolutions: List[int] = get_config().resolutions

    @abstractmethod
    def extract_movies(self, *args, **kwargs) -> Films:
        """
        Abstract method for extracting movie files. Must be implemented by subclasses.

        Parameters
        ----------
            *args :
                Variable length argument list.
            **kwargs :
                Arbitrary keyword arguments.

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a subclass.
        """
        raise NotImplementedError("func extract_movies should have been implemented")
