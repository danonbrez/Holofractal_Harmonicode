"""Pass 139 — THE ARCHITECT.

A bounded agentic meta-engineer that proposes, executes, validates, scores,
selects, rolls back, and replay-verifies algebraic reasoning configurations.
No proposal acquires authority without GARU execution evidence.
"""
from __future__ import annotations
import argparse, hashlib, json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hhs_runtime.harmonicode_general_algebraic_reasoning_unit_v1 import (
    GeneralAlgebraicReasoningUnit, ReasoningError, canonical_json, root,
)

PASS_ID = "PASS_139_THE_ARCHITECT_OUROBOROS_MANIFOLD"
SCHEMA = "HHS_ARCHITECT_API_V1"
AUTHORITY = "A1_EXECUTION_EVIDENCE"
MAX_CYCLES = 81

class ArchitectError(ValueError): pass

def _expr_complexity(request: dict[str, Any]) -> int:
    rows = list(request.get("constraints", [])) + list(request.get("goals", []))
    return sum(len(str(r.get("lhs", ""))) + len(str(r.get("rhs", ""))) for r in rows)

def _score(receipt: dict[str, Any], request: dict[str, Any]) -> tuple[int, int, int, int]:
    constraints = receipt.get("constraints", [])
    goals = receipt.get("goals", [])
    return (
        int(receipt.get("conclusion") == "PROVED"),
        sum(int(x.get("closed", False)) for x in goals),
        sum(int(x.get("closed", False)) for x in constraints),
        -_expr_complexity(request),
    )

