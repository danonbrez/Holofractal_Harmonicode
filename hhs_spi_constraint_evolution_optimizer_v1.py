"""Pass 219 SPI — exact constraint/evolution optimizer v1.

This module makes the development/learning lifecycle executable over already
proved SPI tensor-translation objects:

    FORMALIZE -> PROVE -> IMPLEMENT -> OPTIMIZE -> CANONIZE -> ITERATE

The optimizer is deliberately candidate-only.  It may rank exact symbolic
candidates and emit a deterministic next-cycle seed, but it cannot mutate
VM81, mint canonical Hash72/Hash216 state, or persist canonical state.

Semantic labels are carried as metadata and are excluded from the exact
selection score.  Admission is determined only by the typed computational
constraints represented here and by the closed predecessor proof receipts.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any, Dict, Mapping, Sequence

from hhs_spi_tensor_pair_translation_stack_v1 import (
    lo_shu_translation_stack,
    sudoku_translation_stack,
)

FORMAT = "HHS_SPI_CONSTRAINT_EVOLUTION_OPTIMIZER_V1"
VERSION = "1.0.0"
PROFILE = "FORMALIZE-PROVE-IMPLEMENT-OPTIMIZE-CANONIZE-ITERATE-v1"

LIFECYCLE = (
    "FORMALIZE",
    "PROVE",
    "IMPLEMENT",
    "OPTIMIZE",
    "CANONIZE",
    "ITERATE",
)

VM81_CELL_COUNT = 81
VM81_OPERATION_COUNT = 64
VM5184_ADDRESS_COUNT = VM81_CELL_COUNT * VM81_OPERATION_COUNT
HYDRATION_LANE_COUNT = 4
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class SPIConstraintEvolutionOptimizerError(ValueError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise SPIConstraintEvolutionOptimizerError(f"FLOAT_AUTHORITY_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _stable_json(value: Any) -> str:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _exact_int(value: Any, label: str, *, minimum: int = 0, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SPIConstraintEvolutionOptimizerError(f"{label}_EXACT_INTEGER_REQUIRED")
    if value < minimum:
        raise SPIConstraintEvolutionOptimizerError(f"{label}_OUT_OF_RANGE")
    if maximum is not None and value > maximum:
        raise SPIConstraintEvolutionOptimizerError(f"{label}_OUT_OF_RANGE")
    return value


def _nonempty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SPIConstraintEvolutionOptimizerError(f"{label}_NONEMPTY_TEXT_REQUIRED")
    return value


def _translation_stack(tensor_kind: str, stage_index: int) -> Dict[str, Any]:
    if tensor_kind == "LO_SHU":
        return lo_shu_translation_stack(stage_index)
    if tensor_kind == "SUDOKU":
        return sudoku_translation_stack(stage_index)
    raise SPIConstraintEvolutionOptimizerError("TENSOR_KIND_UNSUPPORTED")


def vm5184_address(cell_index: int, operation_index: int) -> int:
    """Exact 81 x 64 address used as candidate knowledge-coordinate metadata."""
    cell = _exact_int(cell_index, "CELL_INDEX", maximum=VM81_CELL_COUNT - 1)
    operation = _exact_int(
        operation_index,
        "OPERATION_INDEX",
        maximum=VM81_OPERATION_COUNT - 1,
    )
    return cell * VM81_OPERATION_COUNT + operation


def decode_vm5184_address(address: int) -> tuple[int, int]:
    value = _exact_int(address, "VM5184_ADDRESS", maximum=VM5184_ADDRESS_COUNT - 1)
    return value // VM81_OPERATION_COUNT, value % VM81_OPERATION_COUNT


def _stack_is_closed(stack: Mapping[str, Any]) -> bool:
    try:
        return (
            stack["equal_sum_layer"]["closed"] is True
            and stack["fibonacci_pythagorean_scale_layer"]["same_scale_coordinate"] is True
            and stack["cubic_three_set_layer"]["closed"] is True
            and stack["composition"]["projection_only"] is True
            and stack["native_tensor_identity_authorized"] is False
            and stack["native_t_solved"] is False
            and stack["canonical_admission_authority"] is False
            and stack["vm81_mutation_authority"] is False
            and stack["canonical_hash72_authority"] is False
            and stack["canonical_hash216_authority"] is False
            and stack["canonical_persistence_authority"] is False
            and stack["floating_point_authority"] is False
        )
    except (KeyError, TypeError):
        return False


def build_learning_candidate(
    *,
    candidate_id: str,
    tensor_kind: str,
    stage_index: int,
    hydration_lane: int,
    cell_index: int,
    operation_index: int,
    branch_count: int,
    reusable_branch_count: int,
    symbolic_parameter_state: str,
    semantic_label: str = "",
) -> Dict[str, Any]:
    """Build one exact constrained-learning candidate.

    ``branch_count`` and ``reusable_branch_count`` are explicit structural work
    units, not timing claims.  Reuse may reduce unresolved work but cannot
    exceed the declared branch count.
    """
    candidate = _nonempty_text(candidate_id, "CANDIDATE_ID")
    parameter_state = _nonempty_text(symbolic_parameter_state, "SYMBOLIC_PARAMETER_STATE")
    if not isinstance(semantic_label, str):
        raise SPIConstraintEvolutionOptimizerError("SEMANTIC_LABEL_TEXT_REQUIRED")
    stage = _exact_int(stage_index, "STAGE_INDEX")
    lane = _exact_int(hydration_lane, "HYDRATION_LANE", maximum=HYDRATION_LANE_COUNT - 1)
    branches = _exact_int(branch_count, "BRANCH_COUNT", minimum=1)
    reusable = _exact_int(reusable_branch_count, "REUSABLE_BRANCH_COUNT")
    if reusable > branches:
        raise SPIConstraintEvolutionOptimizerError("REUSABLE_BRANCH_COUNT_EXCEEDS_BRANCH_COUNT")

    stack = _translation_stack(tensor_kind, stage)
    if not _stack_is_closed(stack):
        raise SPIConstraintEvolutionOptimizerError("PREDECESSOR_TRANSLATION_STACK_NOT_CLOSED")

    address = vm5184_address(cell_index, operation_index)
    unresolved = branches - reusable

    receipt: Dict[str, Any] = {
        "schema": "HHS_SPI_CONSTRAINT_EVOLUTION_CANDIDATE_RECEIPT_V1",
        "format": FORMAT,
        "version": VERSION,
        "profile": PROFILE,
        "candidate_id": candidate,
        "tensor_kind": tensor_kind,
        "stage_index": stage,
        "symbolic_parameter_state": parameter_state,
        "semantic_label": semantic_label,
        "semantic_label_has_selection_authority": False,
        "coordinate": {
            "hydration_lane": lane,
            "cell81": cell_index,
            "operation64": operation_index,
            "vm5184_address": address,
            "vm5184_address_count": VM5184_ADDRESS_COUNT,
            "four_lane_hydration": True,
        },
        "predecessor": {
            "tensor_translation_receipt_sha256": stack["receipt_sha256"],
            "equal_sum_closed": True,
            "fibonacci_scale_closed": True,
            "cubic_three_set_closed": True,
            "projection_only": True,
        },
        "work": {
            "branch_count": branches,
            "reusable_branch_count": reusable,
            "unresolved_branch_count": unresolved,
            "work_units_are_structural_not_timing": True,
            "empirical_speedup_claimed": False,
        },
        "lifecycle": {
            "FORMALIZE": "PASS",
            "PROVE": "PASS",
            "IMPLEMENT": "PASS",
            "OPTIMIZE": "PENDING_SELECTION",
            "CANONIZE": "PENDING_SELECTION",
            "ITERATE": "PENDING_SELECTION",
        },
        "knowledge_graph": {
            "vm5184_coordinate_metadata_only": True,
            "hash216_vector_store_reference_eligible": True,
            "canonical_hash216_minted": False,
        },
        "authority": {
            "candidate_only": True,
            "canonical_admission": False,
            "vm81_mutation": False,
            "canonical_hash72": False,
            "canonical_hash216": False,
            "canonical_persistence": False,
            "floating_point": False,
        },
    }
    receipt["receipt_sha256"] = _digest(receipt)
    return receipt


def verify_learning_candidate(candidate: Mapping[str, Any]) -> Dict[str, Any]:
    """Fail closed unless the candidate is a deterministic v1 receipt."""
    _reject_float(candidate)
    errors: list[str] = []
    try:
        if candidate.get("schema") != "HHS_SPI_CONSTRAINT_EVOLUTION_CANDIDATE_RECEIPT_V1":
            errors.append("schema")
        if candidate.get("format") != FORMAT or candidate.get("version") != VERSION:
            errors.append("format_or_version")
        lifecycle = candidate["lifecycle"]
        for stage in ("FORMALIZE", "PROVE", "IMPLEMENT"):
            if lifecycle.get(stage) != "PASS":
                errors.append(f"gate:{stage}")
        if lifecycle.get("OPTIMIZE") != "PENDING_SELECTION":
            errors.append("optimize_preselection_state")
        work = candidate["work"]
        branches = _exact_int(work["branch_count"], "BRANCH_COUNT", minimum=1)
        reusable = _exact_int(work["reusable_branch_count"], "REUSABLE_BRANCH_COUNT")
        unresolved = _exact_int(work["unresolved_branch_count"], "UNRESOLVED_BRANCH_COUNT")
        if reusable > branches or unresolved != branches - reusable:
            errors.append("work_conservation")
        coordinate = candidate["coordinate"]
        address = vm5184_address(coordinate["cell81"], coordinate["operation64"])
        if coordinate.get("vm5184_address") != address:
            errors.append("vm5184_address")
        lane = _exact_int(coordinate["hydration_lane"], "HYDRATION_LANE", maximum=HYDRATION_LANE_COUNT - 1)
        if lane != coordinate["hydration_lane"]:
            errors.append("hydration_lane")
        if coordinate.get("vm5184_address_count") != VM5184_ADDRESS_COUNT:
            errors.append("vm5184_cardinality")
        predecessor = candidate["predecessor"]
        if predecessor.get("projection_only") is not True:
            errors.append("predecessor_projection_boundary")
        predecessor_hash = predecessor.get("tensor_translation_receipt_sha256")
        if not isinstance(predecessor_hash, str) or not _HASH_RE.fullmatch(predecessor_hash):
            errors.append("predecessor_receipt_sha256")
        authority = candidate["authority"]
        if authority != {
            "candidate_only": True,
            "canonical_admission": False,
            "vm81_mutation": False,
            "canonical_hash72": False,
            "canonical_hash216": False,
            "canonical_persistence": False,
            "floating_point": False,
        }:
            errors.append("authority_boundary")
        if candidate.get("semantic_label_has_selection_authority") is not False:
            errors.append("semantic_authority")
        supplied = candidate.get("receipt_sha256")
        body = dict(candidate)
        body.pop("receipt_sha256", None)
        if supplied != _digest(body):
            errors.append("receipt_sha256")
    except (KeyError, TypeError, SPIConstraintEvolutionOptimizerError) as exc:
        errors.append(f"{type(exc).__name__}:{exc}")

    return {
        "schema": "HHS_SPI_CONSTRAINT_EVOLUTION_CANDIDATE_VALIDATION_V1",
        "candidate_id": candidate.get("candidate_id"),
        "ok": not errors,
        "errors": errors,
        "canonical_admission_authority": False,
    }


def optimize_learning_candidates(candidates: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Select the exact admissible candidate with minimum unresolved work.

    Ordering is deterministic:

        unresolved branches
        -> greater already-proved reuse
        -> stable candidate id

    This is an exact structural objective.  It makes no latency/speedup claim.
    """
    if not candidates:
        raise SPIConstraintEvolutionOptimizerError("CANDIDATE_SET_EMPTY")

    verified: list[Mapping[str, Any]] = []
    rejected: list[Dict[str, Any]] = []
    ids: set[str] = set()
    for candidate in candidates:
        report = verify_learning_candidate(candidate)
        candidate_id = candidate.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            rejected.append(report)
            continue
        if candidate_id in ids:
            raise SPIConstraintEvolutionOptimizerError("DUPLICATE_CANDIDATE_ID")
        ids.add(candidate_id)
        if report["ok"]:
            verified.append(candidate)
        else:
            rejected.append(report)

    if not verified:
        raise SPIConstraintEvolutionOptimizerError("NO_CANDIDATE_SURVIVED_FORMAL_PROOF_IMPLEMENTATION_GATES")

    def score(candidate: Mapping[str, Any]) -> tuple[int, int, str]:
        work = candidate["work"]
        return (
            int(work["unresolved_branch_count"]),
            -int(work["reusable_branch_count"]),
            str(candidate["candidate_id"]),
        )

    selected = min(verified, key=score)
    selected_score = score(selected)

    iteration_seed_body = {
        "source_candidate_id": selected["candidate_id"],
        "source_candidate_receipt_sha256": selected["receipt_sha256"],
        "vm5184_address": selected["coordinate"]["vm5184_address"],
        "hydration_lane": selected["coordinate"]["hydration_lane"],
        "symbolic_parameter_state": selected["symbolic_parameter_state"],
        "next_cycle": "FORMALIZE",
        "canonical_state_mutation": False,
    }
    iteration_seed = dict(iteration_seed_body)
    iteration_seed["seed_sha256"] = _digest(iteration_seed_body)

    result: Dict[str, Any] = {
        "schema": "HHS_SPI_CONSTRAINT_EVOLUTION_OPTIMIZATION_RECEIPT_V1",
        "format": FORMAT,
        "version": VERSION,
        "profile": PROFILE,
        "lifecycle_order": list(LIFECYCLE),
        "candidate_count": len(candidates),
        "verified_candidate_count": len(verified),
        "rejected_candidate_count": len(rejected),
        "rejected_candidates": rejected,
        "selection_rule": [
            "MIN_UNRESOLVED_BRANCH_COUNT",
            "MAX_REUSABLE_BRANCH_COUNT",
            "STABLE_CANDIDATE_ID",
        ],
        "selected_candidate_id": selected["candidate_id"],
        "selected_candidate_receipt_sha256": selected["receipt_sha256"],
        "selected_score": {
            "unresolved_branch_count": selected_score[0],
            "reusable_branch_count": -selected_score[1],
        },
        "semantic_label_used_for_selection": False,
        "empirical_speedup_claimed": False,
        "lifecycle": {
            "FORMALIZE": "PASS",
            "PROVE": "PASS",
            "IMPLEMENT": "PASS",
            "OPTIMIZE": "PASS",
            "CANONIZE": "PROJECTION_RECEIPT_ELIGIBLE",
            "ITERATE": "NEXT_CYCLE_SEED_EMITTED",
        },
        "canonization": {
            "scope": "SPI_PROJECTION_OPTIMIZER_RECEIPT_ONLY",
            "repository_main_canonized": False,
            "canonical_vm81_state_admitted": False,
        },
        "iteration_seed": iteration_seed,
        "knowledge_graph": {
            "vm5184_coordinate": selected["coordinate"]["vm5184_address"],
            "hash216_vector_store_reference_eligible": True,
            "canonical_hash216_minted": False,
        },
        "authority": {
            "candidate_only": True,
            "canonical_admission": False,
            "vm81_mutation": False,
            "canonical_hash72": False,
            "canonical_hash216": False,
            "canonical_persistence": False,
            "floating_point": False,
        },
    }
    result["receipt_sha256"] = _digest(result)
    return result


def reference_optimizer_cycle() -> Dict[str, Any]:
    """Deterministic two-candidate proof/reuse optimization witness."""
    candidates = [
        build_learning_candidate(
            candidate_id="LOSHU-S4-STRUCTURAL",
            tensor_kind="LO_SHU",
            stage_index=4,
            hydration_lane=0,
            cell_index=0,
            operation_index=0,
            branch_count=64,
            reusable_branch_count=48,
            symbolic_parameter_state="Q4:LO_SHU:EXACT",
            semantic_label="local symbolic tensor candidate",
        ),
        build_learning_candidate(
            candidate_id="SUDOKU-S4-REUSE",
            tensor_kind="SUDOKU",
            stage_index=4,
            hydration_lane=1,
            cell_index=1,
            operation_index=1,
            branch_count=81,
            reusable_branch_count=72,
            symbolic_parameter_state="Q4:SUDOKU:EXACT",
            semantic_label="global symbolic tensor candidate",
        ),
    ]
    return optimize_learning_candidates(candidates)
