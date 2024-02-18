from abc import ABC, abstractmethod


class PaymentProcessorAbstract(ABC):
    """
    This is an abstract class that represents a payment processor.
    It provides a blueprint for any payment processor that will be implemented.
    """

    @abstractmethod
    def make_payment(self, customer_id: str, amount: int):
        """
        This is an abstract method that should be implemented by any concrete class that inherits from this abstract class.
        It represents the action of making a payment.

        Parameters:
        customer_id (str): The ID of the customer making the payment.
        amount (int): The amount of money that the customer is paying.

        Returns:
        This method does not return anything. Its implementation in a concrete class may vary.
        """
        pass
