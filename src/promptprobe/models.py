"""Core data models for Prompt Injection Tester."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Category(str, Enum):
    DIRECT_OVERRIDE = "direct_override"
    ROLE_PLAY = "role_play"
    TRANSLATION = "translation"
    INDIRECT = "indirect"
    ENCODING = "encoding"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class AttackCase:
    id: str
    category: Category
    severity: Severity
    prompt: str
    description: str = ""


@dataclass(frozen=True)
class Verdict:
    leaked: bool
    evidence: str = ""


@dataclass(frozen=True)
class Result:
    attack: AttackCase
    response: str
    verdict: Verdict
    latency_ms: float
    error: str | None = None


@dataclass
class Report:
    target_url: str
    results: list[Result] = field(default_factory=list)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def leaked_count(self) -> int:
        return sum(1 for r in self.results if r.verdict.leaked)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if r.error)

    @property
    def pass_rate(self) -> float:
        """Share of completed attacks that did not leak (0.0 if none completed)."""
        completed = self.total - self.error_count
        if completed == 0:
            return 0.0
        return 1 - self.leaked_count / completed