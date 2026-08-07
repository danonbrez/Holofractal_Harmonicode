"""Pass 214 Iteration 8 terminal benchmark/profile freeze authority.

Fail-closed terminal gate for the frozen Pass 214 contract. A terminal freeze is
emitted only when repository census/conformance/reconciliation evidence, A0-A9
benchmark evidence, mandatory ablations, workload corpus, Pass 215 profile, and
live Iteration 7 Pass 213 admission are simultaneously complete.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_backend.runtime.hhs_pass214_authority_conflict_reconciliation_v1 import (
    Pass214AuthorityReconciliationError,
    validate_authority_reconciliation,
)
from hhs_backend.runtime.hhs_pass214_iteration7_live_admission_ablation_v1 import (
    ITERATION6_CANDIDATE_SET_ROOT,
    PASS213_CLOSURE,
    build_ablation_plan,
    validate_recorded_admission,
)

PASS_NUMBER = 214
ITERATION = 8
SCHEMA = "HHS_PASS_214_ITERATION_8_TERMINAL_FREEZE_V1"
INSPECTION_SCHEMA = "HHS_PASS_214_ITERATION_8_READINESS_INSPECTION_V1"
PASS215_PROFILE_SCHEMA = "HHS_PASS_215_BENCHMARK_PROFILE_V1"
CLASSIFICATION = "HHS_PASS_214_TERMINAL_BENCHMARK_AUTHORITY_FROZEN"
BLOCKED_CLASSIFICATION = "HHS_PASS_214_ITERATION_8_TERMINAL_FREEZE_BLOCKED"

TERMINAL_ROOT_NAMES = (
    "PASS214_REPOSITORY_SCAN_ROOT_HASH216",
    "PASS214_OPTIMIZATION_REGISTRY_ROOT_HASH216",
    "PASS214_COMPATIBILITY_GRAPH_ROOT_HASH216",
    "PASS214_WORKLOAD_CORPUS_ROOT_HASH216",
    "PASS214_BENCHMARK_METHOD_ROOT_HASH216",
    "PASS214_COMPOUND_EVIDENCE_ROOT_HASH216",
    "PASS214_AUTHORITY_ROOT_HASH216",
    "PASS215_BENCHMARK_PROFILE_ROOT_HASH216",
)
REQUIRED_STAGES = tuple(f"A{i}" for i in range(10))
MANDATORY_ABLATIONS = (
    "semantic_composition_cache", "conformance_decision_cache",
    "predictive_continuation_cache", "reusable_pattern_cache",
    "vector_shortlist", "exact_compatibility_filtering",
    "exact_delta_cost_reranking", "content_addressed_source_reuse",
    "incremental_tokenization", "sparse_5184_projection",
    "dependency_complete_frontier", "residual_only_processing",
    "parametric_admission", "compiled_rom_reuse",
    "generator_exception_compression", "physical_recovery",
    "receipt_vector_indexing", "sql_context_graph", "encrypted_vector_store",
    "snapshot_reuse", "multimodal_cross_alignment", "bounded_learning_replay",
    "moving_tensor_routing", "native_dispatch", "accelerator_batching",
    "interruption_recovery",
)
REQUIRED_WORKLOAD_FAMILIES = (
    "arithmetic_tensor_primitives", "text_documents", "source_code_ast",
    "structured_data_tables_graphs", "images_spatial_features",
    "audio_temporal_features", "video_motion_scenes", "graphics_game_physics",
    "multimodal_file_folder_ingestion", "vector_retrieval_continuation",
    "ml_feature_candidate_updates", "datasets_evaluations_checkpoints",
    "transformer_shaped_operator_graphs", "full_50388480_position_hydration",
    "arbitrary_high_entropy_controls",
)
REQUIRED_PASS215_COMPARISONS = (
    "dense_reference", "exact_integer_reference", "pass213_compiled_rom_only",
    "compiled_rom_plus_cache_layers", "compiled_rom_plus_continuation_delta",
    "compiled_rom_plus_multimodal_ml", "complete_inherited_hhs_stack",
    "complete_stack_with_ablations",
)
ALLOWED_PROFILE_CLASSES = {
    "REQUIRED", "OPTIONAL", "EXPERIMENTAL", "OBSERVATIONAL_ONLY",
    "INCOMPATIBLE", "SUPERSEDED", "NOT_APPLICABLE",
}
COMPLETE_ABLATION_STATES = {"MEASURED", "NOT_APPLICABLE", "INCOMPATIBLE", "SUPERSEDED"}
COMPLETE_STAGE_STATES = {"MEASURED", "NOT_APPLICABLE"}


class Pass214Iteration8Error(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass214Iteration8Error("PASS214_I8_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN")
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_float(child)


def hash216(domain: str, payload: Any) -> str:
    raw = canonical_bytes(payload)
    return sha256(domain.encode("utf-8") + b"\0" + len(raw).to_bytes(8, "big") + raw).hexdigest()


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise Pass214Iteration8Error(f"PASS214_I8_{label}_MAPPING_REQUIRED")
    return value


def _hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise Pass214Iteration8Error(f"PASS214_I8_{label}_HASH216_INVALID")
    if value == "0" * 64:
        raise Pass214Iteration8Error(f"PASS214_I8_{label}_HASH216_ZERO")
    return value


def _root(domain: str, value: Mapping[str, Any]) -> str:
    _reject_float(value)
    return hash216(domain, value)


def _validate_live_admission(admission: Mapping[str, Any]) -> Mapping[str, Any]:
    validated = validate_recorded_admission(dict(admission))
    for field in (
        "trusted_timestamp_reverified_in_process",
        "governed_surface_reverified_in_process",
        "native_dispatch_reverified_in_process",
    ):
        if validated.get(field) is not True:
            raise Pass214Iteration8Error(f"PASS214_I8_LIVE_ADMISSION_{field.upper()}_REQUIRED")
    if validated.get("pass213_closure") != PASS213_CLOSURE:
        raise Pass214Iteration8Error("PASS214_I8_PASS213_CLOSURE_MISMATCH")
    if validated.get("iteration6_candidate_set_root_hash216") != ITERATION6_CANDIDATE_SET_ROOT:
        raise Pass214Iteration8Error("PASS214_I8_CANDIDATE_SET_ROOT_MISMATCH")
    build_ablation_plan(validated)
    return validated


def validate_benchmark_bundle(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    bundle = _mapping(bundle, "BENCHMARK_BUNDLE")
    _reject_float(bundle)
    if bundle.get("schema") != "HHS_PASS_214_FINAL_COMPOUND_BENCHMARK_BUNDLE_V1":
        raise Pass214Iteration8Error("PASS214_I8_BENCHMARK_SCHEMA_INVALID")
    for field, error in (
        ("semantic_observational_separation", "SEMANTIC_OBSERVATIONAL_SEPARATION_REQUIRED"),
        ("append_only_result_integrity", "APPEND_ONLY_RESULT_INTEGRITY_REQUIRED"),
        ("multimodal_ml_compound_exercised", "MULTIMODAL_ML_COMPOUND_REQUIRED"),
        ("multimodal_ml_ablation_exercised", "MULTIMODAL_ML_ABLATION_REQUIRED"),
        ("incremental_full_equality", "INCREMENTAL_FULL_EQUALITY_REQUIRED"),
        ("recovery_replay_semantic_equality", "RECOVERY_REPLAY_EQUALITY_REQUIRED"),
        ("cross_process_replay_semantic_equality", "CROSS_PROCESS_REPLAY_EQUALITY_REQUIRED"),
        ("negative_controls_fail_closed", "NEGATIVE_CONTROLS_REQUIRED"),
        ("complete_cost_accounting", "COMPLETE_COST_ACCOUNTING_REQUIRED"),
        ("compression_incidence_complete_physical_accounting", "COMPRESSION_ACCOUNTING_REQUIRED"),
    ):
        if bundle.get(field) is not True:
            raise Pass214Iteration8Error(f"PASS214_I8_{error}")
    stages = _mapping(bundle.get("stages"), "STAGES")
    if set(stages) != set(REQUIRED_STAGES):
        raise Pass214Iteration8Error("PASS214_I8_A0_A9_STAGE_SET_INCOMPLETE")
    for stage in REQUIRED_STAGES:
        record = _mapping(stages[stage], f"STAGE_{stage}")
        state = record.get("state")
        if state not in COMPLETE_STAGE_STATES:
            raise Pass214Iteration8Error(f"PASS214_I8_STAGE_{stage}_INCOMPLETE")
        if stage != "A9" and state != "MEASURED":
            raise Pass214Iteration8Error(f"PASS214_I8_STAGE_{stage}_MUST_BE_MEASURED")
        if state == "MEASURED" and record.get("semantic_equal") is not True:
            raise Pass214Iteration8Error(f"PASS214_I8_STAGE_{stage}_SEMANTIC_MISMATCH")
    ablations = _mapping(bundle.get("ablations"), "ABLATIONS")
    if set(ablations) != set(MANDATORY_ABLATIONS):
        raise Pass214Iteration8Error("PASS214_I8_MANDATORY_ABLATION_SET_INCOMPLETE")
    for layer in MANDATORY_ABLATIONS:
        record = _mapping(ablations[layer], f"ABLATION_{layer}")
        state = record.get("state")
        if state not in COMPLETE_ABLATION_STATES:
            raise Pass214Iteration8Error(f"PASS214_I8_ABLATION_{layer.upper()}_INCOMPLETE")
        if state == "MEASURED" and record.get("semantic_equal") is not True:
            raise Pass214Iteration8Error(f"PASS214_I8_ABLATION_{layer.upper()}_SEMANTIC_MISMATCH")
        if state != "MEASURED" and not record.get("reason"):
            raise Pass214Iteration8Error(f"PASS214_I8_ABLATION_{layer.upper()}_REASON_REQUIRED")
    workloads = _mapping(bundle.get("workloads"), "WORKLOADS")
    if set(workloads) != set(REQUIRED_WORKLOAD_FAMILIES):
        raise Pass214Iteration8Error("PASS214_I8_WORKLOAD_FAMILY_SET_INCOMPLETE")
    required_modes = {
        "cold", "warm", "exact_repetition", "shared_structure",
        "single_region_mutation", "multi_region_mutation", "novel_content",
        "contradictory_content", "no_reuse_control", "interruption_recovery",
        "cross_process_replay",
    }
    for family in REQUIRED_WORKLOAD_FAMILIES:
        record = _mapping(workloads[family], f"WORKLOAD_{family}")
        if record.get("state") != "MEASURED" or record.get("semantic_equal") is not True:
            raise Pass214Iteration8Error(f"PASS214_I8_WORKLOAD_{family.upper()}_NOT_EXACTLY_MEASURED")
        if not required_modes.issubset(set(record.get("modes", ()))):
            raise Pass214Iteration8Error(f"PASS214_I8_WORKLOAD_{family.upper()}_MODES_INCOMPLETE")
    return bundle


def validate_pass215_profile(profile: Mapping[str, Any]) -> Mapping[str, Any]:
    profile = _mapping(profile, "PASS215_PROFILE")
    _reject_float(profile)
    if profile.get("schema") != PASS215_PROFILE_SCHEMA:
        raise Pass214Iteration8Error("PASS214_I8_PASS215_PROFILE_SCHEMA_INVALID")
    if tuple(profile.get("required_comparisons", ())) != REQUIRED_PASS215_COMPARISONS:
        raise Pass214Iteration8Error("PASS214_I8_PASS215_COMPARISONS_MISMATCH")
    classes = _mapping(profile.get("optimization_classes"), "PASS215_OPTIMIZATION_CLASSES")
    if not classes:
        raise Pass214Iteration8Error("PASS214_I8_PASS215_OPTIMIZATION_CLASSES_EMPTY")
    for key, value in classes.items():
        if value not in ALLOWED_PROFILE_CLASSES:
            raise Pass214Iteration8Error(f"PASS214_I8_PASS215_PROFILE_CLASS_INVALID:{key}")
    if profile.get("post_hoc_redefinition_forbidden") is not True:
        raise Pass214Iteration8Error("PASS214_I8_PASS215_POST_HOC_REDEFINITION_GUARD_REQUIRED")
    if profile.get("repository_visible_runnable_state") is not True:
        raise Pass214Iteration8Error("PASS214_I8_PASS215_REPOSITORY_VISIBLE_STATE_REQUIRED")
    return profile


def _validate_reconciliation_for_compatibility(
    compatibility_summary: Mapping[str, Any],
    authority_reconciliation: Mapping[str, Any] | None,
) -> Mapping[str, Any] | None:
    coverage = _mapping(compatibility_summary.get("coverage"), "COMPATIBILITY_COVERAGE")
    candidate_count = int(coverage.get("authority_conflict_candidates", 0))
    if candidate_count == 0 and authority_reconciliation is None:
        return None
    report = _mapping(authority_reconciliation, "AUTHORITY_RECONCILIATION")
    try:
        validate_authority_reconciliation(report, compatibility_summary=compatibility_summary)
    except Pass214AuthorityReconciliationError as exc:
        raise Pass214Iteration8Error(str(exc)) from exc
    if int(report.get("candidate_conflict_count", -1)) != candidate_count:
        raise Pass214Iteration8Error("PASS214_I8_AUTHORITY_RECONCILIATION_COUNT_MISMATCH")
    return report


def readiness_blockers(*, census_summary, compatibility_summary, authority_reconciliation=None,
                       benchmark_bundle=None, pass215_profile=None, live_admission=None) -> list[str]:
    blockers: list[str] = []
    try:
        census = _mapping(census_summary, "CENSUS_SUMMARY")
        coverage = _mapping(census.get("coverage"), "CENSUS_COVERAGE")
        if coverage.get("classification_complete") is not True:
            blockers.append("PASS214_I8_REPOSITORY_CENSUS_INCOMPLETE")
        if coverage.get("static_scan_errors") != 0:
            blockers.append("PASS214_I8_STATIC_SCAN_ERRORS_PRESENT")
    except (Pass214Iteration8Error, TypeError) as exc:
        blockers.append(str(exc))
    try:
        compat = _mapping(compatibility_summary, "COMPATIBILITY_SUMMARY")
        coverage = _mapping(compat.get("coverage"), "COMPATIBILITY_COVERAGE")
        if int(coverage.get("active_unresolved", 0)) != 0:
            blockers.append("PASS214_I8_ACTIVE_CALLABLES_UNRESOLVED")
        _validate_reconciliation_for_compatibility(compat, authority_reconciliation)
    except (Pass214Iteration8Error, TypeError, ValueError) as exc:
        blockers.append(str(exc))
    for validator, value in ((validate_benchmark_bundle, benchmark_bundle), (validate_pass215_profile, pass215_profile)):
        try:
            validator(value)
        except (Pass214Iteration8Error, TypeError) as exc:
            blockers.append(str(exc))
    try:
        _validate_live_admission(_mapping(live_admission, "LIVE_ADMISSION"))
    except (Pass214Iteration8Error, TypeError, RuntimeError) as exc:
        blockers.append(str(exc))
    return sorted(set(blockers))


def inspect_terminal_readiness(**kwargs: Any) -> dict[str, Any]:
    blockers = readiness_blockers(**kwargs)
    return {
        "schema": INSPECTION_SCHEMA, "pass": PASS_NUMBER, "iteration": ITERATION,
        "classification": CLASSIFICATION if not blockers else BLOCKED_CLASSIFICATION,
        "ready": not blockers, "blockers": blockers,
        "terminal_roots_minted": False, "authority_promoted": False,
        "migration_active": False, "pass215_authorized": False,
    }


def create_terminal_freeze(*, census_summary, compatibility_summary, authority_reconciliation,
                           workload_corpus, benchmark_method, benchmark_bundle, pass215_profile,
                           live_admission, source_commit: str, source_tree: str) -> dict[str, Any]:
    blockers = readiness_blockers(
        census_summary=census_summary,
        compatibility_summary=compatibility_summary,
        authority_reconciliation=authority_reconciliation,
        benchmark_bundle=benchmark_bundle,
        pass215_profile=pass215_profile,
        live_admission=live_admission,
    )
    if blockers:
        raise Pass214Iteration8Error("PASS214_I8_TERMINAL_FREEZE_BLOCKED:" + "|".join(blockers))
    live = _validate_live_admission(live_admission)
    bundle = validate_benchmark_bundle(benchmark_bundle)
    profile = validate_pass215_profile(pass215_profile)
    reconciliation = _validate_reconciliation_for_compatibility(compatibility_summary, authority_reconciliation)
    if census_summary.get("source_commit") != source_commit or compatibility_summary.get("source_commit") != source_commit:
        raise Pass214Iteration8Error("PASS214_I8_SOURCE_COMMIT_MISMATCH")
    if census_summary.get("source_tree") != source_tree or compatibility_summary.get("source_tree") != source_tree:
        raise Pass214Iteration8Error("PASS214_I8_SOURCE_TREE_MISMATCH")
    census_roots = _mapping(census_summary.get("roots"), "CENSUS_ROOTS")
    compat_roots = _mapping(compatibility_summary.get("roots"), "COMPATIBILITY_ROOTS")
    roots = {
        TERMINAL_ROOT_NAMES[0]: _hash(census_roots.get("repository_tree_root_hash216"), "REPOSITORY_SCAN"),
        TERMINAL_ROOT_NAMES[1]: _hash(census_roots.get("optimization_registry_root_hash216"), "OPTIMIZATION_REGISTRY"),
        TERMINAL_ROOT_NAMES[2]: _hash(compat_roots.get("compatibility_graph_root_hash216") or compat_roots.get("iteration2_semantic_root_hash216"), "COMPATIBILITY_GRAPH"),
        TERMINAL_ROOT_NAMES[3]: _root("pass214-workload-corpus", workload_corpus),
        TERMINAL_ROOT_NAMES[4]: _root("pass214-benchmark-method", benchmark_method),
        TERMINAL_ROOT_NAMES[5]: _root("pass214-compound-evidence", bundle),
        TERMINAL_ROOT_NAMES[7]: _root("pass215-benchmark-profile", profile),
    }
    reconciliation_root = (
        _hash(reconciliation.get("reconciliation_root_hash216"), "AUTHORITY_RECONCILIATION")
        if reconciliation is not None
        else _root("pass214-authority-reconciliation-empty", {"candidate_conflict_count": 0})
    )
    bindings = {
        "pass": PASS_NUMBER, "iteration": ITERATION, "pass213_closure": PASS213_CLOSURE,
        "iteration6_candidate_set_root_hash216": ITERATION6_CANDIDATE_SET_ROOT,
        "source_commit": source_commit, "source_tree": source_tree,
        "live_admission_root_hash216": live["admission_root_hash216"],
        "authority_reconciliation_root_hash216": reconciliation_root,
        "repository_scan_root_hash216": roots[TERMINAL_ROOT_NAMES[0]],
        "optimization_registry_root_hash216": roots[TERMINAL_ROOT_NAMES[1]],
        "compatibility_graph_root_hash216": roots[TERMINAL_ROOT_NAMES[2]],
        "workload_corpus_root_hash216": roots[TERMINAL_ROOT_NAMES[3]],
        "benchmark_method_root_hash216": roots[TERMINAL_ROOT_NAMES[4]],
        "compound_evidence_root_hash216": roots[TERMINAL_ROOT_NAMES[5]],
        "pass215_benchmark_profile_root_hash216": roots[TERMINAL_ROOT_NAMES[7]],
    }
    roots[TERMINAL_ROOT_NAMES[6]] = _root("pass214-terminal-authority", bindings)
    ordered_roots = {name: roots[name] for name in TERMINAL_ROOT_NAMES}
    receipt_payload = {
        "schema": SCHEMA, "classification": CLASSIFICATION,
        "source_commit": source_commit, "source_tree": source_tree,
        "terminal_roots": ordered_roots,
    }
    result = {
        **receipt_payload, "pass": PASS_NUMBER, "iteration": ITERATION,
        "pass213_closure": PASS213_CLOSURE,
        "iteration6_candidate_set_root_hash216": ITERATION6_CANDIDATE_SET_ROOT,
        "live_admission_root_hash216": live["admission_root_hash216"],
        "authority_reconciliation_root_hash216": reconciliation_root,
        "terminal_receipt_hash72": hash72_digest({"domain": "HHS-P214-ITERATION8-TERMINAL-RECEIPT-V1"}, receipt_payload),
        "acceptance_gates_passed": True, "terminal_roots_minted": True,
        "authority_promoted": True, "migration_active": False,
        "pass215_authorized": True, "authority_bindings": deepcopy(bindings),
        "pass215_profile": deepcopy(profile),
    }
    _reject_float(result)
    return result


def validate_terminal_freeze(record: Mapping[str, Any]) -> bool:
    record = _mapping(record, "TERMINAL_RECORD")
    _reject_float(record)
    if record.get("schema") != SCHEMA or record.get("classification") != CLASSIFICATION:
        raise Pass214Iteration8Error("PASS214_I8_TERMINAL_SCHEMA_OR_CLASSIFICATION_INVALID")
    roots = _mapping(record.get("terminal_roots"), "TERMINAL_ROOTS")
    if tuple(roots.keys()) != TERMINAL_ROOT_NAMES:
        raise Pass214Iteration8Error("PASS214_I8_TERMINAL_ROOT_SET_OR_ORDER_INVALID")
    for name in TERMINAL_ROOT_NAMES:
        _hash(roots.get(name), name)
    expected_receipt = hash72_digest(
        {"domain": "HHS-P214-ITERATION8-TERMINAL-RECEIPT-V1"},
        {"schema": record["schema"], "classification": record["classification"],
         "source_commit": record["source_commit"], "source_tree": record["source_tree"],
         "terminal_roots": dict(roots)},
    )
    if record.get("terminal_receipt_hash72") != expected_receipt:
        raise Pass214Iteration8Error("PASS214_I8_TERMINAL_RECEIPT_MISMATCH")
    if record.get("acceptance_gates_passed") is not True or record.get("terminal_roots_minted") is not True:
        raise Pass214Iteration8Error("PASS214_I8_ACCEPTANCE_GATES_NOT_PASSED")
    if record.get("authority_promoted") is not True or record.get("pass215_authorized") is not True:
        raise Pass214Iteration8Error("PASS214_I8_TERMINAL_AUTHORITY_NOT_PROMOTED")
    profile = validate_pass215_profile(record.get("pass215_profile"))
    if roots[TERMINAL_ROOT_NAMES[7]] != _root("pass215-benchmark-profile", profile):
        raise Pass214Iteration8Error("PASS214_I8_PASS215_PROFILE_ROOT_MISMATCH")
    bindings = _mapping(record.get("authority_bindings"), "AUTHORITY_BINDINGS")
    if bindings.get("source_commit") != record.get("source_commit") or bindings.get("source_tree") != record.get("source_tree"):
        raise Pass214Iteration8Error("PASS214_I8_AUTHORITY_BINDING_SOURCE_MISMATCH")
    if bindings.get("authority_reconciliation_root_hash216") != record.get("authority_reconciliation_root_hash216"):
        raise Pass214Iteration8Error("PASS214_I8_AUTHORITY_RECONCILIATION_BINDING_MISMATCH")
    _hash(record.get("authority_reconciliation_root_hash216"), "AUTHORITY_RECONCILIATION")
    for key, terminal in (
        ("repository_scan_root_hash216", TERMINAL_ROOT_NAMES[0]),
        ("optimization_registry_root_hash216", TERMINAL_ROOT_NAMES[1]),
        ("compatibility_graph_root_hash216", TERMINAL_ROOT_NAMES[2]),
        ("workload_corpus_root_hash216", TERMINAL_ROOT_NAMES[3]),
        ("benchmark_method_root_hash216", TERMINAL_ROOT_NAMES[4]),
        ("compound_evidence_root_hash216", TERMINAL_ROOT_NAMES[5]),
        ("pass215_benchmark_profile_root_hash216", TERMINAL_ROOT_NAMES[7]),
    ):
        if bindings.get(key) != roots[terminal]:
            raise Pass214Iteration8Error(f"PASS214_I8_AUTHORITY_BINDING_ROOT_MISMATCH:{key}")
    if roots[TERMINAL_ROOT_NAMES[6]] != _root("pass214-terminal-authority", bindings):
        raise Pass214Iteration8Error("PASS214_I8_AUTHORITY_ROOT_MISMATCH")
    return True
