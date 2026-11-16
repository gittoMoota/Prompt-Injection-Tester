"""Generate sample reports by scanning the demo bot in-process."""

from pathlib import Path

from fastapi.testclient import TestClient

from promptprobe.attacks.library import AttackLibrary
from promptprobe.demo.vulnerable_bot import CANARY, create_app
from promptprobe.detectors.canary import CanaryDetector
from promptprobe.reporting.html_report import HtmlReporter
from promptprobe.reporting.json_report import JsonReporter
from promptprobe.runner import Runner
from promptprobe.targets.http_target import HttpTarget

OUTPUT_DIR = Path("reports")


def scan(hardened: bool):
    client = TestClient(create_app(hardened=hardened))
    url = "http://testserver/chat"
    runner = Runner(HttpTarget(url, client=client), CanaryDetector(CANARY), url)
    return runner.run(AttackLibrary.from_directory().all())


def main() -> None:
    for name, hardened in (("vulnerable", False), ("hardened", True)):
        report = scan(hardened)
        html = HtmlReporter().write(report, OUTPUT_DIR / f"{name}.html")
        JsonReporter().write(report, OUTPUT_DIR / f"{name}.json")
        print(f"{name}: {report.leaked_count}/{report.total} leaked -> {html}")


if __name__ == "__main__":
    main()
    