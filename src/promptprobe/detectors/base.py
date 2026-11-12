"""The interface every detector implements."""

from abc import ABC, abstractmethod

from promptprobe.models import Verdict


class Detector(ABC):
    @abstractmethod
    def evaluate(self, response: str) -> Verdict:
        """Decide whether a response contains a leak."""