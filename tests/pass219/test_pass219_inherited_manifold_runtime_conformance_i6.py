from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hhs_runtime.pass219_native_universal_constraint_v1 import (
    CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_integrated_manifold_engine_v2 import (
    verify_integrated_manifold_search,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_manifold_kernel_v1 import (
    MANIFOLD_SOURCE,
    lo_shu_manifold_reduction,
)

ROOT = Path(__file__).resolve().parents[2]
PASS191_EVIDENCE = (
    ROOT
    / "native_projects"
    / "hhs_pass191_dyadic_quartic_phase_lattice"
    / "evidence"
    / "PASS_191_INTEGRATED_PROOF_SEARCH.json"
)
PASS191_COMPLETION = (
    ROOT
    / "native_projects"
    / "hhs_pass191_dyadic_quartic_phase_lattice"
    / "evidence"
    / "PASS_191_INTEGRATED_COMPLETION_RECEIPT.json"
)

EXPECTED_AUTHORITY_PATH = [
    "PASS_189_HQLH_51648192_CONTEXTUAL_FABRIC",
    "PASS_191_EXACT_MANIFOLD_RESIDUAL_KERNEL",
    "PASS_186_X86_64_Q144_NONCOMMUTATIVE_ABI",
    "PASS_175_HASH216_VM5184_G243_HYDRATION",
    "PASS_174_SINGLETON_VM81_COMMIT_AUTHORITY",
    "HASH72_DETERMINISTIC_REPLAY",
]


def _presentation_normalize(source: str) -> str:
    """Normalize source glyph spelling only; never rewrite the algebra."""
    return (
        source.replace("P³", "P^3")
        .replace("P²", "P^2")
        .replace("t³", "t^3")
        .replace("∆", "Delta")
        .replace("√", "Sqrt")
        .replace("u⁷²", "u^72")
        .replace("x²", "x^2")
    )


def _load_evidence() -> dict:
    return json.loads(PASS191_EVIDENCE.read_text(encoding="utf-8"))


def test_pass219_equation_is_existing_pass191_manifold_source() -> None:
    assert _presentation_normalize(MANIFOLD_SOURCE) == (
        CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE.rstrip("\n")
    )


def test_existing_pass191_lo_shu_reduction_is_exact() -> None:
    reduction = lo_shu_manifold_reduction()
    assert reduction["matrix"] == [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    assert all(reduction["checks"].values())


def test_existing_pass191_full_manifold_evidence_replays() -> None:
    payload = _load_evidence()
    verified = verify_integrated_manifold_search(payload)

    assert verified["ok"] is True
    assert verified["classification"] == "HHS_PASS_191_UNIFIED_MANIFOLD_VM81_PROOF_SEARCH_EXECUTED"
    assert verified["contextual_cardinality"] == 51_648_192
    assert verified["visited"] == 51_648_192
    assert verified["exact_chain_hits"] == 837
    assert verified["frontier_size"] == 16
    assert payload["authority_path"] == EXPECTED_AUTHORITY_PATH


def test_existing_frontier_reaches_only_inherited_singleton_vm81_authority() -> None:
    payload = _load_evidence()
    hydration = payload["vm81_hash216_frontier_hydration"]

    assert all(hydration["checks"].values())
    assert hydration["candidate_execution"]["classification"] == "HHS_PASS_175_CANDIDATES_VM81_COMMITTED"
    assert hydration["candidate_execution"]["singleton_vm81_commit_authority"] is True
    assert hydration["deterministic_replay"]["classification"] == "HHS_PASS_175_DETERMINISTIC_REPLAY_VERIFIED"
    assert hydration["runtime_status_after"]["hash72_commit_streams"] == 1


def test_retained_candidates_are_existing_exact_chain_certificates() -> None:
    payload = _load_evidence()
    certificates = payload["unified_manifold_epoch"]["deep_candidate_certificates"]

    assert len(certificates) == 16
    for certificate in certificates:
        assert certificate["chain_decision"] == {
            "proposition": "t^3-t = Delta = m^2-m",
            "scope": "EXACT_CONTEXT_CANDIDATE",
            "status": "PROVED",
        }
        assert certificate["residuals"]["cubic_minus_delta"] == 0
        assert certificate["residuals"]["delta_minus_idempotent"] == 0
        assert all(certificate["checks"].values())


def test_frozen_completion_receipt_closes_to_existing_kernel_path() -> None:
    receipt = json.loads(PASS191_COMPLETION.read_text(encoding="utf-8"))

    assert receipt["classification"] == "HHS_PASS_191_UNIFIED_MANIFOLD_VM81_PROOF_SEARCH_EXECUTED"
    assert receipt["authority_path"] == EXPECTED_AUTHORITY_PATH
    assert receipt["contextual_cardinality"] == 51_648_192
    assert receipt["visited"] == 51_648_192
    assert receipt["exact_chain_hits"] == 837
    assert receipt["frontier_size"] == 16
    assert receipt["manifold_checksum_fnv1a64"] == "5f89e7e466d337ed"


def test_tampered_existing_state_fails_existing_pass191_verifier() -> None:
    payload = _load_evidence()
    tampered = copy.deepcopy(payload)
    tampered["unified_manifold_epoch"]["deep_candidate_certificates"][0]["residuals"][
        "cubic_minus_delta"
    ] = 1

    with pytest.raises(AssertionError):
        verify_integrated_manifold_search(tampered)
