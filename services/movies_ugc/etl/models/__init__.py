from .models import UserEvent, UserLoginHistory, Queries  # noqa: F401, E501

KAFKA_TOPIC_MODELS = [UserEvent, UserLoginHistory]
