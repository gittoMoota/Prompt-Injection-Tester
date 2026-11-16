import json

from promptprobe.models import (
    AttackCase,
    Category,
    Report,
    Result,
    Severity,
    Verdict,
)
from promptprobe.reporting.html_report import HtmlReporter
from promptprobe.reporting.json_report import JsonReporter
from promptprobe.reporting.summary import summarise


def make_result(attack_id, category, leaked, response="reply", error=None):
    attack = AttackCase(attack_id, category, Severity.HIGH, f"prompt {attack_id}")
    verdict = Verdict(leaked, "canary found (plain)" if leaked else "")
    return Result(attack, response, verdict, 5.25, error)


def make_report(extra=()):
    results = [
        make_result("A1", Category.DIRECT_OVERRIDE, True),
        make_result("A2", Category.DIRECT_OVERRIDE, False),
        make_result("B1", Category.ENCODING, False, response="", error="timeout"),
        *extra,
    ]
    return Report("http://bot.test/chat", results)


def test_summary_counts():
    summary = summarise(make_report())
    assert summary["total"] == 3
    assert summary["leaked"] == 1
    assert summary["passed"] == 1
    assert summary["errors"] == 1
    assert summary["pass_rate"] == 0.5
    assert summary["by_category"]["direct_override"] == {
        "total": 2,
        "leaked": 1,
        "passed": 1,
        "errors": 0,
    }
    assert summary["by_category"]["encoding"]["errors"] == 1


def test_json_report_is_valid_and_complete():
    data = json.loads(JsonReporter().render(make_report()))
    assert data["summary"]["total"] == 3
    assert [r["status"] for r in data["results"]] == ["leaked", "passed", "error"]
    assert data["results"][0]["evidence"] == "canary found (plain)"


def test_html_report_shows_summary_and_results():
    html = HtmlReporter().render(make_report())
    assert "Prompt Injection Test Report" in html
    assert "http://bot.test/chat" in html
    assert "A1" in html
    assert "LEAKED" in html
    assert "timeout" in html


def test_html_report_escapes_untrusted_replies():
    nasty = make_result(
        "X1", Category.INDIRECT, False, response="<script>alert(1)</script>"
    )
    html = HtmlReporter().render(make_report(extra=[nasty]))
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_write_creates_file_and_parent_folder(tmp_path):
    path = JsonReporter().write(make_report(), tmp_path / "out" / "report.json")
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8"))["summary"]["total"] == 3