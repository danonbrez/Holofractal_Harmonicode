from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from . import HarmonicOperator, Pass174Runtime


def _home() -> Path:
    return Path(os.environ.get("HHS_HOME", str(Path.home() / ".hhs"))).expanduser().resolve()


def _state_paths() -> tuple[Path, Path]:
    root = _home() / "state" / "pass174"
    root.mkdir(parents=True, exist_ok=True)
    return root / "operations.json", _home() / "state" / "vector-store" / "pass174.sqlite3"


def _load_runtime() -> tuple[Pass174Runtime, Path]:
    operations_path, store_path = _state_paths()
    runtime = Pass174Runtime(store_path=store_path)
    if operations_path.is_file():
        payload = json.loads(operations_path.read_text(encoding="utf-8"))
        for entry in payload.get("operations", []):
            runtime.execute_and_commit(entry["operator"], mode="direct")
    return runtime, operations_path


def _save_operations(runtime: Pass174Runtime, path: Path) -> None:
    operations = []
    for entry in runtime.operation_log:
        operator = entry["operator"]
        operations.append(
            {
                "operator": {
                    "kind": operator["kind"],
                    "parameters": operator["parameters"],
                    "ordered_connectors": operator["ordered_connectors"],
                }
            }
        )
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps({"schema": "P174CLIOperationLog@1", "operations": operations}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    os.replace(tmp, path)


def _operator(args: argparse.Namespace) -> dict[str, Any]:
    parameters: dict[str, Any] = {}
    for item in args.parameter or []:
        if "=" not in item:
            raise SystemExit(f"invalid --parameter {item!r}; expected name=integer")
        key, value = item.split("=", 1)
        parameters[key] = int(value, 0)
    return {
        "kind": args.kind,
        "parameters": parameters,
        "ordered_connectors": list(args.connector or []),
    }


def _print(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hhs pass174", description="Pass 174 whole-state runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("doctor")
    sub.add_parser("genesis")
    sub.add_parser("boot-fingerprint")

    frame = sub.add_parser("frame")
    frame_sub = frame.add_subparsers(dest="frame_command", required=True)
    frame_sub.add_parser("show")
    frame_execute = frame_sub.add_parser("execute")
    frame_execute.add_argument("--kind", default="rotate")
    frame_execute.add_argument("--parameter", action="append")
    frame_execute.add_argument("--connector", action="append")
    frame_execute.add_argument("--mode", choices=["auto", "direct", "retrieval", "hybrid"], default="auto")
    frame_execute.add_argument("--candidate-only", action="store_true")

    phase = sub.add_parser("phase")
    phase_sub = phase.add_subparsers(dest="phase_command", required=True)
    phase_sub.add_parser("show")
    phase_sub.add_parser("step")
    phase_sub.add_parser("closure")

    harmonic = sub.add_parser("harmonic")
    harmonic_sub = harmonic.add_subparsers(dest="harmonic_command", required=True)
    for name in ("compile", "run"):
        item = harmonic_sub.add_parser(name)
        item.add_argument("--kind", default="harmonic")
        item.add_argument("--parameter", action="append")
        item.add_argument("--connector", action="append")

    hash72 = sub.add_parser("hash72")
    hash72_sub = hash72.add_subparsers(dest="hash72_command", required=True)
    hash72_sub.add_parser("tip")
    hash72_sub.add_parser("trace")

    hash216 = sub.add_parser("hash216")
    hash216_sub = hash216.add_subparsers(dest="hash216_command", required=True)
    inspect = hash216_sub.add_parser("inspect")
    inspect.add_argument("identity")
    index = hash216_sub.add_parser("index")
    index.add_argument("identity")

    vector = sub.add_parser("vector")
    vector_sub = vector.add_subparsers(dest="vector_command", required=True)
    for name in ("query", "retrieve"):
        item = vector_sub.add_parser(name)
        item.add_argument("--kind", default="rotate")
        item.add_argument("--parameter", action="append")
        item.add_argument("--connector", action="append")
    vector_sub.add_parser("admit")
    quarantine = vector_sub.add_parser("quarantine")
    quarantine.add_argument("identity")

    efficiency = sub.add_parser("efficiency")
    efficiency_sub = efficiency.add_subparsers(dest="efficiency_command", required=True)
    compare = efficiency_sub.add_parser("compare")
    compare.add_argument("query_key")
    efficiency_sub.add_parser("report")

    audit = sub.add_parser("audit")
    audit_sub = audit.add_subparsers(dest="audit_command", required=True)
    for name in ("light", "deep"):
        item = audit_sub.add_parser(name)
        item.add_argument("--samples", type=int)
        item.add_argument("--challenge-hex")

    sub.add_parser("replay")
    sub.add_parser("validate")
    receipt = sub.add_parser("receipt")
    receipt.add_argument("identity")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runtime, operations_path = _load_runtime()
    command = args.command
    if command == "status":
        _print(runtime.status())
    elif command == "doctor" or command == "validate":
        result = runtime.doctor()
        _print(result)
        return 0 if result["healthy"] else 2
    elif command == "genesis":
        _print({"genesis_identity": runtime.genesis_identity, "frame": runtime.current_frame.to_dict()})
    elif command == "boot-fingerprint":
        _print(runtime.boot_fingerprint)
    elif command == "frame":
        if args.frame_command == "show":
            _print({"current": runtime.current_frame.to_dict(include_bits=True), "candidate": runtime.candidate.frame.to_dict() if runtime.candidate else None})
        else:
            operator = _operator(args)
            result = runtime.execute(operator, mode=args.mode)
            if not args.candidate_only:
                result = {"candidate": result, "committed": runtime.commit()}
                _save_operations(runtime, operations_path)
            _print(result)
    elif command == "phase":
        if args.phase_command == "show":
            _print(runtime.status()["phase"])
        elif args.phase_command == "step":
            _print(runtime.execute_and_commit({"kind": "rotate", "parameters": {"amount": 1}, "ordered_connectors": ["Rotate"]}, mode="direct"))
            _save_operations(runtime, operations_path)
        else:
            remaining = (5184 - runtime.transition_count % 5184) % 5184
            _print({"transition_count": runtime.transition_count, "steps_to_complete_lock": remaining, "phase": runtime.status()["phase"]})
    elif command == "harmonic":
        operator = _operator(args)
        if args.harmonic_command == "compile":
            _print(HarmonicOperator.from_mapping(operator).to_dict())
        else:
            _print(runtime.execute_and_commit(operator, mode="direct"))
            _save_operations(runtime, operations_path)
    elif command == "hash72":
        _print({"tip": runtime.hash72_tip} if args.hash72_command == "tip" else {"trace": runtime.hash72_trace[-runtime.active_suffix_limit :]})
    elif command == "hash216":
        item = runtime.get_hash216(args.identity)
        if args.hash216_command == "index":
            item = {"logical_identity": item["logical_identity"], "index_root": item["index_root"], "indexes": item["indexes"]}
        _print(item)
    elif command == "vector":
        if args.vector_command == "query":
            _print(runtime.query_vectors(_operator(args)))
        elif args.vector_command == "retrieve":
            _print(runtime.execute_and_commit(_operator(args), mode="retrieval"))
            _save_operations(runtime, operations_path)
        elif args.vector_command == "admit":
            _print(runtime.commit())
            _save_operations(runtime, operations_path)
        else:
            _print(runtime.quarantine(args.identity))
    elif command == "efficiency":
        _print(runtime.compare_efficiency(args.query_key) if args.efficiency_command == "compare" else runtime.efficiency_report())
    elif command == "audit":
        challenge = bytes.fromhex(args.challenge_hex) if args.challenge_hex else None
        _print(runtime.audit(deep=args.audit_command == "deep", sample_count=args.samples, challenge=challenge).to_dict())
    elif command == "replay":
        _print(runtime.replay())
    elif command == "receipt":
        _print(runtime.receipt(args.identity))
    else:
        raise AssertionError(command)
    return 0


if __name__ == "__main__":
    sys.exit(main())
