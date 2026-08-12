"""Pass 217 Checkpoint 9 parametric admission, compiled-ROM reuse, and generator/exception compression.

This checkpoint extends the validated Checkpoint 8 cumulative authority slice with
three inherited execution classes.  It deliberately distinguishes operational
runtime callables from Pass 215 benchmark analogs:

* parametric_admission -> Pass 213 ``create_parametric_admission``;
* compiled_rom_reuse -> Pass 213 ``CompiledROMStore.lookup_operation``;
* generator_exception_compression -> Pass 212 ``FullHydrationRecoveryRuntime._compress``
  with exact ``_decompress`` replay verification.

Absent domains are mechanically NOT_APPLICABLE.  Partial or malformed applicable
context fails closed.  No benchmark-only descriptor reuse is promoted to runtime
authority and no compression claim is admitted when the inherited codec falls
back to raw packed bytes.
"""

from __future__ import annotations

from hashlib import sha256
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from hhs_runtime.hhs_cumulative_execution_authority_v1 import (
    ACTIVE_IN_PATH,
    EXPLICITLY_SUPERSEDED,
    NOT_APPLICABLE,
    build_authority_reachability,
)
from hhs_runtime.hhs_pass217_checkpoint8_sparse_delta_v1 import (
    CHECKPOINT8_REQUIRED_AUTHORITIES,
    build_checkpoint8_inherited_authority_reachability,
)


VERSION = "PASS_217_CUMULATIVE_EXECUTION_COMPOSER_CHECKPOINT_9_V1"
PARAMETRIC_ADMISSION_REQUEST_SCHEMA = "HHS_PASS217_PARAMETRIC_ADMISSION_REQUEST_V1"
COMPILED_ROM_REUSE_REQUEST_SCHEMA = "HHS_PASS217_COMPILED_ROM_REUSE_REQUEST_V1"
GENERATOR_EXCEPTION_COMPRESSION_REQUEST_SCHEMA = (
    "HHS_PASS217_GENERATOR_EXCEPTION_COMPRESSION_REQUEST_V1"
)

CHECKPOINT9_AUTHORITIES = (
    "parametric_admission",
    "compiled_rom_reuse",
    "generator_exception_compression",
)
CHECKPOINT9_REQUIRED_AUTHORITIES = CHECKPOINT8_REQUIRED_AUTHORITIES + CHECKPOINT9_AUTHORITIES

CHECKPOINT9_AUTHORITY_MAP: Dict[str, Dict[str, Any]] = {
    "parametric_admission": {
        "origin_pass": 213,
        "origin_iteration": 4,
        "module": "hhs_backend.runtime.hhs_pass213_parametric_delta_v1",
        "symbol": "create_parametric_admission",
        "callable_role": (
            "dependency-scoped changed-field admission with affected-constraint "
            "evaluation and authenticated unaffected-witness reuse"
        ),
        "runtime_authority": True,
    },
    "compiled_rom_reuse": {
        "origin_pass": 213,
        "origin_iteration": 1,
        "module": "hhs_backend.runtime.hhs_pass213_compiled_rom_v1",
        "symbol": "CompiledROMStore.lookup_operation",
        "callable_role": "immutable operation-id to authenticated compiled-ROM entry reuse",
        "runtime_authority": True,
        "pass215_descriptor_benchmark_analog_is_authority": False,
    },
    "generator_exception_compression": {
        "origin_pass": 212,
        "module": "hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1",
        "symbol": "FullHydrationRecoveryRuntime._compress",
        "replay_symbol": "FullHydrationRecoveryRuntime._decompress",
        "callable_role": (
            "two-bit affine generator per 5184-bit leaf plus exact sparse XOR "
            "exception positions with raw fallback"
        ),
        "runtime_authority": True,
        "false_compression_claim_forbidden": True,
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


def _request_candidates(
    payload: Optional[Mapping[str, Any]],
    *,
    named_key: str,
    schema: str,
) -> List[Mapping[str, Any]]:
    found: List[Mapping[str, Any]] = []
    for mapping in _walk_mappings(dict(payload or {})):
        named = mapping.get(named_key)
        if isinstance(named, Mapping):
            found.append(named)
        if mapping.get("schema") == schema:
            found.append(mapping)
    return _unique_mappings(found)


def _parametric_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="parametric_admission",
        schema=PARAMETRIC_ADMISSION_REQUEST_SCHEMA,
    )


def _rom_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="compiled_rom_reuse",
        schema=COMPILED_ROM_REUSE_REQUEST_SCHEMA,
    )


