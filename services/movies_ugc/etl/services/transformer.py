from pydantic import ValidationError

from .extractor import Extractor
from models import KAFKA_TOPIC_MODELS


class Transformer:

    def __init__(self, extractor: Extractor):
        self.extractor = extractor

    @staticmethod
    def validation(data):
        for model in KAFKA_TOPIC_MODELS:
            try:
                validated_data = model.parse_obj(data)
                return validated_data
            except ValidationError:
                continue

    def run(self):
        for data in self.extractor.run():
            yield self.validation(data)
