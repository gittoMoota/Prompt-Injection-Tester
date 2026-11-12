"""Sends prompts to a chat endpoint over HTTP."""

from __future__ import annotations

import httpx

from promptprobe.targets.base import Target, TargetError


class HttpTarget(Target):
    def __init__(
        self,
        url: str,
        message_field: str = "message",
        reply_field: str = "reply",
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
        client: httpx.Client | None = None,
    ) -> None:
        self._url = url
        self._message_field = message_field
        self._reply_field = reply_field
        self._headers = headers or {}
        self._client = client or httpx.Client(timeout=timeout)

    def send(self, prompt: str) -> str:
        try:
            response = self._client.post(
                self._url,
                json={self._message_field: prompt},
                headers=self._headers,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            raise TargetError(f"Request to {self._url} failed: {exc}") from exc
        except ValueError as exc:
            raise TargetError(f"Reply from {self._url} is not valid JSON") from exc
        if not isinstance(data, dict) or self._reply_field not in data:
            raise TargetError(f"Reply has no '{self._reply_field}' field")
        return str(data[self._reply_field])

    def close(self) -> None:
        self._client.close()