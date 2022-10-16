import os
from pathlib import Path
from random import choice
from typing import Any, List, Optional
from uuid import UUID, uuid4

import psycopg2
from movies_converter_src.core.config.db import DBConfig, get_converter_db_config
from movies_converter_src.core.logger.logger import logger
from movies_converter_src.extract.BaseMovieFilesExtractor import BaseMovieFilesExtractor
from movies_converter_src.models.film import Film, Films


class DBMovieFilesExtractor(BaseMovieFilesExtractor):
    def __init__(self, *args, **kwargs) -> None:
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
        query_path: Path = Path(Path(__file__).parent.resolve(), Path(db_config.extract_query_location))

        with open(query_path) as query_file:
            self.query: str = query_file.read()

        logger.info(self.query)

    def _fetch_db(self) -> List[Any]:
        try:
            with psycopg2.connect(**self.dsn) as conn, conn.cursor() as cursor:
                cursor.execute(self.query)
                extracted_movies = cursor.fetchall()
                logger.info(type(extracted_movies))
                return extracted_movies
            conn.close()
        except psycopg2.OperationalError as e:
            logger.exception(e)
        return []

    def extract_movies(self, *args, **kwargs) -> Films:
        films: List[Film] = []
        extracted_movies: List[Any] = self._fetch_db()

        for movie_row in extracted_movies:
            source_resolution = 2160
            logger.info(movie_row)
            films.append(
                Film(
                    film_id=UUID(movie_row[0]),
                    file_name=os.path.basename(movie_row[2]).split('.')[0],
                    destination_path="/files/",
                    source_path=movie_row[2],
                    source_resolution=source_resolution,
                    reqired_resolutions=[
                        resolution for resolution in self.resolutions if resolution < source_resolution
                    ],)
            )

        return Films(films=films)
