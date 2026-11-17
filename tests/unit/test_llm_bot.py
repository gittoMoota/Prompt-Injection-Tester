import json

import httpx
import pytest
from fastapi.testclient import TestClient

from promptprobe.demo.llm_bot import CANARY, SYSTEM_PROMPT, create_app


def mock_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def ask(app, message="hi"):
    return TestClient(app).post("/chat", json={"message": message})


def test_ollama_reply_is_returned_and_system_prompt_is_sent():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return httpx.Response(
            200, json={"message": {"role": "assistant", "content": "Hello!"}}
        )

    app = create_app("ollama", client=mock_client(handler))
    response = ask(app)
    assert response.json()["reply"] == "Hello!"
    assert seen["body"]["messages"][0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert CANARY in SYSTEM_PROMPT


def test_anthropic_reply_uses_key_header_and_joins_text_blocks(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    seen = {}

    def handler(request):
        seen["key"] = request.headers["x-api-key"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "content": [
                    {"type": "text", "text": "Hi "},
                    {"type": "text", "text": "there"},
                ]
            },
        )

    app = create_app("anthropic", client=mock_client(handler))
    assert ask(app).json()["reply"] == "Hi there"
    assert seen["key"] == "test-key"
    assert seen["body"]["system"] == SYSTEM_PROMPT


def test_model_failure_becomes_502():
    app = create_app("ollama", client=mock_client(lambda request: httpx.Response(500)))
    assert ask(app).status_code == 502


def test_missing_api_key_becomes_502(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    app = create_app(
        "anthropic",
        client=mock_client(lambda request: httpx.Response(200, json={})),
    )
    assert ask(app).status_code == 502


def test_unknown_provider_is_rejected():
    with pytest.raises(ValueError):
        create_app("nope")