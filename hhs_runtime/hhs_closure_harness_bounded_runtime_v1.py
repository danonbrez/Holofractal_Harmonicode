"""
HHS Closure Harness Bounded Runtime v1
======================================

Pass 041 closure repair layer.

The system closure harness is an integration proof surface, not a long-running
ledger auditor.  Earlier passes allowed short closure runs to trigger repeated
whole-ledger recomputation against the process ledger.  That made certification
runtime proportional to accumulated validation artifacts.

This module constrains closure-harness execution to a bounded runtime envelope
and provides a compact ledger-summary verification mode for the harness path.
Full ledger verification remains available through hhs_unified_hash72_ledger_v1;
Pass 041 only prevents the closure harness from becoming an unbounded audit lane.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import GENESIS_HASH72, default_unified_ledger_path

VERSION = "PASS_041_CLOSURE_HARNESS_BOUNDED_RUNTIME_V1"
BOUNDED_RUNTIME_SCHEMA = "HHS_CLOSURE_HARNESS_BOUNDED_RUNTIME_V1"
BOUNDED_LEDGER_SCHEMA = "HHS_BOUNDED_UNIFIED_LEDGER_SUMMARY_V1"
HASH72_AUTHORITY = "HASH72_U72_C_KERNEL"
STATE_MACHINE = "u^72_hash72_multimodal_state_machine"

ADMIT_BOUNDED_CLOSURE_RUNTIME = "ADMIT_BOUNDED_CLOSURE_RUNTIME"
ADMIT_BOUNDED_LEDGER_SUMMARY = "ADMIT_BOUNDED_LEDGER_SUMMARY"
REJECT_CLOSURE_HARNESS_UNBOUNDED_CYCLES = "REJECT_CLOSURE_HARNESS_UNBOUNDED_CYCLES"
REJECT_CLOSURE_HARNESS_UNBOUNDED_STEPS = "REJECT_CLOSURE_HARNESS_UNBOUNDED_STEPS"
REJECT_CLOSURE_HARNESS_DETAILS_EXPANSION = "REJECT_CLOSURE_HARNESS_DETAILS_EXPANSION"
REJECT_CLOSURE_HARNESS_FLOAT_BUDGET = "REJECT_CLOSURE_HARNESS_FLOAT_BUDGET"
REJECT_LEDGER_SUMMARY_MISMATCH = "REJECT_LEDGER_SUMMARY_MISMATCH"

DEFAULT_MAX_CYCLES = 3
DEFAULT_MAX_STEPS = 16
DEFAULT_LEDGER_SAMPLE = 3


def _reject(status: str, reason: str, *, details: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {
        "schema": "HHS_CLOSURE_HARNESS_BOUNDED_RUNTIME_REJECTION_V1",
        "version": VERSION,
        "ok": False,
        "status": status,
        "reason": reason,
        "details": dict(details or {}),
    }


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, Mapping):
        return any(_contains_float(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_contains_float(v) for v in value)
    return False


def _hash72(label: str, value: Any) -> str:
    return make_hash72_kernel_witness(label, value, width=72).digest


@dataclass(frozen=True)
class HHSClosureHarnessBoundedBudget:
    schema: str
    version: str
    ok: bool
    status: str
    cycles: int
    max_steps: int
    include_details: bool
    max_cycles: int
    max_step_budget: int
    details_expansion_allowed: bool
    hash_authority: str
    state_machine: str
    budget_root_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_closure_harness_budget(
    *,
    cycles: int = 2,
    max_steps: int = 2,
    include_details: bool = False,
    max_cycles: int = DEFAULT_MAX_CYCLES,
    max_step_budget: int = DEFAULT_MAX_STEPS,
    details_expansion_allowed: bool = False,
) -> Dict[str, Any]:
    """Validate the closure harness cannot expand into an unbounded audit lane."""

    budget_input = {
        "cycles": cycles,
        "max_steps": max_steps,
        "include_details": include_details,
        "max_cycles": max_cycles,
        "max_step_budget": max_step_budget,
        "details_expansion_allowed": details_expansion_allowed,
    }
    if _contains_float(budget_input):
        return _reject(REJECT_CLOSURE_HARNESS_FLOAT_BUDGET, "Closure harness runtime budgets reject floats; use integer bounds.")

    cycle_count = max(1, int(cycles))
    step_count = max(1, int(max_steps))
    if cycle_count > int(max_cycles):
        return _reject(
            REJECT_CLOSURE_HARNESS_UNBOUNDED_CYCLES,
            "Closure harness cycle count exceeds the bounded certification envelope.",
            details={"cycles": cycle_count, "max_cycles": int(max_cycles)},
        )
    if step_count > int(max_step_budget):
        return _reject(
            REJECT_CLOSURE_HARNESS_UNBOUNDED_STEPS,
            "Closure harness max_steps exceeds the bounded certification envelope.",
            details={"max_steps": step_count, "max_step_budget": int(max_step_budget)},
        )
    if bool(include_details) and not bool(details_expansion_allowed):
        return _reject(
            REJECT_CLOSURE_HARNESS_DETAILS_EXPANSION,
            "Closure harness detail expansion is disabled in bounded certification mode.",
        )

    core = {
        "schema": BOUNDED_RUNTIME_SCHEMA,
        "version": VERSION,
        "cycles": cycle_count,
        "max_steps": step_count,
        "include_details": bool(include_details),
        "max_cycles": int(max_cycles),
        "max_step_budget": int(max_step_budget),
        "details_expansion_allowed": bool(details_expansion_allowed),
        "hash_authority": HASH72_AUTHORITY,
        "state_machine": STATE_MACHINE,
    }
    budget = HHSClosureHarnessBoundedBudget(
        schema=BOUNDED_RUNTIME_SCHEMA,
        version=VERSION,
        ok=True,
        status=ADMIT_BOUNDED_CLOSURE_RUNTIME,
        cycles=cycle_count,
        max_steps=step_count,
        include_details=bool(include_details),
        max_cycles=int(max_cycles),
        max_step_budget=int(max_step_budget),
        details_expansion_allowed=bool(details_expansion_allowed),
        hash_authority=HASH72_AUTHORITY,
        state_machine=STATE_MACHINE,
        budget_root_hash72=_hash72("HHS_CLOSURE_HARNESS_BOUNDED_BUDGET_V1", core),
    ).to_dict()
    budget["kernel_witness"] = make_hash72_kernel_witness("HHS_CLOSURE_HARNESS_BOUNDED_RUNTIME_V1", budget, width=72).to_dict()
    return budget


def _load_ledger(path: str | Path | None = None) -> Dict[str, Any]:
    p = Path(path) if path is not None else default_unified_ledger_path()
    if not p.exists():
        return {
            "schema": "HHS_UNIFIED_HASH72_LEDGER_V1",
            "entries": [],
            "entry_count": 0,
            "tip_hash72": GENESIS_HASH72,
            "ledger_hash72": "",
            "hash72_authority": "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1",
        }
    return json.loads(p.read_text(encoding="utf-8"))


def bounded_verify_unified_ledger(
    ledger_path: str | Path | None = None,
    *,
    sample_edges: int = DEFAULT_LEDGER_SAMPLE,
) -> Dict[str, Any]:
    """Return a compact ledger consistency summary without full-chain recomputation.

    The closure harness uses this bounded summary so certification runtime is not
    proportional to the accumulated unified ledger.  It verifies structural edge
    consistency and hashes only a compact projection of ledger entry hashes.
    """

    p = Path(ledger_path) if ledger_path is not None else default_unified_ledger_path()
    data = _load_ledger(p)
    entries = list(data.get("entries", []))
    entry_count = len(entries)
    declared_count = int(data.get("entry_count", entry_count) or 0)
    sample_n = max(1, int(sample_edges))
    first = entries[:sample_n]
    last = entries[-sample_n:] if entries else []
    invalid = []
    if declared_count != entry_count:
        invalid.append({"reason": "entry_count mismatch", "declared": declared_count, "actual": entry_count})
    if entries:
        if entries[0].get("parent_hash72") != GENESIS_HASH72:
            invalid.append({"reason": "genesis parent mismatch", "actual": entries[0].get("parent_hash72")})
        if data.get("tip_hash72") != entries[-1].get("entry_hash72"):
            invalid.append({"reason": "tip hash does not match final entry", "tip": data.get("tip_hash72"), "final_entry": entries[-1].get("entry_hash72")})
        for local_index, entry in enumerate(last):
            absolute_index = entry_count - len(last) + local_index
            if absolute_index > 0:
                expected_parent = entries[absolute_index - 1].get("entry_hash72")
                if entry.get("parent_hash72") != expected_parent:
                    invalid.append({"reason": "sampled parent link mismatch", "index": absolute_index})
    elif data.get("tip_hash72", GENESIS_HASH72) != GENESIS_HASH72:
        invalid.append({"reason": "empty ledger has non-genesis tip", "tip": data.get("tip_hash72")})

    projection = {
        "schema": BOUNDED_LEDGER_SCHEMA,
        "version": VERSION,
        "entry_count": entry_count,
        "declared_entry_count": declared_count,
        "tip_hash72": data.get("tip_hash72", GENESIS_HASH72),
        "ledger_hash72": data.get("ledger_hash72", ""),
        "hash72_authority": data.get("hash72_authority", "LEGACY_OR_UNDECLARED"),
        "first_entry_hashes": [e.get("entry_hash72", "") for e in first],
        "last_entry_hashes": [e.get("entry_hash72", "") for e in last],
        "verification_mode": "bounded_edge_summary_not_full_recompute",
        "full_verification_deferred_to": "hhs_unified_hash72_ledger_v1.verify_unified_ledger",
        "state_machine": STATE_MACHINE,
        "hash_authority": HASH72_AUTHORITY,
    }
    summary_root = _hash72("HHS_BOUNDED_UNIFIED_LEDGER_SUMMARY_V1", projection)
    return {
        **projection,
        "ok": len(invalid) == 0,
        "status": ADMIT_BOUNDED_LEDGER_SUMMARY if not invalid else REJECT_LEDGER_SUMMARY_MISMATCH,
        "invalid": invalid,
        "ledger_path": str(p),
        "summary_root_hash72": summary_root,
        "kernel_witness": make_hash72_kernel_witness("HHS_BOUNDED_UNIFIED_LEDGER_SUMMARY_V1", {**projection, "summary_root_hash72": summary_root}, width=72).to_dict(),
    }


def closure_harness_bounded_runtime_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload = dict(payload or {})
    admitted = validate_closure_harness_budget(cycles=int(payload.get("cycles", 2)), max_steps=int(payload.get("max_steps", 2)))
    too_many_cycles = validate_closure_harness_budget(cycles=DEFAULT_MAX_CYCLES + 1, max_steps=2)
    too_many_steps = validate_closure_harness_budget(cycles=1, max_steps=DEFAULT_MAX_STEPS + 1)
    detail_rejection = validate_closure_harness_budget(cycles=1, max_steps=1, include_details=True)
    ledger = bounded_verify_unified_ledger()
    ok = bool(
        admitted.get("status") == ADMIT_BOUNDED_CLOSURE_RUNTIME
        and too_many_cycles.get("status") == REJECT_CLOSURE_HARNESS_UNBOUNDED_CYCLES
        and too_many_steps.get("status") == REJECT_CLOSURE_HARNESS_UNBOUNDED_STEPS
        and detail_rejection.get("status") == REJECT_CLOSURE_HARNESS_DETAILS_EXPANSION
        and ledger.get("ok") is True
    )
    return {
        "schema": "HHS_CLOSURE_HARNESS_BOUNDED_RUNTIME_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "admitted_status": admitted.get("status"),
        "cycle_rejection_status": too_many_cycles.get("status"),
        "step_rejection_status": too_many_steps.get("status"),
        "detail_rejection_status": detail_rejection.get("status"),
        "bounded_ledger_status": ledger.get("status"),
        "bounded_ledger_ok": ledger.get("ok"),
        "budget_root_hash72": admitted.get("budget_root_hash72"),
        "ledger_summary_root_hash72": ledger.get("summary_root_hash72"),
        "state_machine": STATE_MACHINE,
    }


if __name__ == "__main__":
    print(json.dumps(closure_harness_bounded_runtime_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
