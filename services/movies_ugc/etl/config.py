import os
import logging
from pathlib import Path

from pydantic import BaseSettings

from models import Queries

# Инициализация пути к файлу с запросами
queries_file_path = Path('configs/queries.json')


# Настройка и инициализация логирования
def set_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel('DEBUG')
    handler = logging.StreamHandler()
    log_format = '%(asctime)s | %(levelname)s --> %(message)s'
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


# Модели с базовыми настройками
class KafkaConfigs(BaseSettings):
    host = os.environ.get('KAFKA_HOST', 'localhost')
    port = os.environ.get('KAFKA_PORT', 9092)
    topics = os.environ.get('KAFKA_TOPICS')


class ClickHouseConfigs(BaseSettings):
    host = os.environ.get('CLICKHOUSE_HOST', 'localhost')
    database = os.environ.get('CLICKHOUSE_DB', 'default')
    tables = os.environ.get('KAFKA_TOPICS')
    max_batch_len = int(os.environ.get('CLICKHOUSE_MAX_BATCH_LEN', 10))


class ETLConfigs(BaseSettings):
    logger = set_logger()
    kafka = KafkaConfigs()
    queries = Queries.parse_file(queries_file_path)
    click = ClickHouseConfigs()
