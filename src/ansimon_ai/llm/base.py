from abc import ABC, abstractmethod
from typing import Any

class LLMClient(ABC):
    @abstractmethod
    def generate(self, messages: list[dict]) -> str:

        raise NotImplementedError