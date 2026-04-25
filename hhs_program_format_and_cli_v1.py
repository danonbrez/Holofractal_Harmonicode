"""
hhs_program_format_and_cli_v1.py

.hhsprog program format and CLI runner for HARMONICODE.

Purpose
-------
Provide a simple executable program format for the general runtime.

Supported commands
------------------
run      Execute a .hhsprog file through AuditedRunner.
verify   Verify receipt-chain continuity from a saved .hhsrun file.
inspect  Print summary of a .hhsprog or .hhsrun file.
demo     Create a demo .hhsprog file.

File formats
------------
.hhsprog:
{
  "format": "HHS_PROGRAM_V1",
  "program_name": "example",
  "operations": [
    {"op": "ADD", "args": [2, 3]},
    {"op": "SORT", "args": [[3, 1, 2]]},
    {"op": "BINARY_SEARCH", "args": [[1, 2, 3], 2]}
  ],
  "persist": true
}

.hhsrun:
{
  "format": "HHS_RUN_RESULT_V1",
  "program_name": "...",
  "results": [...],
  "receipts": [...],
  "chain": {...},
  "storage_report": {...}
}
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json
import sys

from hhs_general_runtime_layer_v1 import (
    AuditedRunner,
    DEFAULT_KERNEL_PATH,
    canonicalize_for_hash72,
)

from hhs_receipt_replay_verifier_v1 import HHSReceiptReplayVerifierV1

try:
    from hhs_database_integration_layer_v1 import HHSRuntimeDatabaseBridgeV1
except Exception:
    HHSRuntimeDatabaseBridgeV1 = None


PROGRAM_FORMAT = "HHS_PROGRAM_V1"
RUN_RESULT_FORMAT = "HHS_RUN_RESULT_V1"


class HHSProgramFormatError(RuntimeError):
    pass


def load_json(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, payload: Dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def validate_program(program: Dict[str, Any]) -> None:
    if program.get("format") != PROGRAM_FORMAT:
        raise HHSProgramFormatError(f"Expected format {PROGRAM_FORMAT}")
    if not program.get("program_name"):
        raise HHSProgramFormatError("program_name is required")
    ops = program.get("operations")
    if not isinstance(ops, list):
        raise HHSProgramFormatError("operations must be a list")
    for idx, step in enumerate(ops):
        if not isinstance(step, dict):
            raise HHSProgramFormatError(f"operation[{idx}] must be an object")
        if "op" not in step:
            raise HHSProgramFormatError(f"operation[{idx}] missing op")
        if "args" in step and not isinstance(step["args"], list):
            raise HHSProgramFormatError(f"operation[{idx}].args must be a list")


def execute_program(
    program: Dict[str, Any],
    *,
    kernel_path: str | Path = DEFAULT_KERNEL_PATH,
    persist: Optional[bool] = None,
    db_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    validate_program(program)

    runner = AuditedRunner(kernel_path)
    results: List[Dict[str, Any]] = []

    for idx, step in enumerate(program["operations"]):
        op = step["op"]
        args = step.get("args", [])
        input_payload = {
            "program_name": program["program_name"],
            "step_index": idx,
            "step": step,
        }
        out = runner.execute(op, *args, input_payload=input_payload)
        results.append({
            "step_index": idx,
            "op": op,
            "args": canonicalize_for_hash72(args),
            "output": out,
        })

        if not out.get("ok") and not bool(program.get("continue_on_quarantine", False)):
            break

    verifier = HHSReceiptReplayVerifierV1(kernel_path)
    replay = verifier.verify_runner(runner).to_dict()

    storage_report = None
    do_persist = bool(program.get("persist", False)) if persist is None else bool(persist)
    if do_persist:
        if HHSRuntimeDatabaseBridgeV1 is None:
            storage_report = {
                "ok": False,
                "reason": "database integration layer unavailable",
            }
        else:
            bridge_kwargs = {}
            if db_path is not None:
                bridge_kwargs["db_path"] = db_path
            bridge = HHSRuntimeDatabaseBridgeV1(**bridge_kwargs)
            try:
                storage_report = bridge.store_runner(
                    runner,
                    program_name=program["program_name"],
                    metadata={
                        "program_format": PROGRAM_FORMAT,
                        "operation_count": len(program["operations"]),
                    },
                ).to_dict()
            finally:
                bridge.close()

    return {
        "format": RUN_RESULT_FORMAT,
        "program_name": program["program_name"],
        "program_hash72": runner.authority.commit(program, domain="HHS_PROGRAM_FILE"),
        "operation_count_declared": len(program["operations"]),
        "operation_count_executed": len(results),
        "results": results,
        "receipts": [r.to_dict() for r in runner.commitments.receipts],
        "chain": runner.commitments.verify_chain(),
        "replay": replay,
        "storage_report": storage_report,
        "all_ok": all(r["output"].get("ok") for r in results) and replay.get("ok") is True,
    }


def inspect_file(path: str | Path) -> Dict[str, Any]:
    payload = load_json(path)
    fmt = payload.get("format")
    if fmt == PROGRAM_FORMAT:
        validate_program(payload)
        return {
            "type": PROGRAM_FORMAT,
            "program_name": payload["program_name"],
            "operation_count": len(payload["operations"]),
            "operations": [step["op"] for step in payload["operations"]],
            "persist": bool(payload.get("persist", False)),
        }
    if fmt == RUN_RESULT_FORMAT:
        receipts = payload.get("receipts", [])
        return {
            "type": RUN_RESULT_FORMAT,
            "program_name": payload.get("program_name"),
            "operation_count_executed": payload.get("operation_count_executed"),
            "receipt_count": len(receipts),
            "all_ok": payload.get("all_ok"),
            "tip_hash72": payload.get("chain", {}).get("tip_hash72"),
            "replay_ok": payload.get("replay", {}).get("ok"),
            "storage_ok": (payload.get("storage_report") or {}).get("ok"),
        }
    raise HHSProgramFormatError(f"Unknown file format: {fmt}")


def verify_run_file(path: str | Path, *, kernel_path: str | Path = DEFAULT_KERNEL_PATH) -> Dict[str, Any]:
    payload = load_json(path)
    if payload.get("format") != RUN_RESULT_FORMAT:
        raise HHSProgramFormatError(f"Expected format {RUN_RESULT_FORMAT}")

    verifier = HHSReceiptReplayVerifierV1(kernel_path)
    expected_tip = payload.get("chain", {}).get("tip_hash72")
    report = verifier.verify(payload.get("receipts", []), expected_tip_hash72=expected_tip).to_dict()
    return {
        "file": str(path),
        "program_name": payload.get("program_name"),
        "verification": report,
    }


def demo_program() -> Dict[str, Any]:
    return {
        "format": PROGRAM_FORMAT,
        "program_name": "HHS_DEMO_PROGRAM_V1",
        "persist": False,
        "continue_on_quarantine": False,
        "operations": [
            {"op": "ADD", "args": [2, 3]},
            {"op": "MUL", "args": [5, 7]},
            {"op": "SORT", "args": [[19, 3, 42, 11, 7, 7, 1]]},
            {"op": "BINARY_SEARCH", "args": [[1, 3, 7, 11, 19, 42, 55], 42]},
        ],
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="HHS .hhsprog CLI runner")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run a .hhsprog file")
    p_run.add_argument("program")
    p_run.add_argument("-o", "--output", default=None)
    p_run.add_argument("--persist", action="store_true")
    p_run.add_argument("--db-path", default=None)
    p_run.add_argument("--kernel-path", default=str(DEFAULT_KERNEL_PATH))

    p_verify = sub.add_parser("verify", help="Verify a .hhsrun file")
    p_verify.add_argument("run_file")
    p_verify.add_argument("--kernel-path", default=str(DEFAULT_KERNEL_PATH))

    p_inspect = sub.add_parser("inspect", help="Inspect a .hhsprog or .hhsrun file")
    p_inspect.add_argument("file")

    p_demo = sub.add_parser("demo", help="Write a demo .hhsprog file")
    p_demo.add_argument("-o", "--output", default="/mnt/data/demo_program.hhsprog")

    args = parser.parse_args(argv)

    try:
        if args.command == "run":
            program = load_json(args.program)
            result = execute_program(
                program,
                kernel_path=args.kernel_path,
                persist=args.persist or bool(program.get("persist", False)),
                db_path=args.db_path,
            )
            text = json.dumps(result, indent=2, ensure_ascii=False)
            if args.output:
                Path(args.output).write_text(text, encoding="utf-8")
            else:
                print(text)
            return 0 if result.get("all_ok") else 1

        if args.command == "verify":
            report = verify_run_file(args.run_file, kernel_path=args.kernel_path)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report["verification"].get("ok") else 1

        if args.command == "inspect":
            report = inspect_file(args.file)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0

        if args.command == "demo":
            write_json(args.output, demo_program())
            print(args.output)
            return 0

    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": type(exc).__name__,
            "message": str(exc),
        }, indent=2, ensure_ascii=False), file=sys.stderr)
        return 2

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
