import json
import time

import backoff
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from clickhouse_driver import Client

from config import ETLConfigs
from services import Extractor, Transformer, Loader, ClickManager


@backoff.on_exception(backoff.expo, NoBrokersAvailable)
def init_consumer(conf: ETLConfigs) -> list[KafkaConsumer]:
    try:
        consumers_list = []
        for topic in conf.kafka.topics.split(','):
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=[f"{conf.kafka.host}:{conf.kafka.port}"],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                enable_auto_commit=False,
                group_id='users_group',
            )
            consumers_list.append(consumer)

        return consumers_list

    except NoBrokersAvailable:
        conf.logger.info(
            "Error: Брокер Kafka не обнаружен, ожидание брокера..."
        )
        time.sleep(15)
        raise NoBrokersAvailable

    except ValueError:
        conf.logger.info(
            "Error: Брокер Kafka еще не запустился, ожидание брокера..."
        )
        time.sleep(15)
        raise NoBrokersAvailable


if __name__ == '__main__':
    configs = ETLConfigs()
    consumers = init_consumer(conf=configs)

    extractor = Extractor(consumers=consumers, logger=configs.logger)
    transformer = Transformer(extractor=extractor)

    client = Client(host=configs.click.host)
    click_manager = ClickManager(
        client=client,
        queries=configs.queries,
        logger=configs.logger
    )

    loader = Loader(
        consumers=consumers,
        click_manager=click_manager,
        transformer=transformer,
        configs=configs.click,
        logger=configs.logger)

    loader.run()
