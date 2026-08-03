from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_pass203_hydrated_mainframe_v1 import (
    HydratedMainframe,
    InvocationRejectedError,
)


@pytest.fixture()
def mainframe(monkeypatch: pytest.MonkeyPatch) -> HydratedMainframe:
    with tempfile.TemporaryDirectory() as directory:
        monkeypatch.setenv("HHS_PASS203_STATE_ROOT", directory)
        runtime = HydratedMainframe(Path(__file__).resolve().parents[1])
        counter = {"step": 0}

        def authority(source: str):
            counter["step"] += 1
            return {
                "receipt": {"receipt_hash72": "R" * 71 + str(counter["step"] % 10)},
                "runtime": {"step": counter["step"]},
                "source": source,
            }

        runtime.configure_authority(authority)
        yield runtime


def test_catalog_unifies_operations_python_abi_and_adapters(mainframe: HydratedMainframe) -> None:
    report = mainframe.refresh()
    assert report["catalog_count"] > 40
    assert report["duplicate_function_ids"] == []
    catalog = mainframe.catalog()
    kinds = {item["kind"] for item in catalog}
    assert {"GOVERNED_OPERATION", "PYTHON_FUNCTION", "NATIVE_ABI", "MAINFRAME_ADAPTER"} <= kinds
    assert sum(item["kind"] == "GOVERNED_OPERATION" for item in catalog) > 10
    assert sum(item["kind"] == "PYTHON_FUNCTION" for item in catalog) > 10
    assert sum(item["kind"] == "NATIVE_ABI" for item in catalog) > 10
    assert sum(item["kind"] == "MAINFRAME_ADAPTER" for item in catalog) >= 5
    assert len({item["function_id"] for item in catalog}) == len(catalog)
    assert all(not item["hydrated"] or item["callable"] for item in catalog)


def test_exact_interpreter_adapter_and_host_eval_rejection(mainframe: HydratedMainframe) -> None:
    result = mainframe.invoke("adapter:interpreter.exact", {"expression": "1+2*3/4"})
    assert result["ok"] is True
    assert result["result"]["exact_symbolic_value"] == {"numerator": 5, "denominator": 2}
    assert result["receipt"]["receipt_hash72"]

    rejected = mainframe.invoke(
        "adapter:interpreter.exact",
        {"expression": "__import__('os').system('echo unsafe')"},
    )
    assert rejected["result"]["ok"] is False
    assert "REJECT_INTERPRETER_HOST_EVAL" in rejected["result"]["reasons"]


def test_compiler_adapter_creates_non_authorized_artifact(mainframe: HydratedMainframe) -> None:
    result = mainframe.invoke(
        "adapter:compiler.hhs_ir",
        {"source_text": "a²=1 b²=2", "target": "HHS_IR"},
    )
    assert result["result"]["ok"] is True
    assert result["result"]["execution_authorized"] is False
    assert result["result"]["artifact"]["artifact_id"]


def test_pass190_operation_and_replay(mainframe: HydratedMainframe) -> None:
    result = mainframe.invoke("op:system.status", {})
    assert result["ok"] is True
    assert result["result"]["status"] == "ok"
    operation_receipt = result["result"].get("receipt_hash72") or result["result"].get("hash72")
    if operation_receipt:
        assert mainframe.replay(operation_receipt)


def test_isolated_python_self_test(mainframe: HydratedMainframe) -> None:
    functions = mainframe.list_functions(query="live_interpreter_self_test", hydrated_only=True)["functions"]
    target = next(item for item in functions if item["name"] == "live_interpreter_self_test")
    result = mainframe.invoke(target["function_id"], {})
    assert result["result"]["ok"] is True
    assert result["result"]["constraint"] == "NO_ARBITRARY_HOST_LANGUAGE_EVALUATION"


def test_unhydrated_function_fails_closed(mainframe: HydratedMainframe) -> None:
    target = next(item for item in mainframe.catalog() if not item["hydrated"])
    with pytest.raises(InvocationRejectedError):
        mainframe.invoke(target["function_id"], {})


def test_pass_inheritance_and_safe_cloud_boundary(mainframe: HydratedMainframe) -> None:
    status = mainframe.status()
    assert status["pass_inheritance"] == "PASS_203_INHERITS_ALL_PRIOR_PASSES_AS_ONE_INTEGRATED_SYSTEM"
    assert status["arbitrary_host_eval_available"] is False
    assert status["unrestricted_subprocess_available"] is False
    assert status["native_authority_preserved"] is True
    assert status["hydrated_count"] == status["callable_count"]
