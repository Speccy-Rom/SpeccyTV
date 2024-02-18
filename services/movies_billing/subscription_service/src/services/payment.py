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
    """
    This class represents the schema for a payment.

    Attributes:
    id (int): The ID of the payment.
    subscription_id (int): The ID of the subscription associated with the payment.
    date_end (datetime.date): The end date of the payment.
    price (int): The price of the payment.
    duration (int): The duration of the payment.
    stripe_customer_id (str): The ID of the Stripe customer associated with the payment.
    """

    id: int
    subscription_id: int
    date_end: datetime.date
    price: int
    duration: int
    stripe_customer_id: str

    def __str__(self):
        """
        This method returns a string representation of the PaymentSchema object.

        Returns:
        str: A string representation of the PaymentSchema object.
        """
        return f'Payment {self.id}, for subscription {self.subscription_id}, till {self.date_end}, ' \
               f'amount {self.price}, duration {self.duration}'


class PaymentService:
    """
    This class represents a service for processing payments.

    Attributes:
    payment_processor (PaymentProcessorAbstract): The payment processor used by the service.
    """

    def __init__(self, payment_processor: PaymentProcessorAbstract):
        """
        The constructor for the PaymentService class.

        Parameters:
        payment_processor (PaymentProcessorAbstract): The payment processor used by the service.
        """
        self.payment_processor = payment_processor

    def _get_pending_payments(self) -> List[PaymentSchema]:
        """
        This method retrieves all pending payments.

        Returns:
        List[PaymentSchema]: A list of PaymentSchema objects representing the pending payments.
        """
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
        """
        This method updates a subscription based on the result of a payment.

        Parameters:
        payment (PaymentSchema): The payment associated with the subscription.
        result (bool): The result of the payment.
        """
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
        """
        This method processes a payment.

        Parameters:
        payment (PaymentSchema): The payment to be processed.
        """
        logging.info(f'Process payment: {payment}')

        print('Handle payment in STIPE')
        payment_result = self.payment_processor.make_payment(payment.stripe_customer_id, payment.price)

        self._update_subscription(payment, payment_result)

    def process(self):
        """
        This method processes all pending payments.
        """
        payments = self._get_pending_payments()
        if payments:
            logging.info(f'Got {len(payments)} payments to process')
        for payment in payments:
            self._process_payment(payment)
