import os
import logging

from pydantic import BaseSettings


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


logger = set_logger()


class GeneratorConfigs(BaseSettings):
    host = os.environ.get('KAFKA_HOST', 'localhost')
    port = os.environ.get('KAFKA_PORT', 9092)
    topics = ['user_events', 'users_login']