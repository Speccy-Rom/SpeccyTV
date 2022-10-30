from pydantic import BaseModel, ValidationError


# Модели данных для kafka
class UserEvent(BaseModel):

    movie_id: str
    user_id: str
    event: str
    frame: int
    event_time: str


class UserLoginHistory(BaseModel):

    user_id: str
    user_ip: str
    user_agent: str
    login_time: str


class KafkaModel(BaseModel):
    topic: str
    key: str
    value: dict

    @classmethod
    def parse_dict(cls, data: dict):
        pass


class KafkaUserEvent(KafkaModel):

    @classmethod
    def parse_dict(cls, data: dict):
        try:
            model_data = UserEvent.parse_obj(data)
            topic = "user_events"
            key = f"{model_data.user_id} {model_data.movie_id}"
            value = model_data.dict()
            return cls(topic=topic, key=key, value=value)
        except ValidationError as e:
            raise e


class KafkaUserLoginHistory(KafkaModel):

    @classmethod
    def parse_dict(cls, data: dict):
        try:
            model_data = UserLoginHistory.parse_obj(data)
            topic = "users_login"
            key = model_data.user_id
            value = model_data.dict()
            return cls(topic=topic, key=key, value=value)
        except ValidationError as e:
            raise e
