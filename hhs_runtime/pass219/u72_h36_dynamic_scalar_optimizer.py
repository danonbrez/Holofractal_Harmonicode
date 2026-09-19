"""Pass 219 exact u^72/H36 dynamic scalar-state optimizer.

This module advances the already-green nonary/qudit BigInt assembly and VM81/C++
RNA binding into a dynamic exact-state cycle.  One designated depth-72 coordinate
is used as an explicit u^72 resonance coordinate:

    slot s in Z_72
    phase residue = s mod 8
    nonary residue = s mod 9
    local glyph   = CRT(s mod 8, s mod 9) = s

The same slot is therefore simultaneously the exact scalar glyph, the ordered
phase residue, and the nonary residue pair.  The BigInt carrier is updated by
CRT idempotent delta weights rather than reserializing all 72 coordinates.
Every optimized transition is checked against the inherited full reference
serializer before it is admitted as optimization evidence.

The cycle additionally binds each state deterministically to one inherited
six-lane pq/qp metadata record and packs the result through the existing VM5184
binding.  Optional native probes reuse the existing candidate-only C++ RNA route
and signed environmental VM81 admission path.  No new mutation, receipt, Hash72,
Hash216, persistence, key, clock, or floating-point authority is created here.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.pass219.nonary_qudit_bigint_assembly_probe import (
    GLYPH_RADIX,
    HASH72_DEPTH,
    PHASE_RADIX,
    QUDIT_RADIX,
    bigint_from_glyph_stream,
    build_pPq_lane_order_surface,
    canonical_lo_shu_assembly_fixture,
    encode_local_glyph,
    serialize_qudit_assembly,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    pack_vm81_binding_words,
    raw_le_to_words,
    run_native_probe,
    unpack_vm81_binding_words,
    words_to_raw_le,
)
from hhs_runtime.pass219.vm81_rna_bigint_environment_admission_probe import (
    run_native_admission,
)

PASS = 219
ITERATION = "U72_H36_DYNAMIC_SCALAR_OPTIMIZER_1_0"
SCHEMA = "HHS_PASS219_U72_H36_DYNAMIC_SCALAR_OPTIMIZER_V1"

U72_PERIOD = 72
H36_HALF_TURN = 36
QUARTER_TURN = 18
QUARTER_SLOTS = (0, 18, 36, 54)
ANCHOR_SLOTS = (0, 18, 36, 54, 72)

# In the canonical Lo Shu assembly fixture the first phase channel spans the
# first nine positions.  Lo Shu index 7 carries value 1 -> nonary digit 0, so
# position 7 is exactly (phase=0, qudit=0, glyph=0) and is a natural closed
# origin for an explicit u^72 cycle without altering the initial fixture.
RESONANCE_COORDINATE = 7


class U72H36DynamicScalarOptimizerError(RuntimeError):
    pass


def _exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise U72H36DynamicScalarOptimizerError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _digit(value: Any, radix: int, label: str) -> int:
    integer = _exact_int(value, label)
    if integer < 0 or integer >= radix:
        raise U72H36DynamicScalarOptimizerError(f"{label}_OUT_OF_RANGE")
    return integer


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise U72H36DynamicScalarOptimizerError(
            f"FLOAT_DYNAMIC_AUTHORITY_FORBIDDEN:{path}"
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


@lru_cache(maxsize=None)
def crt_idempotent_basis(depth: int = HASH72_DEPTH) -> dict[str, int]:
    """Return exact CRT idempotents for Z_(8^m) x Z_(9^m) -> Z_(72^m)."""
    depth = _exact_int(depth, "DEPTH")
    if depth <= 0:
        raise U72H36DynamicScalarOptimizerError("DEPTH_MUST_BE_POSITIVE")

    phase_modulus = PHASE_RADIX**depth
    qudit_modulus = QUDIT_RADIX**depth
    combined_modulus = GLYPH_RADIX**depth
    if phase_modulus * qudit_modulus != combined_modulus:
        raise AssertionError("CRT_DEPTH_FACTORIZATION_DRIFT")

    phase_idempotent = (
        qudit_modulus * pow(qudit_modulus, -1, phase_modulus)
    ) % combined_modulus
    qudit_idempotent = (
        phase_modulus * pow(phase_modulus, -1, qudit_modulus)
    ) % combined_modulus

    if phase_idempotent % phase_modulus != 1:
        raise AssertionError("PHASE_IDEMPOTENT_PHASE_RESIDUE_DRIFT")
    if phase_idempotent % qudit_modulus != 0:
        raise AssertionError("PHASE_IDEMPOTENT_QUDIT_RESIDUE_DRIFT")
    if qudit_idempotent % phase_modulus != 0:
        raise AssertionError("QUDIT_IDEMPOTENT_PHASE_RESIDUE_DRIFT")
    if qudit_idempotent % qudit_modulus != 1:
        raise AssertionError("QUDIT_IDEMPOTENT_QUDIT_RESIDUE_DRIFT")
    if (phase_idempotent + qudit_idempotent) % combined_modulus != 1:
        raise AssertionError("CRT_IDEMPOTENT_PARTITION_DRIFT")

    return {
        "depth": depth,
        "phase_modulus": phase_modulus,
        "qudit_modulus": qudit_modulus,
        "combined_modulus": combined_modulus,
        "phase_idempotent": phase_idempotent,
        "qudit_idempotent": qudit_idempotent,
    }


def u72_slot_components(slot: int) -> dict[str, int]:
    """Return the exact local CRT factorization of one u^72 slot."""
    slot = _exact_int(slot, "U72_SLOT")
    if slot < 0 or slot > U72_PERIOD:
        raise U72H36DynamicScalarOptimizerError("U72_SLOT_OUT_OF_RANGE")
    normalized = slot % U72_PERIOD
    phase_digit = normalized % PHASE_RADIX
    qudit_digit = normalized % QUDIT_RADIX
    glyph = encode_local_glyph(phase_digit, qudit_digit)
    if glyph != normalized:
        raise AssertionError("LOCAL_U72_CRT_SCALAR_IDENTITY_DRIFT")
    return {
        "slot": slot,
        "normalized_slot": normalized,
        "phase_digit": phase_digit,
        "qudit_digit": qudit_digit,
        "glyph": glyph,
    }


def _coordinate_digit_from_bigint(
    bigint: int,
    index: int,
    radix: int,
    modulus: int,
) -> int:
    return ((bigint % modulus) // (radix**index)) % radix


def optimized_replace_coordinate(
    bigint: int,
    index: int,
    *,
    old_phase: int,
    old_qudit: int,
    new_phase: int,
    new_qudit: int,
    depth: int = HASH72_DEPTH,
) -> int:
    """Replace one exact phase/nonary coordinate with O(1) coordinate work.

    The function validates the caller's old coordinate directly against the
    BigInt residues before applying idempotent delta weights.  This prevents a
    stale or forged dependency record from producing an apparently valid jump.
    """
    bigint = _exact_int(bigint, "BIGINT")
    index = _exact_int(index, "INDEX")
    depth = _exact_int(depth, "DEPTH")
    if index < 0 or index >= depth:
        raise U72H36DynamicScalarOptimizerError("COORDINATE_INDEX_OUT_OF_RANGE")

    old_phase = _digit(old_phase, PHASE_RADIX, "OLD_PHASE")
    old_qudit = _digit(old_qudit, QUDIT_RADIX, "OLD_QUDIT")
    new_phase = _digit(new_phase, PHASE_RADIX, "NEW_PHASE")
    new_qudit = _digit(new_qudit, QUDIT_RADIX, "NEW_QUDIT")

    basis = crt_idempotent_basis(depth)
    modulus = basis["combined_modulus"]
    if bigint < 0 or bigint >= modulus:
        raise U72H36DynamicScalarOptimizerError("BIGINT_OUTSIDE_DYNAMIC_MODULUS")

    actual_phase = _coordinate_digit_from_bigint(
        bigint, index, PHASE_RADIX, basis["phase_modulus"]
    )
    actual_qudit = _coordinate_digit_from_bigint(
        bigint, index, QUDIT_RADIX, basis["qudit_modulus"]
    )
    if actual_phase != old_phase or actual_qudit != old_qudit:
        raise U72H36DynamicScalarOptimizerError("OLD_COORDINATE_MISMATCH")

    phase_delta = (new_phase - old_phase) * (PHASE_RADIX**index)
    qudit_delta = (new_qudit - old_qudit) * (QUDIT_RADIX**index)
    return (
        bigint
        + phase_delta * basis["phase_idempotent"]
        + qudit_delta * basis["qudit_idempotent"]
    ) % modulus


def expected_lane_record_for_slot(slot: int) -> dict[str, Any]:
    """Deterministically bind each u^72 scalar slot to inherited pq/qp metadata."""
    components = u72_slot_components(slot)
    lanes = build_pPq_lane_order_surface()["directed_lanes"]
    row = lanes[components["normalized_slot"] % len(lanes)]
    return {
        "opcode": int(row["opcode"]),
        "lane": int(row["lane"]),
        "direction": str(row["direction"]),
        "source": str(row["source"]),
        "target": str(row["target"]),
    }


def validate_dynamic_frame(words: Sequence[int]) -> dict[str, Any]:
    """Verify scalar/glyph/u72-slot/metadata dependency identity in one VM81 frame."""
    restored = unpack_vm81_binding_words(words)
    glyphs = tuple(int(value) for value in restored["glyph_stream"])
    slot = glyphs[RESONANCE_COORDINATE]
    expected = expected_lane_record_for_slot(slot)
    if restored["metadata"] != expected:
        raise U72H36DynamicScalarOptimizerError("U72_METADATA_DEPENDENCY_MISMATCH")
    components = u72_slot_components(slot)
    if restored["phase_digits"][RESONANCE_COORDINATE] != components["phase_digit"]:
        raise U72H36DynamicScalarOptimizerError("U72_PHASE_DEPENDENCY_MISMATCH")
    if restored["qudit_digits"][RESONANCE_COORDINATE] != components["qudit_digit"]:
        raise U72H36DynamicScalarOptimizerError("U72_QUDIT_DEPENDENCY_MISMATCH")
    if bigint_from_glyph_stream(glyphs) != restored["bigint"]:
        raise U72H36DynamicScalarOptimizerError("U72_BIGINT_GLYPH_DEPENDENCY_MISMATCH")
    return {
        "slot": slot,
        "bigint": int(restored["bigint"]),
        "metadata": dict(restored["metadata"]),
        "phase_digit": components["phase_digit"],
        "qudit_digit": components["qudit_digit"],
        "glyph": components["glyph"],
    }


def build_u72_dynamic_cycle() -> dict[str, Any]:
    """Build and prove one exact 72-step resonance cycle plus closure state."""
    fixture = canonical_lo_shu_assembly_fixture()
    phase_digits = [int(value) for value in fixture["phase_digits"]]
    qudit_digits = [int(value) for value in fixture["qudit_digits"]]
    glyphs = [int(value) for value in fixture["glyph_stream"]]
    bigint = int(fixture["bigint"])

    origin = u72_slot_components(0)
    if (
        phase_digits[RESONANCE_COORDINATE] != origin["phase_digit"]
        or qudit_digits[RESONANCE_COORDINATE] != origin["qudit_digit"]
        or glyphs[RESONANCE_COORDINATE] != origin["glyph"]
    ):
        raise AssertionError("CANONICAL_FIXTURE_RESONANCE_ORIGIN_DRIFT")

    states: list[dict[str, Any]] = []

    def append_state(step: int, current_bigint: int) -> None:
        components = u72_slot_components(step)
        lane = expected_lane_record_for_slot(step)
        words = pack_vm81_binding_words(current_bigint, glyphs, lane)
        frame = validate_dynamic_frame(words)
        raw = words_to_raw_le(words)
        states.append(
            {
                "step": step,
                "slot": components["normalized_slot"],
                "phase_digit": components["phase_digit"],
                "qudit_digit": components["qudit_digit"],
                "glyph": components["glyph"],
                "bigint": current_bigint,
                "bigint_sha256": sha256(str(current_bigint).encode("ascii")).hexdigest(),
                "raw_sha256": sha256(raw).hexdigest(),
                "metadata": lane,
                "frame_dependency_exact": frame["bigint"] == current_bigint,
                "raw_bytes": raw,
            }
        )

    append_state(0, bigint)
    initial_bigint = bigint
    initial_phase = tuple(phase_digits)
    initial_qudit = tuple(qudit_digits)
    initial_glyphs = tuple(glyphs)
    initial_raw_sha256 = states[0]["raw_sha256"]

    optimized_coordinate_updates = 0
    reference_coordinate_visits = 0

    for step in range(1, U72_PERIOD + 1):
        old_phase = phase_digits[RESONANCE_COORDINATE]
        old_qudit = qudit_digits[RESONANCE_COORDINATE]
        components = u72_slot_components(step)

        optimized = optimized_replace_coordinate(
            bigint,
            RESONANCE_COORDINATE,
            old_phase=old_phase,
            old_qudit=old_qudit,
            new_phase=components["phase_digit"],
            new_qudit=components["qudit_digit"],
        )
        optimized_coordinate_updates += 1

        phase_digits[RESONANCE_COORDINATE] = components["phase_digit"]
        qudit_digits[RESONANCE_COORDINATE] = components["qudit_digit"]
        glyphs[RESONANCE_COORDINATE] = components["glyph"]

        reference = serialize_qudit_assembly(phase_digits, qudit_digits)
        reference_coordinate_visits += HASH72_DEPTH
        reference_bigint = int(reference["bigint"])
        if optimized != reference_bigint:
            raise AssertionError("OPTIMIZED_REFERENCE_BIGINT_DIVERGENCE")
        if bigint_from_glyph_stream(glyphs) != optimized:
            raise AssertionError("OPTIMIZED_GLYPH_BIGINT_DIVERGENCE")

        bigint = optimized
        append_state(step, bigint)

    full_cycle_closed = (
        bigint == initial_bigint
        and tuple(phase_digits) == initial_phase
        and tuple(qudit_digits) == initial_qudit
        and tuple(glyphs) == initial_glyphs
        and states[-1]["raw_sha256"] == initial_raw_sha256
    )
    if not full_cycle_closed:
        raise AssertionError("U72_DYNAMIC_CYCLE_DID_NOT_CLOSE")

    reciprocal_pairs: list[dict[str, Any]] = []
    for slot in range(H36_HALF_TURN):
        left = states[slot]
        right = states[slot + H36_HALF_TURN]
        row = {
            "slot": slot,
            "inverse_slot": slot + H36_HALF_TURN,
            "qudit_preserved": left["qudit_digit"] == right["qudit_digit"],
            "phase_half_turn": (
                right["phase_digit"] - left["phase_digit"]
            ) % PHASE_RADIX == 4,
            "glyph_half_turn": (
                right["glyph"] - left["glyph"]
            ) % GLYPH_RADIX == H36_HALF_TURN,
        }
        if not all(
            row[key]
            for key in ("qudit_preserved", "phase_half_turn", "glyph_half_turn")
        ):
            raise AssertionError("H36_RECIPROCAL_PAIR_DRIFT")
        reciprocal_pairs.append(row)

    quarter_rows = [states[slot] for slot in QUARTER_SLOTS]
    quarter_phase_digits = [row["phase_digit"] for row in quarter_rows]
    quarter_qudit_digits = [row["qudit_digit"] for row in quarter_rows]
    if quarter_phase_digits != [0, 2, 4, 6]:
        raise AssertionError("U72_QUARTER_PHASE_DIGIT_DRIFT")
    if len(set(quarter_qudit_digits)) != 1:
        raise AssertionError("U72_QUARTER_NONARY_CELL_DRIFT")

    return {
        "states": states,
        "initial_bigint": initial_bigint,
        "final_bigint": bigint,
        "full_cycle_closed": full_cycle_closed,
        "reciprocal_pairs": reciprocal_pairs,
        "quarter_phase_digits": quarter_phase_digits,
        "quarter_qudit_digits": quarter_qudit_digits,
        "optimized_coordinate_updates": optimized_coordinate_updates,
        "reference_coordinate_visits": reference_coordinate_visits,
        "avoided_coordinate_visits": reference_coordinate_visits - optimized_coordinate_updates,
    }


def _candidate_native_anchor_rows(
    cycle: Mapping[str, Any], native_probe: str | None
) -> list[dict[str, Any]]:
    if native_probe is None:
        return []
    states = cycle["states"]
    rows: list[dict[str, Any]] = []
    for slot in ANCHOR_SLOTS:
        state = states[slot]
        first = run_native_probe(state["raw_bytes"], native_probe)
        second = run_native_probe(state["raw_bytes"], native_probe)
        rows.append(
            {
                "slot": slot,
                "deterministic_repeat_exact": first == second,
                "raw_unchanged": first["raw_unchanged"] == 1,
                "import_export_exact": first["import_export_exact"] == 1,
                "hash216_reference_verified": first["hash216_reference_verified"] == 1,
                "transition_identity_preserved": first["transition_identity_preserved"] == 1,
                "authority_closed": first["authority_closed"] == 1,
                "word_visits": first["word_visits"],
                "graph_edge_visits": first["graph_edge_visits"],
            }
        )
    return rows


def _signed_environment_anchor_rows(
    cycle: Mapping[str, Any], native_probe: str | None
) -> list[dict[str, Any]]:
    if native_probe is None:
        return []
    states = cycle["states"]
    rows: list[dict[str, Any]] = []
    for slot in ANCHOR_SLOTS:
        state = states[slot]
        result = run_native_admission(state["raw_bytes"], native_probe, "commit")
        native = result["native"]
        committed = result["committed_raw"]
        restored = validate_dynamic_frame(raw_le_to_words(committed))
        rows.append(
            {
                "slot": slot,
                "status": native["status"],
                "committed_exact": native["committed_exact"] == 1,
                "committed_bytes_equal_source": committed == state["raw_bytes"],
                "reencoded_bigint_exact": restored["bigint"] == state["bigint"],
                "parent_hash216_verified": native["parent_hash216_verified"] == 1,
                "child_hash216_verified": native["child_hash216_verified"] == 1,
                "inherited_rna_authority_invoked": native["inherited_rna_authority_invoked"] == 1,
                "canonical_receipt_minted": native["canonical_receipt_minted"] == 1,
                "transition_verified": native["transition_verified"] == 1,
                "child_identity_matches": native["child_identity_matches"] == 1,
                "signature_verified": native["signature_verified"] == 1,
                "environment_verified": native["environment_verified"] == 1,
                "authority_handoff_exact": native["authority_handoff_exact"] == 1,
            }
        )
    return rows


def u72_h36_dynamic_scalar_optimizer(
    *,
    candidate_native_probe: str | None = None,
    environment_native_probe: str | None = None,
) -> dict[str, Any]:
    cycle = build_u72_dynamic_cycle()
    candidate_rows = _candidate_native_anchor_rows(cycle, candidate_native_probe)
    environment_rows = _signed_environment_anchor_rows(cycle, environment_native_probe)

    candidate_green = bool(candidate_rows) and all(
        row["deterministic_repeat_exact"]
        and row["raw_unchanged"]
        and row["import_export_exact"]
        and row["hash216_reference_verified"]
        and row["transition_identity_preserved"]
        and row["authority_closed"]
        and row["word_visits"] == 81
        and row["graph_edge_visits"] == 1620
        for row in candidate_rows
    )
    environment_green = bool(environment_rows) and all(
        row["status"] == 0
        and row["committed_exact"]
        and row["committed_bytes_equal_source"]
        and row["reencoded_bigint_exact"]
        and row["parent_hash216_verified"]
        and row["child_hash216_verified"]
        and row["inherited_rna_authority_invoked"]
        and row["canonical_receipt_minted"]
        and row["transition_verified"]
        and row["child_identity_matches"]
        and row["signature_verified"]
        and row["environment_verified"]
        and row["authority_handoff_exact"]
        for row in environment_rows
    )

    state_summaries = [
        {
            "step": row["step"],
            "slot": row["slot"],
            "phase_digit": row["phase_digit"],
            "qudit_digit": row["qudit_digit"],
            "glyph": row["glyph"],
            "bigint": row["bigint"],
            "bigint_sha256": row["bigint_sha256"],
            "raw_sha256": row["raw_sha256"],
            "metadata": row["metadata"],
        }
        for row in cycle["states"]
    ]

    report = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "exact_geometry": {
            "phase_radix": PHASE_RADIX,
            "qudit_radix": QUDIT_RADIX,
            "glyph_radix": GLYPH_RADIX,
            "depth": HASH72_DEPTH,
            "local_factorization_exact": PHASE_RADIX * QUDIT_RADIX == GLYPH_RADIX,
            "vm5184_factorization_exact": 81 * 64 == 5184 == GLYPH_RADIX**2,
            "h36_scale_exact": 5184**H36_HALF_TURN == GLYPH_RADIX**GLYPH_RADIX,
            "u72_period": U72_PERIOD,
            "h36_half_turn": H36_HALF_TURN,
            "quarter_slots": list(QUARTER_SLOTS),
            "resonance_coordinate": RESONANCE_COORDINATE,
        },
        "dynamic_cycle": {
            "state_count_including_closure": len(cycle["states"]),
            "full_u72_cycle_closed": cycle["full_cycle_closed"],
            "initial_bigint": cycle["initial_bigint"],
            "final_bigint": cycle["final_bigint"],
            "every_slot_scalar_equals_local_glyph": all(
                row["slot"] == row["glyph"] for row in cycle["states"]
            ),
            "quarter_phase_digits": cycle["quarter_phase_digits"],
            "quarter_qudit_digits": cycle["quarter_qudit_digits"],
            "h36_reciprocal_pair_count": len(cycle["reciprocal_pairs"]),
            "all_h36_pairs_preserve_nonary_and_flip_phase": all(
                row["qudit_preserved"]
                and row["phase_half_turn"]
                and row["glyph_half_turn"]
                for row in cycle["reciprocal_pairs"]
            ),
            "states": state_summaries,
        },
        "optimization": {
            "reference_coordinate_visits": cycle["reference_coordinate_visits"],
            "optimized_coordinate_updates": cycle["optimized_coordinate_updates"],
            "avoided_coordinate_visits": cycle["avoided_coordinate_visits"],
            "expected_reference_coordinate_visits": U72_PERIOD * HASH72_DEPTH,
            "expected_optimized_coordinate_updates": U72_PERIOD,
            "exact_reference_equality_every_transition": True,
            "new_primitive_algebra_required": False,
        },
        "candidate_rna_anchors": {
            "probe_supplied": candidate_native_probe is not None,
            "anchor_slots": list(ANCHOR_SLOTS),
            "all_candidate_routes_green": candidate_green,
            "rows": candidate_rows,
        },
        "signed_environment_anchors": {
            "probe_supplied": environment_native_probe is not None,
            "anchor_slots": list(ANCHOR_SLOTS),
            "all_signed_environmental_commits_exact": environment_green,
            "rows": environment_rows,
        },
        "authority": {
            "optimizer_is_exact_integer_only": True,
            "existing_candidate_rna_route_reused": candidate_native_probe is not None,
            "existing_signed_environmental_boundary_reused": environment_native_probe is not None,
            "new_canonical_vm81_mutation_authority": False,
            "new_canonical_receipt_authority": False,
            "new_hash72_minting_authority": False,
            "new_hash216_persistence_authority": False,
            "new_pqc_key_authority": False,
            "new_receipt_clock_authority": False,
            "floating_point_authority": False,
            "ordered_phase_nonary_identity_collapsed": False,
        },
    }
    report["report_sha256"] = _digest(report)
    return report


def main() -> None:
    import os

    print(
        json.dumps(
            u72_h36_dynamic_scalar_optimizer(
                candidate_native_probe=os.environ.get(
                    "HHS_PASS219_BIGINT_RNA_NATIVE_PROBE"
                ),
                environment_native_probe=os.environ.get(
                    "HHS_PASS219_BIGINT_ENVIRONMENT_NATIVE_PROBE"
                ),
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
