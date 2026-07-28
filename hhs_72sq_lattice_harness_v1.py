"""
hhs_72sq_lattice_harness_v1.py

Read-only investigation harness for the HHS 72² Lattice.

Observation-first policy: no runtime state is mutated.  All functions
are deterministic, pure, and side-effect-free unless the function
explicitly writes to a JSONL trace file (trace helpers only).

Contents
--------
1. HHS72SqRuntimeTrace  – TypedDict schema for HHS_72SQ_RUNTIME_TRACE.jsonl
2. hash72sq_encode / hash72sq_decode  – 72×72 lattice coordinate mapping
3. dual_radix_encode / dual_radix_decode  – 64×81 lattice coordinate mapping
4. to_balanced_trinary  – 81-state → 4-position balanced-trinary tuple
5. test_reciprocal_closure  – exact rational closure check (fractions.Fraction)
6. Experiment stubs A–H
"""

from __future__ import annotations

import fractions
import json
import traceback
from pathlib import Path
from typing import List, Optional, Tuple, TypedDict

# ---------------------------------------------------------------------------
# 1. Mandatory Trace Schema
# ---------------------------------------------------------------------------

class HHS72SqRuntimeTrace(TypedDict):
    """Exact JSON structure for one line of HHS_72SQ_RUNTIME_TRACE.jsonl.

    Fields
    ------
    sequence : int
        Monotonically increasing event counter starting at 0.
    runtime_session_id : str
        Opaque identifier for the current runtime session.
    input_root_hash72 : str
        Hash72 of the raw input that triggered this trace entry.
    lane_hash72 : List[str]
        Exactly three Hash72 strings representing the three processing lanes.
    lane_sha256 : List[str]
        Exactly three SHA-256 hex-digest strings mirroring the three lanes.
    cache_hit : bool
        True iff the input root was already present in the state cache.
    new_state_record_created : bool
        True iff a new canonical state record was written during this event.
    edge_created : bool
        True iff a new cross-modality edge was created during this event.
    lattice_index_72sq : Optional[int]
        Resolved 1-D index in the 72×72 lattice (0 ≤ i < 5184), or None if
        the event does not correspond to a lattice position.
    lattice_index_dual : Optional[int]
        Resolved 1-D index in the 64×81 dual-radix lattice (0 ≤ i < 5184),
        or None if not applicable.
    receipt_hash72 : str
        Hash72 of the receipt chain tip at time of emission.
    """

    sequence: int
    runtime_session_id: str
    input_root_hash72: str
    lane_hash72: List[str]          # exactly 3 entries
    lane_sha256: List[str]          # exactly 3 entries
    cache_hit: bool
    new_state_record_created: bool
    edge_created: bool
    lattice_index_72sq: Optional[int]
    lattice_index_dual: Optional[int]
    receipt_hash72: str


def validate_trace_record(record: HHS72SqRuntimeTrace) -> None:
    """Raise ValueError if *record* violates structural constraints."""
    if len(record["lane_hash72"]) != 3:
        raise ValueError(
            f"lane_hash72 must have exactly 3 entries, "
            f"got {len(record['lane_hash72'])}"
        )
    if len(record["lane_sha256"]) != 3:
        raise ValueError(
            f"lane_sha256 must have exactly 3 entries, "
            f"got {len(record['lane_sha256'])}"
        )
    if record["lattice_index_72sq"] is not None:
        idx = record["lattice_index_72sq"]
        if not (0 <= idx < 5184):
            raise ValueError(
                f"lattice_index_72sq out of range [0, 5184): {idx}"
            )
    if record["lattice_index_dual"] is not None:
        idx = record["lattice_index_dual"]
        if not (0 <= idx < 5184):
            raise ValueError(
                f"lattice_index_dual out of range [0, 5184): {idx}"
            )


# ---------------------------------------------------------------------------
# 2. Hash72² Lattice Coordinate Mapping  (72 × 72 = 5 184)
# ---------------------------------------------------------------------------

