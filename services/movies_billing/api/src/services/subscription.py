import datetime
import logging
from typing import Optional

from fastapi import Depends
from sqlalchemy import select, insert, update, or_
from sqlalchemy.orm import Session

from core.config import settings
from db.session import get_db
from models.customer import Customer
from models.subscription import Status as SubscriptionStatus
from models.subscription import Subscription
from services.exceptions import AlreadyHasSubscriptions, NoActiveSubscription
from services.payment_processor.abstract import PaymentProcessorAbstract
from services.payment_processor.stripe_processor import PaymentProcessorStripe


class SubscriptionService(object):
    settings = settings

    def __init__(self, db: Session, payment_processor: PaymentProcessorAbstract):
        self.db = db
        self.payment_processor = payment_processor

    async def _get_stripe_customer_id(self, user_id: str) -> Optional[str]:
        user = await self.db.execute(
            select(
                Customer.stripe_customer_id,
            ).where(
                Customer.user_id == user_id,
            ),
        )
        user = user.first()
        if not user:
            return None
        return user.stripe_customer_id

    async def _create_customer(self, user_id: str):
        customer_id = await self.payment_processor.create_customer()

        await self.db.execute(
            insert(
                Customer
            ).values(
                user_id=user_id,
                stripe_customer_id=customer_id
            ),
        )
        return customer_id

    async def get_subscription_status(self, user_id: str) -> bool:
        user = await self.db.execute(
            select(
                Subscription.id,
            ).outerjoin(
                Customer, Subscription.customer_id == Customer.id
            ).where(
                Customer.user_id == user_id,
            ).where(
                or_(Subscription.status == SubscriptionStatus.ACTIVE, Subscription.status == SubscriptionStatus.ENDING)
            ),
        )
        user = user.first()
        return bool(user)

    async def prepare_setup_payment(self, user_id: str) -> str:
        if await self.get_subscription_status(user_id):
            raise AlreadyHasSubscriptions

        stripe_customer_id = await self._get_stripe_customer_id(user_id)

        if not stripe_customer_id:
            logging.info(f'customer {user_id} not exists. Create in stripe')
            stripe_customer_id = await self._create_customer(user_id)
            logging.info(f'customer {stripe_customer_id} created in stripe')

        logging.info(f'create session for user {stripe_customer_id}')

        url = await self.payment_processor.create_setup_session(
            stripe_customer_id,
            settings.success_callback,
            settings.cancel_callback
        )
        return url

    async def create_subscription(self, session_id: str, tariff_id: int):
        stripe_customer_id = await self.payment_processor.get_sustomer_id_from_session(session_id)

        customer = await self.db.execute(
            select(
                Customer.id
            ).where(
                Customer.stripe_customer_id == stripe_customer_id
            ).limit(1))
        customer = customer.first()

        await self.db.execute(
            insert(
                Subscription
            ).values(
                customer_id=customer.id,
                status=SubscriptionStatus.NEW,
                tariff_id=tariff_id,
                date_begin=datetime.datetime.now(),
                date_end=datetime.datetime.now(),
            ),
        )

    async def cancel_subscription(self, user_id: str):
        if not await self.get_subscription_status(user_id):
            raise NoActiveSubscription()

        customer = await self.db.execute(select(Customer.id).where(Customer.user_id == user_id))

        customer_id = customer.first().id

        await self.db.execute(
            update(
                Subscription
            ).where(
                Subscription.customer_id == customer_id
            ).values(
                status=SubscriptionStatus.ENDING
            )
        )


def get_payment_processor() -> PaymentProcessorAbstract:
    return PaymentProcessorStripe(settings.stripe_secret_key)


def get_subscription_service(
        db: Session = Depends(get_db),
        payment_processor=Depends(get_payment_processor)
):
    return SubscriptionService(db, payment_processor)
