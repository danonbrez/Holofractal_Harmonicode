"""Pass 217 Checkpoint 6 retrieval/reuse execution-authority composition.

Checkpoint 6 extends the already validated Pass 043/044/111 authority slice
without reimplementing inherited optimizations.  It binds the next Pass 214/215
required classes to their repository-native callables:

* reusable_pattern_cache -> Pass 086 deterministic pattern-admission ``run``;
* vector_shortlist -> Pass 205 ``Pass205ContinuationRuntime.retrieve``;
* exact_compatibility_filtering -> the same Pass 205 retrieval callable;
* exact_delta_cost_reranking -> the same Pass 205 retrieval callable.

A capability is ACTIVE_IN_PATH only after the inherited callable is actually
executed and a concrete repository-native witness/root is observed.  When an
operation has no exact pattern or retrieval candidate domain, NOT_APPLICABLE is
emitted from mechanical payload facts.  Partial or malformed applicability
markers are never downgraded to NOT_APPLICABLE; they fail closed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from hhs_runtime.hhs_cumulative_execution_authority_v1 import (
    ACTIVE_IN_PATH,
    EXPLICITLY_SUPERSEDED,
    NOT_APPLICABLE,
    build_authority_reachability,
)
from hhs_runtime.hhs_inherited_execution_stage_bridge_v1 import (
    INITIAL_REQUIRED_AUTHORITIES,
    build_initial_inherited_authority_reachability,
)


VERSION = "PASS_217_CUMULATIVE_EXECUTION_COMPOSER_CHECKPOINT_6_V1"
PATTERN_WORKLOAD_SCHEMA = "HHS_DETERMINISTIC_MULTIMODAL_PATTERN_ADMISSION_WORKLOAD_V1"
RETRIEVAL_REQUEST_SCHEMA = "HHS_PASS217_RETRIEVAL_REUSE_REQUEST_V1"
CHECKPOINT6_AUTHORITIES = (
    "reusable_pattern_cache",
    "vector_shortlist",
    "exact_compatibility_filtering",
    "exact_delta_cost_reranking",
)
CHECKPOINT6_REQUIRED_AUTHORITIES = INITIAL_REQUIRED_AUTHORITIES + CHECKPOINT6_AUTHORITIES

CHECKPOINT6_NATIVE_CALLABLES: Dict[str, Dict[str, Any]] = {
    "reusable_pattern_cache": {
        "origin_pass": 86,
        "module": (
            "native_projects.hhs_bifurcation_calibration."
            "hhs_pass086_deterministic_multimodal_pattern_admission_v1"
        ),
        "symbol": "run",
        "callable_role": "deterministic reusable multimodal pattern cache admission",
    },
    "vector_shortlist": {
        "origin_pass": 205,
        "module": "hhs_backend.runtime.hhs_pass205_continuation_runtime_v1",
        "symbol": "Pass205ContinuationRuntime.retrieve",
        "callable_role": "vector-distance shortlist over continuation snapshots",
    },
    "exact_compatibility_filtering": {
        "origin_pass": 205,
        "module": "hhs_backend.runtime.hhs_pass205_continuation_runtime_v1",
        "symbol": "Pass205ContinuationRuntime.retrieve",
        "callable_role": "schema and constraint exact candidate filtering",
    },
    "exact_delta_cost_reranking": {
        "origin_pass": 205,
        "module": "hhs_backend.runtime.hhs_pass205_continuation_runtime_v1",
        "symbol": "Pass205ContinuationRuntime.retrieve",
        "callable_role": "exact state delta-cost reranking after vector shortlist",
    },
}


def _walk_mappings(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk_mappings(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _walk_mappings(child)


def _unique_mappings(values: Iterable[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    seen: set[int] = set()
    output: List[Mapping[str, Any]] = []
    for value in values:
        marker = id(value)
        if marker in seen:
            continue
        seen.add(marker)
        output.append(value)
    return output


def _named_mapping_candidates(value: Any, key: str) -> List[Mapping[str, Any]]:
    found: List[Mapping[str, Any]] = []
    for mapping in _walk_mappings(value):
        child = mapping.get(key)
        if isinstance(child, Mapping):
            found.append(child)
    return _unique_mappings(found)


def _schema_mapping_candidates(value: Any, schema: str) -> List[Mapping[str, Any]]:
    return _unique_mappings(
        mapping for mapping in _walk_mappings(value) if mapping.get("schema") == schema
    )


def _pattern_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    body = dict(payload or {})
    named = _named_mapping_candidates(body, "reusable_pattern_workload")
    schemas = _schema_mapping_candidates(body, PATTERN_WORKLOAD_SCHEMA)
    return _unique_mappings([*named, *schemas])


def _retrieval_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    body = dict(payload or {})
    named = _named_mapping_candidates(body, "retrieval_reuse")
    schemas = _schema_mapping_candidates(body, RETRIEVAL_REQUEST_SCHEMA)
    return _unique_mappings([*named, *schemas])


def pattern_cache_context_facts(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    candidates = _pattern_candidates(payload)
    exact = [row for row in candidates if row.get("schema") == PATTERN_WORKLOAD_SCHEMA]
    return {
        "schema": "HHS_PASS217_REUSABLE_PATTERN_CACHE_APPLICABILITY_FACTS_V1",
        "pattern_candidate_domain_present": bool(candidates),
        "candidate_bundle_count": len(candidates),
        "exact_pattern_workload_count": len(exact),
        "exact_pattern_workload_unique": len(candidates) == 1 and len(exact) == 1,
        "required_workload_schema": PATTERN_WORKLOAD_SCHEMA,
    }


def retrieval_reuse_context_facts(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    candidates = _retrieval_candidates(payload)
    exact_schema = [row for row in candidates if row.get("schema") == RETRIEVAL_REQUEST_SCHEMA]
    target_count = sum(1 for row in candidates if "target_state_words" in row)
    return {
        "schema": "HHS_PASS217_RETRIEVAL_REUSE_APPLICABILITY_FACTS_V1",
        "retrieval_candidate_domain_present": bool(candidates),
        "candidate_bundle_count": len(candidates),
        "declared_request_schema_count": len(exact_schema),
        "target_state_bundle_count": target_count,
        "candidate_bundle_unique": len(candidates) == 1,
        "target_state_bundle_unique": len(candidates) == 1 and target_count == 1,
        "request_schema": RETRIEVAL_REQUEST_SCHEMA,
    }


def _active_failure(
    authority_id: str,
    reason: str,
    facts: Mapping[str, Any],
    *,
    callable_info: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    info = dict(callable_info or CHECKPOINT6_NATIVE_CALLABLES[authority_id])
    return {
        "observed": False,
        "path": [
            "kernel_runtime_autocomposer",
            authority_id,
            f"{info['module']}.{info['symbol']}",
        ],
        "traversal_witness": {
            "schema": "HHS_PASS217_CHECKPOINT6_TRAVERSAL_FAILURE_V1",
            "status": "REJECT_CHECKPOINT6_INHERITED_TRAVERSAL",
            "authority_id": authority_id,
            "reason": str(reason),
            "repository_native_callable": info,
            "applicability_facts": dict(facts),
        },
        "witness_root": "",
    }


def observe_reusable_pattern_cache(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    repo_root: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Execute the inherited Pass 086 pattern admission/cache materialization path."""

    applicability = dict(facts or pattern_cache_context_facts(payload))
    candidates = _pattern_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "reusable_pattern_cache",
            "REJECT_PASS086_PATTERN_WORKLOAD_BUNDLE_COUNT",
            applicability,
        )
    workload = candidates[0]
    if workload.get("schema") != PATTERN_WORKLOAD_SCHEMA:
        return _active_failure(
            "reusable_pattern_cache",
            "REJECT_PASS086_PATTERN_WORKLOAD_SCHEMA",
            applicability,
        )

    try:
        from native_projects.hhs_bifurcation_calibration.hhs_pass086_deterministic_multimodal_pattern_admission_v1 import (
            run as pass086_pattern_run,
        )

        root = (
            Path(repo_root).resolve()
            if repo_root is not None
            else Path(__file__).resolve().parents[1]
        )
        result = pass086_pattern_run(root, workload)
        receipt = result.get("pattern_admission_receipt")
        if not isinstance(receipt, Mapping):
            raise ValueError("REJECT_PASS086_PATTERN_ADMISSION_RECEIPT_MISSING")
        entries = receipt.get("semantic_cache_entries")
        if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)) or not entries:
            raise ValueError("REJECT_PASS086_REUSABLE_PATTERN_CACHE_ENTRIES_MISSING")
        cache_roots: List[str] = []
        for entry in entries:
            if not isinstance(entry, Mapping):
                raise ValueError("REJECT_PASS086_REUSABLE_PATTERN_CACHE_ENTRY_INVALID")
            cache_root = str(entry.get("cache_entry_root_hash72") or "").strip()
            if not cache_root:
                raise ValueError("REJECT_PASS086_REUSABLE_PATTERN_CACHE_ROOT_MISSING")
            if entry.get("cache_authority") is not False:
                raise ValueError("REJECT_PASS086_CACHE_PROMOTED_TO_AUTHORITY")
            if entry.get("replay_verified") is not True:
                raise ValueError("REJECT_PASS086_CACHE_REPLAY_UNVERIFIED")
            cache_roots.append(cache_root)
        witness_root = str(
            receipt.get("pattern_admission_receipt_root_hash72")
            or result.get("result_root_hash72")
            or ""
        ).strip()
        if not witness_root:
            raise ValueError("REJECT_PASS086_PATTERN_CACHE_WITNESS_ROOT_MISSING")
        info = CHECKPOINT6_NATIVE_CALLABLES["reusable_pattern_cache"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "reusable_pattern_cache",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_REUSABLE_PATTERN_CACHE_TRAVERSAL_V1",
                "status": "ADMIT_REUSABLE_PATTERN_CACHE_TRAVERSAL",
                "repository_native_callable": dict(info),
                "pattern_admission_status": result.get("status"),
                "cache_entry_count": len(cache_roots),
                "cache_entry_roots_hash72": cache_roots,
                "cache_is_authority": False,
                "replay_verified": all(
                    bool(entry.get("replay_verified")) for entry in entries
                ),
                "applicability_facts": applicability,
            },
            "witness_root": witness_root,
        }
    except Exception as exc:
        return _active_failure(
            "reusable_pattern_cache",
            f"REJECT_PASS086_REUSABLE_PATTERN_CACHE_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def _retrieval_failure_proofs(
    reason: str,
    facts: Mapping[str, Any],
) -> Dict[str, Dict[str, Any]]:
    return {
        authority_id: _active_failure(authority_id, reason, facts)
        for authority_id in CHECKPOINT6_AUTHORITIES[1:]
    }


