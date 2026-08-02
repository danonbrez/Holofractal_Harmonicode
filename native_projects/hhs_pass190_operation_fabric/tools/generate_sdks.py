#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from hhs_pass190_iteration6_registry import ExpandedOperationRegistry

PY_TARGET = ROOT / "sdk" / "python" / "hhs_pass190_client.py"
TS_TARGET = ROOT / "sdk" / "typescript" / "hhsPass190Client.ts"


def method_name(operation_id: str) -> str:
    return operation_id.replace(".", "_").replace("-", "_")


def generate_python(operations):
    methods = "\n".join(
        f'''    def {method_name(operation["operation_id"])}(self, arguments: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.invoke("{operation["operation_id"]}", arguments or {{}}, **kwargs)
'''
        for operation in operations
    )
    return f'''#!/usr/bin/env python3
"""Generated Pass 190 Python SDK. Do not edit by hand."""
from __future__ import annotations
import json
from typing import Any
from urllib.request import Request, urlopen

OPERATION_IDS = {tuple(operation["operation_id"] for operation in operations)!r}

class HHSClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8190"):
        self.base_url = base_url.rstrip("/")

    def _request(self, path: str, payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request = Request(self.base_url + path, data=body, headers={{"Content-Type":"application/json", **(headers or {{}})}})
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read())

    def operations(self) -> dict[str, Any]: return self._request("/api/pass190/operations")
    def integrity(self) -> dict[str, Any]: return self._request("/api/pass190/integrity")
    def arbitration(self) -> dict[str, Any]: return self._request("/api/pass190/arbitration")
    def resource_registry(self) -> dict[str, Any]: return self._request("/api/pass190/resource-registry")
    def lease_receipts(self, after: int = 0, limit: int = 100) -> dict[str, Any]: return self._request(f"/api/pass190/lease-receipts?after={{after}}&limit={{limit}}")
    def events(self, after: int = 0, limit: int = 100) -> dict[str, Any]: return self._request(f"/api/pass190/events?after={{after}}&limit={{limit}}")
    def receipts(self, after: int = 0, limit: int = 100) -> dict[str, Any]: return self._request(f"/api/pass190/receipts?after={{after}}&limit={{limit}}")
    def replay(self, hash72: str) -> dict[str, Any]: return self._request("/api/pass190/replay", {{"hash72": hash72}})

    def invoke(self, operation_id: str, arguments: dict[str, Any], *, capability_token: str | None = None, idempotency_key: str | None = None, expected_state: str | None = None) -> dict[str, Any]:
        headers: dict[str,str] = {{}}
        if capability_token: headers["Authorization"] = "HHS-Capability " + capability_token
        if idempotency_key: headers["Idempotency-Key"] = idempotency_key
        if expected_state: headers["X-HHS-Expected-State"] = expected_state
        return self._request("/api/pass190/invoke", {{"operation_id":operation_id,"arguments":arguments}}, headers)

{methods}
'''


def generate_ts(operations):
    union = " | ".join(json.dumps(operation["operation_id"]) for operation in operations)
    methods = "\n".join(
        f'''  {method_name(operation["operation_id"])}(arguments: Record<string, unknown> = {{}}, options: InvokeOptions = {{}}) {{
    return this.invoke("{operation["operation_id"]}", arguments, options)
  }}
'''
        for operation in operations
    )
    return f'''// Generated Pass 190 TypeScript SDK. Do not edit by hand.
export type OperationId = {union}
export type InvokeOptions = {{ capabilityToken?: string; idempotencyKey?: string; expectedState?: string }}
export class HHSClient {{
  constructor(readonly baseUrl = "http://127.0.0.1:8190") {{}}
  private async request(path: string, init: RequestInit = {{}}) {{
    const response = await fetch(this.baseUrl.replace(/\\/$/, "") + path, init)
    const payload = await response.json()
    if (!response.ok) throw new Error(payload.message || payload.error || `HTTP ${{response.status}}`)
    return payload
  }}
  operations() {{ return this.request("/api/pass190/operations") }}
  integrity() {{ return this.request("/api/pass190/integrity") }}
  arbitration() {{ return this.request("/api/pass190/arbitration") }}
  resourceRegistry() {{ return this.request("/api/pass190/resource-registry") }}
  leaseReceipts(after = 0, limit = 100) {{ return this.request(`/api/pass190/lease-receipts?after=${{after}}&limit=${{limit}}`) }}
  events(after = 0, limit = 100) {{ return this.request(`/api/pass190/events?after=${{after}}&limit=${{limit}}`) }}
  receipts(after = 0, limit = 100) {{ return this.request(`/api/pass190/receipts?after=${{after}}&limit=${{limit}}`) }}
  replay(hash72: string) {{ return this.request("/api/pass190/replay", {{ method:"POST", headers:{{"Content-Type":"application/json"}}, body:JSON.stringify({{hash72}}) }}) }}
  invoke(operationId: OperationId, arguments_: Record<string, unknown>, options: InvokeOptions = {{}}) {{
    const headers: Record<string,string> = {{"Content-Type":"application/json"}}
    if (options.capabilityToken) headers["Authorization"] = `HHS-Capability ${{options.capabilityToken}}`
    if (options.idempotencyKey) headers["Idempotency-Key"] = options.idempotencyKey
    if (options.expectedState) headers["X-HHS-Expected-State"] = options.expectedState
    return this.request("/api/pass190/invoke", {{method:"POST", headers, body:JSON.stringify({{operation_id:operationId, arguments:arguments_}})}})
  }}
  websocket(after = 0) {{ return new WebSocket(this.baseUrl.replace(/^http/, "ws").replace(/\\/$/, "") + `/api/pass190/ws?after=${{after}}`) }}
{methods}
}}
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    operations = [dict(record.raw) for record in ExpandedOperationRegistry().records]
    python_source = generate_python(operations)
    typescript_source = generate_ts(operations)
    if args.check:
        if PY_TARGET.read_text(encoding="utf-8") != python_source or TS_TARGET.read_text(encoding="utf-8") != typescript_source:
            raise SystemExit("generated SDKs are stale")
    else:
        PY_TARGET.parent.mkdir(parents=True, exist_ok=True)
        TS_TARGET.parent.mkdir(parents=True, exist_ok=True)
        PY_TARGET.write_text(python_source, encoding="utf-8")
        TS_TARGET.write_text(typescript_source, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
