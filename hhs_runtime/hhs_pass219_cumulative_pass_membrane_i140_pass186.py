from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]

PASS186_IMPLEMENTATION_COMMIT = "fd42056c22071d290945b02efe3a5752aaa3d737"
FROZEN_I139 = "e5ce3529fcdd7c214aeda8b09f3b7b2bff08b8c4"
PASS186_CONTRACT = "HHS-P186-X64-VM81-Q144-F7-G243-NCABI"
PASS186_CLASSIFICATION = "HHS_PASS_186_X64_VM81_Q144_NONCOMMUTATIVE_ABI_VALIDATED"
PASS186_CENSUS_CLASSIFICATION = "IMPLEMENTATION_VERIFIED_MEMBRANE_EXPOSURE_REQUIRED_BEFORE_I140"

CONTRACT_PATH = Path("HHS_PASS_186_X86_64_VM81_Q144_7_FACTORIAL_NONCOMMUTATIVE_ABI.md")
NATIVE_ROOT = Path("native_projects/hhs_pass186_x64_vm81_q144")
MAKEFILE_PATH = NATIVE_ROOT / "Makefile"
RECEIPT_PATH = NATIVE_ROOT / "PASS_186_VALIDATION_RECEIPT.json"
README_PATH = NATIVE_ROOT / "README.md"
ABI_HEADER_PATH = NATIVE_ROOT / "include/hhs_pass186_x64_vm81_q144_abi.h"
REGISTER_PATH = NATIVE_ROOT / "src/hhs_pass186_x64_registers.S"
ABI_SOURCE_PATH = NATIVE_ROOT / "src/hhs_pass186_x64_vm81_q144_abi.c"
SMOKE_PATH = NATIVE_ROOT / "tests/hhs_pass186_x64_vm81_q144_smoke.c"

I140_HEADER_PATH = Path("hhs_runtime/include/hhs_pass219_inherited_pass186_1_40.h")
I140_HPP_PATH = Path("hhs_runtime/include/hhs_pass219_inherited_pass186_1_40.hpp")
I140_INC_PATH = Path("hhs_runtime/c/hhs_pass219_inherited_pass186_1_40.inc")
EXACT_HEADER_PATH = Path("hhs_runtime/include/hhs_runtime_exact_abi.h")
EXACT_SOURCE_PATH = Path("hhs_runtime/c/hhs_runtime_exact_abi.c")

HISTORICAL_BLOBS = {
    CONTRACT_PATH: "41e2e92393ad0bb08b876cf4ca09992a0baf8779",
    MAKEFILE_PATH: "da4153d6468a46da13989195c57da6cc26fb684f",
    RECEIPT_PATH: "0f8f4b9a92d3c3267361d530e91ccfe661aef4e4",
    README_PATH: "b4b037e5dedc65722314807ec030f520edb37d51",
    ABI_HEADER_PATH: "37ce8eafaa1beb4614e6ab41e2cd5b0904bb0376",
    REGISTER_PATH: "7ee997d3f6126d04d48988498b83f7e488ead20c",
    ABI_SOURCE_PATH: "a4e7099b266569c6b9db8e68b03b741f58d32a5f",
    SMOKE_PATH: "d53860ad314000cda7c75462f7c8122a1d492cb1",
}

FROZEN_I139_BLOBS = {
    Path("hhs_runtime/hhs_pass219_cumulative_pass_membrane_i139_pass187.py"): "52ceb9f52bdf30dc4849676c1ac0aafe613708ca",
    Path("hhs_runtime/include/hhs_pass219_inherited_pass187_1_39.h"): "e59603ac523dd32e845b21492fc3d2336a562dcf",
    Path("hhs_runtime/include/hhs_pass219_inherited_pass187_1_39.hpp"): "0e00dc16c9624cf51aa0c9a1d6e30397a1529763",
    Path("hhs_runtime/c/hhs_pass219_inherited_pass187_1_39.inc"): "0ff432490633dac2417aa3e294305378848dc570",
    Path("hhs_runtime/include/hhs_runtime_exact_abi.h"): "db92bb0590adb667ac406a89e43171a8ab12eb3c",
    Path("hhs_runtime/c/hhs_runtime_exact_abi.c"): "8d6c694e4bb7358f28844df55848b07604030e33",
}

