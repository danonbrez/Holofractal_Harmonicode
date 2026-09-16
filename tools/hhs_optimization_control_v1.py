#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 90

H_ADDR = Decimal("444.23460010384649012933840792848557726141327470771727270562838225391814480238763")
R_REF = Decimal(323557)
GAMMA_BASIS_REF = Decimal("143735214.50580025880677834725411700792197109492460487760481500247693099317782613")
GAMMA_ROUTE_REF = Decimal("574940858.02320103522711338901646803168788437969841951041926000990772397271130453")
GAMMA_QUDIT_REF = Decimal(23296104)
GAMMA_VM_REF = Decimal(11648052)
DEFAULT_PAIRED_FLOOR = Decimal("0.95")


def d(value: object) -> Decimal:
    return Decimal(str(value))


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metrics(value: dict) -> dict[str, Decimal]:
    obs = value["physical_runner_observation"]
    rate = d(obs["candidate_rate_floor_per_second"])
    return {
        "shot": rate,
        "basis": rate * H_ADDR,
        "route": rate * H_ADDR * Decimal(4),
        "qudit": rate * Decimal(72),
        "vm5184": rate * Decimal(36),
    }


def exact_membrane_ok(value: dict) -> bool:
    authority = value["authority"]
    obs = value["physical_runner_observation"]
    state = value["logical_state_space"]
    return all(
        [
            value.get("result") == "PASS",
            authority.get("observational_only") is True,
            authority.get("canonical_vm81_mutation_authority") is False,
            authority.get("canonical_hash72_authority") is False,
            authority.get("canonical_hash216_authority") is False,
            authority.get("requires_signed_environmental_vm81_admission") is True,
            int(state.get("binary_embedding_bits", 0)) == 445,
            int(state.get("native_address_bytes", 0)) == 56,
            int(obs.get("candidate_count", 0)) > 0,
        ]
    )


def ratio(a: Decimal, b: Decimal) -> Decimal:
    return a / b if b else Decimal(0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--paired-control", type=Path)
    parser.add_argument("--paired-floor", default=str(DEFAULT_PAIRED_FLOOR))
    args = parser.parse_args()

    candidate = load(args.candidate)
    cand_metrics = metrics(candidate)
    exact_ok = exact_membrane_ok(candidate)

    reference_indices = {
        "shot": ratio(cand_metrics["shot"], R_REF),
        "basis": ratio(cand_metrics["basis"], GAMMA_BASIS_REF),
        "route": ratio(cand_metrics["route"], GAMMA_ROUTE_REF),
        "qudit": ratio(cand_metrics["qudit"], GAMMA_QUDIT_REF),
        "vm5184": ratio(cand_metrics["vm5184"], GAMMA_VM_REF),
    }

    paired = None
    paired_ok = None
    if args.paired_control:
        control = load(args.paired_control)
        control_metrics = metrics(control)
        floor = Decimal(args.paired_floor)
        paired_ratios = {k: ratio(cand_metrics[k], control_metrics[k]) for k in cand_metrics}
        paired_ok = exact_membrane_ok(control) and paired_ratios["shot"] >= floor
        paired = {
            "floor": str(floor),
            "ratios": {k: str(v) for k, v in paired_ratios.items()},
            "control_hardware": control.get("hardware_normalization", {}),
            "candidate_hardware": candidate.get("hardware_normalization", {}),
        }

    result = {
        "schema": "HHS_NORMALIZED_OPTIMIZATION_CONTROL_V1",
        "result": "PASS" if exact_ok and (paired_ok is not False) else "FAIL",
        "exact_membrane_pass": exact_ok,
        "historical_reference": {
            "candidate_rate_floor_per_second": str(R_REF),
            "basis_rate_bits_equivalent_per_second": str(GAMMA_BASIS_REF),
            "route_rate_bits_equivalent_per_second": str(GAMMA_ROUTE_REF),
            "qudit_coordinate_symbols_per_second": str(GAMMA_QUDIT_REF),
            "vm5184_block_coordinates_per_second": str(GAMMA_VM_REF),
        },
        "candidate_metrics": {k: str(v) for k, v in cand_metrics.items()},
        "reference_indices": {k: str(v) for k, v in reference_indices.items()},
        "paired_control": paired,
        "paired_performance_pass": paired_ok,
        "authority_note": "Performance indices are observational; exact replay and canonical authority boundaries are mandatory controls.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
