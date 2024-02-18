import stripe
from services.payment_processor.abstract import PaymentProcessorAbstract

from core.config import settings


class PaymentProcessorStripe(PaymentProcessorAbstract):
    """
    This class represents a payment processor using the Stripe API.
    It inherits from the PaymentProcessorAbstract class and implements its abstract methods.

    Attributes:
    secret_key (str): The secret key used to authenticate with the Stripe API.
    """

    def __init__(self, secret_key: str):
        """
        The constructor for the PaymentProcessorStripe class.

        Parameters:
        secret_key (str): The secret key used to authenticate with the Stripe API.
        """
        stripe.api_key = secret_key

    def make_payment(self, customer_id: str, amount: int):
        """
        This method creates a payment intent, lists the customer's payment methods, and confirms the payment intent.

        Parameters:
        customer_id (str): The ID of the customer making the payment.
        amount (int): The amount of money that the customer is paying.

        Returns:
        bool: True if the payment status is 'succeeded', False otherwise.
        """
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            # todo currency to config
            currency="RUB",
            payment_method_types=["card"],
            customer=customer_id,
        )

        payment_methods = stripe.Customer.list_payment_methods(
            customer_id,
            type="card",
        )

        print(payment_methods)

        payment = stripe.PaymentIntent.confirm(
            payment_intent.id, payment_method=payment_methods.data[0].id
        )
        return payment.status == 'succeeded'


def test():
    """
    This function creates an instance of the PaymentProcessorStripe class and tests the make_payment method.
    """
    processor = PaymentProcessorStripe(settings.stripe_settings.stripe_secret_key)
    print(processor.make_payment('cus_LBhLd8P71XiXCr', 20000))


if __name__ == '__main__':
    test()
