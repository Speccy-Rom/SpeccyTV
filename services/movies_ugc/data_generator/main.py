import time
from logging import Logger

import backoff
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaConnectionError, TopicAlreadyExistsError

from services import Generator, Creator
from config import GeneratorConfigs, logger


class Worker:

    def __init__(self, creator: Creator,
                 kafka_admin: KafkaAdminClient,
                 kafka_producer: KafkaProducer,
                 kafka_topics: list,
                 logger: Logger):
        self.creator = creator
        self.kafka_admin = kafka_admin
        self.kafka_producer = kafka_producer
        self.kafka_topics = kafka_topics
        self.logger = logger

    def create_topics(self):
        kafka_topics = self.kafka_admin.list_topics()
        added_topics = []
        for topic in self.kafka_topics:
            if topic not in kafka_topics:
                new_topic = NewTopic(
                    name=topic,
                    num_partitions=1,
                    replication_factor=1
                )
                added_topics.append(new_topic)

        if len(added_topics) != 0:
            try:
                self.kafka_admin.create_topics(new_topics=added_topics)
            except TopicAlreadyExistsError as e:
                self.logger.info(f"Error: {e}")

    @backoff.on_exception(backoff.expo, KafkaConnectionError)
    def listener(self):
        if not self.kafka_producer.bootstrap_connected():
            self.logger.info("Error: Отсутствует подключение к Kafka")
            time.sleep(10)
            self.creator.connect()
            raise KafkaConnectionError

        self.creator.create()

    def run(self):
        self.create_topics()

        while True:
            self.listener()


if __name__ == '__main__':
    configs = GeneratorConfigs()
    kafka_admin = KafkaAdminClient(
        bootstrap_servers=[f"{configs.host}:{configs.port}"]
    )
    kafka_producer = KafkaProducer(
        bootstrap_servers=[f"{configs.host}:{configs.port}"]
    )
    generator = Generator()
    creator = Creator(generator=generator, configs=configs, logger=logger)
    worker = Worker(creator=creator,
                    kafka_admin=kafka_admin,
                    kafka_producer=kafka_producer,
                    kafka_topics=configs.topics,
                    logger=logger)
    worker.run()
