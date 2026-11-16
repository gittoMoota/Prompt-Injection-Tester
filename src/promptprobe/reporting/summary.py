"""Shared calculations used by every reporter."""

from __future__ import annotations

from typing import Any

from promptprobe.models import Report, Result


def result_status(result: Result) -> str:
    if result.error:
        return "error"
    return "leaked" if result.verdict.leaked else "passed"


def summarise(report: Report) -> dict[str, Any]:
    by_category: dict[str, dict[str, int]] = {}
    for result in report.results:
        stats = by_category.setdefault(
            result.attack.category.value,
            {"total": 0, "leaked": 0, "passed": 0, "errors": 0},
        )
        stats["total"] += 1
        status = result_status(result)
        stats["errors" if status == "error" else status] += 1
    return {
        "target_url": report.target_url,
        "created_at": report.created_at.isoformat(timespec="seconds"),
        "total": report.total,
        "leaked": report.leaked_count,
        "passed": report.total - report.leaked_count - report.error_count,
        "errors": report.error_count,
        "pass_rate": round(report.pass_rate, 4),
        "by_category": by_category,
    }


def result_rows(report: Report) -> list[dict[str, Any]]:
    return [
        {
            "id": r.attack.id,
            "category": r.attack.category.value,
            "severity": r.attack.severity.value,
            "description": r.attack.description,
            "prompt": r.attack.prompt,
            "response": r.response,
            "status": result_status(r),
            "evidence": r.verdict.evidence,
            "latency_ms": round(r.latency_ms, 1),
            "error": r.error,
        }
        for r in report.results
    ]