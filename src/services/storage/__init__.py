from abc import ABC, abstractmethod
from typing import BinaryIO
import uuid


class Storage(ABC):
    @abstractmethod
    def save(self, key: str, data: BinaryIO) -> str:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    def __init__(self, base_path: str):
        self._base_path = base_path

    def _get_path(self, key: str) -> str:
        unique_id = uuid.uuid4()
        return f"{self._base_path}/{unique_id}-{key}"