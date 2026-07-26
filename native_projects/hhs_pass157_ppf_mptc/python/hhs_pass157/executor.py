from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
from typing import Any

from .model import construct_exact
from .parser import compile_membrane, hash216

CONTRACT = "HHS-P157-PPF-MPTC"
VERSION = "1.1.0"
TERMINAL = "HHS_PASS_157_PYTHAGOREAN_PLASTIC_FIBONACCI_MODULAR_PHASE_TENSOR_CONSTRUCTOR_VERIFIED"
PENDING_MAIN = "HHS_PASS_157_VERIFIED_PENDING_MAIN_MERGE"
SOURCE = "P^2/(t^3-t)==P^2 Mod pq; x+y<zw<x<z<yx<wz<y<w<xy<b^2<c^2"


def _native_binary() -> Path:
    configured = os.environ.get("HHS_PASS157_NATIVE")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2] / "dist" / "hhs-pass157"


def native_verify() -> dict[str, Any]:
    completed = subprocess.run([str(_native_binary()), "verify"], check=True, text=True, capture_output=True)
    return json.loads(completed.stdout)


def verify() -> dict[str, Any]:
    membrane = compile_membrane(SOURCE, "CHECK_MEMBRANE")
    exact = construct_exact(
        P=5, p=2, q=3, euclid_m=3, euclid_n=2,
        full_rotation=-137, local_modulus=72, centerline=tuple(range(1, 12)),
    )
    native = native_verify()
    checks = {
        "contract": native["contract"] == CONTRACT,
        "version": native["version"] == VERSION,
        "P2": native["P2"] == exact.P2,
        "P4": native["P4"] == exact.P4,
        "Delta": native["Delta"] == exact.Delta,
        "pythagorean": tuple(native["pythagorean"]) == exact.pythagorean,
        "tensor_hash216": native["tensor_hash216"] == exact.tensor_hash216,
        "vm81_projection_hash216": native["vm81_projection_hash216"] == exact.vm81_hash216,
        "native_replay": native["replay"] == "MATCH",
        "membrane_global": membrane["global_simultaneous_constraint"] is True,
        "source_preserved": membrane["parse"]["original_text"] == SOURCE,
        "source_hash216": len(membrane["parse"]["source_hash216"]) == 216,
        "equality_lanes": membrane["lane_count"] == 2,
        "centerline_topology": [label for label, _ in exact.centerline] == ["x+y", "zw", "x", "z", "yx", "wz", "y", "w", "xy", "b^2", "c^2"],
        "vm81_cells": len(exact.vm81_cells) == 81,
        "typed_ast": len(membrane["typed_ast"]) > 0,
        "nfv_object": len(native["result_hash216"]) == 216 and len(native["receipt_hash72"]) == 72,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"Pass 157 verification failed: {failed}")
    canonical = json.dumps({"membrane": membrane["membrane_hash216"], "native": native["result_hash216"], "checks": checks}, sort_keys=True, separators=(",", ":"))
    return {
        "schema": "HHS_PASS_157_VERIFICATION_V1",
        "contract": CONTRACT,
        "version": VERSION,
        "classification": TERMINAL if os.environ.get("HHS_PASS157_MAIN_MERGED") == "1" else PENDING_MAIN,
        "checks": checks,
        "check_count": len(checks),
        "membrane_hash216": membrane["membrane_hash216"],
        "native_result_hash216": native["result_hash216"],
        "receipt_hash72": native["receipt_hash72"],
        "verification_hash216": hash216(canonical.encode()),
        "nfv_object": {
            "schema": "HHS_PASS_154_NFV_OBJECT_V1",
            "identity_hash216": native["result_hash216"],
            "membrane_hash216": membrane["membrane_hash216"],
            "receipt_hash72": native["receipt_hash72"],
            "authority": "VM81",
        },
        "replay": "MATCH",
    }
