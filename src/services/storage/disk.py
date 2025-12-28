from pathlib import Path
import shutil
from typing import BinaryIO
from src.services.storage import Storage


class DiskStorage(Storage):
    def __init__(self, base_path: str):
        super().__init__(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: BinaryIO) -> str:
        path_str = self._get_path(key)
        path = Path(path_str)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "wb") as f:
            shutil.copyfileobj(data, f)

        return str(path)

    def delete(self, key: str) -> None:
        path = self._get_path(key)
        if path.exists():
            path.unlink()
