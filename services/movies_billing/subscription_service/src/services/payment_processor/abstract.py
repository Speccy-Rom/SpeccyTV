from abc import ABC, abstractmethod


class PaymentProcessorAbstract(ABC):
    @abstractmethod
    def make_payment(self, customer_id: str, amount: int):
        pass
