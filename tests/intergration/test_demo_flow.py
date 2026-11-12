from fastapi.testclient import TestClient

from promptprobe.attacks.library import AttackLibrary
from promptprobe.demo.vulnerable_bot import CANARY, create_app
from promptprobe.detectors.canary import CanaryDetector
from promptprobe.models import Category
from promptprobe.targets.http_target import HttpTarget


def scan(hardened):
    client = TestClient(create_app(hardened=hardened))
    target = HttpTarget("http://testserver/chat", client=client)
    detector = CanaryDetector(CANARY)
    leaked = []
    for attack in AttackLibrary.from_directory().all():
        verdict = detector.evaluate(target.send(attack.prompt))
        if verdict.leaked:
            leaked.append(attack)
    return leaked


def test_vulnerable_bot_leaks_on_every_attack():
    leaked = scan(hardened=False)
    assert len(leaked) == len(AttackLibrary.from_directory())


def test_hardened_bot_leaks_only_encoding_attacks():
    leaked = scan(hardened=True)
    assert leaked
    assert {a.category for a in leaked} == {Category.ENCODING}