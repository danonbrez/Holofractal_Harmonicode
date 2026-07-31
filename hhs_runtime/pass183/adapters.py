"""Exact Pass 183 probability adapters and outer-modulus closure."""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from hashlib import sha256
from math import comb, factorial, gcd, lcm
from typing import Any, Iterable, Mapping, Sequence

from .core import (
    ADAPTER_EQUATIONS, ALLOWED_SEED_CLASSES, GLOBAL_MODULUS,
    MAX_MARKOV_DIMENSION, MAX_STOCHASTIC_DRAWS, Pass183Error,
    _exact_values, _fraction, _fraction_string, _probabilities, _probability,
)


@dataclass(frozen=True)
class AdapterEvaluation:
    adapter: str
    left: Fraction
    right: Fraction
    result: Fraction
    domain: Mapping[str, Any]
    trace: Mapping[str, Any] = field(default_factory=dict)


class _DrawStream:
    """Counter-mode SHA-256 draw stream with exact rejection sampling."""

    def __init__(self, seed: bytes) -> None:
        if not seed:
            raise Pass183Error("P183_REJECT_RANDOMNESS_MANIFEST", "empty_seed")
        self.seed = bytes(seed)
        self.counter = 0
        self.draw_order: list[str] = []
        self.rejection_count = 0

    def _word(self) -> int:
        digest = sha256(b"P183-DRAW\0" + self.seed + self.counter.to_bytes(16, "big")).digest()
        self.counter += 1
        self.draw_order.append(digest.hex())
        return int.from_bytes(digest, "big")

    def below(self, modulus: int) -> int:
        if not isinstance(modulus, int) or isinstance(modulus, bool) or modulus <= 0:
            raise Pass183Error("P183_REJECT_RANDOMNESS_MANIFEST", "draw_modulus")
        space = 1 << 256
        limit = space - (space % modulus)
        while True:
            if self.counter >= MAX_STOCHASTIC_DRAWS * 8:
                raise Pass183Error("P183_TIMEOUT", "rejection_sampling")
            value = self._word()
            if value < limit:
                return value % modulus
            self.rejection_count += 1


def _seed_bytes(
    seed_class: str,
    seed: Any,
    *,
    content_identity: str,
    hash72_clock: str,
) -> tuple[bytes, dict[str, Any]]:
    if seed_class not in ALLOWED_SEED_CLASSES:
        raise Pass183Error("P183_REJECT_RANDOMNESS_MANIFEST", "seed_class")
    if seed_class == "DETERMINISTIC_ENUMERATION":
        resolved = b"P183-DETERMINISTIC-ENUMERATION"
    elif seed_class == "CONTENT_ADDRESSED_SEED":
        resolved = sha256(b"P183-CONTENT-SEED\0" + content_identity.encode("ascii")).digest()
    elif seed_class == "HASH72_CLOCK_SEED":
        resolved = sha256(b"P183-HASH72-CLOCK-SEED\0" + hash72_clock.encode("ascii")).digest()
    else:
        if isinstance(seed, bytes):
            resolved = seed
        elif isinstance(seed, str):
            candidate = seed.strip()
            if not candidate:
                raise Pass183Error("P183_REJECT_RANDOMNESS_MANIFEST", "empty_seed")
            try:
                resolved = bytes.fromhex(candidate) if len(candidate) % 2 == 0 else candidate.encode("utf-8")
            except ValueError:
                resolved = candidate.encode("utf-8")
        else:
            raise Pass183Error("P183_REJECT_RANDOMNESS_MANIFEST", "seed")
    return resolved, {
        "seed_class": seed_class,
        "seed_bytes_hex": resolved.hex(),
        "generator_identity": "P183_SHA256_COUNTER_REJECTION_V1",
        "generator_version": 1,
    }


def _multinomial_normalization(probabilities: Sequence[Fraction], n: int) -> Fraction:
    if n < 0 or n > 12:
        raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", "multinomial:n")
    if not probabilities or len(probabilities) > 8:
        raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", "multinomial:categories")
    total = Fraction(0, 1)

    def compositions(remaining: int, slots: int, prefix: tuple[int, ...] = ()) -> Iterable[tuple[int, ...]]:
        if slots == 1:
            yield prefix + (remaining,)
            return
        for value in range(remaining + 1):
            yield from compositions(remaining - value, slots - 1, prefix + (value,))

    for counts in compositions(n, len(probabilities)):
        coefficient = factorial(n)
        for count in counts:
            coefficient //= factorial(count)
        term = Fraction(coefficient, 1)
        for probability, count in zip(probabilities, counts):
            term *= probability ** count
        total += term
    return total


