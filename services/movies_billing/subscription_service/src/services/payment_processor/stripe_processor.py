import stripe
from services.payment_processor.abstract import PaymentProcessorAbstract

from core.config import settings


class PaymentProcessorStripe(PaymentProcessorAbstract):

    def __init__(self, secret_key: str):
        stripe.api_key = secret_key

    def make_payment(self, customer_id: str, amount: int):
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            #todo currency to config
            currency="RUB",
            payment_method_types=["card"],
            customer=customer_id
        )

        payment_methods = stripe.Customer.list_payment_methods(
            customer_id,
            type="card",
        )

        print(payment_methods)

        payment = stripe.PaymentIntent.confirm(
            payment_intent.id,
            payment_method=payment_methods.data[0].id
        )
        return payment.status == 'succeeded'


def test():
    processor = PaymentProcessorStripe(settings.stripe_settings.stripe_secret_key)
    print(processor.make_payment('cus_LBhLd8P71XiXCr', 20000))


if __name__ == '__main__':
    test()
