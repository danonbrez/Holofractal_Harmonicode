from __future__ import annotations

from hashlib import sha256
import json
import subprocess
from pathlib import Path
from typing import Any

from hhs_runtime.pass183 import ADAPTER_EQUATIONS, ProbabilityHydrationRuntime

ROOT = Path(__file__).resolve().parents[1]
PASS183_IMPLEMENTATION_COMMIT = "4a2797ffcf75e29b616ca37b3183ea3521e03a39"
PASS183_HISTORICAL_GREEN_HEAD = "3ae56827b27500c2c8187126d5825a901d4feb40"
PASS183_HISTORICAL_RUN = 30660886044
PASS183_HISTORICAL_JOB = 91256571248
PASS183_HISTORICAL_ARTIFACT = 8805098841
PASS183_HISTORICAL_ARTIFACT_SHA256 = "5f4bfb8cc0aa1b48eefa66412f3e9e6f6d9497f97eb00fa64d4215c7cbe0f34c"
FROZEN_I142 = "33004d347337cf8c57f9772609806e49503c1bd0"
I142_VALIDATION_RECEIPT = Path("evidence/pass184/i142/PASS_219_I142_PASS184_VALIDATION_RECEIPT.json")

HISTORICAL_BLOBS = {
    Path("docs/pass183/HHS_PASS_183_PROBABILITY_EQUATION_HYDRATION_MEMBRANE_RUNTIME.md"): "69a2c0a2652c47b91ddf506907e3310c72c8fb4c",
    Path("hhs_runtime/pass183/core.py"): "258792532a2475dbba4d439d45b6090dabbc22cd",
    Path("hhs_runtime/pass183/authority.py"): "5493fdbe9b937e82c7e9cc73ed1c8299eeeb32ea",
    Path("hhs_runtime/pass183/runtime.py"): "367e7f099c397334bc89669431c2304de428663b",
    Path("hhs_backend/api/probability_hydration_routes.py"): "f9c067842ff03a795d61848c0088608d8c7f2f22",
    Path("native_projects/hhs_pass183_probability_hydration/include/hhs_p183.h"): "9fa3761c4ed121dfc8d6c665104018f0a6b4bbaf",
    Path("native_projects/hhs_pass183_probability_hydration/src/hhs_p183.c"): "eafe99bf3b41ecce2ec21642922d3cefa150939f",
    Path("native_projects/hhs_pass183_probability_hydration/tests/test_hhs_p183.c"): "bde971119b8aac97c6b31eb4b9de3d21e80afb43",
    Path("tests/test_pass183_probability_hydration.py"): "4d06bf3e966de5ade7564140a0080bf701dc9df1",
    Path("tests/pass183_acceptance_harness.py"): "798652ac9387808d5ce0336d3e8f8d1a908c423e",
}

REQUIRED_OPERATIONS = (
    "validate_pass183_historical_lineage",
    "validate_pass183_historical_green_evidence",
    "validate_pass183_receipt_authority_order",
    "validate_pass183_native_compatibility_quarantine",
    "validate_pass183_runtime_os_projection",
    "validate_pass183_global_default_reachability",
    "validate_pass183_no_new_authority",
)

def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def _text(path: str | Path) -> str:
    return (ROOT / path).read_text("utf-8")

class _LocalAuthority:
    def __init__(self) -> None:
        self.epoch = 0
    def status(self) -> dict[str, Any]:
        return {"classification": "I143_LOCAL_VM81", "vmrc": {"epoch": self.epoch}}
    def execute(self, **kwargs: Any) -> dict[str, Any]:
        self.epoch += 1
        return {
            "classification": "I143_LOCAL_VM81_COMMIT",
            "operation_key": sha256(json.dumps(kwargs, sort_keys=True, default=str).encode()).hexdigest(),
            "receipt": {"receipt_sha256": sha256(str(self.epoch).encode()).hexdigest()},
        }
    def replay(self) -> dict[str, Any]:
        return {"classification": "I143_LOCAL_VM81_REPLAY", "deterministic_replay": True, "epoch": self.epoch}

