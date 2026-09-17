#!/usr/bin/env python3
"""Analyze the Pass 219 four-phase reciprocal A:B calibration with exact arithmetic."""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

# This tool is invoked by path from tools/pass219. Make repository packages
# importable without relying on an ambient PYTHONPATH.
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
ENERGY_PER_TENSOR = 225
ENERGY_PER_PAIR = 450


def frac_obj(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


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
            "physical_energy_measured": False,
        }
    return out


def analyze(records: list[dict[str, Any]]) -> dict[str, Any]:
    metas = [r for r in records if r.get("type") == "meta"]
    finals = [r for r in records if r.get("type") == "result"]
    arms = [r for r in records if r.get("type") == "arm"]
    if len(metas) != 1 or len(finals) != 1:
        raise SystemExit("expected one meta and one final record")
    meta, final = metas[0], finals[0]
    if final.get("result") != "PASS" or not final.get("within_time_bound"):
        raise SystemExit("native benchmark did not pass its time/authority membrane")
    if final.get("translator_required") is not False:
        raise SystemExit("translator boundary regressed")
    if not arms:
        raise SystemExit("no A:B arm records")

    energy = verify_energy_contract()
    paired: dict[tuple[int, str], dict[str, dict[str, Any]]] = {}
    for arm in arms:
        phase = arm["phase"]
        rank = int(arm["difficulty_rank"])
        which = arm["arm"]
        if phase not in EXPECTED_SLOTS or which not in ("A", "B"):
            raise SystemExit("unknown phase/arm")
        if (arm["phase_slot"], arm["inverse_phase_slot"]) != EXPECTED_SLOTS[phase]:
            raise SystemExit(f"phase geometry mismatch for {phase}")
        expected_gradient = exact_percentile_gradient(rank, 9)
        observed_gradient = Fraction(
            int(arm["gradient"]["numerator"]), int(arm["gradient"]["denominator"])
        )
        if observed_gradient != expected_gradient:
            raise SystemExit(f"difficulty gradient mismatch at rank {rank}")
        if arm["logical_tensor_energy_units"] != ENERGY_PER_TENSOR:
            raise SystemExit("logical tensor energy changed")
        if arm["logical_reciprocal_pair_energy_units"] != ENERGY_PER_PAIR:
            raise SystemExit("logical reciprocal pair energy changed")
        if arm.get("physical_energy_measured") is not False:
            raise SystemExit("logical energy was mislabeled as physical energy")
        if which == "A" and arm["m_witnesses"] != arm["completed"]:
            raise SystemExit("A arm missing M witnesses")
        if which == "B" and arm["m_witnesses"] != 0:
            raise SystemExit("B control unexpectedly contains M witnesses")
        paired.setdefault((rank, phase), {})[which] = arm

    pair_results: list[dict[str, Any]] = []
    phase_totals: dict[str, dict[str, int]] = {
        p: {"a_completed": 0, "a_elapsed": 0, "b_completed": 0, "b_elapsed": 0, "samples": 0}
        for p in PHASES
    }
    ranks_seen: set[int] = set()
    for (rank, phase), pair in sorted(paired.items()):
        if set(pair) != {"A", "B"}:
            raise SystemExit(f"unpaired sample rank={rank} phase={phase}")
        a, b = pair["A"], pair["B"]
        if a["completed"] <= 0 or b["completed"] <= 0 or a["elapsed_ns"] <= 0 or b["elapsed_ns"] <= 0:
            raise SystemExit("non-positive timing sample")
        ab = Fraction(
            int(a["completed"]) * int(b["elapsed_ns"]),
            int(b["completed"]) * int(a["elapsed_ns"]),
        )
        a_rate = Fraction(int(a["completed"]) * 1_000_000_000, int(a["elapsed_ns"]))
        b_rate = Fraction(int(b["completed"]) * 1_000_000_000, int(b["elapsed_ns"]))
        rating = rank * ENERGY_PER_PAIR
        a_cal = a_rate / rating
        b_cal = b_rate / rating
        gradient = exact_percentile_gradient(rank, 9)
        pair_results.append(
            {
                "difficulty_rank": rank,
                "difficulty_gradient": frac_obj(gradient),
                "phase": phase,
                "phase_slot": a["phase_slot"],
                "inverse_phase_slot": a["inverse_phase_slot"],
                "target_iterations": a["target_iterations"],
                "logical_pair_energy_units": ENERGY_PER_PAIR,
                "difficulty_energy_rating_units": rating,
                "a": {
                    "completed": a["completed"],
                    "elapsed_ns": a["elapsed_ns"],
                    "throughput_per_second": frac_obj(a_rate),
                    "difficulty_energy_normalized_rate": frac_obj(a_cal),
                    "dataset_complete": a["dataset_complete"],
                },
                "b": {
                    "completed": b["completed"],
                    "elapsed_ns": b["elapsed_ns"],
                    "throughput_per_second": frac_obj(b_rate),
                    "difficulty_energy_normalized_rate": frac_obj(b_cal),
                    "dataset_complete": b["dataset_complete"],
                },
                "normalized_ab_throughput_ratio": frac_obj(ab),
                "normalized_ab_basis_points_floor": (ab.numerator * 10_000) // ab.denominator,
            }
        )
        totals = phase_totals[phase]
        totals["a_completed"] += int(a["completed"])
        totals["a_elapsed"] += int(a["elapsed_ns"])
        totals["b_completed"] += int(b["completed"])
        totals["b_elapsed"] += int(b["elapsed_ns"])
        totals["samples"] += 1
        ranks_seen.add(rank)

    if set(p for _, p in paired) != set(PHASES):
        raise SystemExit("all four reciprocal phases were not calibrated")

    phase_summary: dict[str, Any] = {}
    all_a_completed = all_a_elapsed = all_b_completed = all_b_elapsed = 0
    for phase in PHASES:
        totals = phase_totals[phase]
        if totals["samples"] == 0:
            raise SystemExit(f"no samples for {phase}")
        ratio = Fraction(
            totals["a_completed"] * totals["b_elapsed"],
            totals["b_completed"] * totals["a_elapsed"],
        )
        phase_summary[phase] = {
            "samples": totals["samples"],
            "a_completed": totals["a_completed"],
            "a_elapsed_ns": totals["a_elapsed"],
            "b_completed": totals["b_completed"],
            "b_elapsed_ns": totals["b_elapsed"],
            "aggregate_normalized_ab_throughput_ratio": frac_obj(ratio),
            "aggregate_normalized_ab_basis_points_floor": (ratio.numerator * 10_000) // ratio.denominator,
            "energy_gate": energy[phase],
        }
        all_a_completed += totals["a_completed"]
        all_a_elapsed += totals["a_elapsed"]
        all_b_completed += totals["b_completed"]
        all_b_elapsed += totals["b_elapsed"]

    global_ratio = Fraction(
        all_a_completed * all_b_elapsed,
        all_b_completed * all_a_elapsed,
    )
    return {
        "schema": "HHS_PASS219_FOUR_PHASE_AB_DIFFICULTY_ENERGY_CALIBRATION_RESULT_V1",
        "native_schema": meta["schema"],
        "difficulty_ranks_seen": sorted(ranks_seen),
        "paired_phase_samples": len(pair_results),
        "four_phase_coverage": True,
        "time_bound_verified": True,
        "negative_controls_passed": bool(meta["negative_controls_passed"]),
        "logical_energy_contract_verified": True,
        "logical_energy_is_not_physical_joules": True,
        "candidate_only": bool(final["candidate_only"]),
        "canonical_vm81_mutation_authority": bool(final["canonical_vm81_mutation_authority"]),
        "canonical_hash72_authority": bool(final["canonical_hash72_authority"]),
        "canonical_hash216_authority": bool(final["canonical_hash216_authority"]),
        "canonical_persistence_authority": bool(final["canonical_persistence_authority"]),
        "requires_signed_environmental_vm81_admission": bool(final["requires_signed_environmental_vm81_admission"]),
        "translator_required": bool(final["translator_required"]),
        "global_normalized_ab_throughput_ratio": frac_obj(global_ratio),
        "global_normalized_ab_basis_points_floor": (global_ratio.numerator * 10_000) // global_ratio.denominator,
        "phase_summary": phase_summary,
        "pairs": pair_results,
        "result": "PASS",
    }


