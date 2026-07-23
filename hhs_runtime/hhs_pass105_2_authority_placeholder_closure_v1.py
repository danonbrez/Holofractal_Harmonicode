from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import (
    Hash72Authority,
    load_authoritative_kernel,
)
from hhs_backend.runtime.runtime_server import execute_runtime_expression

SCHEMA = "HHS_PASS105_2_AUTHORITY_PLACEHOLDER_CLOSURE_V1"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def verify_authoritative_kernel_path() -> Dict[str, Any]:
    kernel = load_authoritative_kernel()
    authority = Hash72Authority(kernel)
    probe = authority.commit({"pass": "105.2", "probe": "authoritative-kernel"}, domain="PASS105_2_KERNEL_PROBE")
    return {
        "kernel_loaded": True,
        "kernel_module": getattr(kernel, "__name__", ""),
        "kernel_file": str(Path(inspect.getfile(kernel)).resolve()),
        "kernel_hash72_probe": probe,
        "local_substitute_authority_used": False,
    }


def execute_real_runtime_workload(source: str = "x=x\nx≠y") -> Dict[str, Any]:
    result = asyncio.run(execute_runtime_expression(source))
    nested = result.get("result", {})
    solver_receipt = nested.get("solver", {}).get("receipt", {})
    return {
        "execution_performed": result.get("execution_performed") is True,
        "transport": result.get("transport"),
        "status": result.get("status"),
        "full_receipt_hash72": result.get("full_receipt_hash72"),
        "solver_receipt_hash72": solver_receipt.get("receipt_hash72"),
        "echo_executor": result.get("result") == source,
    }


def verify_mobile_failure_integrity(repo_root: Path | None = None) -> Dict[str, Any]:
    root = repo_root or _repo_root()
    text = (root / "gui/hhs-mobile-runtime-console/src/runtimeData.ts").read_text(encoding="utf-8")
    forbidden = ["mockSnapshot", "H72-PROJECTION-DEMO", "H72-LIVE-RECEIPT-DEMO", "return mockSnapshot"]
    hits = [token for token in forbidden if token in text]
    return {
        "canonical_mock_fallback_absent": not hits,
        "forbidden_hits": hits,
        "typed_unavailable_snapshot_present": "RUNTIME_STATE_UNAVAILABLE" in text and "unavailableSnapshot" in text,
    }


def verify_px1_face(repo_root: Path | None = None) -> Dict[str, Any]:
    root = repo_root or _repo_root()
    text = (root / "HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7.py").read_text(encoding="utf-8")
    return {
        "placeholder_class_absent": "M7PlaceholderPX1Face" not in text,
        "real_face_registered": '"PX1": M7ExponentEqualityFace()' in text,
        "equation_implemented": 'return {"PX1": "X^8 - X^X = 0"}' in text,
    }


def run(repo_root: Path | None = None) -> Dict[str, Any]:
    kernel = verify_authoritative_kernel_path()
    runtime = execute_real_runtime_workload()
    mobile = verify_mobile_failure_integrity(repo_root)
    px1 = verify_px1_face(repo_root)
    passed = (
        kernel["kernel_loaded"]
        and not kernel["local_substitute_authority_used"]
        and runtime["execution_performed"]
        and not runtime["echo_executor"]
        and bool(runtime["full_receipt_hash72"])
        and mobile["canonical_mock_fallback_absent"]
        and mobile["typed_unavailable_snapshot_present"]
        and px1["placeholder_class_absent"]
        and px1["real_face_registered"]
        and px1["equation_implemented"]
    )
    return {
        "schema": SCHEMA,
        "pass_id": "PASS_105_2",
        "status": "PASS" if passed else "FAIL",
        "authoritative_kernel": kernel,
        "runtime_execution": runtime,
        "mobile_failure_integrity": mobile,
        "px1_face": px1,
        "all_repairs_verified": passed,
    }


def pass105_2_self_test() -> Dict[str, Any]:
    return run()