def observe_pass205_retrieval_reuse_chain(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    retrieval_runtime: Any = None,
) -> Dict[str, Dict[str, Any]]:
    """Execute Pass 205 retrieval once and expose three exact stage witnesses."""

    applicability = dict(facts or retrieval_reuse_context_facts(payload))
    candidates = _retrieval_candidates(payload)
    if len(candidates) != 1:
        return _retrieval_failure_proofs(
            "REJECT_PASS205_RETRIEVAL_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    target = request.get("target_state_words")
    if not isinstance(target, Sequence) or isinstance(target, (str, bytes)):
        return _retrieval_failure_proofs(
            "REJECT_PASS205_RETRIEVAL_TARGET_STATE_MISSING",
            applicability,
        )
    top_k = request.get("top_k", 32)
    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
        return _retrieval_failure_proofs(
            "REJECT_PASS205_RETRIEVAL_TOP_K_INVALID",
            applicability,
        )

    try:
        if retrieval_runtime is None:
            from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
                PASS205_CONTINUATION_RUNTIME,
            )

            retrieval_runtime = PASS205_CONTINUATION_RUNTIME
        retrieval = retrieval_runtime.retrieve(
            target_state_words=target,
            schema_root216=request.get("schema_root216"),
            constraint_root216=request.get("constraint_root216"),
            top_k=top_k,
        )
        if retrieval.get("schema") != "HHS_PASS_205_COMPATIBLE_SNAPSHOT_RETRIEVAL_V1":
            raise ValueError("REJECT_PASS205_RETRIEVAL_SCHEMA")
        if retrieval.get("ok") is not True:
            raise ValueError("REJECT_PASS205_RETRIEVAL_NOT_OK")
        if retrieval.get("approximate_similarity_is_authority") is not False:
            raise ValueError("REJECT_PASS205_APPROXIMATE_SIMILARITY_AS_AUTHORITY")
        if retrieval.get("exact_rerank_applied") is not True:
            raise ValueError("REJECT_PASS205_EXACT_RERANK_NOT_APPLIED")
        retrieval_root = str(retrieval.get("retrieval_root216") or "").strip()
        selected = str(retrieval.get("selected_parent_root216") or "").strip()
        ranked = retrieval.get("ranked_candidates")
        rejected = retrieval.get("rejected_candidates")
        if not retrieval_root or not selected:
            raise ValueError("REJECT_PASS205_RETRIEVAL_ROOT_OR_SELECTION_MISSING")
        if not isinstance(ranked, Sequence) or isinstance(ranked, (str, bytes)) or not ranked:
            raise ValueError("REJECT_PASS205_RANKED_CANDIDATES_MISSING")
        if not isinstance(rejected, Sequence) or isinstance(rejected, (str, bytes)):
            raise ValueError("REJECT_PASS205_REJECTED_CANDIDATES_INVALID")
        ranked_rows = [dict(row) for row in ranked if isinstance(row, Mapping)]
        if len(ranked_rows) != len(ranked):
            raise ValueError("REJECT_PASS205_RANKED_CANDIDATE_INVALID")
        if selected not in {
            str(row.get("continuation_root216") or "") for row in ranked_rows
        }:
            raise ValueError("REJECT_PASS205_SELECTED_PARENT_OUTSIDE_SHORTLIST")
        if any("exact_delta_cost" not in row or "vector_distance" not in row for row in ranked_rows):
            raise ValueError("REJECT_PASS205_RANKED_COST_FIELDS_MISSING")

        common_path = "hhs_backend.runtime.hhs_pass205_continuation_runtime_v1.Pass205ContinuationRuntime.retrieve"
        vector_info = CHECKPOINT6_NATIVE_CALLABLES["vector_shortlist"]
        compatibility_info = CHECKPOINT6_NATIVE_CALLABLES["exact_compatibility_filtering"]
        rerank_info = CHECKPOINT6_NATIVE_CALLABLES["exact_delta_cost_reranking"]
        return {
            "vector_shortlist": {
                "observed": True,
                "path": ["kernel_runtime_autocomposer", "vector_shortlist", common_path],
                "traversal_witness": {
                    "schema": "HHS_PASS217_VECTOR_SHORTLIST_TRAVERSAL_V1",
                    "status": "ADMIT_VECTOR_SHORTLIST_TRAVERSAL",
                    "repository_native_callable": dict(vector_info),
                    "query_root216": retrieval.get("query_root216"),
                    "retrieval_root216": retrieval_root,
                    "requested_top_k": int(top_k),
                    "shortlist_candidate_count": len(ranked_rows),
                    "ranked_candidate_roots216": [
                        row.get("continuation_root216") for row in ranked_rows
                    ],
                    "selected_parent_root216": selected,
                    "selected_vector_distance": retrieval.get("vector_distance"),
                    "approximate_similarity_is_authority": False,
                    "applicability_facts": applicability,
                },
                "witness_root": retrieval_root,
            },
            "exact_compatibility_filtering": {
                "observed": True,
                "path": [
                    "kernel_runtime_autocomposer",
                    "exact_compatibility_filtering",
                    common_path,
                ],
                "traversal_witness": {
                    "schema": "HHS_PASS217_EXACT_COMPATIBILITY_FILTER_TRAVERSAL_V1",
                    "status": "ADMIT_EXACT_COMPATIBILITY_FILTER_TRAVERSAL",
                    "repository_native_callable": dict(compatibility_info),
                    "schema_root216": request.get("schema_root216")
                    or getattr(retrieval_runtime, "schema_root216", None),
                    "constraint_root216": request.get("constraint_root216")
                    or getattr(retrieval_runtime, "constraint_root216", None),
                    "compatible_shortlist_count": len(ranked_rows),
                    "rejected_candidate_count": len(rejected),
                    "rejected_candidates": [dict(row) for row in rejected if isinstance(row, Mapping)],
                    "selected_parent_root216": selected,
                    "applicability_facts": applicability,
                },
                "witness_root": retrieval_root,
            },
            "exact_delta_cost_reranking": {
                "observed": True,
                "path": [
                    "kernel_runtime_autocomposer",
                    "exact_delta_cost_reranking",
                    common_path,
                ],
                "traversal_witness": {
                    "schema": "HHS_PASS217_EXACT_DELTA_COST_RERANK_TRAVERSAL_V1",
                    "status": "ADMIT_EXACT_DELTA_COST_RERANK_TRAVERSAL",
                    "repository_native_callable": dict(rerank_info),
                    "exact_rerank_applied": True,
                    "selected_parent_root216": selected,
                    "selected_exact_delta_cost": retrieval.get("exact_delta_cost"),
                    "selected_vector_distance": retrieval.get("vector_distance"),
                    "ranked_candidates": ranked_rows,
                    "applicability_facts": applicability,
                },
                "witness_root": retrieval_root,
            },
        }
    except Exception as exc:
        return _retrieval_failure_proofs(
            f"REJECT_PASS205_RETRIEVAL_REUSE_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def _import_prior_decisions(
    record: Mapping[str, Any],
    active: Dict[str, Mapping[str, Any]],
    not_applicable: Dict[str, Mapping[str, Any]],
    superseded: Dict[str, Mapping[str, Any]],
) -> None:
    for row in record.get("decisions", []) or []:
        if not isinstance(row, Mapping):
            continue
        authority_id = str(row.get("authority_id") or "")
        proof = row.get("proof")
        if not authority_id or not isinstance(proof, Mapping):
            continue
        state = row.get("state")
        if state == ACTIVE_IN_PATH or "observed" in proof:
            active[authority_id] = dict(proof)
        elif state == NOT_APPLICABLE or "mechanically_proven" in proof:
            not_applicable[authority_id] = dict(proof)
        elif state == EXPLICITLY_SUPERSEDED or "later_pass" in proof:
            superseded[authority_id] = dict(proof)


