#!/usr/bin/env python3
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools" / "hhs_120ms_reciprocal_wave_series_analyze_v3.py"
STRICT_SCHEMA = "HHS_120MS_GLOBAL_RECIPROCAL_WAVE_XYZW_V3_STRICT"
STRICT_EVIDENCE_SCHEMA = "HHS_120MS_GLOBAL_RECIPROCAL_WAVE_XYZW_V3_STRICT_EVIDENCE"
GLOBAL_BUDGET_NS = 120_000_000


def _load_base():
    spec = spec_from_file_location("wave_v3_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load base reciprocal-wave analyzer")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _parse(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[int, dict[str, Any]], dict[str, Any]]:
    meta: dict[str, Any] | None = None
    records: list[dict[str, Any]] = []
    refs: dict[int, dict[str, Any]] = {}
    result: dict[str, Any] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        rec = json.loads(raw)
        kind = rec.get("type")
        if kind == "batch_meta":
            meta = rec
        elif kind == "benchmark":
            records.append(rec)
        elif kind == "sample_reference":
            refs[int(rec["sample"])] = rec
        elif kind == "invalid_trial":
            raise ValueError(f"runner emitted invalid trial: {rec.get('reason')}")
        elif kind == "batch_result":
            result = rec
    if meta is None or result is None:
        raise ValueError("missing reciprocal-wave batch metadata/result")
    return meta, records, refs, result


def _validate_strict(
    meta: dict[str, Any],
    records: list[dict[str, Any]],
    refs: dict[int, dict[str, Any]],
    result: dict[str, Any],
) -> None:
    if meta.get("schema") != STRICT_SCHEMA:
        raise ValueError("unexpected strict schema")
    if int(meta.get("global_budget_ns", 0)) != GLOBAL_BUDGET_NS:
        raise ValueError("unexpected global budget")
    if not bool(meta.get("strict_positive_residual")) or bool(meta.get("clamping_permitted")):
        raise ValueError("strict positive-residual/no-clamping contract missing")
    if result.get("result") != "PASS":
        raise ValueError("strict reciprocal-wave batch did not pass")
    if bool(result.get("invalid_trial_seen")):
        raise ValueError("invalid trial cannot enter strict evidence")
    if not bool(result.get("stopped_before_unfair_trial")):
        raise ValueError("runner did not stop before an unfair trial")

    elapsed = int(result.get("batch_elapsed_ns", 0))
    remaining = int(result.get("remaining_budget_ns", 0))
    if elapsed <= 0 or elapsed >= GLOBAL_BUDGET_NS:
        raise ValueError("global elapsed time must be strictly inside the budget")
    if remaining <= 0 or remaining != GLOBAL_BUDGET_NS - elapsed:
        raise ValueError("global residual must be exact and strictly positive")

    sample_count = int(result.get("sample_count", 0))
    if sample_count < 3:
        raise ValueError("strict wave fit requires at least three admitted samples")
    if len(records) != 4 * sample_count or set(refs) != set(range(sample_count)):
        raise ValueError("strict sample cardinality mismatch")

    grouped: dict[int, dict[str, dict[str, Any]]] = {}
    for rec in records:
        grouped.setdefault(int(rec["sample"]), {})[str(rec["id"])] = rec

    previous_scale = 0
    for i in range(sample_count):
        legs = grouped.get(i)
        if legs is None or set(legs) != {"A", "B", "C", "D"}:
            raise ValueError(f"sample {i}: missing reciprocal leg")
        ref = refs[i]
        if bool(ref.get("subthreshold")):
            raise ValueError(f"sample {i}: subthreshold trial is inadmissible")
        scale = int(ref["query_scale"])
        if i > 0 and scale != previous_scale * 2:
            raise ValueError("query gradient did not double exactly")
        previous_scale = scale

        budgets = {int(rec["leg_budget_ns"]) for rec in legs.values()}
        if len(budgets) != 1:
            raise ValueError(f"sample {i}: unequal leg budgets")
        leg_budget = next(iter(budgets))
        if leg_budget <= 0:
            raise ValueError(f"sample {i}: non-positive leg budget")

        state = None
        for ident in ("A", "B", "C", "D"):
            rec = legs[ident]
            if not bool(rec.get("dataset_complete")):
                raise ValueError(f"sample {i} {ident}: incomplete trial is inadmissible")
            completion = int(rec.get("completion_elapsed_ns", 0))
            if completion <= 0 or completion >= leg_budget:
                raise ValueError(f"sample {i} {ident}: leg residual must be strictly positive")
            current = (
                int(rec["completed_queries"]),
                int(rec["represented_transitions"]),
                int(rec["descriptor_bits"]),
                int(rec["endpoint_digest"]),
                int(rec["descriptor_digest"]),
            )
            if state is None:
                state = current
            elif current != state:
                raise ValueError(f"sample {i}: reciprocal legs did not converge to one exact state")

        ref_state = (
            int(ref["completed_queries"]),
            int(ref["represented_transitions"]),
            int(ref["descriptor_bits"]),
            int(ref["endpoint_digest"]),
            int(ref["descriptor_digest"]),
        )
        if state != ref_state:
            raise ValueError(f"sample {i}: exact reciprocal state differs from reference")


def analyze(path: Path) -> dict[str, Any]:
    base = _load_base()
    meta, records, refs, result = _parse(path)
    _validate_strict(meta, records, refs, result)

    adapted_meta = dict(meta)
    adapted_meta["schema"] = base.SCHEMA
    evidence = base.analyze(adapted_meta, records, refs, result)
    evidence["schema"] = STRICT_EVIDENCE_SCHEMA
    evidence["strict_admission"] = {
        "all_samples_four_way_complete": True,
        "all_leg_residuals_strictly_positive": True,
        "global_residual_strictly_positive": True,
        "subthreshold_trials_admitted": False,
        "incomplete_trials_admitted": False,
        "zero_residual_trials_admitted": False,
        "clamping_permitted": False,
        "stop_reason": result.get("stop_reason"),
    }
    evidence["claim_scope"]["same_exact_state_required_for_every_admitted_sample"] = True
    evidence["claim_scope"]["incomplete_boundary_samples_excluded"] = True
    evidence["claim_scope"]["supremacy_theorem_borrowed_from_v2"] = False
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("batch_ndjson", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    evidence = analyze(args.batch_ndjson)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("HHS_120MS_GLOBAL_RECIPROCAL_WAVE_XYZW_V3_STRICT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