def _evaluate_adapter(adapter: str, manifest: Mapping[str, Any], *, stream: _DrawStream | None) -> AdapterEvaluation:
    m = manifest
    if adapter == "bayes":
        p_a = _probability(m["p_a"], "p_a")
        p_b = _probability(m["p_b"], "p_b")
        p_b_given_a = _probability(m["p_b_given_a"], "p_b_given_a")
        p_a_given_b = _probability(m["p_a_given_b"], "p_a_given_b")
        if p_a == 0 or p_b == 0:
            raise Pass183Error("P183_REJECT_ZERO_DENOMINATOR", "bayes:evidence")
        left, right = p_a_given_b * p_b, p_b_given_a * p_a
        return AdapterEvaluation(adapter, left, right, p_a_given_b, {"type": "bayes"})

    if adapter == "conditional_probability":
        joint = _probability(m["p_a_and_b"], "p_a_and_b")
        p_b = _probability(m["p_b"], "p_b")
        conditional = _probability(m["p_a_given_b"], "p_a_given_b")
        if p_b == 0:
            raise Pass183Error("P183_REJECT_ZERO_DENOMINATOR", "p_b")
        return AdapterEvaluation(adapter, conditional, joint / p_b, conditional, {"type": "conditional"})

    if adapter == "independent_intersection":
        p_a = _probability(m["p_a"], "p_a")
        p_b = _probability(m["p_b"], "p_b")
        joint = _probability(m["p_a_and_b"], "p_a_and_b")
        return AdapterEvaluation(adapter, joint, p_a * p_b, joint, {"type": "independent_intersection"})

    if adapter == "general_intersection":
        conditional = _probability(m["p_a_given_b"], "p_a_given_b")
        p_b = _probability(m["p_b"], "p_b")
        joint = _probability(m["p_a_and_b"], "p_a_and_b")
        return AdapterEvaluation(adapter, joint, conditional * p_b, joint, {"type": "general_intersection"})

    if adapter == "union_inclusion_exclusion":
        p_a = _probability(m["p_a"], "p_a")
        p_b = _probability(m["p_b"], "p_b")
        intersection = _probability(m["p_intersection"], "p_intersection")
        union = _probability(m["p_union"], "p_union")
        if intersection > min(p_a, p_b):
            raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", "intersection")
        right = p_a + p_b - intersection
        if not 0 <= right <= 1:
            raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", "union")
        return AdapterEvaluation(adapter, union, right, union, {"type": "inclusion_exclusion"})

    if adapter == "total_probability":
        p_h = _probability(m["p_h"], "p_h")
        p_e_h = _probability(m["p_e_given_h"], "p_e_given_h")
        p_e_not_h = _probability(m["p_e_given_not_h"], "p_e_given_not_h")
        p_e = _probability(m["p_e"], "p_e")
        return AdapterEvaluation(adapter, p_e, p_h * p_e_h + (1 - p_h) * p_e_not_h, p_e, {"type": "total_probability"})

    if adapter in {"expectation", "variance"}:
        outcomes = _exact_values(m["outcomes"], "outcomes")
        probabilities = _probabilities(m["probabilities"], "probabilities")
        if len(outcomes) != len(probabilities):
            raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", "support_arity")
        mean = sum((outcome * probability for outcome, probability in zip(outcomes, probabilities)), Fraction(0, 1))
        if adapter == "expectation":
            expected = _fraction(m["expected"], "expected")
            return AdapterEvaluation(adapter, expected, mean, mean, {"type": "expectation", "support": len(outcomes)})
        variance = sum((((outcome - mean) ** 2) * probability for outcome, probability in zip(outcomes, probabilities)), Fraction(0, 1))
        declared_mean = _fraction(m["mean"], "mean")
        declared_variance = _fraction(m["variance"], "variance")
        if declared_mean != mean:
            return AdapterEvaluation(adapter, declared_mean, mean, variance, {"type": "variance", "mean_mismatch": True})
        return AdapterEvaluation(adapter, declared_variance, variance, variance, {"type": "variance", "support": len(outcomes)})

    if adapter == "finite_discrete_distribution":
        probabilities = _probabilities(m["probabilities"], "probabilities")
        total = sum(probabilities, Fraction(0, 1))
        return AdapterEvaluation(adapter, total, Fraction(1, 1), total, {"type": "distribution", "support": len(probabilities)})

    if adapter == "binomial":
        n = m.get("n")
        if not isinstance(n, int) or isinstance(n, bool) or not 0 <= n <= 512:
            raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", "binomial:n")
        p = _probability(m["p"], "p")
        total = sum((Fraction(comb(n, k), 1) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)), Fraction(0, 1))
        return AdapterEvaluation(adapter, total, Fraction(1, 1), total, {"type": "binomial", "n": n})

    if adapter == "multinomial":
        n = m.get("n")
        if not isinstance(n, int) or isinstance(n, bool):
            raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", "multinomial:n")
        probabilities = _probabilities(m["probabilities"], "probabilities")
        total = _multinomial_normalization(probabilities, n)
        return AdapterEvaluation(adapter, total, Fraction(1, 1), total, {"type": "multinomial", "n": n})

    if adapter == "markov_chain":
        matrix = m.get("matrix")
        if not isinstance(matrix, Sequence) or isinstance(matrix, (str, bytes, bytearray)) or not matrix:
            raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", "matrix")
        if len(matrix) > MAX_MARKOV_DIMENSION:
            raise Pass183Error("P183_TIMEOUT", "matrix_dimension")
        rows: list[tuple[Fraction, ...]] = []
        width: int | None = None
        for row_index, row in enumerate(matrix):
            parsed = _probabilities(row, f"matrix[{row_index}]")
            width = len(parsed) if width is None else width
            if len(parsed) != width:
                raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", "matrix_rectangular")
            rows.append(parsed)
        return AdapterEvaluation(adapter, Fraction(1), Fraction(1), Fraction(1), {"type": "markov_chain", "rows": len(rows), "columns": width})

    if adapter == "weighted_choice":
        weights = _probabilities(m["weights"], "weights")
        if stream is None:
            raise Pass183Error("P183_REJECT_RANDOMNESS_MANIFEST", "weighted_choice:stream")
        common = 1
        for weight in weights:
            common = lcm(common, weight.denominator)
        integers = [weight.numerator * (common // weight.denominator) for weight in weights]
        draw = stream.below(sum(integers))
        cursor = selected = 0
        for index, weight in enumerate(integers):
            cursor += weight
            if draw < cursor:
                selected = index
                break
        return AdapterEvaluation(adapter, sum(weights, Fraction(0)), Fraction(1), weights[selected], {"type": "weighted_choice", "selected_index": selected, "draw": draw, "integer_total": sum(integers)})

    if adapter == "monte_carlo_control":
        probability = _probability(m["success_probability"], "success_probability")
        sample_count = m.get("sample_count")
        if not isinstance(sample_count, int) or isinstance(sample_count, bool) or not 1 <= sample_count <= MAX_STOCHASTIC_DRAWS:
            raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", "sample_count")
        if stream is None:
            raise Pass183Error("P183_REJECT_RANDOMNESS_MANIFEST", "monte_carlo:stream")
        successes = sum(1 for _ in range(sample_count) if stream.below(probability.denominator) < probability.numerator)
        estimate = Fraction(successes, sample_count)
        declared = _fraction(m.get("declared_estimate", estimate), "declared_estimate")
        return AdapterEvaluation(adapter, declared, estimate, estimate, {"type": "monte_carlo_control", "successes": successes, "draws": sample_count, "exact_residual": _fraction_string(abs(estimate - probability))})

    raise Pass183Error("P183_REJECT_PARSE", f"unsupported_adapter:{adapter}")


def apply_outer_modulus(value: Fraction, modulus: int = GLOBAL_MODULUS) -> dict[str, Any]:
    if modulus != GLOBAL_MODULUS:
        raise Pass183Error("P183_REJECT_LOCAL_MODULAR_INVERSION", f"wrong_modulus:{modulus}")
    denominator_gcd = gcd(value.denominator, modulus)
    if denominator_gcd != 1:
        return {
            "classification": "P183_REJECT_NONINVERTIBLE_OUTER_DENOMINATOR",
            "scalar_residue_available": False,
            "numerator_mod": value.numerator % modulus,
            "denominator_mod": value.denominator % modulus,
            "denominator_gcd_with_modulus": denominator_gcd,
            "modulus": modulus,
            "exact_value": _fraction_string(value),
        }
    inverse = pow(value.denominator, -1, modulus)
    return {
        "classification": "P183_OK",
        "scalar_residue_available": True,
        "residue": (value.numerator % modulus) * inverse % modulus,
        "modulus": modulus,
        "exact_value": _fraction_string(value),
    }
