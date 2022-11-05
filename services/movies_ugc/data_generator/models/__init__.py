from .models import UserEvent, \
    UserLoginHistory, KafkaModel, KafkaUserEvent, KafkaUserLoginHistory  # noqa: F401, E501

KAFKA_TOPIC_MODELS = [KafkaUserEvent, KafkaUserLoginHistory]
