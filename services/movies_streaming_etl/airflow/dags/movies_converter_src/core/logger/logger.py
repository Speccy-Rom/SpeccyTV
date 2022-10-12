from logging import Logger

from airflow.utils.log.logging_mixin import LoggingMixin

logger: Logger = LoggingMixin().log