def build_checkpoint6_inherited_authority_reachability(
    preflight: Mapping[str, Any],
    surface: Mapping[str, Any],
    payload: Optional[Mapping[str, Any]] = None,
    *,
    semantic_cache: Any = None,
    retrieval_runtime: Any = None,
    pattern_repo_root: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Compose Checkpoint 6 over the already validated Checkpoints 1-5 slice."""

    initial = build_initial_inherited_authority_reachability(
        preflight,
        surface,
        payload,
        semantic_cache=semantic_cache,
    )
    active: Dict[str, Mapping[str, Any]] = {}
    not_applicable: Dict[str, Mapping[str, Any]] = {}
    superseded: Dict[str, Mapping[str, Any]] = {}
    _import_prior_decisions(initial, active, not_applicable, superseded)

    pattern_facts = pattern_cache_context_facts(payload)
    if pattern_facts["pattern_candidate_domain_present"] is False:
        not_applicable["reusable_pattern_cache"] = {
            "mechanically_proven": True,
            "predicate": "pattern_candidate_domain_present == false",
            "observed_facts": pattern_facts,
            "reason": (
                "operation payload contains no exact Pass 086 reusable-pattern "
                "admission workload"
            ),
        }
    else:
        active["reusable_pattern_cache"] = observe_reusable_pattern_cache(
            payload,
            facts=pattern_facts,
            repo_root=pattern_repo_root,
        )

    retrieval_facts = retrieval_reuse_context_facts(payload)
    if retrieval_facts["retrieval_candidate_domain_present"] is False:
        for authority_id in CHECKPOINT6_AUTHORITIES[1:]:
            not_applicable[authority_id] = {
                "mechanically_proven": True,
                "predicate": "retrieval_candidate_domain_present == false",
                "observed_facts": retrieval_facts,
                "reason": (
                    "operation payload contains no Pass 205 target-state candidate "
                    "retrieval domain"
                ),
            }
    else:
        active.update(
            observe_pass205_retrieval_reuse_chain(
                payload,
                facts=retrieval_facts,
                retrieval_runtime=retrieval_runtime,
            )
        )

    operation_id = str(preflight.get("operation") or surface.get("symbol") or "operation")
    record = build_authority_reachability(
        operation_id,
        active_in_path=active,
        not_applicable=not_applicable,
        explicitly_superseded=superseded,
        required_authorities=CHECKPOINT6_REQUIRED_AUTHORITIES,
    )
    record["checkpoint_scope"] = list(CHECKPOINT6_REQUIRED_AUTHORITIES)
    record["checkpoint6_native_callable_map"] = {
        key: dict(value) for key, value in CHECKPOINT6_NATIVE_CALLABLES.items()
    }
    record["pattern_cache_applicability_facts"] = pattern_facts
    record["retrieval_reuse_applicability_facts"] = retrieval_facts
    record["continuation_applicability_facts"] = dict(
        initial.get("continuation_applicability_facts") or {}
    )
    record["prior_checkpoint_reachability_root_hash72"] = initial.get(
        "reachability_root_hash72"
    )
    record["checkpoint"] = 6
    return record


__all__ = [
    "VERSION",
    "PATTERN_WORKLOAD_SCHEMA",
    "RETRIEVAL_REQUEST_SCHEMA",
    "CHECKPOINT6_AUTHORITIES",
    "CHECKPOINT6_REQUIRED_AUTHORITIES",
    "CHECKPOINT6_NATIVE_CALLABLES",
    "pattern_cache_context_facts",
    "retrieval_reuse_context_facts",
    "observe_reusable_pattern_cache",
    "observe_pass205_retrieval_reuse_chain",
    "build_checkpoint6_inherited_authority_reachability",
]