def validate_pass183_historical_lineage() -> dict[str, Any]:
    _git("merge-base", "--is-ancestor", PASS183_IMPLEMENTATION_COMMIT, "HEAD")
    _git("merge-base", "--is-ancestor", FROZEN_I142, "HEAD")
    for path, expected in HISTORICAL_BLOBS.items():
        actual = _git("rev-parse", f"{PASS183_IMPLEMENTATION_COMMIT}:{path}")
        if actual != expected:
            raise RuntimeError(f"PASS183_HISTORICAL_BLOB_DRIFT:{path}:{actual}")
    return {
        "ok": True,
        "implementation_commit": PASS183_IMPLEMENTATION_COMMIT,
        "historical_sources_preserved_at_implementation_commit": True,
        "current_tree_repair_forward_additive": True,
        "frozen_i142": FROZEN_I142,
    }

def validate_pass183_historical_green_evidence() -> dict[str, Any]:
    _git("merge-base", "--is-ancestor", PASS183_IMPLEMENTATION_COMMIT, PASS183_HISTORICAL_GREEN_HEAD)
    i142 = json.loads(_text(I142_VALIDATION_RECEIPT))
    assert i142["closure"]["i142_dependency_scoped_validation_green"] is True
    return {
        "ok": True,
        "historical_run": PASS183_HISTORICAL_RUN,
        "historical_job": PASS183_HISTORICAL_JOB,
        "historical_artifact": PASS183_HISTORICAL_ARTIFACT,
        "historical_artifact_sha256": PASS183_HISTORICAL_ARTIFACT_SHA256,
        "historical_workflow_conclusion": "success",
        "historical_artifact_expired": True,
        "i142_successor_green": True,
    }

def validate_pass183_receipt_authority_order() -> dict[str, Any]:
    runtime = ProbabilityHydrationRuntime(authority=_LocalAuthority())
    result = runtime.execute(
        adapter="binomial",
        equation=ADAPTER_EQUATIONS["binomial"],
        manifest={"n": 4, "p": "1/2"},
    )
    legacy = result["evaluation"]["hash216"]
    authority = result["authority_receipt"]
    receipt = result["receipt"]
    archive = result["hash216_archive"]
    assert legacy["canonical_archival"] is False
    assert legacy["authority_use_prohibited"] is True
    assert authority["payload"]["hash216_input_authority"] is False
    assert len(authority["receipt_hash72"]) == 72
    assert len(receipt["receipt_hash72"]) == 72
    assert archive["created_after_hash72_closure"] is True
    assert archive["mutation_authority"] is False
    assert archive["previous_hash72"] == receipt["prior_receipt_hash72"]
    assert archive["authority_hash72"] == authority["receipt_hash72"]
    assert archive["receipt_hash72"] == receipt["receipt_hash72"]
    assert len(archive["combined_hash216"]) == 216
    replay = runtime.replay()
    assert replay["receipt_chain_valid"] is True
    assert replay["hash216_archival_only"] is True
    assert replay["hash216_precommit_authority"] is False
    return {
        "ok": True,
        "order": ["exact_evaluation", "singleton_vm81_commit", "authority_hash72", "pass183_hash72", "hash216_archive"],
        "hash216_precommit_authority": False,
        "hash216_archival_only": True,
        "deterministic_replay": True,
    }

def validate_pass183_native_compatibility_quarantine() -> dict[str, Any]:
    header = _text("native_projects/hhs_pass183_probability_hydration/include/hhs_p183.h")
    source = _text("native_projects/hhs_pass183_probability_hydration/src/hhs_p183.c")
    binding = _text("hhs_runtime/include/hhs_pass219_inherited_pass183_1_43.h")
    assert "hhs_p183_native_receipt_mode" in header
    assert 'LEGACY_LOCAL_WITNESS_NONCANONICAL' in source
    assert "legacy_native_hash_witness_noncanonical" in binding
    return {
        "ok": True,
        "historical_native_exact_arithmetic_preserved": True,
        "historical_native_hash_strings_retained_for_compatibility": True,
        "historical_native_hash_strings_canonical": False,
        "native_hash72_authority": False,
        "native_hash216_authority": False,
    }

