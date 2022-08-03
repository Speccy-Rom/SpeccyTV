import enum

from sqlalchemy import ForeignKey, Date, Enum

from .base import AbstractModel, RequiredColumn


class Status(str, enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ENDING = 'ending'
    WAIT_PAYMENT = 'wait_payment'
    NEW = 'NEW'


class Subscription(AbstractModel):
    __tablename__ = "subscription"

    customer_id = RequiredColumn(ForeignKey("customer.id"))
    status = RequiredColumn(Enum(Status, name='subscription_status'))
    tariff_id = RequiredColumn(ForeignKey("tariff.id"))
    date_begin = RequiredColumn(Date)
    date_end = RequiredColumn(Date)
