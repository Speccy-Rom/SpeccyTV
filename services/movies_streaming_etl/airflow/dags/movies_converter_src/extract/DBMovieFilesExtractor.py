import os
from pathlib import Path
from typing import Any, List
from uuid import UUID

import psycopg2
from core.config.db import DBConfig, get_converter_db_config
from core.logger.logger import logger
from extract.BaseMovieFilesExtractor import BaseMovieFilesExtractor
from models.film import Film, Films


class DBMovieFilesExtractor(BaseMovieFilesExtractor):
    """
    A class used to extract movie files from a database.

    ...

    Attributes
    ----------
    dsn : dict
        a dictionary containing the database connection parameters
    query : str
        the SQL query to be executed

    Methods
    -------
    _fetch_db():
        Executes the SQL query and fetches the results.
    extract_movies(*args, **kwargs):
        Extracts movie files from the database and returns a list of Film objects.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Constructs all the necessary attributes for the DBMovieFilesExtractor object.

        Parameters
        ----------
            *args :
                Variable length argument list.
            **kwargs :
                Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        db_config: DBConfig = get_converter_db_config()
        self.dsn = {
            "dbname": db_config.postgres_db,
            "user": db_config.postgres_user,
            "password": db_config.postgres_password,
            "host": db_config.postgres_host,
            "port": db_config.postgres_port,
            "options": "-c search_path=content",
        }
        query_path: Path = Path(
            Path(__file__).parent.resolve(), Path(db_config.extract_query_location)
        )

        self.query: str = Path(query_path).read_text()
        logger.info(self.query)

    def _fetch_db(self) -> List[Any]:
        """
        Executes the SQL query and fetches the results.

        Returns
        -------
        list
            a list of tuples containing the movie data
        """
        try:
            with psycopg2.connect(**self.dsn) as conn, conn.cursor() as cursor:
                cursor.execute(self.query)
                extracted_movies = cursor.fetchall()
                logger.info(type(extracted_movies))
                return extracted_movies
        except psycopg2.OperationalError as e:
            logger.exception(e)
            return []

    def extract_movies(self, *args, **kwargs) -> Films:
        """
        Extracts movie files from the database and returns a list of Film objects.

        Parameters
        ----------
            *args :
                Variable length argument list.
            **kwargs :
                Arbitrary keyword arguments.

        Returns
        -------
        Films
            a Films object containing a list of Film objects
        """
        films: List[Film] = []
        extracted_movies: List[Any] = self._fetch_db()

        source_resolution = 2160
        for movie_row in extracted_movies:
            logger.info(movie_row)
            films.append(
                Film(
                    film_id=UUID(movie_row[0]),
                    file_name=os.path.basename(movie_row[2]).split('.')[0],
                    destination_path="/files/",
                    source_path=movie_row[2],
                    source_resolution=source_resolution,
                    reqired_resolutions=[
                        resolution
                        for resolution in self.resolutions
                        if resolution < source_resolution
                    ],
                )
            )

        return Films(films=films)
