import enum

from sqlalchemy import ForeignKey, Enum

from .base import AbstractModel, RequiredColumn


class Status(str, enum.Enum):
    WAIT_PAYMENT = 'wait_payment'
    PAID = 'paid'
    ERROR = 'error'


class Payment(AbstractModel):
    __tablename__ = "payment"

    subscription_id = RequiredColumn(ForeignKey("subscription.id"))
    status = RequiredColumn(Enum(Status, name='payment_status'))
