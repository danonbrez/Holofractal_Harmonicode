from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass219_native_universal_constraint_v1 import (
    CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_integrated_manifold_engine_v2 import (
    verify_integrated_manifold_search,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_manifold_kernel_v1 import (
    MANIFOLD_SOURCE,
)

SCHEMA = "HHS_PASS_219_I121_5_INHERITED_MANIFOLD_AUTHORITY_V1"
CLASSIFICATION = "HHS_PASS_219_I121_5_INHERITED_MANIFOLD_VERIFIED"
DECISION = "PASS169_WHOLE_EXPRESSION_VMIR_VM81_ADMISSION_REQUIRED"

EXPECTED_AUTHORITY_PATH = [
    "PASS_189_HQLH_51648192_CONTEXTUAL_FABRIC",
    "PASS_191_EXACT_MANIFOLD_RESIDUAL_KERNEL",
    "PASS_186_X86_64_Q144_NONCOMMUTATIVE_ABI",
    "PASS_175_HASH216_VM5184_G243_HYDRATION",
    "PASS_174_SINGLETON_VM81_COMMIT_AUTHORITY",
    "HASH72_DETERMINISTIC_REPLAY",
]

EXPECTED_VISITED = 51_648_192
EXPECTED_EXACT_CHAIN_HITS = 837
EXPECTED_FRONTIER_SIZE = 16
EXPECTED_CHECKSUM = "5f89e7e466d337ed"


def presentation_normalize(source: str) -> str:
    """Normalize presentation glyph spelling only; never rewrite algebra."""
    return (
        source.replace("P³", "P^3")
        .replace("P²", "P^2")
        .replace("t³", "t^3")
        .replace("∆", "Delta")
        .replace("√", "Sqrt")
        .replace("u⁷²", "u^72")
        .replace("x²", "x^2")
    )


def _root(root: str | Path | None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected mapping evidence at {path}")
    return value


def _require_exact_context_certificates(payload: Mapping[str, Any]) -> None:
    epoch = payload.get("unified_manifold_epoch", {})
    if not isinstance(epoch, Mapping):
        raise AssertionError("Pass191 manifold epoch missing")
    certificates = epoch.get("deep_candidate_certificates", [])
    if not isinstance(certificates, list) or len(certificates) != EXPECTED_FRONTIER_SIZE:
        raise AssertionError("Pass191 retained frontier size mismatch")
    for certificate in certificates:
        if not isinstance(certificate, Mapping):
            raise AssertionError("Pass191 certificate is not a mapping")
        decision = certificate.get("chain_decision")
        if decision != {
            "proposition": "t^3-t = Delta = m^2-m",
            "scope": "EXACT_CONTEXT_CANDIDATE",
            "status": "PROVED",
        }:
            raise AssertionError("Pass191 certificate exceeded or changed its frozen proof scope")
        residuals = certificate.get("residuals", {})
        if not isinstance(residuals, Mapping):
            raise AssertionError("Pass191 residual set missing")
        if residuals.get("cubic_minus_delta") != 0 or residuals.get("delta_minus_idempotent") != 0:
            raise AssertionError("Pass191 retained exact-chain residual is nonzero")
        checks = certificate.get("checks", {})
        if not isinstance(checks, Mapping) or not checks or not all(checks.values()):
            raise AssertionError("Pass191 retained certificate checks failed")


def _require_completion_continuity(
    payload: Mapping[str, Any], completion: Mapping[str, Any]
) -> str:
    completion_core = {
        key: value
        for key, value in completion.items()
        if key != "completion_hash72"
    }
    expected_completion_hash = hash72_digest(
        {"domain": "HHS-PASS-191-UNIFIED-MANIFOLD-COMPLETION-V2"},
        completion_core,
    )
    if completion.get("completion_hash72") != expected_completion_hash:
        raise AssertionError("Pass191 completion Hash72 mismatch")
    if completion.get("integrated_manifold_search_hash72") != payload.get(
        "integrated_manifold_search_hash72"
    ):
        raise AssertionError("Pass191 completion-to-search link mismatch")
    epoch = payload.get("unified_manifold_epoch", {})
    if not isinstance(epoch, Mapping):
        raise AssertionError("Pass191 manifold epoch missing")
    if completion.get("manifold_epoch_hash72") != epoch.get("manifold_epoch_hash72"):
        raise AssertionError("Pass191 completion-to-manifold link mismatch")
    return expected_completion_hash


def verify_inherited_manifold_authority(root: str | Path | None = None) -> dict[str, Any]:
    """Bind frozen Pass191 execution evidence without manufacturing Pass169 closure.

    This adapter is read-only.  It does not evaluate a replacement equation, mint a
    canonical Hash72 receipt, mutate VM81, or promote Pass191 exact-context hits into
    a whole-expression Pass169 proof.
    """
    repo_root = _root(root)
    native_fixture = (
        repo_root
        / "contracts"
        / "pass219"
        / "PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode"
    )
    evidence_path = (
        repo_root
        / "native_projects"
        / "hhs_pass191_dyadic_quartic_phase_lattice"
        / "evidence"
        / "PASS_191_INTEGRATED_PROOF_SEARCH.json"
    )
    completion_path = (
        repo_root
        / "native_projects"
        / "hhs_pass191_dyadic_quartic_phase_lattice"
        / "evidence"
        / "PASS_191_INTEGRATED_COMPLETION_RECEIPT.json"
    )

    native_bytes = native_fixture.read_bytes()
    expected_native_bytes = MANIFOLD_SOURCE.encode("utf-8")
    if native_bytes != expected_native_bytes:
        raise AssertionError("I120 native source is not byte-identical to frozen Pass191 MANIFOLD_SOURCE")
    native_source = native_bytes.decode("utf-8")
    if presentation_normalize(native_source) != CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE.rstrip("\n"):
        raise AssertionError("presentation-only normalization does not match canonical Pass219 source")

    payload = _load_json(evidence_path)
    completion = _load_json(completion_path)
    verified = verify_integrated_manifold_search(payload)
    expected_completion_hash = _require_completion_continuity(payload, completion)

    if verified.get("ok") is not True:
        raise AssertionError("inherited Pass191 integrated verifier rejected frozen evidence")
    if verified.get("visited") != EXPECTED_VISITED:
        raise AssertionError("Pass191 visited-state count mismatch")
    if verified.get("exact_chain_hits") != EXPECTED_EXACT_CHAIN_HITS:
        raise AssertionError("Pass191 exact-context chain-hit count mismatch")
    if verified.get("frontier_size") != EXPECTED_FRONTIER_SIZE:
        raise AssertionError("Pass191 frontier-size mismatch")
    if verified.get("theorem_status") != "OBSTRUCTED":
        raise AssertionError("Pass191 theorem scope must remain formally OBSTRUCTED")
    if payload.get("authority_path") != EXPECTED_AUTHORITY_PATH:
        raise AssertionError("Pass191 authority path mismatch")

    _require_exact_context_certificates(payload)

    if completion.get("authority_path") != EXPECTED_AUTHORITY_PATH:
        raise AssertionError("Pass191 completion authority path mismatch")
    if completion.get("classification") != "HHS_PASS_191_UNIFIED_MANIFOLD_VM81_PROOF_SEARCH_EXECUTED":
        raise AssertionError("Pass191 completion classification mismatch")
    if completion.get("visited") != EXPECTED_VISITED:
        raise AssertionError("Pass191 completion visited count mismatch")
    if completion.get("exact_chain_hits") != EXPECTED_EXACT_CHAIN_HITS:
        raise AssertionError("Pass191 completion exact-chain count mismatch")
    if completion.get("frontier_size") != EXPECTED_FRONTIER_SIZE:
        raise AssertionError("Pass191 completion frontier mismatch")
    if completion.get("manifold_checksum_fnv1a64") != EXPECTED_CHECKSUM:
        raise AssertionError("Pass191 completion checksum mismatch")
    theorem = completion.get("theorem_decision", {})
    if not isinstance(theorem, Mapping) or theorem.get("status") != "OBSTRUCTED":
        raise AssertionError("Pass191 completion theorem status was broadened")

    hydration = payload.get("vm81_hash216_frontier_hydration", {})
    if not isinstance(hydration, Mapping):
        raise AssertionError("Pass191 VM81 hydration evidence missing")
    hydration_checks = hydration.get("checks", {})
    if not isinstance(hydration_checks, Mapping) or not hydration_checks or not all(hydration_checks.values()):
        raise AssertionError("Pass191 inherited VM81 hydration checks failed")
    candidate_execution = hydration.get("candidate_execution", {})
    deterministic_replay = hydration.get("deterministic_replay", {})
    runtime_status_after = hydration.get("runtime_status_after", {})
    if not isinstance(candidate_execution, Mapping) or candidate_execution.get("classification") != "HHS_PASS_175_CANDIDATES_VM81_COMMITTED":
        raise AssertionError("Pass191 candidate execution did not use frozen Pass175 VM81 authority")
    if candidate_execution.get("singleton_vm81_commit_authority") is not True:
        raise AssertionError("Pass191 candidate execution lost singleton VM81 commit authority")
    if not isinstance(deterministic_replay, Mapping) or deterministic_replay.get("classification") != "HHS_PASS_175_DETERMINISTIC_REPLAY_VERIFIED":
        raise AssertionError("Pass191 deterministic replay evidence mismatch")
    if not isinstance(runtime_status_after, Mapping) or runtime_status_after.get("hash72_commit_streams") != 1:
        raise AssertionError("Pass191 frozen execution did not retain exactly one Hash72 commit stream")

    core = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "decision": DECISION,
        "native_source_exact_pass191": True,
        "presentation_equivalent_pass219_ascii": True,
        "pass191_integrated_manifold_verified": True,
        "pass191_theorem_status": "OBSTRUCTED",
        "exact_context_chain_hits": EXPECTED_EXACT_CHAIN_HITS,
        "exact_context_frontier_size": EXPECTED_FRONTIER_SIZE,
        "contextual_states_visited": EXPECTED_VISITED,
        "pass189_contextual_fabric_bound": True,
        "pass186_ordered_noncommutative_abi_bound": True,
        "pass175_singleton_vm81_authority_bound": True,
        "hash72_deterministic_replay_bound": True,
        "pass159_vmir_effect_binding_observed": False,
        "whole_expression_semantics_resolved": False,
        "canonical_monolithic_proof": False,
        "pass169_whole_expression_admission_required": True,
        "floating_point_authority": False,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "inherited_integrated_manifold_hash72": verified["integrated_manifold_search_hash72"],
        "inherited_completion_hash72": expected_completion_hash,
        "inherited_manifold_checksum_fnv1a64": EXPECTED_CHECKSUM,
        "authority_path": EXPECTED_AUTHORITY_PATH,
    }
    return {
        **core,
        "evidence_hash72": hash72_digest(
            {"domain": "HHS-PASS-219-I121-5-INHERITED-MANIFOLD-EVIDENCE-V1"},
            core,
        ),
    }


__all__ = [
    "SCHEMA",
    "CLASSIFICATION",
    "DECISION",
    "EXPECTED_AUTHORITY_PATH",
    "presentation_normalize",
    "verify_inherited_manifold_authority",
]
