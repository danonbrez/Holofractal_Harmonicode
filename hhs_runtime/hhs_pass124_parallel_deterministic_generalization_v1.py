from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Callable, Mapping, Sequence

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass123_bounded_token_generalization_v1 import _canon

PASS_ID = "PASS_124"
CANDIDATE_SCHEMA = "HHS_PARALLEL_GENERALIZATION_CANDIDATE_V1"
LANE_SCHEMA = "HHS_DETERMINISTIC_GENERALIZATION_LANE_RECEIPT_V1"
ISOLATION_SCHEMA = "HHS_INVARIANT_ISOLATION_RECEIPT_V1"
SELECTION_SCHEMA = "HHS_OVERCONSTRAINED_PROBABILITY_SELECTION_V1"
REPLAY_SCHEMA = "HHS_PARALLEL_GENERALIZATION_REPLAY_V1"

REJECTION_CODES = {
    "REJECT_EMPTY_CANDIDATE_SET", "REJECT_CANDIDATE_ROOT_MISMATCH",
    "REJECT_NONDETERMINISTIC_LANE", "REJECT_PARALLEL_DISAGREEMENT",
    "REJECT_INSUFFICIENT_INVARIANT_WITNESSES", "REJECT_INVARIANT_DRIFT",
    "REJECT_PROBABILITY_CREATED_AUTHORITY", "REJECT_INVALID_WEIGHT",
    "REJECT_NO_ADMISSIBLE_CANDIDATE", "REJECT_SELECTION_ROOT_MISMATCH",
    "REJECT_REPLAY_MISMATCH", "REJECT_RESOURCE_BOUND",
}


class Pass124Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class ParallelGeneralizationBounds:
    max_candidates: int = 256
    max_lanes: int = 16
    max_invariants: int = 128
    min_independent_witnesses: int = 3