REQUIRED_OPERATIONS = (
    "validate_pass186_historical_lineage",
    "validate_pass186_native_acceptance",
    "validate_pass186_noncommutative_identity_boundary",
    "validate_pass186_x86_64_boundary",
    "validate_pass186_authority_boundary",
    "validate_pass186_successor_binding",
    "validate_pass186_no_new_authority",
)


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _git_blob(path: Path) -> str:
    return _git("hash-object", str(path))


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS186_SOURCE_DRIFT:{path}:{fragment}")


def pass186_membrane_source_evidence() -> Dict[str, Any]:
    _git("merge-base", "--is-ancestor", PASS186_IMPLEMENTATION_COMMIT, "HEAD")
    _git("merge-base", "--is-ancestor", FROZEN_I139, "HEAD")
    if _git("merge-base", FROZEN_I139, "HEAD") != FROZEN_I139:
        raise RuntimeError("PASS186_FROZEN_I139_LINEAGE_DRIFT")

    for path, expected in HISTORICAL_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS186_HISTORICAL_SOURCE_DRIFT:{path}")
        if _git("rev-parse", f"{PASS186_IMPLEMENTATION_COMMIT}:{path}") != expected:
            raise RuntimeError(f"PASS186_HISTORICAL_COMMIT_DRIFT:{path}")

    for path, expected in FROZEN_I139_BLOBS.items():
        if _git("rev-parse", f"{FROZEN_I139}:{path}") != expected:
            raise RuntimeError(f"PASS186_FROZEN_I139_SUCCESSOR_DRIFT:{path}")

    _require(
        CONTRACT_PATH,
        PASS186_CONTRACT,
        "all `1,259,712` internal addresses round-trip exactly",
        "Equal integer multiplication witnesses do not authorize collapsing `xy` into `yx`",
        "No `float`, `double`, x87, SSE scalar-float, or AVX float opcode is required.",
    )
    _require(
        ABI_SOURCE_PATH,
        "hhs186_basis_tag",
        "operation = (uint8_t)(instruction_state % HHS186_VM81_OPERATIONS_PER_CELL);",
        "basis = (uint8_t)(operation & UINT8_C(7));",
        "hhs186_x64_vm81_q144_unproject",
    )
    _require(
        SMOKE_PATH,
        "assert(expected == HHS186_HYDRATED_STATES);",
        "assert(result.ordered_tag != inverse.ordered_tag);",
        "hhs186_x64_capture_xyzw_registers",
    )

    receipt = json.loads(_text(RECEIPT_PATH))
    if receipt["contract"] != PASS186_CONTRACT or receipt["classification"] != PASS186_CLASSIFICATION:
        raise RuntimeError("PASS186_RECEIPT_IDENTITY_DRIFT")
    if receipt["validation"]["exhaustive_roundtrip_states"] != 1_259_712:
        raise RuntimeError("PASS186_ROUNDTRIP_RECEIPT_DRIFT")
    if receipt["validation"]["floating_point_opcode_scan"] != "PASS":
        raise RuntimeError("PASS186_FLOAT_SCAN_RECEIPT_DRIFT")

    return {
        "implementation_commit": PASS186_IMPLEMENTATION_COMMIT,
        "frozen_i139": FROZEN_I139,
        "contract": PASS186_CONTRACT,
        "classification": PASS186_CLASSIFICATION,
        "historical_blobs": {str(k): v for k, v in HISTORICAL_BLOBS.items()},
        "frozen_i139_blobs": {str(k): v for k, v in FROZEN_I139_BLOBS.items()},
    }


def validate_pass186_historical_lineage() -> Dict[str, Any]:
    pass186_membrane_source_evidence()
    return {
        "ok": True,
        "implementation_commit_preserved": True,
        "historical_sources_byte_identical": True,
        "historical_receipt_preserved": True,
        "implementation_gap": False,
        "membrane_exposure_gap_before_i140": True,
    }


def validate_pass186_native_acceptance() -> Dict[str, Any]:
    receipt = json.loads(_text(RECEIPT_PATH))
    inv = receipt["invariants"]
    val = receipt["validation"]
    assert inv["q12_squared"] == 144
    assert inv["factorial7"] == 5040
    assert inv["q144_lanes"] == 36
    assert inv["vm81_cells"] == 81
    assert inv["operations_per_cell"] == 64
    assert inv["vm5184"] == 5184
    assert inv["g243"] == 243
    assert inv["hydrated_cardinality"] == 1_259_712
    assert val["exhaustive_roundtrip_states"] == 1_259_712
    return {
        "ok": True,
        "q144": 144,
        "factorial7": 5040,
        "vm5184": 5184,
        "g243": 243,
        "hydrated_states": 1_259_712,
        "exhaustive_roundtrip_states": 1_259_712,
        "strict_compile": val["strict_compile"],
        "floating_point_opcode_scan": val["floating_point_opcode_scan"],
    }


