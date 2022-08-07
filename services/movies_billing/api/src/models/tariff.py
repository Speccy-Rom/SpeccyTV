from sqlalchemy import String, Integer, Boolean

from .base import AbstractModel, RequiredColumn


class Tariff(AbstractModel):
    __tablename__ = "tariff"

    name = RequiredColumn(String(100))
    description = RequiredColumn(String(255))
    price = RequiredColumn(Integer)
    duration = RequiredColumn(Integer)
    active = RequiredColumn(Boolean)
