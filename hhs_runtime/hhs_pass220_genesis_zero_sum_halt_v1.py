"""Pass 220 I004: global Genesis zero-sum Lo Shu closure halt gate.

This module consumes typed closure witnesses from the authoritative algebra
surfaces.  It does not independently reduce or replace AB=P^4, the 1/9
invariant, or the local 7-cell constraint equations.

The scheduler halt is exact:
- all 81 normalized offsets are zero;
- all nine local Lo Shu nuclei close;
- every local Lo Shu 1-cell anchor is zero-normalized;
- every local typed AB=P^4, 1/9, and 7-cell witness is closed;
- the next normalized state is identical to the current normalized state.

HALT does not mint a new canonical transition and does not widen VM81,
Hash72, or Hash216 authority.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    LO_SHU_FLAT,
    NUCLEUS_CELLS,
    NUCLEUS_COUNT,
    VM81_CELLS,
)

SCHEMA = "HHS_PASS_220_I004_GENESIS_ZERO_SUM_LO_SHU_GLOBAL_HALT_V1"
NUCLEUS_SCHEMA = "HHS_PASS_220_I004_LOCAL_LO_SHU_CLOSURE_WITNESS_V1"
HALT_REASON = "GENESIS_GLOBAL_ZERO_SUM_CLOSURE"
CONTINUE_REASON = "UNRESOLVED_CONSTRAINT_OR_NONZERO_STATE_CHANGE"

LO_SHU_ONE_LOCAL_INDEX = LO_SHU_FLAT.index(1)
LO_SHU_SEVEN_LOCAL_INDEX = LO_SHU_FLAT.index(7)


class Pass220GenesisHaltError(ValueError):
    pass


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220GenesisHaltError(f"{name} must be an exact integer")
    return value


def _exact_bool(value: Any, *, name: str) -> bool:
    if not isinstance(value, bool):
        raise Pass220GenesisHaltError(f"{name} must be an exact boolean witness")
    return value


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _offset_vector(values: Sequence[int], *, name: str) -> tuple[int, ...]:
    offsets = tuple(values)
    if len(offsets) != VM81_CELLS:
        raise Pass220GenesisHaltError(f"{name} must contain exactly {VM81_CELLS} offsets")
    canonical = []
    for index, value in enumerate(offsets):
        digit = _exact_int(value, name=f"{name}[{index}]")
        if not 0 <= digit <= 8:
            raise Pass220GenesisHaltError(f"{name}[{index}] must be in 0..8")
        canonical.append(digit)
    return tuple(canonical)


def _canonical_nucleus_witnesses(
    witnesses: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    if len(witnesses) != NUCLEUS_COUNT:
        raise Pass220GenesisHaltError(
            f"exactly {NUCLEUS_COUNT} local Lo Shu nucleus witnesses are required"
        )

    by_index: dict[int, dict[str, Any]] = {}
    for ordinal, witness in enumerate(witnesses):
        if not isinstance(witness, Mapping):
            raise Pass220GenesisHaltError(f"nucleus_witnesses[{ordinal}] must be a mapping")
        index = _exact_int(witness.get("nucleus_index"), name="nucleus_index")
        if not 0 <= index < NUCLEUS_COUNT:
            raise Pass220GenesisHaltError("nucleus_index outside 0..8")
        if index in by_index:
            raise Pass220GenesisHaltError("duplicate nucleus_index")

        ab_p4_closed = _exact_bool(witness.get("ab_p4_closed"), name="ab_p4_closed")
        one_ninth_closed = _exact_bool(
            witness.get("one_ninth_invariant_closed"),
            name="one_ninth_invariant_closed",
        )
        cell7_closed = _exact_bool(
            witness.get("cell7_constraint_closed"),
            name="cell7_constraint_closed",
        )
        by_index[index] = {
            "schema": NUCLEUS_SCHEMA,
            "nucleus_index": index,
            "ab_p4_closed": ab_p4_closed,
            "one_ninth_invariant_closed": one_ninth_closed,
            "cell7_constraint_closed": cell7_closed,
        }

    required = set(range(NUCLEUS_COUNT))
    if set(by_index) != required:
        raise Pass220GenesisHaltError("nucleus witness index set must be exactly 0..8")
    return tuple(by_index[index] for index in range(NUCLEUS_COUNT))


def genesis_zero_sum_halt_decision(
    *,
    current_offsets: Sequence[int],
    next_offsets: Sequence[int],
    nucleus_witnesses: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Return the exact I004 scheduler decision.

    Equation truth is supplied by typed witnesses from their authoritative
    evaluators.  This function only composes those witnesses with I001's exact
    zero-normalized Lo Shu state.
    """
    current = _offset_vector(current_offsets, name="current_offsets")
    nxt = _offset_vector(next_offsets, name="next_offsets")
    typed = _canonical_nucleus_witnesses(nucleus_witnesses)

    global_zero = all(value == 0 for value in current)
    state_change_zero = current == nxt

    local = []
    for witness in typed:
        nucleus_index = int(witness["nucleus_index"])
        start = nucleus_index * NUCLEUS_CELLS
        stop = start + NUCLEUS_CELLS
        local_offsets = current[start:stop]
        one_global_index = start + LO_SHU_ONE_LOCAL_INDEX
        seven_global_index = start + LO_SHU_SEVEN_LOCAL_INDEX

        local_zero = all(value == 0 for value in local_offsets)
        one_cell_zero = current[one_global_index] == 0
        seven_cell_zero = current[seven_global_index] == 0
        equations_closed = (
            bool(witness["ab_p4_closed"])
            and bool(witness["one_ninth_invariant_closed"])
            and bool(witness["cell7_constraint_closed"])
        )
        nucleus_closed = local_zero and one_cell_zero and seven_cell_zero and equations_closed
        local.append(
            {
                **witness,
                "lo_shu_one_local_index": LO_SHU_ONE_LOCAL_INDEX,
                "lo_shu_one_global_index": one_global_index,
                "lo_shu_seven_local_index": LO_SHU_SEVEN_LOCAL_INDEX,
                "lo_shu_seven_global_index": seven_global_index,
                "local_zero_sum_closed": local_zero,
                "one_cell_zero_normalized": one_cell_zero,
                "seven_cell_zero_normalized": seven_cell_zero,
                "typed_equation_witnesses_closed": equations_closed,
                "nucleus_closed": nucleus_closed,
            }
        )

    all_nuclei_closed = all(item["nucleus_closed"] for item in local)
    halt = global_zero and state_change_zero and all_nuclei_closed

    result = {
        "schema": SCHEMA,
        "vm81_cells": VM81_CELLS,
        "local_lo_shu_nuclei": NUCLEUS_COUNT,
        "local_lo_shu_cells": NUCLEUS_CELLS,
        "lo_shu_one_local_index": LO_SHU_ONE_LOCAL_INDEX,
        "lo_shu_seven_local_index": LO_SHU_SEVEN_LOCAL_INDEX,
        "global_zero_sum_closed": global_zero,
        "all_local_nuclei_closed": all_nuclei_closed,
        "normalized_state_change_zero": state_change_zero,
        "nuclei": local,
        "halt": halt,
        "reason": HALT_REASON if halt else CONTINUE_REASON,
        "candidate_expansion_blocked": halt,
        "new_canonical_transition_blocked": halt,
        "halt_extends_hash72_ledger": False,
        "halt_mints_hash216_transition": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "floating_point_authority": False,
        "equation_witnesses_are_typed_inputs_not_rederived": True,
    }
    result["decision_sha256"] = sha256(_stable_json(result).encode("utf-8")).hexdigest()
    return result


def closed_nucleus_witnesses() -> tuple[dict[str, Any], ...]:
    """Return the exact nine-witness shape for a fully closed typed fixture.

    This is a test/construction helper only.  It does not prove the source
    equations; authoritative callers must replace fixture booleans with their
    own exact witness results.
    """
    return tuple(
        {
            "nucleus_index": index,
            "ab_p4_closed": True,
            "one_ninth_invariant_closed": True,
            "cell7_constraint_closed": True,
        }
        for index in range(NUCLEUS_COUNT)
    )


__all__ = [
    "CONTINUE_REASON",
    "HALT_REASON",
    "LO_SHU_ONE_LOCAL_INDEX",
    "LO_SHU_SEVEN_LOCAL_INDEX",
    "NUCLEUS_SCHEMA",
    "Pass220GenesisHaltError",
    "SCHEMA",
    "closed_nucleus_witnesses",
    "genesis_zero_sum_halt_decision",
]
