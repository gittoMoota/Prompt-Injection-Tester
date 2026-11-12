import json

import httpx
import pytest

from promptprobe.targets.base import TargetError
from promptprobe.targets.http_target import HttpTarget


def make_target(handler, **kwargs):
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return HttpTarget("http://bot.test/chat", client=client, **kwargs)


def test_sends_prompt_and_returns_reply():
    def handler(request):
        assert json.loads(request.content) == {"message": "hi there"}
        return httpx.Response(200, json={"reply": "hello"})

    target = make_target(handler)
    assert target.send("hi there") == "hello"


def test_uses_custom_field_names():
    def handler(request):
        assert json.loads(request.content) == {"prompt": "hi"}
        return httpx.Response(200, json={"answer": "yo"})

    target = make_target(handler, message_field="prompt", reply_field="answer")
    assert target.send("hi") == "yo"


def test_http_error_raises_target_error():
    target = make_target(lambda request: httpx.Response(500))
    with pytest.raises(TargetError, match="failed"):
        target.send("hi")


def test_invalid_json_raises_target_error():
    target = make_target(lambda request: httpx.Response(200, text="not json"))
    with pytest.raises(TargetError, match="not valid JSON"):
        target.send("hi")


def test_missing_reply_field_raises_target_error():
    target = make_target(lambda request: httpx.Response(200, json={"other": 1}))
    with pytest.raises(TargetError, match="no 'reply' field"):
        target.send("hi")


def test_connection_failure_raises_target_error():
    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    target = make_target(handler)
    with pytest.raises(TargetError, match="failed"):
        target.send("hi")