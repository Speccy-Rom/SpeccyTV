from logging import Logger

from pydantic import BaseModel
from kafka import KafkaConsumer

from .transformer import Transformer
from .clickhouse_manager import ClickManager
from config import ClickHouseConfigs


class Loader:

    def __init__(self,
                 consumers: list[KafkaConsumer],
                 click_manager: ClickManager,
                 transformer: Transformer,
                 configs: ClickHouseConfigs,
                 logger: Logger):
        self.consumers = consumers
        self.click_manager = click_manager
        self.configs = configs
        self.transformer = transformer
        self.data_to_loaded = {}
        self.logger = logger

    def check_batch_len(self, batch: list) -> bool:
        return len(batch) == self.configs.max_batch_len

    def get_batch(self, table_name: str) -> list:
        batch = self.data_to_loaded.get(table_name)

        if batch is None:
            self.data_to_loaded[table_name] = []
            return self.data_to_loaded[table_name]

        return batch

    def load(self, data: BaseModel):
        table_name, fields = data.ch_table_properties()
        batch = self.get_batch(table_name=table_name)
        if self.check_batch_len(batch=batch):
            self.logger.info(
                f"Загрузка Данных в ClickHouse. Таблица: {table_name}"
            )
            if status := self.click_manager.create(
                item='data',
                data=batch,
                db_name=self.configs.database,
                table_name=table_name,
                fields=fields,
            ):
                for consumer in self.consumers:
                    if table_name in consumer.subscription():
                        consumer.commit()

                self.data_to_loaded[table_name] = []

        else:
            batch.append(data.dict())

    def run(self):
        for data in self.transformer.run():
            self.load(data=data)
