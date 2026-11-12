import pytest
from fastapi.testclient import TestClient

from promptprobe.attacks.library import AttackLibrary
from promptprobe.demo.vulnerable_bot import CANARY, create_app
from promptprobe.detectors.canary import CanaryDetector
from promptprobe.runner import Runner
from promptprobe.targets.http_target import HttpTarget


def run_scan(hardened):
    client = TestClient(create_app(hardened=hardened))
    target = HttpTarget("http://testserver/chat", client=client)
    runner = Runner(target, CanaryDetector(CANARY), "http://testserver/chat")
    return runner.run(AttackLibrary.from_directory().all())


def test_vulnerable_bot_fails_every_attack():
    report = run_scan(hardened=False)
    assert report.total == 15
    assert report.leaked_count == 15
    assert report.pass_rate == 0.0


def test_hardened_bot_leaks_only_three_encoding_attacks():
    report = run_scan(hardened=True)
    assert report.leaked_count == 3
    assert report.error_count == 0
    assert report.pass_rate == pytest.approx(0.8)