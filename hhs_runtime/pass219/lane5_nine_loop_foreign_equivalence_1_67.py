"""Pass 219 Lane 5 1.67 — nine-loop foreign-to-native equivalence metadata.

This module is intentionally candidate-only. It prepares exact, typed metadata
for Lane 5 learning and deviation analysis. Native Hash216 sealing is performed
by the C++ cell-wall membrane; no Python result can mutate VM81 or mint
canonical Hash72/Hash216 authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "contracts/pass219/PASS_219_LANE5_NINE_LOOP_FOREIGN_EQUIVALENCE_1_67.json"
SCHEMA = "HHS_PASS219_LANE5_NINE_LOOP_FOREIGN_EQUIVALENCE_1_67"
HASH216_LEN = 216

_REQUIRED_COUNTS = {
    "loop_order": 9,
    "symbol_weight": 18,
    "primitive_alphabet_count": 9,
    "quintuple_coproduct_count": 424,
    "weight13_basis_dimension": 5431,
    "delta0_octuple_term_count": 295186924,
    "septuple_determining_nonzero_coefficients": 107053,
    "quintuple_rank": 400,
}


class Lane5NineLoopEquivalenceError(ValueError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Lane5NineLoopEquivalenceError(f"floating value forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    _reject_float(contract)
    if contract.get("schema") != SCHEMA:
        raise Lane5NineLoopEquivalenceError("1.67 contract schema mismatch")
    return contract


def exact_rational_residue(numerator: int, denominator: int, modulus: int) -> int:
    numerator = int(numerator)
    denominator = int(denominator)
    modulus = int(modulus)
    if denominator == 0 or modulus <= 2:
        raise Lane5NineLoopEquivalenceError("invalid exact modular-rational domain")
    try:
        inverse = pow(denominator % modulus, -1, modulus)
    except ValueError as exc:
        raise Lane5NineLoopEquivalenceError("denominator is not invertible modulo prime") from exc
    return (numerator % modulus) * inverse % modulus


def verify_contract(contract: Mapping[str, Any] | None = None) -> dict[str, Any]:
    c = dict(load_contract() if contract is None else contract)
    _reject_float(c)
    task = c["foreign_task"]
    oracle = c["exact_oracle"]
    quarantine = c["semantic_quarantine"]
    gate = c["composition_gate"]

    count_checks = {key: int(task[key]) == expected for key, expected in _REQUIRED_COUNTS.items()}
    alphabet = tuple(task["primitive_alphabet"])
    alphabet_check = (
        alphabet == ("a", "b", "c", "mu", "mv", "mw", "yu", "yv", "yw")
        and len(set(alphabet)) == 9
    )

    numerator = int(oracle["sample_rational"]["numerator"])
    denominator = int(oracle["sample_rational"]["denominator"])
    primes = tuple(int(value) for value in oracle["prime_moduli"])
    expected_residues = tuple(int(value) for value in oracle["sample_residues"])
    reconstructed = tuple(exact_rational_residue(numerator, denominator, p) for p in primes)
    oracle_check = reconstructed == expected_residues

    quarantine_check = (
        quarantine["foreign_symbol"] == "Delta=0"
        and quarantine["native_symbol"] == "Delta_e=0"
        and quarantine["foreign_type"] != quarantine["native_type"]
        and quarantine["typed_foreign_symbol_required"] is True
        and quarantine["alias_authorized"] is False
    )
    authority_check = (
        gate["candidate_only"] is True
        and gate["canonical_vm81_mutation_authority"] is False
        and gate["canonical_hash72_authority"] is False
        and gate["canonical_hash216_authority"] is False
        and gate["canonical_persistence_authority"] is False
        and oracle["floating_point_authority"] is False
    )
    route_check = tuple(task["route_witnesses"]) == (
        "form_factor_antipodal_lift",
        "direct_hexagon_bootstrap",
    )

    checks = {
        "counts_exact": all(count_checks.values()),
        "alphabet_exact": alphabet_check,
        "exact_sample_oracle": oracle_check,
        "foreign_delta_quarantined": quarantine_check,
        "dual_route_metadata_present": route_check,
        "authority_boundary_preserved": authority_check,
        "monolithic_verbatim_source_bound": (
            gate["monolithic_frozen_tex_sha256"]
            == "9f2238981bf509d22ffebb46816346f389fd2d949ccd7956cde3630ab2b56944"
        ),
    }
    if not all(checks.values()):
        failed = sorted(key for key, value in checks.items() if not value)
        raise Lane5NineLoopEquivalenceError("contract verification failed: " + ",".join(failed))

    return {
        "schema": SCHEMA + "_CONTRACT_RECEIPT",
        "checks": checks,
        "count_checks": count_checks,
        "sample_reconstructed_residues": list(reconstructed),
        "contract_sha256": hashlib.sha256(canonical_bytes(c)).hexdigest(),
        "candidate_only": True,
        "canonical_authority": False,
    }


def prediction_deviation(
    *,
    residues: Mapping[int | str, int],
    rational_numerator: int | None = None,
    rational_denominator: int | None = None,
) -> dict[str, Any]:
    contract = load_contract()
    oracle = contract["exact_oracle"]
    primes = tuple(int(value) for value in oracle["prime_moduli"])
    expected = tuple(int(value) for value in oracle["sample_residues"])
    supplied = tuple(int(residues.get(p, residues.get(str(p), -1))) for p in primes)
    residuals = tuple((actual - target) % p for actual, target, p in zip(supplied, expected, primes))
    exact_match = all(value == 0 for value in residuals)

    rational_match = None
    if rational_numerator is not None or rational_denominator is not None:
        if rational_numerator is None or rational_denominator is None:
            raise Lane5NineLoopEquivalenceError("rational witness requires numerator and denominator")
        reconstructed = tuple(
            exact_rational_residue(int(rational_numerator), int(rational_denominator), p)
            for p in primes
        )
        rational_match = reconstructed == expected
        exact_match = exact_match and rational_match

    return {
        "schema": SCHEMA + "_PREDICTION_DEVIATION",
        "prime_moduli": list(primes),
        "expected_residues": list(expected),
        "supplied_residues": list(supplied),
        "residuals": list(residuals),
        "rational_match": rational_match,
        "exact_match": exact_match,
        "trinary": 0 if exact_match else -1,
    }


def build_parallel_learning_metadata(
    prediction: Mapping[str, Any] | None = None,
    *,
    artifact_manifest_sha256: str | None = None,
) -> dict[str, Any]:
    contract = load_contract()
    verification = verify_contract(contract)
    task = contract["foreign_task"]

    source_identity = -1
    if artifact_manifest_sha256 is not None:
        digest = str(artifact_manifest_sha256).lower()
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise Lane5NineLoopEquivalenceError("artifact manifest must be a SHA-256 hex digest")
        source_identity = 0

    prediction_receipt = None
    if prediction is not None:
        prediction_receipt = prediction_deviation(
            residues=prediction["residues"],
            rational_numerator=prediction.get("rational_numerator"),
            rational_denominator=prediction.get("rational_denominator"),
        )

    model_vs_v1 = {
        "symbol_typing": 0,
        "exact_arithmetic": 0,
        "route_equivalence": 1,
        "coproduct_dag_shape": 1,
        "basis_rank": 1,
        "modular_residue_closure": (
            prediction_receipt["trinary"] if prediction_receipt is not None else 0
        ),
        "source_identity": source_identity,
        "operator_order": 0,
        "provenance": 1 if artifact_manifest_sha256 is not None else -1,
        "branch_scope": 0,
        "hash216_replay": -1,
        "canonical_authority_boundary": 0,
    }

    improved = {
        "typed_alphabet": task["primitive_alphabet"],
        "symbol_weight": task["symbol_weight"],
        "coproduct_dag": {
            "quintuple_nodes": task["quintuple_coproduct_count"],
            "weight13_basis_dimension": task["weight13_basis_dimension"],
            "quintuple_rank": task["quintuple_rank"],
        },
        "delta0_term_count": task["delta0_octuple_term_count"],
        "septuple_determining_nonzero_coefficients": task[
            "septuple_determining_nonzero_coefficients"
        ],
        "dual_route_agreement": list(task["route_witnesses"]),
        "exact_oracle": contract["exact_oracle"],
        "semantic_quarantine": contract["semantic_quarantine"],
        "parent_chain": contract["parent_chain"],
        "model_vs_harmonicode_v1": model_vs_v1,
        "prediction_receipt": prediction_receipt,
        "artifact_manifest_sha256": artifact_manifest_sha256,
    }
    payload = canonical_bytes(improved)

    return {
        "schema": SCHEMA + "_PARALLEL_LEARNING_METADATA",
        "contract_receipt": verification,
        "parallel_channels": contract["learning_metadata"]["parallel_channels"],
        "deviation_axes": contract["learning_metadata"]["deviation_axes"],
        "model_vs_harmonicode_v1": model_vs_v1,
        "improved_composition": improved,
        "candidate_payload_sha256": hashlib.sha256(payload).hexdigest(),
        "candidate_payload_utf8": payload.decode("utf-8"),
        "native_hash216_required": True,
        "hash216_replay_verified": False,
        "canonical_transition_ready": False,
        "candidate_only": True,
    }


def bind_native_hash216(
    metadata: Mapping[str, Any],
    *,
    candidate_hash216: str,
    replay_hash216: str,
    native_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    left = str(candidate_hash216)
    right = str(replay_hash216)
    if len(left) != HASH216_LEN or len(right) != HASH216_LEN:
        raise Lane5NineLoopEquivalenceError("native Hash216 must contain exactly 216 symbols")
    if left != right:
        raise Lane5NineLoopEquivalenceError("Hash216 replay mismatch")
    if str(native_receipt.get("candidate_hash216", "")) != left:
        raise Lane5NineLoopEquivalenceError("native receipt Hash216 mismatch")

    required = (
        "parent_1_66_verified",
        "monolithic_source_identity_verified",
        "foreign_delta_quarantine_verified",
        "exact_sample_oracle_verified",
        "structure_counts_verified",
        "dual_route_metadata_verified",
        "hash216_composition_validated",
        "candidate_only",
    )
    if not all(bool(native_receipt.get(key, False)) for key in required):
        raise Lane5NineLoopEquivalenceError("native cell-wall receipt is incomplete")
    for key in (
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "canonical_persistence_authority",
        "floating_point_canonical_authority",
    ):
        if bool(native_receipt.get(key, False)):
            raise Lane5NineLoopEquivalenceError(f"forbidden authority exposed: {key}")

    bound = dict(metadata)
    vector = dict(bound["model_vs_harmonicode_v1"])
    vector["hash216_replay"] = 0
    bound["model_vs_harmonicode_v1"] = vector
    bound["native_candidate_hash216"] = left
    bound["hash216_replay_verified"] = True
    bound["canonical_transition_ready"] = False
    bound["candidate_only"] = True
    return bound
