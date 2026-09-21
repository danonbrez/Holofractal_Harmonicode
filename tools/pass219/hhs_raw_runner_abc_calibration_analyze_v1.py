#!/usr/bin/env python3
"""Analyze Pass 219 Lane 5 A:B:C normalization against a raw workflow runner baseline."""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hhs_backend.runtime.hhs_lo_shu_harmonic_phase_energy_v1 import (  # noqa: E402
    exact_percentile_gradient,
    run_harmonic_phase_energy,
)

PHASES = ("xy", "yx", "zw", "wz")
EXPECTED_SLOTS = {
    "xy": (0, 36),
    "yx": (36, 0),
    "zw": (18, 54),
    "wz": (54, 18),
}
ARMS = ("A", "B", "C")
ENERGY_PER_TENSOR = 225
ENERGY_PER_PAIR = 450


def frac_obj(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def bp_floor(value: Fraction) -> int:
    return (value.numerator * 10_000) // value.denominator


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    if not records:
        raise SystemExit("empty benchmark record")
    return records


def verify_energy_contract() -> dict[str, Any]:
    run = run_harmonic_phase_energy()
    if not run.get("ok"):
        raise SystemExit("Pass 067.1 logical energy contract did not pass")
    gates = run["ordered_phase_gates"]
    out: dict[str, Any] = {}
    for phase in PHASES:
        gate = gates[phase]
        if not gate["continuation_admitted"]:
            raise SystemExit(f"energy gate {phase} not admitted")
        left = gate["zero_sum_closure"]["left_cluster"]
        right = gate["zero_sum_closure"]["right_cluster"]
        if (left["numerator"], left["denominator"]) != (ENERGY_PER_TENSOR, 1):
            raise SystemExit(f"energy gate {phase} left cluster changed")
        if (right["numerator"], right["denominator"]) != (ENERGY_PER_TENSOR, 1):
            raise SystemExit(f"energy gate {phase} right cluster changed")
        out[phase] = {
            "gate_root_hash72": gate["gate_root_hash72"],
            "logical_left_energy_units": ENERGY_PER_TENSOR,
            "logical_right_energy_units": ENERGY_PER_TENSOR,
            "logical_pair_energy_units": ENERGY_PER_PAIR,
            "zero_sum_closure": True,
        }
    return out


def rate(record: dict[str, Any]) -> Fraction:
    completed = int(record["completed"])
    elapsed = int(record["elapsed_ns"])
    if completed <= 0 or elapsed <= 0:
        raise SystemExit("non-positive timing sample")
    return Fraction(completed * 1_000_000_000, elapsed)


def ratio(left: dict[str, Any], right: dict[str, Any]) -> Fraction:
    return rate(left) / rate(right)


def analyze(records: list[dict[str, Any]]) -> dict[str, Any]:
    metas = [r for r in records if r.get("type") == "meta"]
    finals = [r for r in records if r.get("type") == "result"]
    arms = [r for r in records if r.get("type") == "arm"]
    if len(metas) != 1 or len(finals) != 1:
        raise SystemExit("expected one meta and one final record")
    meta, final = metas[0], finals[0]
    if final.get("result") != "PASS" or not final.get("within_time_bound"):
        raise SystemExit("native benchmark did not pass its time membrane")
    if final.get("same_dataset_verified") is not True:
        raise SystemExit("native benchmark did not verify same-dataset identity")
    if final.get("raw_runner_control_present") is not True:
        raise SystemExit("raw runner control missing")
    if final.get("translator_required") is not False:
        raise SystemExit("translator boundary regressed")
    if meta.get("raw_arm_hhs_energy_authority") is not False:
        raise SystemExit("raw arm was incorrectly granted HHS energy authority")
    if meta.get("physical_energy_measured") is not False:
        raise SystemExit("benchmark incorrectly claims physical energy measurement")
    if not arms:
        raise SystemExit("no A:B:C arm records")

    energy = verify_energy_contract()
    triples: dict[tuple[int, str], dict[str, dict[str, Any]]] = {}
    for arm in arms:
        phase = arm["phase"]
        rank = int(arm["difficulty_rank"])
        which = arm["arm"]
        if phase not in EXPECTED_SLOTS or which not in ARMS:
            raise SystemExit("unknown phase/arm")
        if (int(arm["phase_slot"]), int(arm["inverse_phase_slot"])) != EXPECTED_SLOTS[phase]:
            raise SystemExit(f"phase geometry mismatch for {phase}")
        expected_gradient = exact_percentile_gradient(rank, 9)
        observed_gradient = Fraction(
            int(arm["gradient"]["numerator"]), int(arm["gradient"]["denominator"])
        )
        if observed_gradient != expected_gradient:
            raise SystemExit(f"difficulty gradient mismatch at rank {rank}")
        if int(arm["calibration_tensor_energy_units"]) != ENERGY_PER_TENSOR:
            raise SystemExit("calibration tensor energy denominator changed")
        if int(arm["calibration_reciprocal_pair_energy_units"]) != ENERGY_PER_PAIR:
            raise SystemExit("calibration reciprocal pair energy denominator changed")
        if arm.get("physical_energy_measured") is not False:
            raise SystemExit("sample mislabeled as physical energy")
        if arm.get("dataset_complete") is not True:
            raise SystemExit(f"incomplete dataset rank={rank} phase={phase} arm={which}")
        if which == "A":
            if int(arm["route_receipts"]) != int(arm["completed"]):
                raise SystemExit("A missing route receipts")
            if int(arm["m_witnesses"]) != int(arm["completed"]):
                raise SystemExit("A missing M witnesses")
            if int(arm["raw_validations"]) != 0:
                raise SystemExit("A unexpectedly used raw control validation")
        elif which == "B":
            if int(arm["route_receipts"]) != int(arm["completed"]):
                raise SystemExit("B missing route receipts")
            if int(arm["m_witnesses"]) != 0 or int(arm["raw_validations"]) != 0:
                raise SystemExit("B contains proof/raw work")
        else:
            if int(arm["route_receipts"]) != 0 or int(arm["m_witnesses"]) != 0:
                raise SystemExit("raw C unexpectedly called HHS route/proof path")
            if int(arm["raw_validations"]) != int(arm["completed"]):
                raise SystemExit("raw C validation count mismatch")
        triples.setdefault((rank, phase), {})[which] = arm

    phase_totals: dict[str, dict[str, int]] = {
        p: {
            "a_completed": 0, "a_elapsed": 0,
            "b_completed": 0, "b_elapsed": 0,
            "c_completed": 0, "c_elapsed": 0,
            "samples": 0,
        }
        for p in PHASES
    }
    triple_results: list[dict[str, Any]] = []
    ranks_seen: set[int] = set()

    for (rank, phase), triple in sorted(triples.items()):
        if set(triple) != set(ARMS):
            raise SystemExit(f"incomplete A:B:C triple rank={rank} phase={phase}")
        a, b, c = triple["A"], triple["B"], triple["C"]
        completed = {int(a["completed"]), int(b["completed"]), int(c["completed"])}
        if len(completed) != 1:
            raise SystemExit(f"completed count differs across A:B:C rank={rank} phase={phase}")
        digests = {int(a["dataset_digest"]), int(b["dataset_digest"]), int(c["dataset_digest"])}
        if len(digests) != 1:
            raise SystemExit(f"dataset identity differs across A:B:C rank={rank} phase={phase}")
        if int(a["route_digest"]) != int(b["route_digest"]):
            raise SystemExit(f"A/B route work differs rank={rank} phase={phase}")

        a_rate, b_rate, c_rate = rate(a), rate(b), rate(c)
        ab, ac, bc = a_rate / b_rate, a_rate / c_rate, b_rate / c_rate
        rating = rank * ENERGY_PER_PAIR
        gradient = exact_percentile_gradient(rank, 9)
        triple_results.append({
            "difficulty_rank": rank,
            "difficulty_gradient": frac_obj(gradient),
            "phase": phase,
            "phase_slot": int(a["phase_slot"]),
            "inverse_phase_slot": int(a["inverse_phase_slot"]),
            "target_iterations": int(a["target_iterations"]),
            "dataset_digest": int(a["dataset_digest"]),
            "calibration_pair_energy_units": ENERGY_PER_PAIR,
            "difficulty_energy_rating_units": rating,
            "a": {
                "elapsed_ns": int(a["elapsed_ns"]),
                "throughput_per_second": frac_obj(a_rate),
                "difficulty_energy_normalized_rate": frac_obj(a_rate / rating),
            },
            "b": {
                "elapsed_ns": int(b["elapsed_ns"]),
                "throughput_per_second": frac_obj(b_rate),
                "difficulty_energy_normalized_rate": frac_obj(b_rate / rating),
            },
            "c": {
                "elapsed_ns": int(c["elapsed_ns"]),
                "throughput_per_second": frac_obj(c_rate),
                "difficulty_energy_normalized_rate": frac_obj(c_rate / rating),
            },
            "ab_ratio": frac_obj(ab),
            "ab_bp_floor": bp_floor(ab),
            "ac_ratio": frac_obj(ac),
            "ac_bp_floor": bp_floor(ac),
            "bc_ratio": frac_obj(bc),
            "bc_bp_floor": bp_floor(bc),
        })

        t = phase_totals[phase]
        t["a_completed"] += int(a["completed"])
        t["a_elapsed"] += int(a["elapsed_ns"])
        t["b_completed"] += int(b["completed"])
        t["b_elapsed"] += int(b["elapsed_ns"])
        t["c_completed"] += int(c["completed"])
        t["c_elapsed"] += int(c["elapsed_ns"])
        t["samples"] += 1
        ranks_seen.add(rank)

    if set(p for _, p in triples) != set(PHASES):
        raise SystemExit("all four reciprocal phases were not calibrated")
    if ranks_seen != set(range(1, 10)):
        raise SystemExit(f"expected difficulty ranks 1..9, observed {sorted(ranks_seen)}")

    phase_summary: dict[str, Any] = {}
    totals = {k: 0 for k in (
        "a_completed", "a_elapsed", "b_completed", "b_elapsed", "c_completed", "c_elapsed"
    )}
    for phase in PHASES:
        t = phase_totals[phase]
        if t["samples"] != 9:
            raise SystemExit(f"expected nine samples for {phase}")
        a_rate = Fraction(t["a_completed"] * 1_000_000_000, t["a_elapsed"])
        b_rate = Fraction(t["b_completed"] * 1_000_000_000, t["b_elapsed"])
        c_rate = Fraction(t["c_completed"] * 1_000_000_000, t["c_elapsed"])
        ab, ac, bc = a_rate / b_rate, a_rate / c_rate, b_rate / c_rate
        phase_summary[phase] = {
            "samples": t["samples"],
            "a_completed": t["a_completed"],
            "a_elapsed_ns": t["a_elapsed"],
            "b_completed": t["b_completed"],
            "b_elapsed_ns": t["b_elapsed"],
            "c_completed": t["c_completed"],
            "c_elapsed_ns": t["c_elapsed"],
            "ab_ratio": frac_obj(ab), "ab_bp_floor": bp_floor(ab),
            "ac_ratio": frac_obj(ac), "ac_bp_floor": bp_floor(ac),
            "bc_ratio": frac_obj(bc), "bc_bp_floor": bp_floor(bc),
            "energy_gate": energy[phase],
        }
        for key in totals:
            totals[key] += t[key]

    global_a = Fraction(totals["a_completed"] * 1_000_000_000, totals["a_elapsed"])
    global_b = Fraction(totals["b_completed"] * 1_000_000_000, totals["b_elapsed"])
    global_c = Fraction(totals["c_completed"] * 1_000_000_000, totals["c_elapsed"])
    global_ab = global_a / global_b
    global_ac = global_a / global_c
    global_bc = global_b / global_c

    return {
        "schema": "HHS_PASS219_RAW_RUNNER_ABC_NORMALIZATION_RESULT_V1",
        "native_schema": meta["schema"],
        "difficulty_ranks_seen": sorted(ranks_seen),
        "triplet_phase_samples": len(triple_results),
        "four_phase_coverage": True,
        "same_dataset_verified": True,
        "time_bound_verified": True,
        "negative_controls_passed": bool(meta["negative_controls_passed"]),
        "logical_energy_contract_verified": True,
        "raw_arm_hhs_energy_authority": False,
        "physical_energy_measured": False,
        "candidate_only": bool(final["candidate_only"]),
        "canonical_vm81_mutation_authority": bool(final["canonical_vm81_mutation_authority"]),
        "canonical_hash72_authority": bool(final["canonical_hash72_authority"]),
        "canonical_hash216_authority": bool(final["canonical_hash216_authority"]),
        "canonical_persistence_authority": bool(final["canonical_persistence_authority"]),
        "requires_signed_environmental_vm81_admission": bool(final["requires_signed_environmental_vm81_admission"]),
        "translator_required": bool(final["translator_required"]),
        "global": {
            "a_rate": frac_obj(global_a),
            "b_rate": frac_obj(global_b),
            "c_rate": frac_obj(global_c),
            "ab_ratio": frac_obj(global_ab), "ab_bp_floor": bp_floor(global_ab),
            "ac_ratio": frac_obj(global_ac), "ac_bp_floor": bp_floor(global_ac),
            "bc_ratio": frac_obj(global_bc), "bc_bp_floor": bp_floor(global_bc),
        },
        "phase_summary": phase_summary,
        "triples": triple_results,
        "result": "PASS",
    }


def ratio_text(obj: dict[str, int]) -> str:
    return f"{obj['numerator']}/{obj['denominator']}"


def write_report(result: dict[str, Any], path: Path) -> None:
    g = result["global"]
    lines = [
        "# Pass 219 — Lane 5 vs Raw Workflow Runner A:B:C Normalization",
        "",
        "## Result",
        "",
        f"- Result: **{result['result']}**",
        f"- Triplet phase samples: `{result['triplet_phase_samples']}`",
        f"- Difficulty ranks: `{result['difficulty_ranks_seen']}`",
        "- Same deterministic dataset identity: **verified across A/B/C**",
        f"- Global A:B = `{ratio_text(g['ab_ratio'])}` (`{g['ab_bp_floor']} bp` floor)",
        f"- Global A:C = `{ratio_text(g['ac_ratio'])}` (`{g['ac_bp_floor']} bp` floor)",
        f"- Global B:C = `{ratio_text(g['bc_ratio'])}` (`{g['bc_bp_floor']} bp` floor)",
        "",
        "A is Lane 5 route + direct H36/Hash216 M proof. B is Lane 5 route-only. C is raw native-C validation/folding of the identical deterministic dataset record with zero Lane 5 route receipts and zero M witnesses.",
        "",
        "## Phase aggregates",
        "",
        "| phase | samples | A:B | A:C | B:C | A:B bp | A:C bp | B:C bp |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for phase in PHASES:
        p = result["phase_summary"][phase]
        lines.append(
            f"| {phase} | {p['samples']} | {ratio_text(p['ab_ratio'])} | "
            f"{ratio_text(p['ac_ratio'])} | {ratio_text(p['bc_ratio'])} | "
            f"{p['ab_bp_floor']} | {p['ac_bp_floor']} | {p['bc_bp_floor']} |"
        )
    lines += [
        "",
        "## Calibration semantics",
        "",
        "The 450-unit reciprocal-pair quantity is retained only as the shared difficulty-normalization denominator so A, B, and C are rated on the same dataset scale. It does not grant HHS logical-energy authority to raw arm C and is not a measurement of physical joules.",
        "",
        "## Authority membrane",
        "",
        "A and B remain candidate-only. Canonical VM81 mutation, Hash72, Hash216, and persistence authority remain false; signed environmental VM81 admission remains required; no translator is introduced. C bypasses those HHS services entirely and exists only as the same-runner native control.",
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("output_md", type=Path)
    args = parser.parse_args()
    result = analyze(load_records(args.input))
    args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    write_report(result, args.output_md)
    print(json.dumps({
        "result": result["result"],
        "triplet_phase_samples": result["triplet_phase_samples"],
        "difficulty_ranks_seen": result["difficulty_ranks_seen"],
        "global": result["global"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
