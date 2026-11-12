"""The interface every target implements."""

from abc import ABC, abstractmethod


class TargetError(Exception):
    """Raised when a target cannot return a usable reply."""


class Target(ABC):
    @abstractmethod
    def send(self, prompt: str) -> str:
        """Send a prompt and return the reply text."""