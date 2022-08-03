from sqlalchemy import String

from .base import AbstractModel, RequiredColumn


class Customer(AbstractModel):
    __tablename__ = "customer"

    user_id = RequiredColumn(String(50))
    stripe_customer_id = RequiredColumn(String(50))
