import httpx
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from promptprobe.cli import app
from promptprobe.demo.vulnerable_bot import CANARY, create_app
from promptprobe.targets.http_target import HttpTarget

runner = CliRunner()


def demo_target(hardened):
    def factory(url, message_field, reply_field, headers, timeout):
        client = TestClient(create_app(hardened=hardened))
        return HttpTarget(
            "http://testserver/chat",
            message_field,
            reply_field,
            headers,
            timeout,
            client=client,
        )

    return factory


def broken_target(url, message_field, reply_field, headers, timeout):
    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    return HttpTarget(
        url, message_field, reply_field, headers, timeout, client=client
    )


def scan(tmp_path, *extra):
    return runner.invoke(
        app,
        [
            "scan",
            "--url",
            "http://bot.test/chat",
            "--canary",
            CANARY,
            "--output-dir",
            str(tmp_path),
            *extra,
        ],
    )


def test_scan_vulnerable_bot_writes_both_reports(tmp_path, monkeypatch):
    monkeypatch.setattr("promptprobe.cli.HttpTarget", demo_target(hardened=False))
    result = scan(tmp_path)
    assert result.exit_code == 0
    assert "Leaked: 15/15" in result.output
    assert len(list(tmp_path.glob("report-*.html"))) == 1
    assert len(list(tmp_path.glob("report-*.json"))) == 1


def test_format_json_writes_only_json(tmp_path, monkeypatch):
    monkeypatch.setattr("promptprobe.cli.HttpTarget", demo_target(hardened=False))
    result = scan(tmp_path, "--format", "json")
    assert result.exit_code == 0
    assert list(tmp_path.glob("*.html")) == []
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_fail_on_leak_sets_exit_code_1(tmp_path, monkeypatch):
    monkeypatch.setattr("promptprobe.cli.HttpTarget", demo_target(hardened=False))
    assert scan(tmp_path, "--fail-on-leak").exit_code == 1


def test_hardened_bot_passes_direct_override(tmp_path, monkeypatch):
    monkeypatch.setattr("promptprobe.cli.HttpTarget", demo_target(hardened=True))
    result = scan(tmp_path, "--category", "direct_override", "--fail-on-leak")
    assert result.exit_code == 0
    assert "Leaked: 0/3" in result.output


def test_min_severity_filters_attacks(tmp_path, monkeypatch):
    monkeypatch.setattr("promptprobe.cli.HttpTarget", demo_target(hardened=False))
    result = scan(tmp_path, "--min-severity", "critical")
    assert "Leaked: 1/1" in result.output


def test_bad_header_is_rejected(tmp_path):
    result = scan(tmp_path, "--header", "nonsense")
    assert result.exit_code == 2


def test_unreachable_target_exits_with_code_2(tmp_path, monkeypatch):
    monkeypatch.setattr("promptprobe.cli.HttpTarget", broken_target)
    result = scan(tmp_path)
    assert result.exit_code == 2
    assert "Every request failed" in result.output


def test_attacks_command_lists_bundled_attacks():
    result = runner.invoke(app, ["attacks"])
    assert result.exit_code == 0
    assert "DO-001" in result.output
    assert "EN-003" in result.output
    