import abc
import json
import logging
from typing import Any, Optional

module_logger = logging.getLogger('JsonFileStorage')


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        if self.file_path is None:
            return None

        with open(self.file_path, 'w') as f:
            json.dump(state, f)

    def retrieve_state(self) -> Optional[dict]:
        if self.file_path is None:
            module_logger.warning('No state file provided. Continue with in-memory state')
            return {}

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            self.save_state({})
        return {}


class State:
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.state = storage.retrieve_state() or {}

    def set_state(self, key: str, value: Any) -> None:
        self.state[key] = value
        self.storage.save_state(self.state)
        module_logger.info('Set key %s with value %s to storage', key, value)

    def get_state(self, key: str) -> Any:
        return self.state.get(key)