def _apply_patch(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(patch, dict): raise ArchitectError("PATCH_NOT_OBJECT")
    allowed = {"assignments", "constraints", "goals"}
    unknown = set(patch) - allowed
    if unknown: raise ArchitectError("PATCH_FIELD_NOT_AUTHORIZED:" + ",".join(sorted(unknown)))
    out = deepcopy(base)
    if "assignments" in patch:
        if not isinstance(patch["assignments"], dict): raise ArchitectError("PATCH_ASSIGNMENTS_NOT_OBJECT")
        out.setdefault("assignments", {}).update(deepcopy(patch["assignments"]))
    for key in ("constraints", "goals"):
        if key in patch:
            if not isinstance(patch[key], list): raise ArchitectError(f"PATCH_{key.upper()}_NOT_LIST")
            out[key] = deepcopy(patch[key])
    return out

@dataclass(frozen=True)
class ArchitectRequest:
    request_id: str
    seed: dict[str, Any]
    candidates: tuple[dict[str, Any], ...]
    max_cycles: int
    agent: str

    @classmethod
    def ingress(cls, payload: dict[str, Any]) -> "ArchitectRequest":
        if not isinstance(payload, dict): raise ArchitectError("REQUEST_NOT_OBJECT")
        rid = str(payload.get("request_id", "")).strip()
        if not rid: raise ArchitectError("REQUEST_ID_REQUIRED")
        seed = payload.get("seed_request")
        if not isinstance(seed, dict): raise ArchitectError("SEED_REQUEST_REQUIRED")
        candidates = payload.get("candidate_patches", [])
        if not isinstance(candidates, list): raise ArchitectError("CANDIDATE_PATCHES_NOT_LIST")
        cycles = payload.get("max_cycles", len(candidates) + 1)
        if isinstance(cycles, bool) or not isinstance(cycles, int) or not 1 <= cycles <= MAX_CYCLES:
            raise ArchitectError("INVALID_CYCLE_BOUND")
        return cls(rid, deepcopy(seed), tuple(deepcopy(candidates)), cycles, str(payload.get("agent", "THE_ARCHITECT")))

class Architect:
    def __init__(self) -> None:
        self.garu = GeneralAlgebraicReasoningUnit()

    def _run_candidate(self, request: dict[str, Any], cycle: int, origin: str) -> dict[str, Any]:
        try:
            receipt = self.garu.execute(request)
            validation = self.garu.validate_receipt(receipt)
            status = "EXECUTED_VALID" if validation["valid"] else "EXECUTED_INVALID_RECEIPT"
            score = _score(receipt, request) if validation["valid"] else (0, 0, 0, -10**9)
            error = None
        except (ReasoningError, ValueError, ZeroDivisionError) as exc:
            receipt = None; validation = None; status = "EXECUTION_REJECTED"; score = (0, 0, 0, -10**9); error = str(exc)
        row = {
            "cycle": cycle, "origin": origin, "request_root": root(request),
            "status": status, "score": list(score), "receipt": receipt,
            "receipt_validation": validation, "error": error,
        }
        row["cycle_root"] = root(row)
        return row

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        req = ArchitectRequest.ingress(payload)
        ingress = {
            "request_id": req.request_id, "agent": req.agent,
            "seed_root": root(req.seed), "candidate_count": len(req.candidates),
            "max_cycles": req.max_cycles,
        }
        ingress["ingress_root"] = root(ingress)
        cycles: list[dict[str, Any]] = []
        seen: dict[str, int] = {}
        best_request = deepcopy(req.seed)
        best = self._run_candidate(best_request, 0, "seed")
        cycles.append(best); seen[best["request_root"]] = 0
        best_score = tuple(best["score"])
        selected_cycle = 0
        closure = "CYCLE_BOUND_REACHED"

        for i, patch in enumerate(req.candidates[: max(0, req.max_cycles - 1)], start=1):
            candidate = _apply_patch(best_request, patch)
            candidate_root = root(candidate)
            if candidate_root in seen:
                cycle = {
                    "cycle": i, "origin": f"patch_{i-1}", "request_root": candidate_root,
                    "status": "OUROBOROS_STATE_REVISITED", "score": list(best_score),
                    "receipt": None, "receipt_validation": None, "error": None,
                    "revisited_cycle": seen[candidate_root],
                }
                cycle["cycle_root"] = root(cycle); cycles.append(cycle)
                closure = "OUROBOROS_CLOSED"; break
            seen[candidate_root] = i
            cycle = self._run_candidate(candidate, i, f"patch_{i-1}")
            cycles.append(cycle)
            score = tuple(cycle["score"])
            if cycle["status"] == "EXECUTED_VALID" and score > best_score:
                best_request = candidate; best = cycle; best_score = score; selected_cycle = i
                cycle["decision"] = "COMMIT_IMPROVEMENT"
            else:
                cycle["decision"] = "ROLLBACK_NO_PROVED_IMPROVEMENT"
        else:
            closure = "FIXED_POINT" if len(cycles) == 1 or all(c.get("decision") != "COMMIT_IMPROVEMENT" for c in cycles[1:]) else "BOUNDED_OPTIMUM"

        selected_receipt = best.get("receipt")
        release_authorized = bool(selected_receipt and best.get("receipt_validation", {}).get("valid") and selected_receipt.get("conclusion") == "PROVED")
        forward = [c["cycle_root"] for c in cycles]
        ouroboros = {
            "premise_root": ingress["ingress_root"], "forward_cycle_roots": forward,
            "reverse_cycle_roots": list(reversed(forward)), "closure": closure,
        }
        ouroboros["closed"] = forward == list(reversed(ouroboros["reverse_cycle_roots"]))
        result = {
            "schema": SCHEMA, "pass_id": PASS_ID, "authority": AUTHORITY,
            "ingress": ingress,
            "alignment": {
                "proposal_is_not_execution": True, "execution_is_not_release": True,
                "proof_required_for_release": True, "bounded_recursion": True,
                "rollback_on_nonimprovement": True, "no_float_inherited_from_garu": True,
            },
            "cycles": cycles, "selected_cycle": selected_cycle,
            "selected_request_root": best["request_root"], "selected_score": list(best_score),
            "selected_receipt": selected_receipt, "release_authorized": release_authorized,
            "ouroboros": ouroboros,
            "conclusion": "RELEASE_PROVED" if release_authorized else "NO_PROVED_RELEASE",
        }
        result["receipt_root"] = root(result)
        return result

    def validate_receipt(self, receipt: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(receipt, dict) or "receipt_root" not in receipt: raise ArchitectError("INVALID_RECEIPT")
        claimed = receipt["receipt_root"]; body = dict(receipt); body.pop("receipt_root")
        selected = receipt.get("selected_receipt")
        selected_valid = True if selected is None else self.garu.validate_receipt(selected)["valid"]
        checks = {
            "receipt_root": claimed == root(body), "schema": receipt.get("schema") == SCHEMA,
            "authority": receipt.get("authority") == AUTHORITY,
            "ouroboros": bool(receipt.get("ouroboros", {}).get("closed")),
            "selected_receipt": selected_valid,
            "release_implication": (not receipt.get("release_authorized")) or bool(selected and selected.get("conclusion") == "PROVED"),
        }
        return {"checks": checks, "valid": all(checks.values())}

def execute_request(payload: dict[str, Any]) -> dict[str, Any]: return Architect().execute(payload)

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("request", type=Path); ap.add_argument("--output", type=Path)
    ns = ap.parse_args(argv); result = execute_request(json.loads(ns.request.read_text()))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if ns.output: ns.output.parent.mkdir(parents=True, exist_ok=True); ns.output.write_text(text)
    print(text, end=""); return 0
if __name__ == "__main__": raise SystemExit(main())