_LATTICE_72_SIDE: int = 72
_LATTICE_72SQ_SIZE: int = _LATTICE_72_SIDE * _LATTICE_72_SIDE  # 5 184


def hash72sq_encode(u: int, v: int) -> int:
    """Map ordered pair (u, v) to 1-D index i₇₂ = 72·u + v.

    Parameters
    ----------
    u, v : int
        Lattice coordinates; both must satisfy 0 ≤ x < 72.

    Returns
    -------
    int
        Index i₇₂ with 0 ≤ i₇₂ < 5184.

    Raises
    ------
    ValueError
        If either coordinate is outside [0, 72).
    """
    if not (0 <= u < _LATTICE_72_SIDE):
        raise ValueError(f"u={u} out of range [0, {_LATTICE_72_SIDE})")
    if not (0 <= v < _LATTICE_72_SIDE):
        raise ValueError(f"v={v} out of range [0, {_LATTICE_72_SIDE})")
    index = _LATTICE_72_SIDE * u + v
    assert 0 <= index < _LATTICE_72SQ_SIZE  # kernel invariant guard
    return index


def hash72sq_decode(index: int) -> Tuple[int, int]:
    """Decode 1-D index i₇₂ back to ordered pair (u, v).

    Parameters
    ----------
    index : int
        1-D lattice index with 0 ≤ index < 5184.

    Returns
    -------
    (u, v) : Tuple[int, int]
        Reconstructed coordinates where u = ⌊i₇₂ / 72⌋, v = i₇₂ mod 72.

    Raises
    ------
    ValueError
        If *index* is outside [0, 5184).
    """
    if not (0 <= index < _LATTICE_72SQ_SIZE):
        raise ValueError(
            f"index={index} out of range [0, {_LATTICE_72SQ_SIZE})"
        )
    u, v = divmod(index, _LATTICE_72_SIDE)
    return u, v


# ---------------------------------------------------------------------------
# 3. Base64 & Balanced-Trinary Mapping  (64 × 81 = 5 184)
# ---------------------------------------------------------------------------

_DUAL_BASE64_SIDE: int = 64   # a ∈ {0, …, 63}
_DUAL_TRIT81_SIDE: int = 81   # t ∈ {0, …, 80}
_DUAL_SIZE: int = _DUAL_BASE64_SIDE * _DUAL_TRIT81_SIDE  # 5 184


def dual_radix_encode(a: int, t: int) -> int:
    """Encode (a, t) into 1-D dual-radix index i₆₄×₈₁ = 81·a + t.

    Parameters
    ----------
    a : int
        Base-64 coordinate; 0 ≤ a < 64.
    t : int
        Balanced-trinary 81-state coordinate; 0 ≤ t < 81.

    Returns
    -------
    int
        Index i₆₄×₈₁ with 0 ≤ i < 5184.

    Raises
    ------
    ValueError
        If either coordinate is out of its valid range.
    """
    if not (0 <= a < _DUAL_BASE64_SIDE):
        raise ValueError(f"a={a} out of range [0, {_DUAL_BASE64_SIDE})")
    if not (0 <= t < _DUAL_TRIT81_SIDE):
        raise ValueError(f"t={t} out of range [0, {_DUAL_TRIT81_SIDE})")
    index = _DUAL_TRIT81_SIDE * a + t
    assert 0 <= index < _DUAL_SIZE  # kernel invariant guard
    return index


def dual_radix_decode(index: int) -> Tuple[int, int]:
    """Decode dual-radix index back to (a, t).

    Parameters
    ----------
    index : int
        1-D index with 0 ≤ index < 5184.

    Returns
    -------
    (a, t) : Tuple[int, int]
        a = ⌊index / 81⌋, t = index mod 81.

    Raises
    ------
    ValueError
        If *index* is outside [0, 5184).
    """
    if not (0 <= index < _DUAL_SIZE):
        raise ValueError(
            f"index={index} out of range [0, {_DUAL_SIZE})"
        )
    a, t = divmod(index, _DUAL_TRIT81_SIDE)
    return a, t


