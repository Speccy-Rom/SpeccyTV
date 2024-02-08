import os
import logging
from pathlib import Path

from pydantic import BaseSettings

from models import Queries

# Initialize the path to the file containing queries
queries_file_path = Path('configs/queries.json')


def set_logger() -> logging.Logger:
    """
    Set up and initialize logging.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel('DEBUG')
    handler = logging.StreamHandler()
    log_format = '%(asctime)s | %(levelname)s --> %(message)s'
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class KafkaConfigs(BaseSettings):
    """
    Model for Kafka configuration settings.
    """

    host = os.environ.get('KAFKA_HOST', 'localhost')  # Kafka host
    port = os.environ.get('KAFKA_PORT', 9092)  # Kafka port
    topics = os.environ.get('KAFKA_TOPICS')  # Kafka topics


class ClickHouseConfigs(BaseSettings):
    """
    Model for ClickHouse configuration settings.
    """

    host = os.environ.get('CLICKHOUSE_HOST', 'localhost')  # ClickHouse host
    database = os.environ.get('CLICKHOUSE_DB', 'default')  # ClickHouse database
    tables = os.environ.get('KAFKA_TOPICS')  # ClickHouse tables
    max_batch_len = int(
        os.environ.get('CLICKHOUSE_MAX_BATCH_LEN', 10)
    )  # Maximum batch length for ClickHouse


class ETLConfigs(BaseSettings):
    """
    Model for ETL configuration settings.
    """

    logger = set_logger()  # Logger
    kafka = KafkaConfigs()  # Kafka configurations
    queries = Queries.parse_file(queries_file_path)  # Queries
    click = ClickHouseConfigs()  # ClickHouse configurations
