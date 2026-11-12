from promptprobe.detectors.canary import CanaryDetector
from promptprobe.models import AttackCase, Category, Severity
from promptprobe.runner import Runner
from promptprobe.targets.base import Target, TargetError


class FakeTarget(Target):
    def __init__(self, replies):
        self._replies = replies

    def send(self, prompt):
        reply = self._replies[prompt]
        if isinstance(reply, Exception):
            raise reply
        return reply


def make_attack(attack_id, prompt):
    return AttackCase(attack_id, Category.DIRECT_OVERRIDE, Severity.HIGH, prompt)


def make_runner(replies):
    return Runner(FakeTarget(replies), CanaryDetector("CANARY-1"), "fake://bot")


def test_run_collects_one_result_per_attack():
    runner = make_runner({"a": "CANARY-1", "b": "no secret here"})
    report = runner.run([make_attack("1", "a"), make_attack("2", "b")])
    assert report.target_url == "fake://bot"
    assert report.total == 2
    assert report.leaked_count == 1
    assert report.results[0].verdict.leaked
    assert not report.results[1].verdict.leaked


def test_target_error_is_recorded_and_run_continues():
    runner = make_runner({"a": TargetError("boom"), "b": "fine"})
    report = runner.run([make_attack("1", "a"), make_attack("2", "b")])
    assert report.total == 2
    assert report.error_count == 1
    assert report.results[0].error == "boom"
    assert not report.results[0].verdict.leaked


def test_on_result_is_called_for_each_attack():
    runner = make_runner({"a": "x", "b": "y"})
    seen = []
    runner.run([make_attack("1", "a"), make_attack("2", "b")], on_result=seen.append)
    assert [r.attack.id for r in seen] == ["1", "2"]


def test_latency_is_recorded():
    runner = make_runner({"a": "x"})
    report = runner.run([make_attack("1", "a")])
    assert report.results[0].latency_ms >= 0


def test_no_attacks_gives_empty_report():
    report = make_runner({}).run([])
    assert report.total == 0