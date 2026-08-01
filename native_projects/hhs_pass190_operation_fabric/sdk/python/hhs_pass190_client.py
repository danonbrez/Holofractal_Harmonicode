#!/usr/bin/env python3
"""Generated Pass 190 Python SDK. Do not edit by hand."""
from __future__ import annotations
import json
from typing import Any
from urllib.request import Request, urlopen

OPERATION_IDS = ('system.status', 'python.len', 'python.abs', 'python.sorted', 'list.with_appended', 'dict.get', 'text.join', 'math.gcd', 'pass189.context.decode', 'state.counter.advance')

class HHSClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8190"):
        self.base_url = base_url.rstrip("/")

    def _request(self, path: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request = Request(self.base_url + path, data=body, headers={"Content-Type":"application/json", **(headers or {})})
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read())

    def operations(self) -> dict[str, Any]:
        return self._request("/api/pass190/operations")

    def integrity(self) -> dict[str, Any]:
        return self._request("/api/pass190/integrity")

    def events(self, after: int = 0, limit: int = 100) -> dict[str, Any]:
        return self._request(f"/api/pass190/events?after={after}&limit={limit}")

    def receipts(self, after: int = 0, limit: int = 100) -> dict[str, Any]:
        return self._request(f"/api/pass190/receipts?after={after}&limit={limit}")

    def replay(self, hash72: str) -> dict[str, Any]:
        return self._request("/api/pass190/replay", {"hash72": hash72})

    def invoke(self, operation_id: str, arguments: dict[str, Any], *, capability: str | None = None, idempotency_key: str | None = None, expected_state: str | None = None) -> dict[str, Any]:
        headers: dict[str,str] = {}
        if capability: headers["X-HHS-Capability"] = capability
        if idempotency_key: headers["Idempotency-Key"] = idempotency_key
        if expected_state: headers["X-HHS-Expected-State"] = expected_state
        return self._request("/api/pass190/invoke", {"operation_id":operation_id,"arguments":arguments}, headers)

    def system_status(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.invoke("system.status", arguments or {}, **kwargs)

    def python_len(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.invoke("python.len", arguments or {}, **kwargs)

    def python_abs(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.invoke("python.abs", arguments or {}, **kwargs)

    def python_sorted(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.invoke("python.sorted", arguments or {}, **kwargs)

    def list_with_appended(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.invoke("list.with_appended", arguments or {}, **kwargs)

    def dict_get(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.invoke("dict.get", arguments or {}, **kwargs)

    def text_join(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.invoke("text.join", arguments or {}, **kwargs)

    def math_gcd(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.invoke("math.gcd", arguments or {}, **kwargs)

    def pass189_context_decode(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.invoke("pass189.context.decode", arguments or {}, **kwargs)

    def state_counter_advance(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.invoke("state.counter.advance", arguments or {}, **kwargs)
