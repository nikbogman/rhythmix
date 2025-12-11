from abc import ABC, abstractmethod


class AudioSource(ABC):
    @abstractmethod
    async def get_bytes(self) -> bytes:
        """Return the audio content as bytes"""
        pass
