import datetime
import logging
from typing import List

from dateutil.relativedelta import relativedelta
from pydantic.main import BaseModel
from sqlalchemy import select, update

from db.session import db_session
from models.customer import Customer
from models.payment import Payment, Status as PaymentStatus
from models.subscription import Subscription, Status as SubscriptionStatus
from models.tariff import Tariff
from .payment_processor.abstract import PaymentProcessorAbstract


class PaymentSchema(BaseModel):
    id: int
    subscription_id: int
    date_end: datetime.date
    price: int
    duration: int
    stripe_customer_id: str

    def __str__(self):
        return f'Payment {self.id}, for subscription {self.subscription_id}, till {self.date_end}, ' \
               f'amount {self.price}, duration {self.duration}'


class PaymentService:
    def __init__(self, payment_processor: PaymentProcessorAbstract):
        self.payment_processor = payment_processor

    def _get_pending_payments(self) -> List[PaymentSchema]:
        payments = db_session.execute(
            select(
                Payment.id,
                Payment.subscription_id,
                Subscription.date_end,
                Tariff.price,
                Tariff.duration,
                Customer.stripe_customer_id,
            ).outerjoin(
                Subscription, Payment.subscription_id == Subscription.id
            ).outerjoin(
                Tariff, Subscription.tariff_id == Tariff.id
            ).outerjoin(
                Customer, Subscription.customer_id == Customer.id
            ).where(
                Payment.status == PaymentStatus.WAIT_PAYMENT
            )
        ).all()

        return [PaymentSchema(**payment_data) for payment_data in payments]

    def _update_subscription(self, payment: PaymentSchema, result: bool):
        logging.info(f'Update subscription. Payment result={result}')

        if result:
            payment_status = PaymentStatus.PAID
            subscription_status = SubscriptionStatus.ACTIVE
        else:
            payment_status = PaymentStatus.ERROR
            subscription_status = SubscriptionStatus.INACTIVE
        db_session.commit()
        with db_session.begin():
            db_session.execute(
                update(
                    Payment
                ).where(
                    Payment.id == payment.id
                ).values(
                    status=payment_status
                )
            )
            db_session.execute(
                update(
                    Subscription
                ).where(
                    Subscription.id == payment.subscription_id
                ).values(
                    status=subscription_status,
                    date_end=payment.date_end + relativedelta(months=payment.duration)
                )
            )

            db_session.commit()

    def _process_payment(self, payment: PaymentSchema):
        logging.info(f'Process payment: {payment}')

        print('Handle payment in STIPE')
        payment_result = self.payment_processor.make_payment(payment.stripe_customer_id, payment.price)

        self._update_subscription(payment, payment_result)

    def process(self):

        payments = self._get_pending_payments()
        if payments:
            logging.info(f'Got {len(payments)} payments to process')
        for payment in payments:
            self._process_payment(payment)