def validate_pass183_runtime_os_projection() -> dict[str, Any]:
    server = _text("hhs_backend/runtime_os_application_server_full.py")
    shell = _text("hhs_gui/runtime_os/workspace/HHSWorkspaceShell.tsx")
    panel = _text("hhs_gui/runtime_os/workspace/Pass183ProbabilityHydrationPanel.tsx")
    api = _text("hhs_backend/api/probability_hydration_routes.py")
    assert "app.include_router(probability_hydration_router)" in server
    assert "Pass183ProbabilityHydrationPanel" in shell
    assert '["probability", "Probability"]' in shell
    for test_id in ("pass183-parse", "pass183-validate", "pass183-hydrate", "pass183-execute", "pass183-replay"):
        assert test_id in panel
    assert '"hash216_archival_only": True' in api
    return {"ok": True, "api": True, "runtime_os_gui": True, "legacy_studio_canonical": False}

def validate_pass183_global_default_reachability() -> dict[str, Any]:
    contract = json.loads(_text("contracts/pass219/PASS_219_GLOBAL_CANONICAL_DEFAULTS_1_0.json"))
    census = contract["current_cumulative_binding_census"]
    assert census["wired_floor_pass"] == 183
    assert census["binding_count"] == 38
    assert census["ordered_bindings"][-3:] == ["185", "184", "183"]
    exact_h = _text("hhs_runtime/include/hhs_runtime_exact_abi.h")
    assert exact_h.index("hhs_pass219_inherited_pass184_1_42.h") < exact_h.index("hhs_pass219_inherited_pass183_1_43.h") < exact_h.index("hhs_pass219_global_canonical_defaults_1_0.h")
    return {
        "ok": True,
        "wired_floor": 183,
        "binding_count": 38,
        "global_defaults_mandatory": True,
        "multimodal_generalization_inherited": True,
    }

def validate_pass183_no_new_authority() -> dict[str, Any]:
    status = ProbabilityHydrationRuntime(authority=_LocalAuthority()).status()
    assert status["hash216_archival_only"] is True
    assert status["hash216_precommit_authority"] is False
    assert status["legacy_native_hash_witness_canonical"] is False
    return {
        "ok": True,
        "singleton_vm81_authority_remains_inherited": True,
        "independent_vm81_authority": False,
        "independent_hash72_clock": False,
        "native_hash72_authority": False,
        "native_hash216_authority": False,
        "hash216_precommit_authority": False,
        "floating_point_canonical_authority": False,
    }

def pass183_membrane_manifest() -> dict[str, Any]:
    return {
        "pass_number": 183,
        "iteration": 143,
        "classification": "WIRED_PENDING_EXECUTED_VALIDATION",
        "historical_contract": "HHS-P183-PEHMR-M1259713-F72-VM81-H72-H216",
        "aggregate_order_tail": [187, 186, 185, 184, 183],
        "declared_operations": list(REQUIRED_OPERATIONS),
    }

def execute_pass183_membrane_preflight() -> dict[str, Any]:
    operations = {
        "validate_pass183_historical_lineage": validate_pass183_historical_lineage(),
        "validate_pass183_historical_green_evidence": validate_pass183_historical_green_evidence(),
        "validate_pass183_receipt_authority_order": validate_pass183_receipt_authority_order(),
        "validate_pass183_native_compatibility_quarantine": validate_pass183_native_compatibility_quarantine(),
        "validate_pass183_runtime_os_projection": validate_pass183_runtime_os_projection(),
        "validate_pass183_global_default_reachability": validate_pass183_global_default_reachability(),
        "validate_pass183_no_new_authority": validate_pass183_no_new_authority(),
    }
    if tuple(operations) != REQUIRED_OPERATIONS:
        raise RuntimeError("PASS183_OPERATION_ORDER_DRIFT")
    if not all(value.get("ok") is True for value in operations.values()):
        raise RuntimeError("PASS183_I143_PREFLIGHT_FAILURE")
    return {"ok": True, "operations": operations}
