"""
HHS Node Proxy Contract v1
==========================

Pass 045 demotes Node/Vite to GUI/proxy infrastructure.  Node may serve static
assets and proxy /api plus /ws to FastAPI.  It may not synthesize runtime events
or act as runtime authority.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

VERSION = "PASS_045_NODE_PROXY_CONTRACT_V1"

FORBIDDEN_STUB_TOKENS = (
    '"phase"',
    '"runtime_loop"',
    '"throughput"',
    '"nodes"',
    '"edges"',
    'status": "online"',
)


def node_proxy_contract() -> Dict[str, Any]:
    return {
        "schema": "HHS_NODE_PROXY_CONTRACT_V1",
        "version": VERSION,
        "node_role": "GUI_PROXY_ONLY",
        "runtime_authority": "hhs_backend.server:app",
        "api_proxy": "/api -> http://127.0.0.1:8000",
        "websocket_proxy": "/ws -> ws://127.0.0.1:8000",
        "forbidden": ["synthetic runtime event generation", "stub websocket payloads", "runtime authority in Node"],
    }


def validate_no_node_runtime_stub(repo_root: str | Path = ".") -> Dict[str, Any]:
    root = Path(repo_root)
    stub_file = root / "hhs_runtime" / "runtime_ws_server.py"
    content = stub_file.read_text(encoding="utf-8") if stub_file.exists() else ""
    found = [token for token in FORBIDDEN_STUB_TOKENS if token in content]
    return {
        "schema": "HHS_NODE_PROXY_STUB_VALIDATION_V1",
        "version": VERSION,
        "ok": not found,
        "status": "NODE_RUNTIME_STUB_DEPRECATED" if not found else "REJECT_NODE_SYNTHETIC_RUNTIME_STREAM",
        "file": str(stub_file),
        "forbidden_tokens_found": found,
    }


def node_proxy_contract_self_test() -> Dict[str, Any]:
    validation = validate_no_node_runtime_stub(Path(__file__).resolve().parents[2])
    return {
        "schema": "HHS_NODE_PROXY_CONTRACT_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(validation.get("ok")),
        "contract": node_proxy_contract(),
        "validation": validation,
    }


if __name__ == "__main__":
    print(node_proxy_contract_self_test())
