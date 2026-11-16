"""Renders a report as a standalone HTML page."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from promptprobe.models import Report
from promptprobe.reporting.base import Reporter
from promptprobe.reporting.summary import result_rows, summarise

_TEMPLATE_DIR = Path(__file__).parent / "templates"


class HtmlReporter(Reporter):
    extension = ".html"

    def __init__(self) -> None:
        # Autoescape matters: replies from a target are untrusted text.
        self._env = Environment(
            loader=FileSystemLoader(_TEMPLATE_DIR),
            autoescape=True,
        )

    def render(self, report: Report) -> str:
        template = self._env.get_template("report.html.j2")
        return template.render(summary=summarise(report), rows=result_rows(report))