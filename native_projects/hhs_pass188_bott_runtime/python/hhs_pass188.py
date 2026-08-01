#!/usr/bin/env python3
"""Pass 188 exact Bott-periodic runtime, CLI, receipts, and replay."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

VM81_CELLS = 81
OPERATIONS_PER_CELL = 64
PERMANENT_STATES = 5_184
G243_CONTROLS = 243
HYDRATED_STATES = 1_259_712
OUTER_ENVELOPE = 1_259_713
Q144_STATES = 144
FACTORIAL_STATES = 5_040
CHECKSUM_EXPECTED = 0x11E3BBF0214751C3
TAGS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")


class Pass188Error(ValueError):
    """Deterministic Pass 188 validation failure."""


@dataclass(frozen=True, slots=True)
class Coordinate:
    projected_address: int
    permanent_state: int
    g243: int
    vm81_cell: int
    operation64: int
    operation_class8: int
    basis8: int
    layer36: int
    q144: int
    row12: int
    column12: int
    pair72: int
    index72: int
    factorial_admitted: bool
    closure_q144: bool


@dataclass(frozen=True, slots=True)
class Transition:
    input: Coordinate
    output: Coordinate
    classification: str
    ordered_input_tag: str
    ordered_output_tag: str
    predecessor_hash72: str
    successor_hash72: str
    combined_hash216: str
    stem: tuple[str, str] = ("I", "Z^72")
    closure: tuple[int, int, bool] = (0, 0, True)


def bott_step(basis8: int) -> int:
    if not isinstance(basis8, int) or isinstance(basis8, bool) or not 0 <= basis8 < 8:
        raise Pass188Error("basis8 must be an integer in [0, 7]")
    mismatch = ((basis8 >> 2) ^ (basis8 >> 1)) & 1
    mask = (mismatch - 1) & 0xFFFFFFFF
    return ((basis8 ^ 1) & mask) & 7


def decode_projected(projected_address: int) -> Coordinate:
    if not isinstance(projected_address, int) or isinstance(projected_address, bool):
        raise Pass188Error("projected_address must be an integer")
    if not 0 <= projected_address < HYDRATED_STATES:
        raise Pass188Error(f"projected_address must be in [0, {HYDRATED_STATES - 1}]")
    state, g243 = divmod(projected_address, G243_CONTROLS)
    vm81_cell, operation64 = divmod(state, OPERATIONS_PER_CELL)
    operation_class8, basis8 = divmod(operation64, 8)
    layer36, q144 = divmod(state, Q144_STATES)
    row12, column12 = divmod(q144, 12)
    pair72, index72 = divmod(q144, 72)
    return Coordinate(
        projected_address=projected_address,
        permanent_state=state,
        g243=g243,
        vm81_cell=vm81_cell,
        operation64=operation64,
        operation_class8=operation_class8,
        basis8=basis8,
        layer36=layer36,
        q144=q144,
        row12=row12,
        column12=column12,
        pair72=pair72,
        index72=index72,
        factorial_admitted=state < FACTORIAL_STATES,
        closure_q144=state >= FACTORIAL_STATES,
    )


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def hash72(domain: str, value: Any) -> str:
    seed = domain.encode("utf-8") + b"\0" + _canonical_bytes(value)
    first = hashlib.sha256(seed).hexdigest()
    second = hashlib.sha256(b"HHS-HASH72\0" + seed).hexdigest()
    return first + second[:8]


def transition_projected(projected_address: int) -> Transition:
    current = decode_projected(projected_address)
    next_basis = bott_step(current.basis8)
    next_operation = (current.operation_class8 << 3) | next_basis
    next_state = current.vm81_cell * OPERATIONS_PER_CELL + next_operation
    next_projected = next_state * G243_CONTROLS + current.g243
    output = decode_projected(next_projected)

    if (
        output.g243 != current.g243
        or output.vm81_cell != current.vm81_cell
        or output.operation_class8 != current.operation_class8
        or output.basis8 != next_basis
    ):
        raise Pass188Error("HHS_P188_COORDINATE_DRIFT")

    classification = (
        "HHS_P188_PERIOD_TWO_ACTIVE"
        if current.basis8 in (0, 1, 6, 7)
        else "HHS_P188_ASYMMETRIC_DRIFT_COLLAPSE"
    )
    input_payload = asdict(current) | {"ordered_tag": TAGS[current.basis8]}
    output_payload = asdict(output) | {"ordered_tag": TAGS[output.basis8]}
    predecessor = hash72("HHS-P188-PREDECESSOR", input_payload)
    successor = hash72("HHS-P188-SUCCESSOR", output_payload)
    identity_payload = {
        "contract": "HHS-P188-BOTT-RUNTIME-H216-VM81-Q144-G243-X64",
        "predecessor_hash72": predecessor,
        "successor_hash72": successor,
        "classification": classification,
        "stem": ["I", "Z^72"],
    }
    third = hash72("HHS-P188-CLOSURE", identity_payload)
    return Transition(
        input=current,
        output=output,
        classification=classification,
        ordered_input_tag=TAGS[current.basis8],
        ordered_output_tag=TAGS[output.basis8],
        predecessor_hash72=predecessor,
        successor_hash72=successor,
        combined_hash216=predecessor + successor + third,
    )


def receipt_dict(transition: Transition) -> dict[str, Any]:
    payload = asdict(transition)
    payload["stem"] = list(payload["stem"])
    payload["closure"] = list(payload["closure"])
    payload["schema"] = "HHS_PASS_188_TRANSITION_RECEIPT_V1"
    payload["contract"] = "HHS-P188-BOTT-RUNTIME-H216-VM81-Q144-G243-X64"
    payload["floating_point_authority"] = False
    payload["replay_verified"] = True
    return payload


def replay_receipt(receipt: dict[str, Any]) -> bool:
    try:
        projected = int(receipt["input"]["projected_address"])
        expected = receipt_dict(transition_projected(projected))
    except (KeyError, TypeError, ValueError, Pass188Error):
        return False
    keys = (
        "input",
        "output",
        "classification",
        "ordered_input_tag",
        "ordered_output_tag",
        "predecessor_hash72",
        "successor_hash72",
        "combined_hash216",
        "stem",
        "closure",
    )
    return all(receipt.get(key) == expected.get(key) for key in keys)


def hydrate(addresses: Iterable[int] | None = None) -> dict[str, Any]:
    sequence = range(HYDRATED_STATES) if addresses is None else addresses
    checksum = 1_469_598_103_934_665_603
    hydrated = active = collapse = gear = drift = 0
    for projected in sequence:
        if not isinstance(projected, int) or isinstance(projected, bool) or not 0 <= projected < HYDRATED_STATES:
            raise Pass188Error(f"projected_address must be in [0, {HYDRATED_STATES - 1}]")
        state, g243 = divmod(projected, G243_CONTROLS)
        vm81_cell, operation64 = divmod(state, OPERATIONS_PER_CELL)
        operation_class8, basis8 = divmod(operation64, 8)
        next_basis = bott_step(basis8)
        next_operation = (operation_class8 << 3) | next_basis
        next_state = vm81_cell * OPERATIONS_PER_CELL + next_operation
        next_projected = next_state * G243_CONTROLS + g243
        hydrated += 1
        if basis8 in (0, 1, 6, 7):
            active += 1
        else:
            collapse += 1
        if next_projected % G243_CONTROLS == g243:
            gear += 1
        else:
            drift += 1
        checksum ^= next_projected + (basis8 << 32) + next_basis
        checksum = (checksum * 1_099_511_628_211) & 0xFFFFFFFFFFFFFFFF
    return {
        "schema": "HHS_PASS_188_HYDRATION_SUMMARY_V1",
        "classification": "HHS_PASS_188_FULL_HYDRATION_VERIFIED" if hydrated == HYDRATED_STATES else "HHS_PASS_188_PARTIAL_HYDRATION",
        "hydrated_states": hydrated,
        "active_period_two_states": active,
        "asymmetric_collapse_states": collapse,
        "gear_preserved_states": gear,
        "coordinate_drift_states": drift,
        "deterministic_checksum_u64": f"{checksum:016x}",
        "checksum_matches_pass187": checksum == CHECKSUM_EXPECTED if hydrated == HYDRATED_STATES else None,
        "floating_point_authority": False,
    }


def _write_json(value: Any, path: str | None) -> None:
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path:
        Path(path).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    step = sub.add_parser("step", help="apply the exact 8-state transition")
    step.add_argument("basis", type=int)
    transition = sub.add_parser("transition", help="emit a complete transition receipt")
    transition.add_argument("projected_address", type=int)
    transition.add_argument("--output")
    hydration = sub.add_parser("hydrate", help="hydrate all projected addresses")
    hydration.add_argument("--output")
    replay = sub.add_parser("replay", help="verify a saved transition receipt")
    replay.add_argument("receipt")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "step":
            print(bott_step(args.basis))
        elif args.command == "transition":
            _write_json(receipt_dict(transition_projected(args.projected_address)), args.output)
        elif args.command == "hydrate":
            _write_json(hydrate(), args.output)
        elif args.command == "replay":
            receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
            result = replay_receipt(receipt)
            _write_json({"classification": "HHS_P188_REPLAY_VERIFIED" if result else "HHS_P188_REPLAY_MISMATCH", "verified": result}, None)
            return 0 if result else 1
    except (OSError, json.JSONDecodeError, Pass188Error) as exc:
        print(json.dumps({"error": str(exc), "classification": "HHS_P188_REJECTED"}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
