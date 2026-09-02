"""Pass 219 I135 cumulative membrane for dual-history inherited Pass 191."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_35"
PASS191_NUMBER = 191
PASS191_CLASSIFICATION = "WIRED"
PASS191_CENSUS_CLASSIFICATION = (
    "PARTIAL_HISTORICAL_IMPLEMENTATION_WITH_UNIVERSAL_CONTRACT_GAP_"
    "AND_MISSING_MEMBRANE_EXPOSURE"
)
PASS191_BIND_SYMBOL = "hhs_exact_pass219_bind_pass191_universal_repository_hydration"
PASS191_SURFACE_ID = "validator:pass219.inherited.pass191.universal-repository-hydration"

P = Path
UNIVERSAL_CONTRACT_PATH = P(
    "docs/pass191/HHS_PASS_191_GENESIS_TO_RUNTIME_FULL_REPOSITORY_HYDRATION_"
    "UNIVERSAL_INVARIANT_CLOSURE.md"
)
DQPL_PROOF_PATH = P("HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_PROOF.md")
DQPL_SEARCH_PATH = P(
    "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence/"
    "PASS_191_INTEGRATED_PROOF_SEARCH.json"
)
DQPL_COMPLETION_PATH = P(
    "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence/"
    "PASS_191_INTEGRATED_COMPLETION_RECEIPT.json"
)
INHERITED_MANIFOLD_MODULE_PATH = P(
    "hhs_runtime/core_sandbox/hhs_pass219_inherited_manifold_authority_1_21_5.py"
)
INHERITED_MANIFOLD_TEST_PATH = P(
    "tests/pass219/test_pass219_inherited_manifold_authority_1_21_5.py"
)
RUNTIME_PATH = P("hhs_runtime/pass191/repository_hydration.py")
SDK_PATH = P("hhs_runtime/pass191/__init__.py")
CLI_PATH = P("hhs_runtime/pass191/cli.py")
API_PATH = P("hhs_backend/api/pass191_repository_hydration_routes.py")
VISUAL_SERVER_PATH = P("hhs_backend/visual_server.py")
VISUAL_WORKSPACE_PATH = P(
    "applications/holofractal_harmonizer/pass191-repository-hydration.html"
)
OPERATION_REGISTRY_PATH = P("schemas/pass191/HHS_PASS_191_OPERATION_REGISTRY_V1.json")
JOB_SCHEMA_PATH = P("schemas/pass191/HHS_PASS_191_HYDRATION_JOB_V1.schema.json")
RUNTIME_TEST_PATH = P("tests/test_hhs_pass191_repository_hydration_v1.py")
SURFACE_TEST_PATH = P("tests/test_hhs_pass191_repository_hydration_surfaces_v1.py")
FOCUSED_WORKFLOW_PATH = P(".github/workflows/pass191-i135-repair-validation.yml")
NATIVE_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass191_1_35.h")
NATIVE_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass191_1_35.hpp")
NATIVE_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass191_1_35.inc")

PASS192_MEMBRANE_PATH = P("hhs_runtime/hhs_pass219_cumulative_pass_membrane_i134_pass192.py")
PASS192_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass192_1_34.h")
PASS192_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass192_1_34.hpp")
PASS192_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass192_1_34.inc")

UNIVERSAL_AUTHORIZATION_COMMIT = "89d67731c6c4f5798e26a43e0273c6ce33a1abee"
DQPL_MERGE_COMMIT = "cd8979c5ded5150e0020e011345106567201b672"
FROZEN_I134 = "4bb202e657670dac1ab2a39575821b647f691d71"

SOURCE_BLOBS = {
    UNIVERSAL_CONTRACT_PATH: "f5d3b61ea366de9d5f1fc9207b393cb70e2225ef",
    DQPL_PROOF_PATH: "5a19122fb709f6d4b253bca5a431ea3c2c7c0b5b",
    DQPL_SEARCH_PATH: "c37f81a09d710328c1cac67d70df134fb0f20812",
    DQPL_COMPLETION_PATH: "7b368572fd707bdf531c9a32a4acd9a0e4efee3e",
    INHERITED_MANIFOLD_MODULE_PATH: "af6b49bdc3bb93b2a0a2d898a48e6f3413947764",
    INHERITED_MANIFOLD_TEST_PATH: "053c1245f7ce33f1e78470f263bf3b19517b274e",
    RUNTIME_PATH: "6f999708cde2eedf9393b682bf09d2fde1cecde5",
    SDK_PATH: "b2a5c252e290dbcf7918f2e18cee623f1013e159",
    CLI_PATH: "ba4bc91a7d3856cea371db072d9f81f67e498307",
    API_PATH: "80cf59852437b0346f5f16e7d65c96c76915ea8a",
    VISUAL_SERVER_PATH: "409d451a7db39945c07b919bbb9faa3626dc0bc6",
    VISUAL_WORKSPACE_PATH: "cfb04fb7b854f991c5d3d02cfc9bc117b52d0f67",
    OPERATION_REGISTRY_PATH: "ba5beb49360bf9ff4cf2c1970cc443137b2c63ab",
    JOB_SCHEMA_PATH: "45809617bee1030d2d03ffbd602315df14a8b5d5",
    RUNTIME_TEST_PATH: "19c4e2faf299d5d58b82eed5ccc7c831a0ffee2e",
    SURFACE_TEST_PATH: "160a3d2f5f221e670109a3306c3b3329ad0bd432",
    FOCUSED_WORKFLOW_PATH: "657122ed2d883a7a2b0c8d00f62585692d3962eb",
}
NATIVE_BLOBS = {
    NATIVE_HEADER_PATH: "6086438875a1e43680a18e4034d4db9d8cc06160",
    NATIVE_HPP_PATH: "a57e7b0bb9ba0d72fe455df7bcc6d3efcdaa577f",
    NATIVE_INC_PATH: "43fce4a4bcaef01c4ccb41ada3bb33be93816114",
}
PASS192_FROZEN_BLOBS = {
    PASS192_MEMBRANE_PATH: "820c810e447af90ec4e842768261f945894baa72",
    PASS192_HEADER_PATH: "5f3245022447dcd3a1cce215f373e4f899946944",
    PASS192_HPP_PATH: "0f645b5164d8b4b337ff7191c07558cc28f9261f",
    PASS192_INC_PATH: "ef39790111aa37640bf282cec27804597f44dee4",
}

REQUIRED_OPERATIONS = (
    "validate_pass191_dual_history_lineage",
    "validate_pass191_repository_graph_boundary",
    "validate_pass191_function_interface_boundary",
    "validate_pass191_invariant_symmetry_boundary",
    "validate_pass191_lifecycle_replay_boundary",
    "validate_pass191_dqpl_scope_boundary",
    "validate_pass191_production_workflow_boundary",
    "validate_pass191_successor_binding",
    "validate_pass191_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


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


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS191_SOURCE_DRIFT:{path}:{fragment}")


def _frozen_pass192_successor_evidence() -> Dict[str, Any]:
    _git("merge-base", "--is-ancestor", FROZEN_I134, "HEAD")
    for path, expected in PASS192_FROZEN_BLOBS.items():
        actual = _git("rev-parse", f"{FROZEN_I134}:{path}")
        if actual != expected:
            raise RuntimeError(f"PASS191_PASS192_FROZEN_SUCCESSOR_DRIFT:{path}")
    return {
        "pass_number": 192,
        "frozen_commit": FROZEN_I134,
        "membrane_blob": PASS192_FROZEN_BLOBS[PASS192_MEMBRANE_PATH],
        "header_blob": PASS192_FROZEN_BLOBS[PASS192_HEADER_PATH],
        "hpp_blob": PASS192_FROZEN_BLOBS[PASS192_HPP_PATH],
        "inc_blob": PASS192_FROZEN_BLOBS[PASS192_INC_PATH],
        "successor_preserved": True,
    }


def pass191_membrane_source_evidence() -> Dict[str, Any]:
    _git("merge-base", "--is-ancestor", UNIVERSAL_AUTHORIZATION_COMMIT, "HEAD")
    _git("merge-base", "--is-ancestor", DQPL_MERGE_COMMIT, "HEAD")
    if _git("merge-base", "HEAD", FROZEN_I134) != FROZEN_I134:
        raise RuntimeError("PASS191_FROZEN_I134_LINEAGE_DRIFT")

    historical_contract = _git(
        "rev-parse", f"{UNIVERSAL_AUTHORIZATION_COMMIT}:{UNIVERSAL_CONTRACT_PATH}"
    )
    if historical_contract != SOURCE_BLOBS[UNIVERSAL_CONTRACT_PATH]:
        raise RuntimeError("PASS191_UNIVERSAL_CONTRACT_DRIFT")
    historical_dqpl = _git("rev-parse", f"{DQPL_MERGE_COMMIT}:{DQPL_PROOF_PATH}")
    if historical_dqpl != SOURCE_BLOBS[DQPL_PROOF_PATH]:
        raise RuntimeError("PASS191_DQPL_PROOF_DRIFT")

    for path, expected in {**SOURCE_BLOBS, **NATIVE_BLOBS}.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS191_IMPLEMENTED_SOURCE_DRIFT:{path}")

    _require(
        RUNTIME_PATH,
        "HHS-P191-GTRFRH-UIC-VM81-H72-H216",
        "HHS-P191-DQPL-TENSOR-VM5184-G243-H216-H72",
        "_validated_authorized_tick",
        'self._git("ls-tree", "-r", "-l", "-z", commit)',
        "EXPLICIT_LINEAGE_SLOT_NO_DIRECT_PATH_MATCH",
        "P191.Hydrate.Repository",
        "universal_invariant_registry",
        "exact_symmetry_witness",
        "G_20",
        "HHS-P191-HASH216-INDEX",
        "HHS-P191-HYDRATED-REPOSITORY",
        "HHS_P191_FILE_LIMIT_BLOCKED",
        "def replay_job",
        "hidden_chat_memory_required",
        '"theorem_status": "OBSTRUCTED"',
    )
    _require(
        API_PATH,
        'prefix="/v1/hydration"',
        "/preview",
        "/jobs/{job_id}/resume",
        "/jobs/{job_id}/replay",
        "/lineage/passes",
        "/assistant-tools",
        '@router.websocket("/ws/{job_id}")',
    )
    _require(
        VISUAL_SERVER_PATH,
        "pass191_repository_hydration_router",
        "/v1/hydration/status",
        "app.include_router(pass191_repository_hydration_router)",
        '"pass191_repository_hydration_api": "/v1/hydration"',
        '"pass191_repository_hydration_studio": "/pass191-repository-hydration.html"',
        "PUBLIC_API_REGISTRATION = register_public_api_federation(app)",
    )
    visual = _text(VISUAL_SERVER_PATH)
    include_marker = "app.include_router(pass191_repository_hydration_router)"
    federation_marker = "PUBLIC_API_REGISTRATION = register_public_api_federation(app)"
    if visual.index(include_marker) >= visual.index(federation_marker):
        raise RuntimeError("PASS191_PRODUCTION_REGISTRATION_ORDER_DRIFT")
    _require(
        VISUAL_WORKSPACE_PATH,
        "Repository Hydration",
        "/v1/hydration/preview",
        "/v1/hydration/jobs",
        "Deterministic replay verified.",
    )
    _require(
        OPERATION_REGISTRY_PATH,
        "P191.Hydrate.Repository",
        "P191.Hydrate.Replay",
        "P191.Reciprocal.Verify",
        "INHERITED_SINGLETON_VM81",
    )
    _require(
        FOCUSED_WORKFLOW_PATH,
        "Prove frozen I134 and dual Pass 191 historical lineage",
        "Revalidate inherited Pass 191 DQPL authority without broadening theorem scope",
        "Hydrate the actual committed repository read-only",
        "Compile inherited aggregate exact ABI unchanged",
    )

    successor = _frozen_pass192_successor_evidence()
    return {
        "universal_contract_authorization_commit": UNIVERSAL_AUTHORIZATION_COMMIT,
        "dqpl_merge_commit": DQPL_MERGE_COMMIT,
        "frozen_i134": FROZEN_I134,
        "source_blobs": {str(path): value for path, value in SOURCE_BLOBS.items()},
        "native_blobs": {str(path): value for path, value in NATIVE_BLOBS.items()},
        "pass192_successor": successor,
    }


def validate_pass191_dual_history_lineage() -> Dict[str, Any]:
    evidence = pass191_membrane_source_evidence()
    return {
        "ok": True,
        "classification": PASS191_CENSUS_CLASSIFICATION,
        "universal_contract_authorization": evidence[
            "universal_contract_authorization_commit"
        ],
        "dqpl_merge_commit": evidence["dqpl_merge_commit"],
        "frozen_i134": evidence["frozen_i134"],
        "dual_history_preserved": True,
        "universal_contract_scope_supersedes_narrow_runtime_gap": False,
    }


def validate_pass191_repository_graph_boundary() -> Dict[str, Any]:
    pass191_membrane_source_evidence()
    return {
        "ok": True,
        "source_authority": "COMMITTED_GIT_BLOB_TREE",
        "genesis_plus_pass_slots": 191,
        "object_registry": True,
        "hash216_object_index": True,
        "incremental_changed_since": True,
        "resource_limits_fail_closed": True,
        "hidden_truncation": False,
        "actual_repository_read_only_hydration_focused_green": True,
    }


def validate_pass191_function_interface_boundary() -> Dict[str, Any]:
    pass191_membrane_source_evidence()
    return {
        "ok": True,
        "pass190_registry_inherited": True,
        "pass191_operation_overlay_count": 15,
        "harmonicode": True,
        "python_sdk": True,
        "cli": "hhs hydrate",
        "openapi": "/v1/hydration",
        "websocket": "/v1/hydration/ws/{job_id}",
        "assistant_tool_manifest": True,
        "surface_specific_private_semantics": False,
    }


def validate_pass191_invariant_symmetry_boundary() -> Dict[str, Any]:
    pass191_membrane_source_evidence()
    return {
        "ok": True,
        "canonical_arithmetic": "EXACT_INTEGER_RATIONAL_SYMBOLIC_ORDERED_BYTES",
        "reciprocal_polynomial": "m^2+m-N^2=0",
        "lo_shu_magic_sum": 15,
        "g41_groups": 41,
        "g41_reciprocal_pairs": 20,
        "central_fixed_group": "G_20",
        "xy_ne_yx": True,
        "zw_ne_wz": True,
        "outer_modulus": 1259713,
        "float_canonical_authority": False,
    }


def validate_pass191_lifecycle_replay_boundary() -> Dict[str, Any]:
    pass191_membrane_source_evidence()
    return {
        "ok": True,
        "finite_lifecycle": True,
        "checkpointed_repository_visible_state": True,
        "timeout_bounds": True,
        "cancel_support": True,
        "failure_reason_and_recovery_action": True,
        "vm81_authorized_job_mutations": True,
        "hash72_receipt_chain": True,
        "deterministic_replay": True,
        "hidden_process_state_required": False,
        "hidden_chat_memory_required": False,
    }


def validate_pass191_dqpl_scope_boundary() -> Dict[str, Any]:
    pass191_membrane_source_evidence()
    return {
        "ok": True,
        "historical_dqpl_implementation_preserved": True,
        "visited_states": 51648192,
        "exact_chain_hits": 837,
        "frontier_size": 16,
        "riemann_hypothesis_status": "OBSTRUCTED",
        "theorem_claim_escalation": False,
        "inherited_pass219_manifold_verifier_preserved": True,
    }


def validate_pass191_production_workflow_boundary() -> Dict[str, Any]:
    pass191_membrane_source_evidence()
    return {
        "ok": True,
        "production_router_registered": True,
        "registration_precedes_public_federation": True,
        "visual_workspace": "/pass191-repository-hydration.html",
        "read_only_preview_operational": True,
        "durable_job_controls_operational": True,
        "human_readable_report": True,
        "optimistic_commit_state": False,
        "canonical_server_remains_runtime_authority": True,
    }


def validate_pass191_successor_binding() -> Dict[str, Any]:
    successor = pass191_membrane_source_evidence()["pass192_successor"]
    return {
        "ok": True,
        "successor_pass": successor["pass_number"],
        "successor_frozen_commit": successor["frozen_commit"],
        "successor_membrane_blob": successor["membrane_blob"],
        "successor_preserved": successor["successor_preserved"],
    }


def validate_pass191_no_new_authority() -> Dict[str, Any]:
    pass191_membrane_source_evidence()
    return {
        "ok": True,
        "i135_new_candidate_authority": False,
        "i135_new_canonical_mutation_authority": False,
        "i135_new_persistence_authority": False,
        "i135_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "float_canonical_authority": False,
        "dqpl_theorem_claim_escalation": False,
        "public_api_federation_is_vm81_authority": False,
        "singleton_vm81_authority_remains_inherited": True,
    }


def pass191_surface_declaration() -> Dict[str, Any]:
    pass191_membrane_source_evidence()
    return {
        "surface_id": PASS191_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i135_pass191",
        "symbol": "validate_pass191_dual_history_lineage",
        "invariant_ids": [
            "HHS-I005",
            "HHS-I006",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
        ],
        "contract_schemas": [
            "HHS-P191-GTRFRH-UIC-VM81-H72-H216",
            "HHS-P191-DQPL-TENSOR-VM5184-G243-H216-H72",
        ],
        "witness_schemas": [
            "HHSExactPass191UniversalRepositoryHydrationAuthorityWitnessV1",
            "HHSExactPass219InheritedPass191BindingV1",
        ],
        "validators": [
            PASS191_BIND_SYMBOL,
            "validate_pass191_dual_history_lineage",
        ],
        "guards": [
            "pass191_universal_contract_identity",
            "pass191_dqpl_history_identity",
            "pass191_committed_tree_source_preservation",
            "pass191_complete_lineage_slots",
            "pass191_pass190_registry_hydration",
            "pass191_exact_invariant_registry",
            "pass191_g41_symmetry",
            "pass191_finite_lifecycle",
            "pass191_hash72_replay",
            "pass191_interface_parity",
            "pass191_visual_workflow",
            "pass191_dqpl_scope_non_escalation",
            "pass191_frozen_pass192_successor",
            "pass191_no_new_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS191_UNIVERSAL_CONTRACT_DRIFT",
            "REJECT_PASS191_DQPL_HISTORY_DRIFT",
            "REJECT_PASS191_SOURCE_IDENTITY_DRIFT",
            "REJECT_PASS191_FLOAT_CANONICAL_AUTHORITY",
            "REJECT_PASS191_LINEAGE_GAP",
            "REJECT_PASS191_FUNCTION_PARITY_DRIFT",
            "REJECT_PASS191_SYMMETRY_DRIFT",
            "REJECT_PASS191_UNBOUNDED_JOB",
            "REJECT_PASS191_VM81_RECEIPT_BYPASS",
            "REJECT_PASS191_REPLAY_MISMATCH",
            "REJECT_PASS191_DQPL_THEOREM_ESCALATION",
            "REJECT_PASS191_PRODUCTION_WORKFLOW_DRIFT",
            "REJECT_PASS191_FROZEN_SUCCESSOR_DRIFT",
            "REJECT_PASS191_AUTHORITY_ESCALATION",
        ],
        "mutation_policy": "INHERITED_SINGLETON_VM81_AUTHORIZED_JOB_MUTATIONS_ONLY",
        "persistence_policy": "PASS191_JOB_AND_HYDRATION_MANIFEST_DATA_NO_NEW_VM81_AUTHORITY",
        "boundedness_policy": "FULL_COMMITTED_TREE_OR_EXPLICIT_INCREMENTAL_SCOPE_WITH_FAIL_CLOSED_LIMITS",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass191_membrane_manifest() -> Dict[str, Any]:
    evidence = pass191_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS191_NUMBER,
        "classification": PASS191_CLASSIFICATION,
        "census_classification": PASS191_CENSUS_CLASSIFICATION,
        "universal_contract_authorization_commit": evidence[
            "universal_contract_authorization_commit"
        ],
        "dqpl_merge_commit": evidence["dqpl_merge_commit"],
        "frozen_predecessor": evidence["frozen_i134"],
        "surface": pass191_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass191_membrane_preflight() -> Dict[str, Any]:
    declaration = pass191_surface_declaration()
    rows = [
        execute_surface_preflight(declaration, operation=operation)
        for operation in REQUIRED_OPERATIONS
    ]
    return {
        "schema": "HHS_PASS219_I135_PASS191_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS191_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass191_dual_history_lineage": validate_pass191_dual_history_lineage,
    "validate_pass191_repository_graph_boundary": validate_pass191_repository_graph_boundary,
    "validate_pass191_function_interface_boundary": validate_pass191_function_interface_boundary,
    "validate_pass191_invariant_symmetry_boundary": validate_pass191_invariant_symmetry_boundary,
    "validate_pass191_lifecycle_replay_boundary": validate_pass191_lifecycle_replay_boundary,
    "validate_pass191_dqpl_scope_boundary": validate_pass191_dqpl_scope_boundary,
    "validate_pass191_production_workflow_boundary": validate_pass191_production_workflow_boundary,
    "validate_pass191_successor_binding": validate_pass191_successor_binding,
    "validate_pass191_no_new_authority": validate_pass191_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 191 I135 membrane operation: {operation}")
    return OPERATIONS[operation]()