def _compression_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="generator_exception_compression",
        schema=GENERATOR_EXCEPTION_COMPRESSION_REQUEST_SCHEMA,
    )


def checkpoint9_context_facts(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    parametric = _parametric_candidates(payload)
    rom = _rom_candidates(payload)
    compression = _compression_candidates(payload)
    return {
        "schema": "HHS_PASS217_CHECKPOINT9_APPLICABILITY_FACTS_V1",
        "parametric_admission_domain_present": bool(parametric),
        "parametric_admission_candidate_count": len(parametric),
        "parametric_admission_exact_schema_count": sum(
            row.get("schema") == PARAMETRIC_ADMISSION_REQUEST_SCHEMA for row in parametric
        ),
        "compiled_rom_reuse_domain_present": bool(rom),
        "compiled_rom_reuse_candidate_count": len(rom),
        "compiled_rom_reuse_exact_schema_count": sum(
            row.get("schema") == COMPILED_ROM_REUSE_REQUEST_SCHEMA for row in rom
        ),
        "generator_exception_compression_domain_present": bool(compression),
        "generator_exception_compression_candidate_count": len(compression),
        "generator_exception_compression_exact_schema_count": sum(
            row.get("schema") == GENERATOR_EXCEPTION_COMPRESSION_REQUEST_SCHEMA
            for row in compression
        ),
    }


def _active_failure(authority_id: str, reason: str, facts: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "observed": False,
        "path": ["kernel_runtime_autocomposer", authority_id],
        "traversal_witness": {
            "schema": "HHS_PASS217_CHECKPOINT9_TRAVERSAL_FAILURE_V1",
            "status": "REJECT_CHECKPOINT9_INHERITED_TRAVERSAL",
            "authority_id": authority_id,
            "reason": str(reason),
            "authority_map": dict(CHECKPOINT9_AUTHORITY_MAP[authority_id]),
            "applicability_facts": dict(facts),
        },
        "witness_root": "",
    }


def observe_parametric_admission(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    parametric_template: Any = None,
    parametric_base_entry: Any = None,
    parametric_opening_boundary: Any = None,
    parametric_validation_key: Optional[bytes] = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint9_context_facts(payload))
    candidates = _parametric_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "parametric_admission",
            "REJECT_PASS213_PARAMETRIC_ADMISSION_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != PARAMETRIC_ADMISSION_REQUEST_SCHEMA:
        return _active_failure(
            "parametric_admission",
            "REJECT_PASS213_PARAMETRIC_ADMISSION_REQUEST_SCHEMA",
            applicability,
        )
    try:
        if parametric_template is None:
            raise ValueError("REJECT_PASS213_PARAMETRIC_TEMPLATE_MISSING")
        if parametric_base_entry is None:
            raise ValueError("REJECT_PASS213_PARAMETRIC_BASE_ENTRY_MISSING")
        if parametric_opening_boundary is None:
            raise ValueError("REJECT_PASS213_PARAMETRIC_OPENING_BOUNDARY_MISSING")
        if not isinstance(parametric_validation_key, bytes) or len(parametric_validation_key) < 32:
            raise ValueError("REJECT_PASS213_PARAMETRIC_VALIDATION_KEY_MISSING_OR_SHORT")

        if request.get("template_hash216") != getattr(parametric_template, "template_hash216", None):
            raise ValueError("REJECT_PASS213_PARAMETRIC_TEMPLATE_HASH_MISMATCH")
        if request.get("base_entry_hash216") != getattr(parametric_base_entry, "entry_hash216", None):
            raise ValueError("REJECT_PASS213_PARAMETRIC_BASE_ENTRY_HASH_MISMATCH")
        if request.get("opening_boundary_hash216") != getattr(
            parametric_opening_boundary, "boundary_hash216", None
        ):
            raise ValueError("REJECT_PASS213_PARAMETRIC_OPENING_BOUNDARY_HASH_MISMATCH")
        candidate = request.get("candidate")
        if not isinstance(candidate, Mapping):
            raise ValueError("REJECT_PASS213_PARAMETRIC_CANDIDATE_MISSING")

        from hhs_backend.runtime.hhs_pass213_parametric_delta_v1 import (
            create_parametric_admission,
        )

        admission = create_parametric_admission(
            template=parametric_template,
            base_entry=parametric_base_entry,
            candidate=candidate,
            opening_boundary=parametric_opening_boundary,
            validation_key=parametric_validation_key,
        )
        admission.validate(
            parametric_validation_key,
            parametric_template,
            parametric_base_entry,
            parametric_opening_boundary,
        )
        if not admission.vm81_admission_root_hash216 or not admission.authentication_tag:
            raise ValueError("REJECT_PASS213_PARAMETRIC_ADMISSION_ROOT_OR_TAG_MISSING")

        info = CHECKPOINT9_AUTHORITY_MAP["parametric_admission"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "parametric_admission",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_PARAMETRIC_ADMISSION_TRAVERSAL_V1",
                "status": "ADMIT_PARAMETRIC_ADMISSION_TRAVERSAL",
                "repository_native_callable": dict(info),
                "template_hash216": admission.template_hash216,
                "base_entry_hash216": admission.base_entry_hash216,
                "candidate_hash216": admission.candidate_hash216,
                "changed_paths": list(admission.changed_paths),
                "affected_constraint_ids": list(admission.affected_constraint_ids),
                "reused_constraint_ids": list(admission.reused_constraint_ids),
                "reused_constraint_root_hash216": admission.reused_constraint_root_hash216,
                "delta_root_hash216": admission.delta_root_hash216,
                "vm81_admission_root_hash216": admission.vm81_admission_root_hash216,
                "authentication_tag_present": True,
                "applicability_facts": applicability,
            },
            "witness_root": admission.vm81_admission_root_hash216,
        }
    except Exception as exc:
        return _active_failure(
            "parametric_admission",
            f"REJECT_PASS213_PARAMETRIC_ADMISSION_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def observe_compiled_rom_reuse(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    compiled_rom_store: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint9_context_facts(payload))
    candidates = _rom_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "compiled_rom_reuse",
            "REJECT_PASS213_COMPILED_ROM_REUSE_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != COMPILED_ROM_REUSE_REQUEST_SCHEMA:
        return _active_failure(
            "compiled_rom_reuse",
            "REJECT_PASS213_COMPILED_ROM_REUSE_REQUEST_SCHEMA",
            applicability,
        )
    try:
        if compiled_rom_store is None:
            raise ValueError("REJECT_PASS213_COMPILED_ROM_STORE_MISSING")
        operation_id = request.get("operation_id")
        expected_hash = request.get("expected_entry_hash216")
        expected_inventory = request.get("expected_inventory_root_hash216")
        if not isinstance(operation_id, str) or not operation_id:
            raise ValueError("REJECT_PASS213_COMPILED_ROM_OPERATION_ID_MISSING")
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            raise ValueError("REJECT_PASS213_COMPILED_ROM_ENTRY_HASH_MISSING")
        if not isinstance(expected_inventory, str) or len(expected_inventory) != 64:
            raise ValueError("REJECT_PASS213_COMPILED_ROM_INVENTORY_ROOT_MISSING")

        before_len = len(compiled_rom_store)
        before_inventory = compiled_rom_store.inventory_root()
        if before_inventory != expected_inventory:
            raise ValueError("REJECT_PASS213_COMPILED_ROM_INVENTORY_ROOT_MISMATCH")
        entry = compiled_rom_store.lookup_operation(operation_id)
        after_inventory = compiled_rom_store.inventory_root()
        if entry.entry_hash216 != expected_hash:
            raise ValueError("REJECT_PASS213_COMPILED_ROM_ENTRY_HASH_MISMATCH")
        if len(compiled_rom_store) != before_len or after_inventory != before_inventory:
            raise ValueError("REJECT_PASS213_COMPILED_ROM_LOOKUP_MUTATED_STORE")

        info = CHECKPOINT9_AUTHORITY_MAP["compiled_rom_reuse"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "compiled_rom_reuse",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_COMPILED_ROM_REUSE_TRAVERSAL_V1",
                "status": "ADMIT_COMPILED_ROM_REUSE_TRAVERSAL",
                "repository_native_callable": dict(info),
                "operation_id": entry.operation_id,
                "entry_hash216": entry.entry_hash216,
                "inventory_root_hash216": before_inventory,
                "vm81_cell_id": entry.vm81_cell_id,
                "operation_slot": entry.operation_slot,
                "g243_control_id": entry.g243_control_id,
                "native_dispatch_id": entry.native_dispatch_id,
                "lookup_mutated_store": False,
                "runtime_authority": True,
                "benchmark_descriptor_analog_used": False,
                "applicability_facts": applicability,
            },
            "witness_root": entry.entry_hash216,
        }
    except Exception as exc:
        return _active_failure(
            "compiled_rom_reuse",
            f"REJECT_PASS213_COMPILED_ROM_REUSE_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def _exact_exception_positions(value: Any, *, upper_bound: int) -> tuple[int, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError("REJECT_PASS212_EXCEPTION_POSITIONS_MISSING")
    output: list[int] = []
    previous = -1
    for item in value:
        if not isinstance(item, int) or isinstance(item, bool):
            raise ValueError("REJECT_PASS212_EXCEPTION_POSITION_NONINTEGER")
        position = int(item)
        if not 0 <= position < upper_bound:
            raise ValueError("REJECT_PASS212_EXCEPTION_POSITION_OUT_OF_RANGE")
        if position <= previous:
            raise ValueError("REJECT_PASS212_EXCEPTION_POSITIONS_NOT_STRICTLY_ASCENDING")
        output.append(position)
        previous = position
    return tuple(output)


def observe_generator_exception_compression(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint9_context_facts(payload))
    candidates = _compression_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "generator_exception_compression",
            "REJECT_PASS212_GENERATOR_EXCEPTION_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != GENERATOR_EXCEPTION_COMPRESSION_REQUEST_SCHEMA:
        return _active_failure(
            "generator_exception_compression",
            "REJECT_PASS212_GENERATOR_EXCEPTION_REQUEST_SCHEMA",
            applicability,
        )
    try:
        from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import (
            AFFINE_SEED_BYTES,
            FULL_FRAME_COUNT,
            FULL_HYDRATION_BITS,
            FULL_HYDRATION_BYTES,
            FullHydrationRecoveryRuntime,
            apply_bit_exceptions,
            generate_affine_hydration,
            pack_frame_seeds,
        )

        seed_value = request.get("uniform_seed")
        if not isinstance(seed_value, int) or isinstance(seed_value, bool) or seed_value not in range(4):
            raise ValueError("REJECT_PASS212_UNIFORM_AFFINE_SEED_INVALID")
        positions = _exact_exception_positions(
            request.get("exception_positions"),
            upper_bound=FULL_HYDRATION_BITS,
        )
        require_strict = request.get("require_strict_compression", True)
        if require_strict is not True:
            raise ValueError("REJECT_PASS212_STRICT_COMPRESSION_REQUIRED_FOR_AUTHORITY")

        seed_bytes = pack_frame_seeds([seed_value] * FULL_FRAME_COUNT)
        if len(seed_bytes) != AFFINE_SEED_BYTES:
            raise ValueError("REJECT_PASS212_AFFINE_SEED_BYTE_GEOMETRY")
        generated = generate_affine_hydration(seed_bytes)
        state = apply_bit_exceptions(generated, positions)
        if len(state) != FULL_HYDRATION_BYTES:
            raise ValueError("REJECT_PASS212_FULL_HYDRATION_GEOMETRY")

        compressed, codec, exception_count = FullHydrationRecoveryRuntime._compress(state)
        if codec != "AFFINE_9720_LEAF_SEEDS_PLUS_SPARSE_XOR":
            raise ValueError("REJECT_PASS212_RAW_FALLBACK_NOT_COMPRESSION_AUTHORITY")
        recovered, recovered_codec, recovered_exception_count = (
            FullHydrationRecoveryRuntime._decompress(compressed, codec)
        )
        if recovered != state:
            raise ValueError("REJECT_PASS212_GENERATOR_EXCEPTION_REPLAY_MISMATCH")
        if recovered_codec != codec or recovered_exception_count != exception_count:
            raise ValueError("REJECT_PASS212_GENERATOR_EXCEPTION_METADATA_MISMATCH")
        if exception_count != len(positions):
            raise ValueError("REJECT_PASS212_GENERATOR_EXCEPTION_COUNT_MISMATCH")
        if len(compressed) >= len(state):
            raise ValueError("REJECT_PASS212_STRICT_COMPRESSION_NOT_ACHIEVED")

        state_root = sha256(state).hexdigest()
        compressed_root = sha256(compressed).hexdigest()
        info = CHECKPOINT9_AUTHORITY_MAP["generator_exception_compression"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "generator_exception_compression",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_GENERATOR_EXCEPTION_COMPRESSION_TRAVERSAL_V1",
                "status": "ADMIT_GENERATOR_EXCEPTION_COMPRESSION_TRAVERSAL",
                "repository_native_callable": dict(info),
                "codec": codec,
                "full_hydration_bits": FULL_HYDRATION_BITS,
                "full_hydration_bytes": FULL_HYDRATION_BYTES,
                "frame_count": FULL_FRAME_COUNT,
                "affine_seed_bytes": AFFINE_SEED_BYTES,
                "uniform_seed": seed_value,
                "exception_positions": list(positions),
                "exception_count": exception_count,
                "compressed_payload_bytes": len(compressed),
                "compression_ratio_exact": {
                    "numerator": len(state),
                    "denominator": len(compressed),
                },
                "state_sha256": state_root,
                "compressed_sha256": compressed_root,
                "replay_verified": True,
                "raw_fallback_used": False,
                "false_compression_claim": False,
                "applicability_facts": applicability,
            },
            "witness_root": compressed_root,
        }
    except Exception as exc:
        return _active_failure(
            "generator_exception_compression",
            f"REJECT_PASS212_GENERATOR_EXCEPTION_COMPRESSION_TRAVERSAL:{type(exc).__name__}:{exc}",
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


def build_checkpoint9_inherited_authority_reachability(
    preflight: Mapping[str, Any],
    surface: Mapping[str, Any],
    payload: Optional[Mapping[str, Any]] = None,
    *,
    semantic_cache: Any = None,
    retrieval_runtime: Any = None,
    pattern_repo_root: Any = None,
    source_reuse_service: Any = None,
    projection_service: Any = None,
    delta_compiled_tensor: Any = None,
    parametric_template: Any = None,
    parametric_base_entry: Any = None,
    parametric_opening_boundary: Any = None,
    parametric_validation_key: Optional[bytes] = None,
    compiled_rom_store: Any = None,
) -> Dict[str, Any]:
    prior = build_checkpoint8_inherited_authority_reachability(
        preflight,
        surface,
        payload,
        semantic_cache=semantic_cache,
        retrieval_runtime=retrieval_runtime,
        pattern_repo_root=pattern_repo_root,
        source_reuse_service=source_reuse_service,
        projection_service=projection_service,
        delta_compiled_tensor=delta_compiled_tensor,
    )
    active: Dict[str, Mapping[str, Any]] = {}
    not_applicable: Dict[str, Mapping[str, Any]] = {}
    superseded: Dict[str, Mapping[str, Any]] = {}
    _import_prior_decisions(prior, active, not_applicable, superseded)
    facts = checkpoint9_context_facts(payload)

    if facts["parametric_admission_domain_present"] is False:
        not_applicable["parametric_admission"] = {
            "mechanically_proven": True,
            "predicate": "parametric_admission_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no Pass 213 parametric-admission domain",
        }
    else:
        active["parametric_admission"] = observe_parametric_admission(
            payload,
            facts=facts,
            parametric_template=parametric_template,
            parametric_base_entry=parametric_base_entry,
            parametric_opening_boundary=parametric_opening_boundary,
            parametric_validation_key=parametric_validation_key,
        )

    if facts["compiled_rom_reuse_domain_present"] is False:
        not_applicable["compiled_rom_reuse"] = {
            "mechanically_proven": True,
            "predicate": "compiled_rom_reuse_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no Pass 213 compiled-ROM reuse domain",
        }
    else:
        active["compiled_rom_reuse"] = observe_compiled_rom_reuse(
            payload,
            facts=facts,
            compiled_rom_store=compiled_rom_store,
        )

    if facts["generator_exception_compression_domain_present"] is False:
        not_applicable["generator_exception_compression"] = {
            "mechanically_proven": True,
            "predicate": "generator_exception_compression_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no Pass 212 generator/exception compression domain",
        }
    else:
        active["generator_exception_compression"] = observe_generator_exception_compression(
            payload,
            facts=facts,
        )

    operation_id = str(preflight.get("operation") or surface.get("symbol") or "operation")
    record = build_authority_reachability(
        operation_id,
        active_in_path=active,
        not_applicable=not_applicable,
        explicitly_superseded=superseded,
        required_authorities=CHECKPOINT9_REQUIRED_AUTHORITIES,
    )
    record["checkpoint_scope"] = list(CHECKPOINT9_REQUIRED_AUTHORITIES)
    record["checkpoint9_authority_map"] = {
        key: dict(value) for key, value in CHECKPOINT9_AUTHORITY_MAP.items()
    }
    record["checkpoint9_applicability_facts"] = facts
    for key in (
        "continuation_applicability_facts",
        "pattern_cache_applicability_facts",
        "retrieval_reuse_applicability_facts",
        "checkpoint6_native_callable_map",
        "content_reuse_applicability_facts",
        "checkpoint7_authority_map",
        "checkpoint8_applicability_facts",
        "checkpoint8_authority_map",
    ):
        if key in prior:
            value = prior[key]
            record[key] = dict(value) if isinstance(value, Mapping) else value
    record["prior_checkpoint_reachability_root_hash72"] = prior.get(
        "reachability_root_hash72"
    )
    record["checkpoint"] = 9
    return record


__all__ = [
    "VERSION",
    "PARAMETRIC_ADMISSION_REQUEST_SCHEMA",
    "COMPILED_ROM_REUSE_REQUEST_SCHEMA",
    "GENERATOR_EXCEPTION_COMPRESSION_REQUEST_SCHEMA",
    "CHECKPOINT9_AUTHORITIES",
    "CHECKPOINT9_REQUIRED_AUTHORITIES",
    "CHECKPOINT9_AUTHORITY_MAP",
    "checkpoint9_context_facts",
    "observe_parametric_admission",
    "observe_compiled_rom_reuse",
    "observe_generator_exception_compression",
    "build_checkpoint9_inherited_authority_reachability",
]
