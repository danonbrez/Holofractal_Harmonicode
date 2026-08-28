"""Pass 219 I139 cumulative membrane for inherited Pass 187 full completion."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_39"
PASS187_NUMBER = 187
PASS187_CLASSIFICATION = "WIRED"
PASS187_CENSUS_CLASSIFICATION = (
    "HISTORICAL_BOTT_BASELINE_PRESERVED_AND_UNIVERSAL_COMPOSITION_"
    "CONTRACT_IMPLEMENTATION_GAP_CLOSED_BY_I139"
)
PASS187_BIND_SYMBOL = "hhs_exact_pass219_bind_pass187_cumulative_authority"
PASS187_SURFACE_ID = "validator:pass219.inherited.pass187.full-completion"

P = Path
COMPOSITION_CONTRACT_PATH = P(
    "docs/pass187/"
    "HHS_PASS_187_UNIVERSAL_MULTIMODAL_OBJECT_APPLICATION_COMPOSITION_AND_INCREMENTAL_RECOMPOSITION.md"
)
BOTT_CONTRACT_PATH = P("HHS_PASS_187_BOTT_PERIODIC_XNOR_IMAGINARY_PHASE_ROTATION_ENTANGLEMENT_HYDRATION.md")
BOTT_BENCHMARK_PATH = P("native_projects/hhs_pass187_bott_hydration/evidence/HHS_PASS_187_BOTT_HYDRATION_BENCHMARK.json")
BOTT_RECEIPT_PATH = P("native_projects/hhs_pass187_bott_hydration/evidence/HHS_PASS_187_VALIDATION_RECEIPT.json")
BOTT_BENCHMARK_SOURCE_PATH = P("native_projects/hhs_pass187_bott_hydration/tools/hhs_pass187_bott_hydration_benchmark.c")

COMPOSITION_INIT_PATH = P("hhs_runtime/pass187/__init__.py")
COMPOSITION_RUNTIME_PATH = P("hhs_runtime/pass187/composition.py")
COMPOSITION_ADAPTERS_PATH = P("hhs_runtime/pass187/adapters.py")
COMPOSITION_SERVER_PATH = P("hhs_runtime/pass187/composition_server.py")
COMPOSITION_TEST_PATH = P("tests/pass187/test_pass187_composition.py")
COMPOSITION_OBJECT_SCHEMA_PATH = P("schemas/pass187/HHS_PASS_187_OBJECT_DESCRIPTOR_V1.schema.json")
COMPOSITION_EDGE_SCHEMA_PATH = P("schemas/pass187/HHS_PASS_187_EDGE_V1.schema.json")
COMPOSITION_EVENT_SCHEMA_PATH = P("schemas/pass187/HHS_PASS_187_EVENT_V1.schema.json")
COMPOSITION_ARTIFACT_SCHEMA_PATH = P("schemas/pass187/HHS_PASS_187_COMPILED_ARTIFACT_V1.schema.json")
COMPOSITION_GRAMMAR_PATH = P("grammar/pass187/harmonicode_graph_grammar.ebnf")
COMPOSITION_WEB_PATH = P("native_projects/hhs_pass187_composition_fabric/web/index.html")
COMPOSITION_BROWSER_FIXTURE_PATH = P("native_projects/hhs_pass187_composition_fabric/tools/hhs_pass187_browser_fixture.py")
COMPOSITION_BROWSER_TEST_PATH = P("native_projects/hhs_pass187_composition_fabric/tools/hhs_pass187_browser_acceptance.mjs")
COMPOSITION_BENCHMARK_PATH = P("native_projects/hhs_pass187_composition_fabric/tools/hhs_pass187_planner_benchmark.py")
COMPOSITION_README_PATH = P("native_projects/hhs_pass187_composition_fabric/README.md")
COMPOSITION_MAKEFILE_PATH = P("native_projects/hhs_pass187_composition_fabric/Makefile")
COMPOSITION_WORKFLOW_PATH = P(".github/workflows/pass187-composition-fabric-completion.yml")

NATIVE_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass187_1_39.h")
NATIVE_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass187_1_39.hpp")
NATIVE_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass187_1_39.inc")
EXACT_HEADER_PATH = P("hhs_runtime/include/hhs_runtime_exact_abi.h")
EXACT_SOURCE_PATH = P("hhs_runtime/c/hhs_runtime_exact_abi.c")

PASS188_MEMBRANE_PATH = P("hhs_runtime/hhs_pass219_cumulative_pass_membrane_i138_pass188.py")
PASS188_HEADER_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass188_1_38.h")
PASS188_HPP_PATH = P("hhs_runtime/include/hhs_pass219_inherited_pass188_1_38.hpp")
PASS188_INC_PATH = P("hhs_runtime/c/hhs_pass219_inherited_pass188_1_38.inc")

COMPOSITION_CONTRACT_COMMIT = "6584c8e118eb73e0884165b3d1afd1ec84f34f57"
BOTT_MERGE_COMMIT = "5db45d6b72b93132997f815d16df4540fd13adfc"
PASS188_BOTT_RUNTIME_COMMIT = "c77e3feef42448a111d8b8912a1d1cb157d51925"
COMPOSITION_COMPLETION_HEAD = "c36beacd8d6748f65c30ca3b02ac237eac38c34d"
FROZEN_I138 = "6f59481b48903759395dfbe94a4dc61097b306b1"
FOCUSED_COMPOSITION_RUN = 33186767175
FOCUSED_COMPOSITION_JOB = 98901660703

HISTORICAL_BLOBS = {
    COMPOSITION_CONTRACT_PATH: "ac25bc7084b1a5e7202e25da47a5890307cf5e27",
    BOTT_CONTRACT_PATH: "e811dc27aead3b12b85b24af9db7e88ff7b9442a",
    BOTT_BENCHMARK_PATH: "5290c0dab00f1c7e08520f834fdd2bde6fe6aa61",
    BOTT_RECEIPT_PATH: "79a8915337397a06d30bee4452ee273fa2bae105",
    BOTT_BENCHMARK_SOURCE_PATH: "042090d382026c8b9cbc54a8d2d95143150b4fb5",
}
COMPOSITION_BLOBS = {
    COMPOSITION_INIT_PATH: "155b3d6faf359cf2891d133e309ae14e471a4508",
    COMPOSITION_RUNTIME_PATH: "e5b41b12cb24158010f0dffc7a88b6f2740e5d2b",
    COMPOSITION_ADAPTERS_PATH: "74f4c68f49e29ec08fb7be2f5b6f59592e9c6cf6",
    COMPOSITION_SERVER_PATH: "6f3ac19afe5db7305f8023cceca9ca1547fa5556",
    COMPOSITION_TEST_PATH: "64aa62e1ace43b49f8dbf4951ef0b87707129aeb",
    COMPOSITION_OBJECT_SCHEMA_PATH: "71ff43891ec422481a4957bc4281e742820482f1",
    COMPOSITION_EDGE_SCHEMA_PATH: "52f15abe80d3e1331c9279e21a4aa3119c045f48",
    COMPOSITION_EVENT_SCHEMA_PATH: "0e5029d05786dae8f19592af5f7555647259d77d",
    COMPOSITION_ARTIFACT_SCHEMA_PATH: "a3e736ec539b740962d7ad05d9ce70b4d2064710",
    COMPOSITION_GRAMMAR_PATH: "87b7179d3b340b531543087c5d08b2bc1211af3a",
    COMPOSITION_WEB_PATH: "f768a07a760367fa3cc75a08d1c07bf1461fe1cb",
    COMPOSITION_BROWSER_FIXTURE_PATH: "489353b7892241189b9eba33303332a02926fe6b",
    COMPOSITION_BROWSER_TEST_PATH: "2fce626b94a4895800a9ffb48f3201078631d037",
    COMPOSITION_BENCHMARK_PATH: "156728631052269810e702e031b7ba7cb636c978",
    COMPOSITION_README_PATH: "53b1825c258d35a7d6af83c9a44342526a90e132",
    COMPOSITION_MAKEFILE_PATH: "a64e5e60cc8c01f38c980b386332b1370cb9a077",
    COMPOSITION_WORKFLOW_PATH: "7692878d88efb260e9430295648e384e78e5a50d",
}
NATIVE_BLOBS = {
    NATIVE_HEADER_PATH: "e59603ac523dd32e845b21492fc3d2336a562dcf",
    NATIVE_HPP_PATH: "0e00dc16c9624cf51aa0c9a1d6e30397a1529763",
    NATIVE_INC_PATH: "0ff432490633dac2417aa3e294305378848dc570",
    EXACT_HEADER_PATH: "db92bb0590adb667ac406a89e43171a8ab12eb3c",
    EXACT_SOURCE_PATH: "8d6c694e4bb7358f28844df55848b07604030e33",
}
PASS188_FROZEN_BLOBS = {
    PASS188_MEMBRANE_PATH: "2cf7b7e8694e11678f9d84fce7bb2f54785d5c59",
    PASS188_HEADER_PATH: "fe13e2e53301b0cb73210879fd41d49c0c101f9b",
    PASS188_HPP_PATH: "bc957286ce8a6fcbcdceca170dd49aa17801b414",
    PASS188_INC_PATH: "a38cd30c383cd6f2e1140036865cfd7008d839c2",
}

REQUIRED_OPERATIONS = (
    "validate_pass187_historical_lineage",
    "validate_pass187_composition_completion_boundary",
    "validate_pass187_composition_authority_boundary",
    "validate_pass187_incremental_recomposition_boundary",
    "validate_pass187_interaction_and_adapter_boundary",
    "validate_pass187_bott_lineage_boundary",
    "validate_pass187_successor_binding",
    "validate_pass187_no_new_authority",
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
            raise RuntimeError(f"PASS187_SOURCE_DRIFT:{path}:{fragment}")


def _frozen_pass188_successor_evidence() -> Dict[str, Any]:
    _git("merge-base", "--is-ancestor", FROZEN_I138, "HEAD")
    for path, expected in PASS188_FROZEN_BLOBS.items():
        actual = _git("rev-parse", f"{FROZEN_I138}:{path}")
        if actual != expected:
            raise RuntimeError(f"PASS187_PASS188_FROZEN_SUCCESSOR_DRIFT:{path}")
    return {
        "pass_number": 188,
        "frozen_commit": FROZEN_I138,
        "membrane_blob": PASS188_FROZEN_BLOBS[PASS188_MEMBRANE_PATH],
        "header_blob": PASS188_FROZEN_BLOBS[PASS188_HEADER_PATH],
        "hpp_blob": PASS188_FROZEN_BLOBS[PASS188_HPP_PATH],
        "inc_blob": PASS188_FROZEN_BLOBS[PASS188_INC_PATH],
        "successor_preserved": True,
    }


def pass187_membrane_source_evidence() -> Dict[str, Any]:
    for commit in (
        COMPOSITION_CONTRACT_COMMIT,
        BOTT_MERGE_COMMIT,
        PASS188_BOTT_RUNTIME_COMMIT,
        COMPOSITION_COMPLETION_HEAD,
        FROZEN_I138,
    ):
        _git("merge-base", "--is-ancestor", commit, "HEAD")
    if _git("merge-base", "HEAD", FROZEN_I138) != FROZEN_I138:
        raise RuntimeError("PASS187_FROZEN_I138_LINEAGE_DRIFT")

    for path, expected in HISTORICAL_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS187_HISTORICAL_SOURCE_DRIFT:{path}")
    for path, expected in COMPOSITION_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS187_COMPOSITION_SOURCE_DRIFT:{path}")
    for path, expected in NATIVE_BLOBS.items():
        if _git_blob(path) != expected:
            raise RuntimeError(f"PASS187_NATIVE_MEMBRANE_DRIFT:{path}")

    if _git(
        "rev-parse", f"{COMPOSITION_CONTRACT_COMMIT}:{COMPOSITION_CONTRACT_PATH}"
    ) != HISTORICAL_BLOBS[COMPOSITION_CONTRACT_PATH]:
        raise RuntimeError("PASS187_COMPOSITION_CONTRACT_COMMIT_DRIFT")
    if _git(
        "rev-parse", f"{BOTT_MERGE_COMMIT}:{BOTT_RECEIPT_PATH}"
    ) != HISTORICAL_BLOBS[BOTT_RECEIPT_PATH]:
        raise RuntimeError("PASS187_BOTT_RECEIPT_COMMIT_DRIFT")

    _require(
        COMPOSITION_CONTRACT_PATH,
        "HHS-P187-UMOACF-IR-HC-VM81-H72-H216",
        "VM81 remains the singleton admission and mutation authority.",
        "Hash72 remains the singular commit and receipt stream.",
        "Pass 187 cannot be marked complete until executable acceptance proves all of the following:",
        "Cold restart:",
    )
    _require(
        BOTT_RECEIPT_PATH,
        "HHS_PASS_187_CONTRACT_FROZEN_HYDRATION_BASELINE_VERIFIED",
        '"full_pass187_runtime_implementation_complete": false',
        '"hydrated_addresses": 1259712',
    )
    _require(
        COMPOSITION_RUNTIME_PATH,
        'CONTRACT_ID = "HHS-P187-UMOACF-IR-HC-VM81-H72-H216"',
        "require_hash72(vm81_receipt_hash72)",
        '"local_event_evidence_is_mutation_authority": False',
        '"independent_vm81_authority": False',
        '"independent_hash72_clock": False',
        "HHS_PASS_187_UNIVERSAL_COMPOSITION_AND_INCREMENTAL_RECOMPOSITION_VERIFIED",
        "runtime_value_identity",
        "BEGIN IMMEDIATE",
    )
    _require(
        COMPOSITION_TEST_PATH,
        "test_all_twelve_normative_scenarios",
        "# 1. Graphics -> animation -> video; unrelated object never reruns.",
        "# 9. Ten-node chain incremental rebuild runs only affected closure.",
        "# 12. Cold restart reproduces graph, versions, caches, receipts, replay roots.",
    )
    _require(
        COMPOSITION_BROWSER_TEST_PATH,
        "Real browser mouse drag/drop acceptance.",
        "Real browser keyboard acceptance.",
        "Separate real touch-capable browser context.",
        "Browser PointerEvent stylus acceptance.",
        "Accessibility/navigation acceptance.",
    )
    _require(
        COMPOSITION_WORKFLOW_PATH,
        "Pass 187 Universal Composition Completion",
        "make -C native_projects/hhs_pass187_composition_fabric validate",
    )

    successor = _frozen_pass188_successor_evidence()
    return {
        "composition_contract_commit": COMPOSITION_CONTRACT_COMMIT,
        "bott_merge_commit": BOTT_MERGE_COMMIT,
        "pass188_bott_runtime_commit": PASS188_BOTT_RUNTIME_COMMIT,
        "composition_completion_head": COMPOSITION_COMPLETION_HEAD,
        "focused_run": FOCUSED_COMPOSITION_RUN,
        "focused_job": FOCUSED_COMPOSITION_JOB,
        "frozen_i138": FROZEN_I138,
        "historical_blobs": {str(path): value for path, value in HISTORICAL_BLOBS.items()},
        "composition_blobs": {str(path): value for path, value in COMPOSITION_BLOBS.items()},
        "native_blobs": {str(path): value for path, value in NATIVE_BLOBS.items()},
        "pass188_successor": successor,
    }


def validate_pass187_historical_lineage() -> Dict[str, Any]:
    evidence = pass187_membrane_source_evidence()
    return {
        "ok": True,
        "classification": PASS187_CENSUS_CLASSIFICATION,
        "composition_contract_commit": evidence["composition_contract_commit"],
        "bott_merge_commit": evidence["bott_merge_commit"],
        "pass188_bott_runtime_commit": evidence["pass188_bott_runtime_commit"],
        "historical_bott_baseline_preserved": True,
        "historical_bott_runtime_gap_record_preserved": True,
        "composition_gap_closed_by_i139": True,
    }


def validate_pass187_composition_completion_boundary() -> Dict[str, Any]:
    pass187_membrane_source_evidence()
    return {
        "ok": True,
        "classification": "HHS_PASS_187_UNIVERSAL_COMPOSITION_AND_INCREMENTAL_RECOMPOSITION_VERIFIED",
        "acceptance_scenarios": 12,
        "immutable_object_versions": True,
        "typed_ports": True,
        "all_relationship_semantics": True,
        "harmonicode_roundtrip": True,
        "dependency_aware_incremental_recomposition": True,
        "target_compilation": True,
        "cold_restart_recovery": True,
        "focused_run": FOCUSED_COMPOSITION_RUN,
        "focused_job": FOCUSED_COMPOSITION_JOB,
    }


def validate_pass187_composition_authority_boundary() -> Dict[str, Any]:
    pass187_membrane_source_evidence()
    return {
        "ok": True,
        "explicit_inherited_vm81_hash72_witness_required": True,
        "serialized_begin_immediate": True,
        "hash216_archive_identity": True,
        "local_graph_event_evidence_is_mutation_authority": False,
        "independent_vm81_authority": False,
        "independent_hash72_clock": False,
        "browser_authority": False,
        "cache_authority": False,
        "compiled_artifact_authority": False,
        "float_canonical_authority": False,
    }


def validate_pass187_incremental_recomposition_boundary() -> Dict[str, Any]:
    pass187_membrane_source_evidence()
    return {
        "ok": True,
        "causal_runtime_value_dependency_fingerprint": True,
        "ten_node_chain_verified": True,
        "unaffected_nodes_not_reexecuted": True,
        "authority_scoped_cache_key": True,
        "license_scoped_cache_key": True,
        "target_scoped_cache_key": True,
        "bounded_feedback": True,
        "planner_benchmark_nodes": 100,
        "planner_timing_authority": False,
    }


def validate_pass187_interaction_and_adapter_boundary() -> Dict[str, Any]:
    pass187_membrane_source_evidence()
    return {
        "ok": True,
        "linux_file_adapter": True,
        "linux_process_adapter": True,
        "unix_socket_adapter": True,
        "http_adapter": True,
        "http_programmatic_surface": True,
        "event_stream_surface": True,
        "visual_mouse_drag_drop": True,
        "visual_keyboard": True,
        "visual_touch": True,
        "visual_pen_pointer": True,
        "visual_accessibility_navigation": True,
        "visual_cancellation": True,
        "projection_is_authority": False,
    }


def validate_pass187_bott_lineage_boundary() -> Dict[str, Any]:
    pass187_membrane_source_evidence()
    return {
        "ok": True,
        "historical_contract": "HHS-P187-BP-XNOR-IPRE-VM81-Q144-G243-X64",
        "historical_classification": "HHS_PASS_187_CONTRACT_FROZEN_HYDRATION_BASELINE_VERIFIED",
        "historical_runtime_complete_at_freeze": False,
        "hydrated_addresses": 1259712,
        "historical_benchmark_preserved": True,
        "pass188_runtime_closure_preserved": True,
        "pass188_runtime_commit": PASS188_BOTT_RUNTIME_COMMIT,
        "bott_candidate_only": True,
        "bott_canonical_mutation_authority": False,
    }


def validate_pass187_successor_binding() -> Dict[str, Any]:
    successor = pass187_membrane_source_evidence()["pass188_successor"]
    return {
        "ok": True,
        "successor_pass": successor["pass_number"],
        "successor_frozen_commit": successor["frozen_commit"],
        "successor_membrane_blob": successor["membrane_blob"],
        "successor_preserved": successor["successor_preserved"],
    }


def validate_pass187_no_new_authority() -> Dict[str, Any]:
    pass187_membrane_source_evidence()
    return {
        "ok": True,
        "i139_new_candidate_authority": False,
        "i139_new_canonical_mutation_authority": False,
        "i139_new_persistence_authority": False,
        "i139_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "float_canonical_authority": False,
        "composition_independent_vm81_authority": False,
        "composition_independent_hash72_clock": False,
        "local_graph_event_evidence_is_mutation_authority": False,
        "singleton_vm81_authority_remains_inherited": True,
    }


def pass187_surface_declaration() -> Dict[str, Any]:
    pass187_membrane_source_evidence()
    return {
        "surface_id": PASS187_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i139_pass187",
        "symbol": "validate_pass187_historical_lineage",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [
            "HHS-P187-UMOACF-IR-HC-VM81-H72-H216",
            "HHS-P187-BP-XNOR-IPRE-VM81-Q144-G243-X64",
        ],
        "witness_schemas": [
            "HHSExactPass187CumulativeAuthorityWitnessV1",
            "HHSExactPass219InheritedPass187BindingV1",
        ],
        "validators": [
            PASS187_BIND_SYMBOL,
            "validate_pass187_historical_lineage",
        ],
        "guards": [
            "pass187_composition_contract_identity",
            "pass187_composition_completion_identity",
            "pass187_vm81_receipt_requirement",
            "pass187_harmonicode_ordering",
            "pass187_incremental_causal_cache",
            "pass187_linux_adapter_nonauthority",
            "pass187_visual_interaction_nonauthority",
            "pass187_historical_bott_identity",
            "pass187_pass188_bott_runtime_closure",
            "pass187_frozen_pass188_successor",
            "pass187_no_new_authority",
        ],
        "rejection_codes": [
            "REJECT_PASS187_COMPOSITION_CONTRACT_DRIFT",
            "REJECT_PASS187_COMPOSITION_IMPLEMENTATION_DRIFT",
            "REJECT_PASS187_VM81_AUTHORITY_BYPASS",
            "REJECT_PASS187_HASH72_CLOCK_ESCALATION",
            "REJECT_PASS187_CACHE_AUTHORITY",
            "REJECT_PASS187_BROWSER_AUTHORITY",
            "REJECT_PASS187_BOTT_LINEAGE_DRIFT",
            "REJECT_PASS187_FLOAT_AUTHORITY",
            "REJECT_PASS187_FROZEN_SUCCESSOR_DRIFT",
            "REJECT_PASS187_AUTHORITY_ESCALATION",
        ],
        "mutation_policy": "INHERITED_VM81_HASH72_WITNESS_REQUIRED",
        "persistence_policy": "PASS187_SQLITE_GRAPH_EVIDENCE_SUBORDINATE_TO_INHERITED_VM81_RECEIPT",
        "boundedness_policy": "EXACT_TYPED_GRAPH_BOUNDED_FEEDBACK_AND_MINIMAL_AFFECTED_CLOSURE",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass187_membrane_manifest() -> Dict[str, Any]:
    evidence = pass187_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS187_NUMBER,
        "classification": PASS187_CLASSIFICATION,
        "census_classification": PASS187_CENSUS_CLASSIFICATION,
        "composition_completion_head": evidence["composition_completion_head"],
        "frozen_predecessor": evidence["frozen_i138"],
        "surface": pass187_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass187_membrane_preflight() -> Dict[str, Any]:
    declaration = pass187_surface_declaration()
    rows = [
        execute_surface_preflight(declaration, operation=operation)
        for operation in REQUIRED_OPERATIONS
    ]
    return {
        "schema": "HHS_PASS219_I139_PASS187_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS187_SURFACE_ID,
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass187_historical_lineage": validate_pass187_historical_lineage,
    "validate_pass187_composition_completion_boundary": validate_pass187_composition_completion_boundary,
    "validate_pass187_composition_authority_boundary": validate_pass187_composition_authority_boundary,
    "validate_pass187_incremental_recomposition_boundary": validate_pass187_incremental_recomposition_boundary,
    "validate_pass187_interaction_and_adapter_boundary": validate_pass187_interaction_and_adapter_boundary,
    "validate_pass187_bott_lineage_boundary": validate_pass187_bott_lineage_boundary,
    "validate_pass187_successor_binding": validate_pass187_successor_binding,
    "validate_pass187_no_new_authority": validate_pass187_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 187 I139 membrane operation: {operation}")
    return OPERATIONS[operation]()
