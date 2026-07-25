from __future__ import annotations

import json
from urllib.request import Request, urlopen


class HHSAgentClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(self.base_url + path, data=data, method=method, headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def status(self) -> dict:
        return self._request("GET", "/api/pass153/status")

    def create_session(self, model_id: str = "hhs-reference-open-model-v1", session_id: str | None = None) -> dict:
        return self._request("POST", "/api/pass153/sessions", {"model_id": model_id, "session_id": session_id})

    def chat(self, session_id: str, prompt: str, max_tokens: int = 64) -> dict:
        return self._request("POST", f"/api/pass153/sessions/{session_id}/chat", {"prompt": prompt, "max_tokens": max_tokens})

    def invoke_tool(self, session_id: str, tool_name: str, arguments: dict | None = None) -> dict:
        return self._request("POST", f"/api/pass153/sessions/{session_id}/tools/{tool_name}", {"arguments": arguments or {}})
