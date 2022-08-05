from abc import ABC, abstractmethod


class PaymentProcessorAbstract(ABC):
    @abstractmethod
    async def create_customer(self) -> str:
        pass

    @abstractmethod
    async def create_setup_session(self, customer_id: str, success_callback: str, cancel_callback: str) -> str:
        pass

    @abstractmethod
    async def get_sustomer_id_from_session(self, session_id: str) -> str:
        pass
