"""Command-line control surface for the Pass 175 virtual instruction processor."""
from __future__ import annotations

import argparse
from base64 import b64decode
import json
import os
from pathlib import Path
from typing import Any, Sequence

from hhs_runtime.pass174 import Pass174Runtime
from .runtime import (
    ControlWord,
    HydratedMicrocodeStore,
    InstructionAddress,
    InstructionRequest,
    Pass175Error,
    Pass175Runtime,
    ReciprocalLane,
)


def _runtime() -> Pass175Runtime:
    state_root = Path(os.environ.get("HHS_PASS175_STATE_DIR", ".hhs/pass175")).resolve()
    return Pass175Runtime(
        authority=Pass174Runtime(repository_root=Path.cwd()),
        microcode_store=HydratedMicrocodeStore(state_root / "hash216_microcode.jsonl"),
    )


def _print(value: Any) -> int:
    print(json.dumps(value, sort_keys=True, indent=2, default=str))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hhs-pass175", description="Pass 175 VM5184 × G243 virtual instruction processor")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("status")
    commands.add_parser("hydrate-bootstrap").add_argument("--no-seal", action="store_true")

    address = commands.add_parser("address")
    address.add_argument("--state", type=int)
    address.add_argument("--cell", type=int)
    address.add_argument("--operation", type=int)
    address.add_argument("--control", type=int)
    address.add_argument("--projected", type=int)

    control = commands.add_parser("control")
    control.add_argument("--encoded", type=int)
    control.add_argument("--trits", nargs=5, type=int)

    hydrate = commands.add_parser("hydrate")
    hydrate.add_argument("exact_bytes_b64")
    hydrate.add_argument("--mode", default="LONG_64")
    hydrate.add_argument("--read", nargs="*", type=int, default=[])
    hydrate.add_argument("--write", nargs="*", type=int, default=[])

    execute = commands.add_parser("execute")
    execute.add_argument("exact_bytes_b64")
    execute.add_argument("--sequence", type=int, default=0)
    execute.add_argument("--thread", type=int, default=0)
    execute.add_argument("--read", nargs="*", type=int, default=[])
    execute.add_argument("--write", nargs="*", type=int, default=[])
    execute.add_argument("--delta", nargs="*", default=[])
    execute.add_argument("--allow-privileged", action="store_true")

    project = commands.add_parser("project-ab")
    project.add_argument("p_squared", type=int)
    project.add_argument("source_root_sha256")
    project.add_argument("provenance_root_sha256")

    commands.add_parser("replay")
    return parser


def _parse_delta(values: Sequence[str]) -> tuple[tuple[int, int], ...]:
    result: list[tuple[int, int]] = []
    for item in values:
        try:
            position, value = item.split("=", 1)
            result.append((int(position), int(value)))
        except Exception as exc:
            raise Pass175Error("HHS_P175_CLI_DELTA_FORMAT", item) from exc
    return tuple(result)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runtime = _runtime()
    try:
        if args.command == "status":
            return _print(runtime.status())
        if args.command == "hydrate-bootstrap":
            return _print(runtime.cold_hydrate_bootstrap(seal=not args.no_seal))
        if args.command == "address":
            if args.projected is not None:
                address, control = InstructionAddress.unproject(args.projected)
                return _print({"address": address.__dict__, "control": control, "projected": args.projected})
            address = InstructionAddress.from_state(args.state) if args.state is not None else InstructionAddress.from_cell_operation(args.cell, args.operation)
            payload = {"address": address.__dict__}
            if args.control is not None:
                payload.update({"control": args.control, "projected": address.project(args.control)})
            return _print(payload)
        if args.command == "control":
            word = ControlWord.from_int(args.encoded) if args.encoded is not None else ControlWord.from_trits(args.trits)
            return _print({"encoded": word.encoded, "trits": list(word.trits)})
        if args.command == "hydrate":
            record = runtime.hydrate_x86(b64decode(args.exact_bytes_b64, validate=True), decoder_mode=args.mode, read_set=args.read, write_set=args.write)
            return _print(record.to_dict())
        if args.command == "execute":
            request = InstructionRequest(
                exact_bytes=b64decode(args.exact_bytes_b64, validate=True),
                sequence=args.sequence,
                thread_id=args.thread,
                read_set=tuple(args.read),
                write_set=tuple(args.write),
                explicit_delta=_parse_delta(args.delta),
                allow_privileged=args.allow_privileged,
            )
            return _print(runtime.execute_batch([request]))
        if args.command == "project-ab":
            a = ReciprocalLane("xy", 0, args.p_squared, 1, args.source_root_sha256, args.provenance_root_sha256)
            b = ReciprocalLane("yx", 36, args.p_squared, 1, args.provenance_root_sha256, args.source_root_sha256)
            return _print(runtime.project_ab(a, b))
        if args.command == "replay":
            return _print(runtime.replay())
    except Exception as exc:
        return _print({
            "schema": "HHS_P175_CLI_REJECTION_V1",
            "classification": getattr(exc, "classification", type(exc).__name__),
            "detail": getattr(exc, "detail", str(exc)),
        }) or 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
