"""The interface every reporter implements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from promptprobe.models import Report


class Reporter(ABC):
    extension = ""

    @abstractmethod
    def render(self, report: Report) -> str:
        """Turn a report into text."""

    def write(self, report: Report, path: Path | str) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(report), encoding="utf-8")
        return path