import abc
import json
import logging
from typing import Any, Optional, Dict

module_logger = logging.getLogger('JsonFileStorage')


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """
        Save the state to the storage.

        Args:
            state (Dict[str, Any]): The state to save.
        """
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """
        Retrieve the state from the storage.

        Returns:
            Dict[str, Any]: The retrieved state.
        """
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        """
        Save the state to a JSON file.

        Args:
            state (Dict[str, Any]): The state to save.
        """
        if self.file_path is None:
            return

        with open(self.file_path, 'w') as f:
            json.dump(state, f)

    def retrieve_state(self) -> Dict[str, Any]:
        """
        Retrieve the state from a JSON file.

        Returns:
            Dict[str, Any]: The retrieved state.
        """
        if self.file_path is None:
            module_logger.warning('No state file provided. Continue with in-memory state')
            return {}

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            module_logger.warning('State file not found. Initializing with empty state.')
            self.save_state({})
            return {}
