from pathlib import Path

from hhs_backend.runtime.node_proxy_contract_v1 import (
    node_proxy_contract,
    validate_no_node_runtime_stub,
    node_proxy_contract_self_test,
)


def test_node_contract_is_proxy_only():
    contract = node_proxy_contract()
    assert contract["node_role"] == "GUI_PROXY_ONLY"
    assert contract["runtime_authority"] == "hhs_backend.server:app"


def test_runtime_ws_stub_delegates_to_fastapi():
    repo_root = Path(__file__).resolve().parents[1]
    result = validate_no_node_runtime_stub(repo_root)
    assert result["ok"] is True
    assert result["status"] == "NODE_RUNTIME_STUB_DEPRECATED"


def test_node_proxy_contract_self_test():
    result = node_proxy_contract_self_test()
    assert result["ok"] is True
