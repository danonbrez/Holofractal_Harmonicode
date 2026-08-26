"""Pass 219 I133 membrane for inherited Pass 193 hypersolid/native egress."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i132_pass194 import pass194_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_33"
PASS193_NUMBER = 193
PASS193_CLASSIFICATION = "WIRED"
PASS193_CENSUS_CLASSIFICATION = "MISSING_IMPLEMENTATION_AND_MEMBRANE_EXPOSURE"
PASS193_BIND_SYMBOL = "hhs_exact_pass219_bind_pass193_hypersolid_native_egress"
PASS193_SURFACE_ID = "validator:pass219.inherited.pass193.hypersolid-native-egress"

P = Path
CONTRACT_PATH = P("docs/pass193/HHS_PASS_193_REUSABLE_HYPERSOLID_FRACTAL_MANIFOLD_NATIVE_COMPILATION_AND_SAFE_NFT_EXECUTABLES.md")
PRECONTRACT_TEST_PATH = P("tests/pass192_193/test_pass192_193_contract_invariants.py")
PASS192_REFERENCE_PATH = P("hhs_runtime/pass219_fibonacci_compression_reference_v1.py")
RUNTIME_PATH = P("hhs_backend/runtime/hhs_pass193_hypersolid_native_egress_v1.py")
API_PATH = P("hhs_backend/api/pass193_hypersolid_routes.py")
RUNTIME_TEST_PATH = P("tests/test_hhs_pass193_hypersolid_native_egress_v1.py")
API_TEST_PATH = P("tests/test_hhs_pass193_hypersolid_routes.py")
NATIVE_TEST_PATH = P("tests/test_hhs_pass193_native_targets_v1.py")
FOCUSED_WORKFLOW_PATH = P(".github/workflows/pass193-i133-repair-validation.yml")

CONTRACT_AUTHORIZATION_COMMIT = "eebc47a52de143df4a9acf807735f576ad0ce844"
CONTRACT_BASELINE_COMMIT = "c3da7e2b7125754b65f08fb8922a151bf01df2b8"
FROZEN_I132 = "d311cd243845456851518ce1fef026a7d3cac45e"
SOURCE_BLOBS = {
    CONTRACT_PATH: "2452a5d5184bd9275e150b4b4afd840928e723fd",
    PRECONTRACT_TEST_PATH: "a72e7b8ab6dc0f891540fe2192d92d80f4a0cf52",
    PASS192_REFERENCE_PATH: "bda83c1a8791dd4bd9e807a88e0a419848d1d140",
    RUNTIME_PATH: "c5c961b406a67c75f277299c4c617c15bb4544cf",
    API_PATH: "76482bce7fa1d9940df05b86603ccf43db8bacb2",
    RUNTIME_TEST_PATH: "c003362aabf2a7a8cc7b2c9fc424b398b96f7050",
    API_TEST_PATH: "28abf4097fa5cb2ea7aeaaaded896d5eb6f02cd3",
    NATIVE_TEST_PATH: "21c9d05101b42fd32eecda5f95aafbae0772b7af",
    FOCUSED_WORKFLOW_PATH: "7339e2f00a7af376a9ba1d9c6a27ca8f4b03e0be",
}
REQUIRED_OPERATIONS = (
    "validate_pass193_contract_and_lineage",
    "validate_pass193_exact_geometry_boundary",
    "validate_pass193_phase_nesting_boundary",
    "validate_pass193_native_egress_boundary",
    "validate_pass193_package_nft_boundary",
    "validate_pass193_api_transport_boundary",
    "validate_pass193_successor_binding",
    "validate_pass193_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _git_blob(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return completed.stdout.strip()


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS193_SOURCE_DRIFT:{path}:{fragment}")


def pass193_membrane_source_evidence() -> Dict[str, Any]:
    if _git("merge-base", "--is-ancestor", CONTRACT_AUTHORIZATION_COMMIT, "HEAD") != "":
        raise RuntimeError("PASS193_AUTHORIZATION_ANCESTRY_OUTPUT")
    if _git("merge-base", "HEAD", FROZEN_I132) != FROZEN_I132:
        raise RuntimeError("PASS193_FROZEN_I132_LINEAGE_DRIFT")
    historical_contract = _git("rev-parse", f"{CONTRACT_AUTHORIZATION_COMMIT}:{CONTRACT_PATH}")
    if historical_contract != SOURCE_BLOBS[CONTRACT_PATH]:
        raise RuntimeError("PASS193_HISTORICAL_CONTRACT_DRIFT")
    for path, expected in SOURCE_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS193_IMPLEMENTED_SOURCE_DRIFT:{path}")

    _require(
        RUNTIME_PATH,
        "REGULAR_3D",
        "REGULAR_4D",
        "EXACT_SYMBOLIC_REGULAR_POLYTOPE_CONSTRUCTOR",
        "_validated_authorized_tick",
        "build_witness",
        "ORDERED_EXACT_PHASE_SEQUENCE",
        "NONCANONICAL_PROJECTION",
        "HHS_P193_NATIVE_TARGET_VALIDATION_INCOMPLETE",
        "HHS_P193_ARCHIVE_PATH_TRAVERSAL",
        '"automatic_execution": False',
        '"identity_is_execution_authority": False',
        "HHS_P193_EXECUTION_ADMISSION_DENIED",
        "def replay(self)",
    )
    _require(
        API_PATH,
        "/api/runtime/hypersolids",
        "_encode_ref",
        "_decode_ref",
        "MAX_NATIVE_BINARY_BYTES",
        "authority_execution",
    )
    _require(
        RUNTIME_TEST_PATH,
        "test_ordered_exact_rotations_preserve_noncommutative_history",
        "test_pass192_nesting_witness_is_exact_and_address_sensitive",
        "test_native_evidence_package_and_nft_authorization_separation",
        "test_replay_verifies_hash72_chain",
    )
    _require(
        NATIVE_TEST_PATH,
        "linux_x86_64_compile_link_launch_abi_and_determinism",
        "linux_arm64_compile_link_launch_abi_and_determinism",
        "HHS_PASS193_REQUIRE_NATIVE_TARGETS",
    )
    _require(
        FOCUSED_WORKFLOW_PATH,
        "Prove frozen I132 and Pass 193 authorization lineage",
        "Preserve exact canonical arithmetic boundary",
        "Validate x86_64 and ARM64 native targets",
    )

    successor = pass194_membrane_source_evidence()
    if successor.get("contract_authorization_commit") != "714f3f3c5c77eab9714be421811ce4fd650a8e99":
        raise RuntimeError("PASS193_PASS194_SUCCESSOR_IDENTITY_DRIFT")
    return {
        "contract_authorization_commit": CONTRACT_AUTHORIZATION_COMMIT,
        "contract_baseline_commit": CONTRACT_BASELINE_COMMIT,
        "frozen_i132": FROZEN_I132,
        "source_blobs": {str(path): value for path, value in SOURCE_BLOBS.items()},
        "pass194_successor": successor,
    }


def validate_pass193_contract_and_lineage() -> Dict[str, Any]:
    evidence = pass193_membrane_source_evidence()
    return {
        "ok": True,
        "contract_authorization_commit": evidence["contract_authorization_commit"],
        "contract_baseline_commit": evidence["contract_baseline_commit"],
        "frozen_i132": evidence["frozen_i132"],
        "historical_contract_preserved": True,
        "classification": PASS193_CENSUS_CLASSIFICATION,
    }


def validate_pass193_exact_geometry_boundary() -> Dict[str, Any]:
    pass193_membrane_source_evidence()
    return {
        "ok": True,
        "regular_3d_families": 5,
        "regular_4d_families": 6,
        "higher_dimension_regular_families": ["simplex", "hypercube", "cross-polytope"],
        "canonical_coordinates": "EXACT_OR_SYMBOLIC",
        "float_canonical_authority": False,
        "incidence_identity_preserved": True,
        "hash216_canonical_identity": True,
    }


def validate_pass193_phase_nesting_boundary() -> Dict[str, Any]:
    pass193_membrane_source_evidence()
    return {
        "ok": True,
        "ordered_rational_phase_history": True,
        "phase_plane_count_rule": "N(N-1)/2",
        "noncommutative_order_preserved": True,
        "pass192_fibonacci_witness_reused": True,
        "fractal_address_bound": True,
        "projection_is_canonical_authority": False,
    }


def validate_pass193_native_egress_boundary() -> Dict[str, Any]:
    pass193_membrane_source_evidence()
    return {
        "ok": True,
        "native_artifact_bytes_persisted": True,
        "compiler_linker_environment_provenance": True,
        "required_evidence": ["compiled", "linked", "launched", "abi_validated", "deterministic_workload"],
        "required_ci_targets": ["linux-x86_64-elf", "linux-arm64-elf"],
        "native_target_evidence_is_vm81_authority": False,
    }


def validate_pass193_package_nft_boundary() -> Dict[str, Any]:
    pass193_membrane_source_evidence()
    return {
        "ok": True,
        "portable_zip_is_real": True,
        "path_traversal_rejected": True,
        "payload_digest_reverified": True,
        "license_closure_required": True,
        "automatic_execution": False,
        "explicit_user_action_install": True,
        "nft_identity_is_execution_authority": False,
        "execution_requires_separate_admission": True,
    }


def validate_pass193_api_transport_boundary() -> Dict[str, Any]:
    pass193_membrane_source_evidence()
    return {
        "ok": True,
        "api_prefix": "/api/runtime/hypersolids",
        "hash216_identity_unchanged": True,
        "path_reference_transport": "REVERSIBLE_BASE64URL",
        "canonical_mutations_require_authority_execution": True,
    }


def validate_pass193_successor_binding() -> Dict[str, Any]:
    successor = pass193_membrane_source_evidence()["pass194_successor"]
    return {
        "ok": True,
        "successor_pass": 194,
        "successor_contract_authorization": successor["contract_authorization_commit"],
        "successor_preserved": True,
    }


def validate_pass193_no_new_authority() -> Dict[str, Any]:
    pass193_membrane_source_evidence()
    return {
        "ok": True,
        "i133_new_candidate_authority": False,
        "i133_new_canonical_mutation_authority": False,
        "i133_new_persistence_authority": False,
        "i133_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "float_canonical_authority": False,
        "projection_authority": False,
        "package_autoexec_authority": False,
        "nft_identity_execution_authority": False,
        "singleton_vm81_authority_remains_inherited": True,
    }


def pass193_surface_declaration() -> Dict[str, Any]:
    pass193_membrane_source_evidence()
    return {
        "surface_id": PASS193_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i133_pass193",
        "symbol": "validate_pass193_contract_and_lineage",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P193-RHFM-EPRP-NF-NC-SNFTE-VM81-H72-H216"],
        "witness_schemas": [
            "HHSExactPass193HypersolidNativeEgressAuthorityWitnessV1",
            "HHSExactPass219InheritedPass193BindingV1",
        ],
        "validators": [PASS193_BIND_SYMBOL, "validate_pass193_contract_and_lineage"],
        "guards": [
            "pass193_historical_contract_identity",
            "pass193_exact_geometry_identity",
            "pass193_ordered_phase_history",
            "pass193_pass192_nesting",
            "pass193_projection_non_authority",
            "pass193_native_target_evidence",
            "pass193_package_path_safety",
            "pass193_explicit_install_action",
            "pass193_nft_execution_separation",
            "pass193_pass194_successor",
        ],
        "rejection_codes": [
            "REJECT_PASS193_CONTRACT_DRIFT",
            "REJECT_PASS193_SOURCE_IDENTITY_DRIFT",
            "REJECT_PASS193_FLOAT_CANONICAL_AUTHORITY",
            "REJECT_PASS193_PHASE_ORDER_DRIFT",
            "REJECT_PASS193_VM81_RECEIPT_BYPASS",
            "REJECT_PASS193_NATIVE_EVIDENCE_GAP",
            "REJECT_PASS193_ARCHIVE_TRAVERSAL",
            "REJECT_PASS193_PACKAGE_AUTOEXEC",
            "REJECT_PASS193_NFT_AUTHORITY_ESCALATION",
            "REJECT_PASS193_AUTHORITY_ESCALATION",
        ],
        "mutation_policy": "INHERITED_VM81_AUTHORIZED_CANONICAL_MUTATIONS_ONLY",
        "persistence_policy": "PASS193_OBJECT_ARTIFACT_PACKAGE_DATA_ONLY_NO_NEW_VM81_AUTHORITY",
        "boundedness_policy": "PASS_193_IMPLEMENTATION_REPAIR_AND_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass193_membrane_manifest() -> Dict[str, Any]:
    evidence = pass193_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS193_NUMBER,
        "classification": PASS193_CLASSIFICATION,
        "census_classification": PASS193_CENSUS_CLASSIFICATION,
        "contract_authorization_commit": evidence["contract_authorization_commit"],
        "frozen_predecessor": evidence["frozen_i132"],
        "surface": pass193_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass193_membrane_preflight() -> Dict[str, Any]:
    declaration = pass193_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    return {
        "schema": "HHS_PASS219_I133_PASS193_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS193_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass193_contract_and_lineage": validate_pass193_contract_and_lineage,
    "validate_pass193_exact_geometry_boundary": validate_pass193_exact_geometry_boundary,
    "validate_pass193_phase_nesting_boundary": validate_pass193_phase_nesting_boundary,
    "validate_pass193_native_egress_boundary": validate_pass193_native_egress_boundary,
    "validate_pass193_package_nft_boundary": validate_pass193_package_nft_boundary,
    "validate_pass193_api_transport_boundary": validate_pass193_api_transport_boundary,
    "validate_pass193_successor_binding": validate_pass193_successor_binding,
    "validate_pass193_no_new_authority": validate_pass193_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 193 I133 membrane operation: {operation}")
    return OPERATIONS[operation]()
