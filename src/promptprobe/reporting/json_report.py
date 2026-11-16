"""Renders a report as JSON."""

from __future__ import annotations

import json

from promptprobe.models import Report
from promptprobe.reporting.base import Reporter
from promptprobe.reporting.summary import result_rows, summarise


class JsonReporter(Reporter):
    extension = ".json"

    def render(self, report: Report) -> str:
        data = {"summary": summarise(report), "results": result_rows(report)}
        return json.dumps(data, indent=2, ensure_ascii=False)