import datetime

from pydantic import BaseModel, validator


class UserEvent(BaseModel):

    movie_id: str
    user_id: str
    event: str
    frame: int
    event_time: datetime.datetime

    def ch_table_properties(self) -> [str, str]:
        """
            :return: Возвращает названия таблицы
            (table_name) и столбцов (fields)
        """
        table_name = "user_events"
        fields = f"{', '.join(field for field in self.__fields__.keys())}"
        return table_name, fields

    @validator('event_time', pre=True, always=True)
    def event_time_validator(cls, v):
        return datetime.datetime.strptime(v, "%d-%m-%Y %H:%M:%S")


class UserLoginHistory(BaseModel):

    user_id: str
    user_ip: str
    user_agent: str
    login_time: datetime.datetime

    def ch_table_properties(self) -> [str, str]:
        """
            :return: Возвращает названия таблицы
            (table_name) и столбцов (fields)
        """
        table_name = "users_login"
        fields = f"{', '.join(field for field in self.__fields__.keys())}"
        return table_name, fields

    @validator('login_time', pre=True, always=True)
    def login_time_validator(cls, v):
        return datetime.datetime.strptime(v, "%d-%m-%Y %H:%M:%S")


class CreateQueries(BaseModel):
    database: str
    table: str
    data: str


class ReadQueries(BaseModel):
    databases: str
    tables: str
    data: str


class Queries(BaseModel):

    create: CreateQueries
    read: ReadQueries
    update: dict
    delete: dict
