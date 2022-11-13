from queue import Queue
from threading import Thread
from logging import Logger

import backoff
from kafka import KafkaConsumer
from kafka.errors import KafkaConnectionError


class Extractor:

    def __init__(self, consumers: list[KafkaConsumer], logger: Logger):
        self.consumers = consumers
        self.data_queue = Queue()
        self.logger = logger

    @backoff.on_exception(backoff.expo, KafkaConnectionError)
    def consumer_listener(self, consumer: KafkaConsumer):
        if not consumer.bootstrap_connected():
            self.logger.info("Error: Отсутствует подключение к Kafka")
            raise KafkaConnectionError

        for message in consumer:
            self.data_queue.put(message.value)

    def run(self):
        for consumer in self.consumers:
            consumer_thread = Thread(
                target=self.consumer_listener,
                args=(consumer, )
            )
            consumer_thread.start()

        while True:
            data = self.data_queue.get()
            self.logger.info("Есть данные для загрузки в ClickHouse")
            yield data
