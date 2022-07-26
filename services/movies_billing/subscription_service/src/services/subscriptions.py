import datetime
import logging
from typing import List

from sqlalchemy import select, insert, update, or_
from sqlalchemy import text

from db.session import db_session
from models.payment import Payment, Status as PaymentStatus
from models.subscription import Subscription, Status as SubscriptionStatus


class SubscriptionService:

    def _get_pending_subscriptions(self) -> List[int]:
        now = text('NOW()')
        subscriptions = db_session.execute(
            select(
                Subscription.id
            ).where(
                or_(Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.status == SubscriptionStatus.NEW),
            ).where(
                Subscription.date_end <= datetime.date.today()
            )
        ).all()

        return [subscription.id for subscription in subscriptions]

    def _add_payment(self, subscription_id: int):
        db_session.commit()
        with db_session.begin():
            db_session.execute(
                insert(
                    Payment
                ).values(
                    subscription_id=subscription_id,
                    status=PaymentStatus.WAIT_PAYMENT
                )
            )

            db_session.execute(
                update(Subscription).
                    where(
                    Subscription.id == subscription_id
                ).
                    values(
                    status=SubscriptionStatus.WAIT_PAYMENT
                )
            )

    def process(self):
        subscriptions = self._get_pending_subscriptions()

        for subscription_id in subscriptions:
            logging.info(f'Add payment for subscription={subscription_id}')
            self._add_payment(subscription_id)
