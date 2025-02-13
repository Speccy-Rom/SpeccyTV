import backoff
from logging import Logger
from typing import Optional, List

from clickhouse_driver import Client
from clickhouse_driver.errors import NetworkError

from models import Queries


class ClickManager:
    """
    Класс для работы с ClickHouse
    """
    def __init__(self, client: Client, queries: Queries, logger: Logger):
        self.client = client
        self.queries = queries
        self.logger = logger

    def get_query(self, action: str, item: str) -> str:
        action_obj = getattr(self.queries, action)
        return getattr(action_obj, item)

    @backoff.on_exception(backoff.expo, NetworkError)
    def create(self, item: str, data: Optional[List[dict]] = None, **kwargs) -> bool:
        query = self.get_query(action='create', item=item)

        try:
            format_query = query.format(**kwargs)

            if data is not None:
                self.client.execute(format_query, data)
            else:
                self.client.execute(format_query)

            return True

        except NetworkError as e:
            self.logger.info(f"Ошибка подключения к ClickHouse: {e}")
            raise

        except Exception as e:
            self.logger.info(f"Error: {e}")
            return False
