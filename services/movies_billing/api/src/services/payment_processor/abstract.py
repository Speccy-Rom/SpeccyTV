from abc import ABC, abstractmethod


class PaymentProcessorAbstract(ABC):
    """
    This is an abstract class that represents a payment processor.
    It provides a blueprint for any payment processor that will be implemented.
    """

    @abstractmethod
    async def create_customer(self) -> str:
        """
        This is an abstract method that should be implemented by any concrete class that inherits from this abstract class.
        It represents the action of creating a customer.

        Returns:
        str: The ID of the created customer. The implementation in a concrete class may vary.
        """
        pass

    @abstractmethod
    async def create_setup_session(self, customer_id: str, success_callback: str, cancel_callback: str) -> str:
        """
        This is an abstract method that should be implemented by any concrete class that inherits from this abstract class.
        It represents the action of creating a setup session.

        Parameters:
        customer_id (str): The ID of the customer for whom the setup session is being created.
        success_callback (str): The URL to which the user will be redirected upon successful setup.
        cancel_callback (str): The URL to which the user will be redirected upon setup cancellation.

        Returns:
        str: The ID of the created setup session. The implementation in a concrete class may vary.
        """
        pass

    @abstractmethod
    async def get_sustomer_id_from_session(self, session_id: str) -> str:
        """
        This is an abstract method that should be implemented by any concrete class that inherits from this abstract class.
        It represents the action of retrieving a customer ID from a session.

        Parameters:
        session_id (str): The ID of the session from which the customer ID is being retrieved.

        Returns:
        str: The ID of the customer associated with the session. The implementation in a concrete class may vary.
        """
        pass