def to_balanced_trinary(t: int) -> Tuple[int, int, int, int]:
    """Convert 81-state coordinate *t* to a 4-position balanced-trinary tuple.

    Canonical offset mapping: d_k = τ_k + 1 ∈ {0, 1, 2}
    Reconstruction:           t = Σ_{k=0}^{3} d_k · 3^k

    Parameters
    ----------
    t : int
        81-state trit value; 0 ≤ t < 81.

    Returns
    -------
    (τ₃, τ₂, τ₁, τ₀) : Tuple[int, int, int, int]
        Each τ_k ∈ {-1, 0, +1} (most-significant trit first).

    Raises
    ------
    ValueError
        If *t* is outside [0, 81).
    """
    if not (0 <= t < _DUAL_TRIT81_SIDE):
        raise ValueError(f"t={t} out of range [0, {_DUAL_TRIT81_SIDE})")

    # Canonical formula: d_k ∈ {0,1,2}, τ_k = d_k - 1
    d: List[int] = []
    remainder = t
    for _ in range(4):
        remainder, d_k = divmod(remainder, 3)
        d.append(d_k)
    # d = [d₀, d₁, d₂, d₃]  (least-significant first)

    tau = [d_k - 1 for d_k in d]  # τ_k = d_k - 1 ∈ {-1, 0, +1}

    # Return most-significant first: (τ₃, τ₂, τ₁, τ₀)
    return tau[3], tau[2], tau[1], tau[0]


def from_balanced_trinary(tau3: int, tau2: int, tau1: int, tau0: int) -> int:
    """Invert :func:`to_balanced_trinary`: reconstruct *t* from τ tuple.

    Parameters
    ----------
    tau3, tau2, tau1, tau0 : int
        Balanced-trinary digits, each ∈ {-1, 0, +1}, most-significant first.

    Returns
    -------
    int
        Original 81-state coordinate *t* with 0 ≤ t < 81.

    Raises
    ------
    ValueError
        If any trit is outside {-1, 0, +1} or the reconstructed *t* is
        outside [0, 81).
    """
    taus = (tau3, tau2, tau1, tau0)
    for k, tau in enumerate(taus):
        if tau not in (-1, 0, 1):
            raise ValueError(f"τ[{k}]={tau} not in {{-1, 0, +1}}")
    # Reconstruct: t = Σ d_k · 3^k  where d_k = τ_k + 1
    # taus is (τ₃, τ₂, τ₁, τ₀) — reverse to get (τ₀, τ₁, τ₂, τ₃)
    t = sum((tau + 1) * (3 ** k) for k, tau in enumerate(reversed(taus)))
    if not (0 <= t < _DUAL_TRIT81_SIDE):
        raise ValueError(
            f"Reconstructed t={t} out of range [0, {_DUAL_TRIT81_SIDE}); "
            f"input taus={taus}"
        )
    return t


# ---------------------------------------------------------------------------
# 4. Reciprocal Closure Test
# ---------------------------------------------------------------------------

def test_reciprocal_closure() -> bool:
    """Verify that (81/64) × (64/81) == 1 using exact rational arithmetic.

    Uses :mod:`fractions.Fraction` exclusively; no float arithmetic.

    Returns
    -------
    bool
        True iff the product equals exactly 1.

    Raises
    ------
    AssertionError
        If the exact rational product is not 1 (hard failure).
    """
    x = fractions.Fraction(81, 64)
    y = fractions.Fraction(64, 81)
    product = x * y
    expected = fractions.Fraction(1)
    assert product == expected, (
        f"Reciprocal closure FAILED: {x} × {y} = {product} ≠ {expected}"
    )
    print(
        f"[PASS] reciprocal_closure: "
        f"Fraction(81,64) × Fraction(64,81) = {product} == 1  (exact)"
    )
    return True


# ---------------------------------------------------------------------------
# 5. Experiment Test Harness Stubs  (A – H)
# ---------------------------------------------------------------------------

