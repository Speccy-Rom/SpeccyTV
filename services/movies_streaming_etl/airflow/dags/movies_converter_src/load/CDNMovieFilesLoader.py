from datetime import datetime, timezone
from pathlib import Path
from typing import List
from uuid import uuid4

import psycopg2
from movies_converter_src.core.config.converter_api import ConverterAPIConfig, get_converter_API_config
from movies_converter_src.core.config.db import DBConfig, get_converter_db_config
from movies_converter_src.core.logger.logger import logger
from movies_converter_src.load.BaseMovieFilesLoader import BaseMovieFilesLoader
from movies_converter_src.models.film import Film, Films, LoaderResults


class CDNMovieFilesLoader(BaseMovieFilesLoader):
    def __init__(self, transform_results: str, *args, **kwargs) -> None:
        super().__init__(transform_results, *args, **kwargs)
        self.config: ConverterAPIConfig = get_converter_API_config()
        db_config: DBConfig = get_converter_db_config()
        self.dsn = {
            "dbname": db_config.postgres_db,
            "user": db_config.postgres_user,
            "password": db_config.postgres_password,
            "host": db_config.postgres_host,
            "port": db_config.postgres_port,
            "options": "-c search_path=content",
        }
        self.query_path: Path = Path(Path(__file__).parent.resolve(), Path(db_config.load_query_location))

        logger.info(self.query_path)

    def _build_query(self) -> str:
        query_values: List[str] = []
        for transform_result in self.transform_results.results:
            for film_file in transform_result.film_files:
                query_values.append(
                    "(" + ",".join(
                        (
                            f"'{str(uuid4())}'",
                            f"'{film_file.destination_path}/{film_file.file_name}_{str(film_file.resolution)}p.avi'",
                            f"'{str(film_file.resolution)}p'",
                            f"'{str(datetime.now(timezone.utc))}'",
                            f"'{str(datetime.now(timezone.utc))}'",
                        )
                    ) + ")"
                )
        with open(self.query_path) as query_file:
            query: str = query_file.read()

        logger.info(query)
        return query.format(",".join(query_values))

    def _update_db(self):
        if not self.transform_results.results:
            return

        query: str = self._build_query()
        try:
            with psycopg2.connect(**self.dsn) as conn, conn.cursor() as cursor:
                cursor.execute(query)
            conn.close()
        except psycopg2.OperationalError as e:
            logger.exception(e)

    def load(self, *args, **kwargs) -> LoaderResults:
        self._update_db()

        return LoaderResults(
            loaded_files=len(self.transform_results.results),
            updated_movies=len(self.transform_results.results),
        )