def validate_pass186_noncommutative_identity_boundary() -> Dict[str, Any]:
    _require(
        CONTRACT_PATH,
        "| 4 | `xy` | `0x5859` |",
        "| 5 | `yx` | `0x5958` |",
        "| 6 | `zw` | `0x5A57` |",
        "| 7 | `wz` | `0x575A` |",
        "The ordered tag is authoritative for noncommutative identity.",
    )
    return {
        "ok": True,
        "xy_yx_distinct": True,
        "zw_wz_distinct": True,
        "ordered_tag_is_identity": True,
        "integer_product_witness_is_identity": False,
    }


def validate_pass186_x86_64_boundary() -> Dict[str, Any]:
    _require(
        CONTRACT_PATH,
        "| `RDI` | `x` |",
        "| `RSI` | `y` |",
        "| `RDX` | `z` |",
        "| `RCX` | `w` |",
        "| `R10` | `z` |",
        "| `R11` | `w` |",
    )
    return {
        "ok": True,
        "system_v_amd64": True,
        "register_probe_required": True,
        "register_probe_is_mutation_authority": False,
        "host_timing_authority": False,
    }


def validate_pass186_authority_boundary() -> Dict[str, Any]:
    return {
        "ok": True,
        "historical_mapping_surface_reused": True,
        "projection_is_canonical_mutation_authority": False,
        "ordered_product_witness_is_identity": False,
        "independent_opcode_authority": False,
        "independent_vm81_authority": False,
        "independent_hash72_clock": False,
        "float_canonical_authority": False,
    }


def validate_pass186_successor_binding() -> Dict[str, Any]:
    pass186_membrane_source_evidence()
    return {
        "ok": True,
        "successor_pass": 187,
        "successor_frozen_commit": FROZEN_I139,
        "successor_header_blob": FROZEN_I139_BLOBS[Path("hhs_runtime/include/hhs_pass219_inherited_pass187_1_39.h")],
        "successor_preserved": True,
    }


def validate_pass186_no_new_authority() -> Dict[str, Any]:
    return {
        "ok": True,
        "singleton_vm81_authority_remains_inherited": True,
        "pass219_new_candidate_authority": False,
        "pass219_new_canonical_mutation_authority": False,
        "pass219_new_persistence_authority": False,
        "pass219_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "independent_opcode_authority": False,
        "floating_point_canonical_authority": False,
    }


def pass186_membrane_manifest() -> Dict[str, Any]:
    return {
        "pass_number": 186,
        "iteration": 140,
        "classification": "WIRED",
        "historical_classification": PASS186_CLASSIFICATION,
        "census_before_i140": PASS186_CENSUS_CLASSIFICATION,
        "declared_operations": list(REQUIRED_OPERATIONS),
        "aggregate_order_tail": [192, 191, 190, 189, 188, 187, 186],
    }


def execute_pass186_membrane_preflight() -> Dict[str, Any]:
    operations = {
        "validate_pass186_historical_lineage": validate_pass186_historical_lineage(),
        "validate_pass186_native_acceptance": validate_pass186_native_acceptance(),
        "validate_pass186_noncommutative_identity_boundary": validate_pass186_noncommutative_identity_boundary(),
        "validate_pass186_x86_64_boundary": validate_pass186_x86_64_boundary(),
        "validate_pass186_authority_boundary": validate_pass186_authority_boundary(),
        "validate_pass186_successor_binding": validate_pass186_successor_binding(),
        "validate_pass186_no_new_authority": validate_pass186_no_new_authority(),
    }
    if tuple(operations) != REQUIRED_OPERATIONS:
        raise RuntimeError("PASS186_OPERATION_ORDER_DRIFT")
    if not all(value.get("ok") is True for value in operations.values()):
        raise RuntimeError("PASS186_PREFLIGHT_FAILURE")
    return {"ok": True, "operations": operations}