def experiment_a_boundary_replay(
    snapshot_path: Optional[str] = None,
    event_start: int = 65,
    event_end: int = 80,
) -> None:
    """Experiment A – Boundary replay for events 65–80 from a clean snapshot.

    Observation policy: reads the snapshot; does NOT mutate runtime state.

    Parameters
    ----------
    snapshot_path : str, optional
        Path to the serialised clean-state snapshot.  If None the experiment
        is skipped with a logged warning.
    event_start, event_end : int
        Inclusive range of event indices to replay (default 65–80).
    """
    print(f"\n[EXP-A] Boundary replay  events {event_start}–{event_end}")
    if snapshot_path is None:
        print("  [SKIP] No snapshot_path provided — experiment not run.")
        return

    snapshot_file = Path(snapshot_path)
    if not snapshot_file.exists():
        print(f"  [SKIP] Snapshot file not found: {snapshot_path}")
        return

    with snapshot_file.open() as fh:
        snapshot = json.load(fh)

    print(f"  [INFO] Loaded snapshot with {len(snapshot)} top-level keys.")

    # TODO: wire up AuditedRunner or receipt-chain replay for the event window
    for seq in range(event_start, event_end + 1):
        print(f"  [STUB] Would replay event seq={seq} — not yet implemented.")

    print("[EXP-A] Stub complete — replace stubs with actual replay calls.")


def experiment_b_cache_miss_path(
    input_hash72: Optional[str] = None,
) -> None:
    """Experiment B – Force a cache-miss and observe new-record creation path."""
    print("\n[EXP-B] Cache-miss path")
    print("  [STUB] Not yet implemented.")


def experiment_c_edge_creation_audit(
    left_hash72: Optional[str] = None,
    right_hash72: Optional[str] = None,
) -> None:
    """Experiment C – Verify cross-modality edge creation is receipt-committed."""
    print("\n[EXP-C] Edge creation audit")
    print("  [STUB] Not yet implemented.")


def experiment_d_lane_hash_integrity(
    trace_jsonl_path: Optional[str] = None,
) -> None:
    """Experiment D – Verify lane_hash72 and lane_sha256 consistency in trace."""
    print("\n[EXP-D] Lane hash integrity")
    print("  [STUB] Not yet implemented.")


def experiment_e_receipt_chain_continuity(
    trace_jsonl_path: Optional[str] = None,
) -> None:
    """Experiment E – Confirm receipt_hash72 chain has no gaps or forks."""
    print("\n[EXP-E] Receipt chain continuity")
    print("  [STUB] Not yet implemented.")