class ParallelDeterministicGeneralizationEngine:
    """Parallel deterministic admission with invariant isolation and probability-after-authority selection."""

    def __init__(self, bounds: ParallelGeneralizationBounds | None = None):
        self.bounds = bounds or ParallelGeneralizationBounds()
        if min(self.bounds.max_candidates, self.bounds.max_lanes, self.bounds.max_invariants, self.bounds.min_independent_witnesses) <= 0:
            raise Pass124Error("REJECT_RESOURCE_BOUND", "positive bounds required")

    def make_candidate(self, *, candidate_id: str, semantic_root_hash72: str,
                       invariant_claims: Mapping[str, Any], evidence_roots: Sequence[str],
                       utility: Fraction = Fraction(1, 1), cost: Fraction = Fraction(1, 1)) -> dict[str, Any]:
        if not semantic_root_hash72 or not evidence_roots:
            raise Pass124Error("REJECT_INSUFFICIENT_INVARIANT_WITNESSES", candidate_id)
        if len(invariant_claims) > self.bounds.max_invariants:
            raise Pass124Error("REJECT_RESOURCE_BOUND", "invariant count")
        if utility < 0 or cost <= 0:
            raise Pass124Error("REJECT_INVALID_WEIGHT", candidate_id)
        obj = {
            "schema": CANDIDATE_SCHEMA, "pass_id": PASS_ID,
            "candidate_id": str(candidate_id), "semantic_root_hash72": semantic_root_hash72,
            "invariant_claims": _canon(invariant_claims),
            "evidence_roots": sorted(set(str(x) for x in evidence_roots)),
            "utility": _canon(utility), "cost": _canon(cost),
        }
        obj["candidate_root_hash72"] = _hash("hhs_pass124_candidate_v1", obj)
        return obj

    def evaluate_parallel(self, candidates: Sequence[Mapping[str, Any]], *,
                          lane_validators: Sequence[tuple[str, Callable[[Mapping[str, Any]], Mapping[str, Any]]]]) -> dict[str, Any]:
        if not candidates:
            raise Pass124Error("REJECT_EMPTY_CANDIDATE_SET", "no candidates")
        if len(candidates) > self.bounds.max_candidates or not lane_validators or len(lane_validators) > self.bounds.max_lanes:
            raise Pass124Error("REJECT_RESOURCE_BOUND", "candidate/lane count")
        verified = [self._verify_candidate(x) for x in candidates]
        names = [x[0] for x in lane_validators]
        if len(set(names)) != len(names):
            raise Pass124Error("REJECT_NONDETERMINISTIC_LANE", "duplicate lane identity")

        def run(item: tuple[str, Callable[[Mapping[str, Any]], Mapping[str, Any]]], candidate: Mapping[str, Any]) -> dict[str, Any]:
            lane_id, validator = item
            first = _canon(validator(deepcopy(candidate)))
            second = _canon(validator(deepcopy(candidate)))
            if first != second:
                raise Pass124Error("REJECT_NONDETERMINISTIC_LANE", lane_id)
            admitted = bool(first.get("admitted", False))
            invariants = first.get("validated_invariants", {})
            if not isinstance(invariants, Mapping):
                raise Pass124Error("REJECT_INVARIANT_DRIFT", lane_id)
            receipt = {
                "schema": LANE_SCHEMA, "lane_id": lane_id,
                "candidate_root_hash72": candidate["candidate_root_hash72"],
                "admitted": admitted, "validated_invariants": _canon(invariants),
                "reason_codes": sorted(str(x) for x in first.get("reason_codes", [])),
            }
            receipt["lane_receipt_root_hash72"] = _hash("hhs_pass124_lane_v1", receipt)
            return receipt

        lane_receipts = []
        with ThreadPoolExecutor(max_workers=len(lane_validators)) as pool:
            futures = [pool.submit(run, lane, candidate) for candidate in verified for lane in lane_validators]
            for f in futures:
                lane_receipts.append(f.result())
        lane_receipts.sort(key=lambda x: (x["candidate_root_hash72"], x["lane_id"]))

        isolated = []
        for candidate in verified:
            receipts = [r for r in lane_receipts if r["candidate_root_hash72"] == candidate["candidate_root_hash72"]]
            decisions = {r["admitted"] for r in receipts}
            if len(decisions) != 1:
                raise Pass124Error("REJECT_PARALLEL_DISAGREEMENT", candidate["candidate_id"])
            common = dict(receipts[0]["validated_invariants"])
            for r in receipts[1:]:
                common = {k: v for k, v in common.items() if k in r["validated_invariants"] and r["validated_invariants"][k] == v}
            claims = candidate["invariant_claims"]
            if any(k not in common or common[k] != v for k, v in claims.items()):
                if receipts[0]["admitted"]:
                    raise Pass124Error("REJECT_INVARIANT_DRIFT", candidate["candidate_id"])
            independent = len({r["lane_id"] for r in receipts if r["admitted"]})
            admitted = receipts[0]["admitted"] and independent >= self.bounds.min_independent_witnesses
            isolation = {
                "schema": ISOLATION_SCHEMA,
                "candidate_root_hash72": candidate["candidate_root_hash72"],
                "isolated_invariants": common,
                "independent_witness_count": independent,
                "required_witness_count": self.bounds.min_independent_witnesses,
                "admitted": admitted,
                "lane_receipt_roots": [r["lane_receipt_root_hash72"] for r in receipts],
            }
            isolation["isolation_root_hash72"] = _hash("hhs_pass124_isolation_v1", isolation)
            isolated.append(isolation)

        return {"candidates": verified, "lane_receipts": lane_receipts, "isolations": isolated,
                "parallel_root_hash72": _hash("hhs_pass124_parallel_v1", {"lanes": lane_receipts, "isolations": isolated})}

    def select(self, parallel_result: Mapping[str, Any], *, entropy_seed_root_hash72: str) -> dict[str, Any]:
        candidates = {x["candidate_root_hash72"]: self._verify_candidate(x) for x in parallel_result["candidates"]}
        admissible = [x for x in parallel_result["isolations"] if x.get("admitted") is True]
        if not admissible:
            raise Pass124Error("REJECT_NO_ADMISSIBLE_CANDIDATE", "authority gate removed all candidates")
        weights = []
        for iso in admissible:
            c = candidates[iso["candidate_root_hash72"]]
            utility = Fraction(c["utility"]["numerator"], c["utility"]["denominator"])
            cost = Fraction(c["cost"]["numerator"], c["cost"]["denominator"])
            witness = Fraction(iso["independent_witness_count"], iso["required_witness_count"])
            weight = utility * witness / cost
            if weight < 0:
                raise Pass124Error("REJECT_INVALID_WEIGHT", c["candidate_id"])
            weights.append((c, iso, weight))
        positive = [x for x in weights if x[2] > 0]
        if not positive:
            raise Pass124Error("REJECT_NO_ADMISSIBLE_CANDIDATE", "zero weights")
        total = sum((x[2] for x in positive), Fraction(0, 1))
        ticket = int(_hash("hhs_pass124_ticket_v1", {"seed": entropy_seed_root_hash72, "parallel": parallel_result["parallel_root_hash72"]})[:16], 16)
        denominator = total.denominator
        scaled_total = total.numerator
        cursor = ticket % scaled_total
        selected = None
        cumulative = 0
        normalized = []
        for c, iso, w in sorted(positive, key=lambda x: x[0]["candidate_root_hash72"]):
            scaled = w.numerator * (denominator // w.denominator)
            cumulative += scaled
            normalized.append({"candidate_root_hash72": c["candidate_root_hash72"], "weight": _canon(w)})
            if selected is None and cursor < cumulative:
                selected = (c, iso)
        assert selected is not None
        c, iso = selected
        result = {
            "schema": SELECTION_SCHEMA, "parallel_root_hash72": parallel_result["parallel_root_hash72"],
            "entropy_seed_root_hash72": entropy_seed_root_hash72,
            "admissible_candidate_roots": sorted(x[0]["candidate_root_hash72"] for x in positive),
            "weights": normalized, "selected_candidate_root_hash72": c["candidate_root_hash72"],
            "selected_semantic_root_hash72": c["semantic_root_hash72"],
            "selected_isolation_root_hash72": iso["isolation_root_hash72"],
            "probability_created_authority": False,
            "selection_status": "OVERCONSTRAINED_PROBABILITY_SELECTED_ADMISSIBLE_CANDIDATE",
        }
        result["selection_root_hash72"] = _hash("hhs_pass124_selection_v1", result)
        return result

    def replay(self, parallel_result: Mapping[str, Any], entropy_seed_root_hash72: str, expected: Mapping[str, Any]) -> dict[str, Any]:
        actual = self.select(parallel_result, entropy_seed_root_hash72=entropy_seed_root_hash72)
        if actual["selection_root_hash72"] != expected.get("selection_root_hash72"):
            raise Pass124Error("REJECT_REPLAY_MISMATCH", "selection root")
        receipt = {"schema": REPLAY_SCHEMA, "selection_root_hash72": actual["selection_root_hash72"],
                   "replay_status": "PARALLEL_DETERMINISTIC_GENERALIZATION_REPLAY_VALIDATED"}
        receipt["replay_receipt_root_hash72"] = _hash("hhs_pass124_replay_v1", receipt)
        return receipt

    @staticmethod
    def _verify_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
        body = deepcopy(dict(candidate)); root = body.pop("candidate_root_hash72", None)
        if root != _hash("hhs_pass124_candidate_v1", body):
            raise Pass124Error("REJECT_CANDIDATE_ROOT_MISMATCH", str(candidate.get("candidate_id")))
        body["candidate_root_hash72"] = root
        return body


def _validator(name: str, admit: bool = True):
    def validate(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"admitted": admit, "validated_invariants": candidate["invariant_claims"], "reason_codes": [f"{name}_VALIDATED"]}
    return validate


def pass124_self_test() -> dict[str, Any]:
    e = ParallelDeterministicGeneralizationEngine()
    cs = [e.make_candidate(candidate_id=f"c{i}", semantic_root_hash72=_hash("s", i), invariant_claims={"relation":"RECIPROCAL_CLOSED","arity":2}, evidence_roots=[_hash("ev", [i,j]) for j in range(3)], utility=Fraction(i+1), cost=Fraction(1)) for i in range(3)]
    lanes = [("symbolic", _validator("symbolic")), ("runtime", _validator("runtime")), ("replay", _validator("replay"))]
    p = e.evaluate_parallel(cs, lane_validators=lanes)
    s = e.select(p, entropy_seed_root_hash72=_hash("seed", 124))
    r = e.replay(p, _hash("seed", 124), s)
    return {"ok": r["replay_status"] == "PARALLEL_DETERMINISTIC_GENERALIZATION_REPLAY_VALIDATED", "parallel_root_hash72": p["parallel_root_hash72"], "selection_root_hash72": s["selection_root_hash72"], "admissible_count": len(s["admissible_candidate_roots"])}


if __name__ == "__main__":
    import json
    print(json.dumps(pass124_self_test(), indent=2, sort_keys=True))
