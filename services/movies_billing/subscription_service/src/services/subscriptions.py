import datetime
import logging
from typing import List

from sqlalchemy import select, insert, update, or_
from sqlalchemy import text

from db.session import db_session
from models.payment import Payment, Status as PaymentStatus
from models.subscription import Subscription, Status as SubscriptionStatus


class SubscriptionService:
    """
    This class represents a service for managing subscriptions.

    """

    def _get_pending_subscriptions(self) -> List[int]:
        """
        This method retrieves all subscriptions that are either active or new and have an end date that is today or earlier.

        Returns:
        List[int]: A list of IDs of the pending subscriptions.
        """
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
        """
        This method adds a payment for a given subscription and updates the status of the subscription to 'WAIT_PAYMENT'.

        Parameters:
        subscription_id (int): The ID of the subscription for which a payment is being added.
        """
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
        """
        This method processes all pending subscriptions by adding a payment for each one.
        """
        subscriptions = self._get_pending_subscriptions()

        for subscription_id in subscriptions:
            logging.info(f'Add payment for subscription={subscription_id}')
            self._add_payment(subscription_id)
            logging.info(f'Payment added for subscription={subscription_id}')
        db_session.commit()
        logging.info('All payments added')
        db_session.close()
        logging.info('DB session closed')