def experiment_f_full_lattice_round_trip() -> bool:
    """Experiment F – Verify exact reversible correspondence across all 5 184 positions.

    Loops through all positions in both the 72×72 and 64×81 projections and
    confirms that encode∘decode and decode∘encode are perfect inverses.

    Returns
    -------
    bool
        True iff every position round-trips correctly in both projections.

    Raises
    ------
    AssertionError
        On the first round-trip mismatch found.
    """
    print("\n[EXP-F] Full-lattice round-trip  (5 184 positions × 2 projections)")

    # --- 72×72 projection ---
    failures_72sq: List[str] = []
    for index in range(_LATTICE_72SQ_SIZE):
        u, v = hash72sq_decode(index)
        reconstructed = hash72sq_encode(u, v)
        if reconstructed != index:
            failures_72sq.append(
                f"72sq index={index}: decode→({u},{v}) re-encode={reconstructed}"
            )

    for u in range(_LATTICE_72_SIDE):
        for v in range(_LATTICE_72_SIDE):
            index = hash72sq_encode(u, v)
            ru, rv = hash72sq_decode(index)
            if (ru, rv) != (u, v):
                failures_72sq.append(
                    f"72sq ({u},{v}): encode={index} decode→({ru},{rv})"
                )

    if failures_72sq:
        for msg in failures_72sq[:10]:
            print(f"  [FAIL] {msg}")
        raise AssertionError(
            f"72sq round-trip FAILED with {len(failures_72sq)} error(s)"
        )
    print(f"  [PASS] 72×72 lattice: all {_LATTICE_72SQ_SIZE} positions round-trip correctly.")

    # --- 64×81 dual-radix projection ---
    failures_dual: List[str] = []
    for index in range(_DUAL_SIZE):
        a, t = dual_radix_decode(index)
        reconstructed = dual_radix_encode(a, t)
        if reconstructed != index:
            failures_dual.append(
                f"dual index={index}: decode→({a},{t}) re-encode={reconstructed}"
            )

    for a in range(_DUAL_BASE64_SIDE):
        for t in range(_DUAL_TRIT81_SIDE):
            index = dual_radix_encode(a, t)
            ra, rt = dual_radix_decode(index)
            if (ra, rt) != (a, t):
                failures_dual.append(
                    f"dual ({a},{t}): encode={index} decode→({ra},{rt})"
                )

    if failures_dual:
        for msg in failures_dual[:10]:
            print(f"  [FAIL] {msg}")
        raise AssertionError(
            f"64×81 round-trip FAILED with {len(failures_dual)} error(s)"
        )
    print(f"  [PASS] 64×81 lattice: all {_DUAL_SIZE} positions round-trip correctly.")

    # --- Balanced-trinary round-trip for all t ∈ [0, 81) ---
    failures_bt: List[str] = []
    for t in range(_DUAL_TRIT81_SIDE):
        tau = to_balanced_trinary(t)
        rt = from_balanced_trinary(*tau)
        if rt != t:
            failures_bt.append(
                f"balanced_trinary t={t}: encode→{tau} decode→{rt}"
            )

    if failures_bt:
        for msg in failures_bt[:10]:
            print(f"  [FAIL] {msg}")
        raise AssertionError(
            f"balanced-trinary round-trip FAILED with {len(failures_bt)} error(s)"
        )
    print(
        f"  [PASS] balanced-trinary: all {_DUAL_TRIT81_SIDE} states "
        f"round-trip correctly."
    )

    print("[EXP-F] All round-trip checks passed.")
    return True


def experiment_g_state_basis_completeness(
    state_db_path: Optional[str] = None,
) -> None:
    """Experiment G – Confirm 72 distinct primitive states have been observed."""
    print("\n[EXP-G] State basis completeness")
    print("  [STUB] Not yet implemented.")


def experiment_h_invariant_gate_coverage(
    trace_jsonl_path: Optional[str] = None,
) -> None:
    """Experiment H – Verify drift_gate and Manifold9 are exercised for every entry."""
    print("\n[EXP-H] Invariant gate coverage")
    print("  [STUB] Not yet implemented.")


# ---------------------------------------------------------------------------
# Self-test runner
# ---------------------------------------------------------------------------

def run_all_self_tests() -> None:
    """Run all non-stub tests in this harness and print a summary."""
    passed: List[str] = []
    failed: List[str] = []

    tests = [
        ("reciprocal_closure", test_reciprocal_closure),
        ("experiment_f_full_lattice_round_trip", experiment_f_full_lattice_round_trip),
    ]

    for name, fn in tests:
        try:
            fn()
            passed.append(name)
        except Exception:
            failed.append(name)
            print(f"[FAIL] {name}")
            traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"Self-test summary: {len(passed)} passed, {len(failed)} failed")
    if failed:
        print(f"  FAILED: {failed}")
    else:
        print("  All harness self-tests PASSED.")
    print("=" * 60)


if __name__ == "__main__":
    run_all_self_tests()
    # Stub experiments (read-only, no mutations)
    experiment_a_boundary_replay()
    experiment_b_cache_miss_path()
    experiment_c_edge_creation_audit()
    experiment_d_lane_hash_integrity()
    experiment_e_receipt_chain_continuity()
    experiment_g_state_basis_completeness()
    experiment_h_invariant_gate_coverage()
