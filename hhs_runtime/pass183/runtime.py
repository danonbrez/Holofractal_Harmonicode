"""Receipt-producing Pass 183 probability hydration runtime."""
from __future__ import annotations

from dataclasses import asdict
from fractions import Fraction
from hashlib import sha256
from math import gcd
import json
from typing import Any, Mapping

from .core import (
    ADAPTER_EQUATIONS, CANONICAL_FORMULA, CONTRACT_ID, FACTORIAL_72,
    FORWARD_LANE_TOKEN, GLOBAL_MODULUS, RECIPROCAL_LANE_TOKEN,
    RUNTIME_VERSION, ZERO_SHA256, Pass183Error, _canonical, _check_source,
    _fraction_string, _hash216, _hash72, _require_equation, build_membrane_tree,
)
from .adapters import _DrawStream, _evaluate_adapter, _seed_bytes, apply_outer_modulus
from .authority import Authority, EvaluationRecord, ProbabilityVM81Authority


class ProbabilityHydrationRuntime:
    """Exact, bounded, receipt-producing Pass 183 runtime."""

    def __init__(self, *, authority: Authority | ProbabilityVM81Authority | None = None) -> None:
        self.authority = authority if isinstance(authority, ProbabilityVM81Authority) else ProbabilityVM81Authority(authority)
        self._records: list[EvaluationRecord] = []
        self._receipt_head = ZERO_SHA256

    @staticmethod
    def status() -> dict[str, Any]:
        return {
            "classification": "HHS_PASS_183_PROBABILITY_HYDRATION_RUNTIME_IMPLEMENTED",
            "contract": CONTRACT_ID,
            "runtime_version": RUNTIME_VERSION,
            "canonical_formula": CANONICAL_FORMULA,
            "forward_lane_token": FORWARD_LANE_TOKEN,
            "reciprocal_lane_token": RECIPROCAL_LANE_TOKEN,
            "factorial72_digits": len(str(FACTORIAL_72)),
            "global_modulus": GLOBAL_MODULUS,
            "factorial72_modulus_gcd": gcd(FACTORIAL_72, GLOBAL_MODULUS),
            "local_factorial_modular_inverse_available": False,
            "required_adapters": sorted(ADAPTER_EQUATIONS),
            "canonical_numeric_authority": "EXACT_INTEGER_RATIONAL_SYMBOLIC_TYPED_RESIDUE",
            "float_authority": False,
            "singleton_vm81_authority": True,
        }

    def inspect(self, *, adapter: str, equation: str) -> dict[str, Any]:
        _require_equation(adapter, equation)
        raw = _check_source(equation)
        membranes = build_membrane_tree(equation)
        return {
            "classification": "P183_OK",
            "adapter": adapter,
            "equation": equation,
            "equation_sha256": sha256(raw).hexdigest(),
            "membranes": [asdict(record) for record in membranes],
            "membrane_count": len(membranes),
            "lexical_identity_preserved": True,
        }

    def _evaluate(
        self,
        *,
        adapter: str,
        equation: str,
        manifest: Mapping[str, Any],
        seed_class: str,
        seed: Any,
        hash72_clock: str,
        modulus: int,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        _require_equation(adapter, equation)
        equation_bytes = _check_source(equation)
        membranes = build_membrane_tree(equation)
        source_identity = sha256(b"P183-SOURCE\0" + equation_bytes + _canonical(manifest)).hexdigest()

        stochastic = adapter in {"weighted_choice", "monte_carlo_control"}
        stream: _DrawStream | None = None
        randomness: dict[str, Any]
        if stochastic:
            resolved_seed, randomness = _seed_bytes(
                seed_class,
                seed,
                content_identity=source_identity,
                hash72_clock=hash72_clock,
            )
            stream = _DrawStream(resolved_seed)
        else:
            if seed_class not in {"DETERMINISTIC_ENUMERATION", "CONTENT_ADDRESSED_SEED"}:
                raise Pass183Error("P183_REJECT_RANDOMNESS_MANIFEST", "nonstochastic_seed_class")
            randomness = {
                "seed_class": "DETERMINISTIC_ENUMERATION",
                "seed_bytes_hex": b"P183-NONSTOCHASTIC".hex(),
                "generator_identity": "NONE_EXACT_ENUMERATION",
                "generator_version": 1,
            }

        evaluated = _evaluate_adapter(adapter, manifest, stream=stream)
        if evaluated.left != evaluated.right:
            raise Pass183Error(
                "P183_REJECT_EQUATION_FALSE",
                f"{_fraction_string(evaluated.left)}!={_fraction_string(evaluated.right)}",
            )

        randomness.update(
            {
                "draw_count": stream.counter if stream else 0,
                "draw_order_sha256": sha256(
                    b"".join(bytes.fromhex(item) for item in (stream.draw_order if stream else []))
                ).hexdigest(),
                "draw_order": list(stream.draw_order if stream else []),
                "rejection_sampling_count": stream.rejection_count if stream else 0,
                "termination_state": "CLOSED",
            }
        )

        x, y = evaluated.left, evaluated.right
        forward = (x * FACTORIAL_72, y / FACTORIAL_72)
        reciprocal = (y / FACTORIAL_72, x * FACTORIAL_72)
        lane_recovery = {
            "forward_lane_0_div_factorial72": forward[0] / FACTORIAL_72 == x,
            "forward_lane_1_mul_factorial72": forward[1] * FACTORIAL_72 == y,
            "reciprocal_lane_0_mul_factorial72": reciprocal[0] * FACTORIAL_72 == y,
            "reciprocal_lane_1_div_factorial72": reciprocal[1] / FACTORIAL_72 == x,
        }
        if not all(lane_recovery.values()):
            raise Pass183Error("P183_REJECT_FACTORIAL_LANE")

        zero_bypass = x * y == 0
        if zero_bypass:
            closure = Fraction(0, 1)
            closure_classification = "P183_ZERO_BYPASS"
            reciprocal_transport = None
        else:
            reciprocal_transport = Fraction(1, 1) / evaluated.result if evaluated.result != 0 else None
            closure = (x * y) / (x * y)
            if closure != 1:
                raise Pass183Error("P183_REJECT_RECIPROCAL_CONSTRUCTION")
            closure_classification = "P183_OK"

        residue = apply_outer_modulus(closure, modulus)
        payload = {
            "schema": "P183_EXACT_PROBABILITY_EVALUATION_V1",
            "contract": CONTRACT_ID,
            "runtime_version": RUNTIME_VERSION,
            "adapter": adapter,
            "equation": equation,
            "equation_sha256": sha256(equation_bytes).hexdigest(),
            "manifest": json.loads(_canonical(manifest)),
            "source_identity_sha256": source_identity,
            "canonical_formula": CANONICAL_FORMULA,
            "canonical_formula_sha256": sha256(CANONICAL_FORMULA.encode("ascii")).hexdigest(),
            "forward_lane_token": FORWARD_LANE_TOKEN,
            "reciprocal_lane_token": RECIPROCAL_LANE_TOKEN,
            "membranes": [asdict(record) for record in membranes],
            "probability_domain_valid": True,
            "source_equation_true": True,
            "left_exact": _fraction_string(evaluated.left),
            "right_exact": _fraction_string(evaluated.right),
            "result_exact": _fraction_string(evaluated.result),
            "adapter_domain": dict(evaluated.domain),
            "adapter_trace": dict(evaluated.trace),
            "hydration_roles": {
                "x": _fraction_string(x),
                "y": _fraction_string(y),
                "z": _fraction_string(evaluated.result),
                "w": _fraction_string(reciprocal_transport) if reciprocal_transport is not None else None,
                "u72": "1",
            },
            "forward_lane_exact": [_fraction_string(item) for item in forward],
            "reciprocal_lane_exact": [_fraction_string(item) for item in reciprocal],
            "lane_recovery": lane_recovery,
            "factorial72_exact": str(FACTORIAL_72),
            "factorial72_modulus_gcd": gcd(FACTORIAL_72, GLOBAL_MODULUS),
            "local_factorial_modular_inverse_attempted": False,
            "typed_zero_bypass": zero_bypass,
            "closure_classification": closure_classification,
            "closure_exact": _fraction_string(closure),
            "u72_closure_valid": True,
            "outer_modulus": residue,
            "randomness_manifest": randomness,
            "global_modulus_applied_after_closure": True,
            "membrane_interiors_reduced": False,
        }
        identity = _hash216(payload, equation_bytes)
        payload["hash216"] = identity
        payload["evaluation_identity_sha256"] = sha256(
            b"P183-EVALUATION\0" + bytes.fromhex(identity["logical_identity_sha256"]) + _canonical(payload)
        ).hexdigest()
        request = {
            "adapter": adapter,
            "equation": equation,
            "manifest": json.loads(_canonical(manifest)),
            "seed_class": randomness["seed_class"],
            "resolved_seed_hex": randomness["seed_bytes_hex"],
            "hash72_clock": hash72_clock,
            "modulus": modulus,
        }
        return payload, request

    def execute(
        self,
        *,
        adapter: str,
        equation: str,
        manifest: Mapping[str, Any],
        seed_class: str = "DETERMINISTIC_ENUMERATION",
        seed: Any = None,
        modulus: int = GLOBAL_MODULUS,
        commit: bool = True,
    ) -> dict[str, Any]:
        evaluated, request = self._evaluate(
            adapter=adapter,
            equation=equation,
            manifest=manifest,
            seed_class=seed_class,
            seed=seed,
            hash72_clock=self._receipt_head,
            modulus=modulus,
        )
        if not commit:
            return evaluated

        authority_receipt = self.authority.commit(
            operation_identity=evaluated["evaluation_identity_sha256"],
            hash216_identity=evaluated["hash216"]["logical_identity_sha256"],
            exact_result=Fraction(evaluated["closure_exact"]),
        )
        receipt_payload = {
            "schema": "P183_PROBABILITY_HYDRATION_RECEIPT_V1",
            "sequence": len(self._records),
            "prior_receipt_sha256": self._receipt_head,
            "evaluation_identity_sha256": evaluated["evaluation_identity_sha256"],
            "hash216_identity_sha256": evaluated["hash216"]["logical_identity_sha256"],
            "authority_receipt_sha256": authority_receipt["receipt_sha256"],
            "classification": (
                "HHS_PASS_183_TYPED_ZERO_BYPASS_VERIFIED"
                if evaluated["typed_zero_bypass"]
                else "HHS_PASS_183_PROBABILITY_HYDRATION_ADMITTED"
            ),
        }
        receipt_hash72 = _hash72(receipt_payload, _canonical(evaluated))
        receipt = {
            **receipt_payload,
            "receipt_hash72": receipt_hash72,
            "receipt_sha256": sha256(
                b"P183-RECEIPT\0" + receipt_hash72.encode("ascii") + _canonical(receipt_payload)
            ).hexdigest(),
        }
        self._receipt_head = receipt["receipt_sha256"]
        self._records.append(EvaluationRecord(request, evaluated, receipt, authority_receipt))
        return {
            "classification": receipt_payload["classification"],
            "evaluation": evaluated,
            "receipt": receipt,
            "authority_receipt": authority_receipt,
        }

    def replay(self) -> dict[str, Any]:
        prior = ZERO_SHA256
        replayed: list[str] = []
        for index, record in enumerate(self._records):
            if record.receipt["sequence"] != index or record.receipt["prior_receipt_sha256"] != prior:
                raise Pass183Error("P183_REJECT_RECEIPT", f"sequence:{index}")
            request = record.request
            replay_evaluation, _ = self._evaluate(
                adapter=str(request["adapter"]),
                equation=str(request["equation"]),
                manifest=dict(request["manifest"]),
                seed_class=str(request["seed_class"]),
                seed=str(request["resolved_seed_hex"]),
                hash72_clock=str(request["hash72_clock"]),
                modulus=int(request["modulus"]),
            )
            if replay_evaluation["evaluation_identity_sha256"] != record.evaluation["evaluation_identity_sha256"]:
                raise Pass183Error("P183_REJECT_REPLAY", f"evaluation:{index}")
            body = {key: value for key, value in record.receipt.items() if key not in {"receipt_hash72", "receipt_sha256"}}
            expected_hash72 = _hash72(body, _canonical(record.evaluation))
            expected_sha = sha256(
                b"P183-RECEIPT\0" + expected_hash72.encode("ascii") + _canonical(body)
            ).hexdigest()
            if expected_hash72 != record.receipt["receipt_hash72"] or expected_sha != record.receipt["receipt_sha256"]:
                raise Pass183Error("P183_REJECT_RECEIPT", f"digest:{index}")
            prior = str(record.receipt["receipt_sha256"])
            replayed.append(replay_evaluation["evaluation_identity_sha256"])
        authority_replay = self.authority.replay()
        root = sha256(b"P183-REPLAY\0" + b"".join(bytes.fromhex(item) for item in replayed)).hexdigest()
        return {
            "classification": "HHS_PASS_183_DETERMINISTIC_REPLAY_VERIFIED",
            "records": len(self._records),
            "receipt_chain_valid": True,
            "final_receipt_sha256": prior,
            "replay_root_sha256": root,
            "authority_replay": authority_replay,
        }

    def records(self) -> tuple[dict[str, Any], ...]:
        return tuple(
            {
                "request": dict(record.request),
                "evaluation": dict(record.evaluation),
                "receipt": dict(record.receipt),
                "authority_receipt": dict(record.authority_receipt),
            }
            for record in self._records
        )
