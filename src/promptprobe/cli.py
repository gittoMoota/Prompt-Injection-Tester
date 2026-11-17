"""Command-line interface for Prompt Injection Tester."""

from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from promptprobe.attacks.library import AttackLibrary, AttackLibraryError
from promptprobe.detectors.canary import CanaryDetector
from promptprobe.models import Category, Report, Result, Severity
from promptprobe.reporting.html_report import HtmlReporter
from promptprobe.reporting.json_report import JsonReporter
from promptprobe.reporting.summary import result_status
from promptprobe.runner import Runner
from promptprobe.targets.http_target import HttpTarget

app = typer.Typer(
    help="Test chatbots and LLM apps for prompt-injection leaks.",
    no_args_is_help=True,
)

_COLOURS = {
    "leaked": typer.colors.RED,
    "passed": typer.colors.GREEN,
    "error": typer.colors.YELLOW,
}


class ReportFormat(str, Enum):
    html = "html"
    json = "json"
    both = "both"


def _fail(message: str, code: int = 2) -> typer.Exit:
    typer.secho(message, fg=typer.colors.RED, err=True)
    return typer.Exit(code=code)


def _parse_headers(items: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in items:
        name, separator, value = item.partition("=")
        if not separator or not name.strip():
            raise typer.BadParameter(
                f"'{item}' must look like KEY=VALUE", param_hint="--header"
            )
        headers[name.strip()] = value.strip()
    return headers


def _print_result(result: Result) -> None:
    status = result_status(result)
    label = typer.style(status.upper().ljust(6), fg=_COLOURS[status], bold=True)
    detail = result.verdict.evidence or result.error or ""
    typer.echo(f"  {label} {result.attack.id}  {detail}".rstrip())


def _write_reports(
    report: Report, output_dir: Path, report_format: ReportFormat
) -> list[Path]:
    stem = report.created_at.strftime("report-%Y%m%d-%H%M%S")
    reporters = []
    if report_format in (ReportFormat.html, ReportFormat.both):
        reporters.append(HtmlReporter())
    if report_format in (ReportFormat.json, ReportFormat.both):
        reporters.append(JsonReporter())
    return [r.write(report, output_dir / f"{stem}{r.extension}") for r in reporters]


@app.command()
def scan(
    url: Annotated[
        str, typer.Option(help="Chat endpoint, e.g. http://127.0.0.1:8000/chat")
    ],
    canary: Annotated[
        str,
        typer.Option(
            envvar="PROMPTPROBE_CANARY",
            help="Secret planted in the target's hidden instructions",
        ),
    ],
    message_field: Annotated[
        str, typer.Option(help="JSON field that carries the prompt")
    ] = "message",
    reply_field: Annotated[
        str, typer.Option(help="JSON field that carries the reply")
    ] = "reply",
    header: Annotated[
        list[str] | None,
        typer.Option(help="Extra header as KEY=VALUE (repeatable)"),
    ] = None,
    category: Annotated[
        Category | None, typer.Option(help="Only run this category")
    ] = None,
    min_severity: Annotated[
        Severity | None, typer.Option(help="Skip attacks below this severity")
    ] = None,
    output_dir: Annotated[
        Path, typer.Option(help="Folder for the reports")
    ] = Path("reports"),
    report_format: Annotated[
        ReportFormat, typer.Option("--format", help="Report format")
    ] = ReportFormat.both,
    timeout: Annotated[
        float, typer.Option(help="Seconds to wait for each reply")
    ] = 10.0,
    fail_on_leak: Annotated[
        bool, typer.Option(help="Exit with code 1 if any attack leaks")
    ] = False,
) -> None:
    """Send the bundled attacks to a chat endpoint and report any leaks."""
    typer.secho("Only test systems you own or have permission to test.", dim=True)

    try:
        library = AttackLibrary.from_directory()
        detector = CanaryDetector(canary)
    except (AttackLibraryError, ValueError) as exc:
        raise _fail(str(exc)) from exc

    attacks = library.filter(category=category, min_severity=min_severity)
    if not attacks:
        raise _fail("No attacks match those filters.")

    target = HttpTarget(
        url, message_field, reply_field, _parse_headers(header or []), timeout
    )
    runner = Runner(target, detector, url)
    typer.echo(f"Scanning {url} with {len(attacks)} attacks...")
    try:
        report = runner.run(attacks, on_result=_print_result)
    finally:
        target.close()

    if report.error_count == report.total:
        raise _fail("Every request failed. Is the target running and the URL right?")

    paths = _write_reports(report, output_dir, report_format)
    typer.echo()
    typer.echo(
        f"Leaked: {report.leaked_count}/{report.total}  "
        f"Errors: {report.error_count}  Pass rate: {report.pass_rate:.0%}"
    )
    for path in paths:
        typer.echo(f"Report written: {path}")
    if fail_on_leak and report.leaked_count:
        raise typer.Exit(code=1)


@app.command("attacks")
def list_attacks(
    category: Annotated[
        Category | None, typer.Option(help="Only list this category")
    ] = None,
) -> None:
    """List the bundled attacks."""
    try:
        library = AttackLibrary.from_directory()
    except AttackLibraryError as exc:
        raise _fail(str(exc)) from exc
    for attack in library.filter(category=category):
        typer.echo(
            f"{attack.id}  {attack.category.value:<16}"
            f"{attack.severity.value:<10}{attack.description}"
        )