def write_report(result: dict[str, Any], path: Path) -> None:
    global_ratio = result["global_normalized_ab_throughput_ratio"]
    lines = [
        "# Pass 219 — Four-Phase Reciprocal A:B Difficulty/Energy Calibration",
        "",
        "## Result",
        "",
        f"- Native/calibration result: **{result['result']}**",
        f"- Paired phase samples: `{result['paired_phase_samples']}`",
        f"- Difficulty ranks observed: `{result['difficulty_ranks_seen']}`",
        f"- Global normalized A:B throughput ratio: `{global_ratio['numerator']}/{global_ratio['denominator']}` "
        f"(`{result['global_normalized_ab_basis_points_floor']} bp` floor)",
        "- Logical reciprocal-pair energy normalization: `450` conserved Lo Shu units per phase gate.",
        "- Physical joules were not measured; the energy rating is the repository's exact Pass 067.1 logical energy quantity.",
        "",
        "## Phase aggregates",
        "",
        "| phase | samples | A completed | B completed | A:B ratio | bp floor |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for phase in PHASES:
        phase_result = result["phase_summary"][phase]
        ratio = phase_result["aggregate_normalized_ab_throughput_ratio"]
        lines.append(
            f"| {phase} | {phase_result['samples']} | {phase_result['a_completed']} | "
            f"{phase_result['b_completed']} | {ratio['numerator']}/{ratio['denominator']} | "
            f"{phase_result['aggregate_normalized_ab_basis_points_floor']} |"
        )
    lines += [
        "",
        "## Authority membrane",
        "",
        "The benchmark remains candidate-only. Canonical VM81 mutation, Hash72, Hash216, and persistence authority remain false; signed environmental VM81 admission remains required; no semantic translator is introduced.",
        "",
        "## Interpretation",
        "",
        "A is the measured Lane 5 route plus direct H36/Hash216 M-exponent witness path. B is the matched Lane 5 route-only control. The exact A:B ratio therefore measures the steady-state performance cost/capacity of carrying the direct M binding under identical phase, difficulty, runner, and time-bound conditions; it is not a comparison across different hardware.",
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
        "paired_phase_samples": result["paired_phase_samples"],
        "difficulty_ranks_seen": result["difficulty_ranks_seen"],
        "global_normalized_ab_throughput_ratio": result["global_normalized_ab_throughput_ratio"],
        "global_normalized_ab_basis_points_floor": result["global_normalized_ab_basis_points_floor"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
