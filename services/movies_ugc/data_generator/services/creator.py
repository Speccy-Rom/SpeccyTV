import json
from time import sleep
from random import randint
from logging import Logger

from pydantic import ValidationError, BaseModel
from kafka import KafkaProducer

from .generator import Generator
from models import KafkaModel, KAFKA_TOPIC_MODELS


class Creator:

    kafka_producer = None

    def __init__(self,
                 generator: Generator,
                 configs: BaseModel,
                 logger: Logger):
        self.generator = generator
        self.logger = logger
        self.configs = configs
        self.connect()

    def connect(self):
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=[
                f"{self.configs.host}:{self.configs.port}"
            ],
            key_serializer=lambda v: bytes(v, 'utf-8'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            reconnect_backoff_ms=100
        )

    @staticmethod
    def validate_data(data: dict) -> KafkaModel:
        for model in KAFKA_TOPIC_MODELS:
            try:
                return model.parse_dict(data)
            except ValidationError:
                continue

    def create(self):
        for data in self.generator.get_data():
            validated_data = self.validate_data(data)
            self.kafka_producer.send(**validated_data.dict())
            self.logger.info(f"Created values: {validated_data}")
            sleep(randint(3, 10))
