from async_stripe import stripe

from services.payment_processor.abstract import PaymentProcessorAbstract


class PaymentProcessorStripe(PaymentProcessorAbstract):

    def __init__(self, secret_key: str):
        stripe.api_key = secret_key

    async def create_customer(self) -> str:
        customer = await stripe.Customer.create(
            description="customer",
        )
        return customer.id

    async def create_setup_session(self, customer_id: str, success_callback: str, cancel_callback: str) -> str:
        print(success_callback)
        session = await stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='setup',
            customer=customer_id,
            success_url=success_callback,
            cancel_url=cancel_callback,
        )
        print(session)
        print(session.url)
        return session.url

    async def get_sustomer_id_from_session(self, session_id: str) -> str:
        session = await stripe.checkout.Session.retrieve(session_id, expand=['customer'])
        return session.customer.id
