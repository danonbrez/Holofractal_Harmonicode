"""Pass 213 Iteration 10 native dispatch command-line transport."""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Sequence, TextIO

from hhs_backend.runtime.hhs_pass213_governed_native_dispatch_v1 import (
    DISPATCH_SCOPES,
    GovernedNativeDispatchService,
    Pass213NativeDispatchError,
    get_default_native_dispatch_service,
)


def _print(value: Any, output: TextIO) -> None:
    print(
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False),
        file=output,
    )


def _integer(value: str) -> int:
    try:
        result = int(value, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    if not 0 <= result < 1 << 64:
        raise argparse.ArgumentTypeError(
            "integer must be in the unsigned 64-bit range"
        )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hhs-pass213-dispatch",
        description="Pass 213 governed native compiled dispatch",
    )
    parser.add_argument(
        "--capability",
        default=None,
        help=(
            "Scoped native-dispatch capability; defaults to "
            "HHS_PASS213_DISPATCH_CAPABILITY"
        ),
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")

    execute = commands.add_parser("execute")
    execute.add_argument("--entry-hash216", required=True)
    execute.add_argument("--operation-id", required=True)
    execute.add_argument("--expected-parent-hash216", required=True)
    execute.add_argument("--expected-tensor-root-hash216", required=True)
    execute.add_argument("--timestamp-ns", type=int, required=True)
    execute.add_argument("--hydration-lane", type=int, default=0)
    execute.add_argument("--operand", action="append", type=_integer, required=True)
    execute.add_argument("--read", action="append", default=[])
    execute.add_argument("--write", action="append", default=[])

    receipt = commands.add_parser("receipt")
    receipt.add_argument("sequence", type=int)

    capability = commands.add_parser("capability")
    capability_commands = capability.add_subparsers(
        dest="capability_command", required=True
    )
    issue = capability_commands.add_parser("issue")
    issue.add_argument("--subject", required=True)
    issue.add_argument(
        "--scope",
        action="append",
        required=True,
        choices=sorted(DISPATCH_SCOPES),
    )
    issue.add_argument("--ttl-seconds", type=int, default=900)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    service: GovernedNativeDispatchService | None = None,
    output: TextIO | None = None,
) -> int:
    stream = output or sys.stdout
    args = build_parser().parse_args(argv)
    authority = service or get_default_native_dispatch_service()
    try:
        if args.command == "capability":
            token = authority.capabilities.issue(
                subject=args.subject,
                scopes=args.scope,
                ttl_seconds=args.ttl_seconds,
            )
            _print(
                {
                    "schema": "HHS_PASS_213_LOCAL_NATIVE_DISPATCH_CAPABILITY_ISSUANCE_V1",
                    "ok": True,
                    "network_exposed": False,
                    "subject": args.subject,
                    "scopes": sorted(set(args.scope)),
                    "ttl_seconds": args.ttl_seconds,
                    "capability": token,
                },
                stream,
            )
            return 0
        if args.command == "status":
            operation = "native-dispatch.status"
            arguments: dict[str, Any] = {}
        elif args.command == "receipt":
            operation = "native-dispatch.receipt"
            arguments = {"sequence": args.sequence}
        else:
            operation = "native-dispatch.execute"
            arguments = {
                "entry_hash216": args.entry_hash216,
                "operation_id": args.operation_id,
                "expected_parent_hash216": args.expected_parent_hash216,
                "expected_tensor_root_hash216": (
                    args.expected_tensor_root_hash216
                ),
                "timestamp_ns": args.timestamp_ns,
                "hydration_lane": args.hydration_lane,
                "operands": tuple(args.operand),
                "read_set": tuple(sorted(set(args.read))),
                "write_set": tuple(sorted(set(args.write))),
            }
        capability = args.capability or os.environ.get(
            "HHS_PASS213_DISPATCH_CAPABILITY"
        )
        _print(
            authority.invoke(
                operation,
                arguments,
                capability=capability,
            ),
            stream,
        )
        return 0
    except Pass213NativeDispatchError as exc:
        _print(
            {
                "schema": "HHS_PASS_213_NATIVE_DISPATCH_CLI_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
            stream,
        )
        return 2
    except (OSError, ValueError, RuntimeError) as exc:
        _print(
            {
                "schema": "HHS_PASS_213_NATIVE_DISPATCH_CLI_FAILURE_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
            stream,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
