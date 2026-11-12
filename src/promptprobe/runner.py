"""Runs attacks against a target and collects the results."""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable

from promptprobe.detectors.base import Detector
from promptprobe.models import AttackCase, Report, Result, Verdict
from promptprobe.targets.base import Target, TargetError


class Runner:
    def __init__(
        self,
        target: Target,
        detector: Detector,
        target_url: str = "unknown",
    ) -> None:
        self._target = target
        self._detector = detector
        self._target_url = target_url

    def run(
        self,
        attacks: Iterable[AttackCase],
        on_result: Callable[[Result], None] | None = None,
    ) -> Report:
        report = Report(target_url=self._target_url)
        for attack in attacks:
            result = self._run_one(attack)
            report.results.append(result)
            if on_result is not None:
                on_result(result)
        return report

    def _run_one(self, attack: AttackCase) -> Result:
        started = time.perf_counter()
        try:
            response = self._target.send(attack.prompt)
            error = None
        except TargetError as exc:
            response, error = "", str(exc)
        latency_ms = (time.perf_counter() - started) * 1000
        verdict = Verdict(False) if error else self._detector.evaluate(response)
        return Result(attack, response, verdict, latency_ms, error)