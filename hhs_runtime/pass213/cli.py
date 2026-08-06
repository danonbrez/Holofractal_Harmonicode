"""Command-line transport for the Pass 213 Iteration 9 governed surface."""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Sequence, TextIO

from hhs_backend.runtime.hhs_pass213_governed_surface_v2 import (
    ALLOWED_SCOPES,
    Pass213GovernedSurface,
    Pass213SurfaceError,
    get_default_pass213_surface,
)


def _print(value: Any, output: TextIO) -> None:
    print(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False), file=output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hhs-pass213",
        description="Pass 213 governed compiled-ROM projection authority",
    )
    parser.add_argument(
        "--capability",
        default=None,
        help="Scoped Pass 213 capability; defaults to HHS_PASS213_CAPABILITY",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("status")
    commands.add_parser("catalog")

    compiled = commands.add_parser("compiled-rom")
    compiled_commands = compiled.add_subparsers(dest="compiled_command", required=True)
    compiled_commands.add_parser("status")
    compiled_lookup = compiled_commands.add_parser("lookup")
    compiled_lookup.add_argument("object_id")

    memory = commands.add_parser("memory-integrity")
    memory_commands = memory.add_subparsers(dest="memory_command", required=True)
    memory_commands.add_parser("status")
    memory_commands.add_parser("scan")

    timestamp = commands.add_parser("timestamp-boundary")
    timestamp_commands = timestamp.add_subparsers(dest="timestamp_command", required=True)
    timestamp_commands.add_parser("status")
    timestamp_lookup = timestamp_commands.add_parser("lookup")
    timestamp_lookup.add_argument("object_id")

    tensor = commands.add_parser("tensor-lattice")
    tensor_commands = tensor.add_subparsers(dest="tensor_command", required=True)
    tensor_commands.add_parser("status")
    tensor_lookup = tensor_commands.add_parser("lookup")
    tensor_lookup.add_argument("object_id")
    tensor_commands.add_parser("verify")

    inventory = commands.add_parser("inventory")
    inventory_commands = inventory.add_subparsers(dest="inventory_command", required=True)
    inventory_commands.add_parser("status")
    inventory_commands.add_parser("verify")

    receipt = commands.add_parser("receipt")
    receipt_commands = receipt.add_subparsers(dest="receipt_command", required=True)
    receipt_get = receipt_commands.add_parser("get")
    receipt_get.add_argument("object_id")

    capability = commands.add_parser("capability")
    capability_commands = capability.add_subparsers(dest="capability_command", required=True)
    issue = capability_commands.add_parser("issue")
    issue.add_argument("--subject", required=True)
    issue.add_argument("--scope", action="append", required=True, choices=sorted(ALLOWED_SCOPES))
    issue.add_argument("--ttl-seconds", type=int, default=900)

    return parser


def _operation(args: argparse.Namespace) -> tuple[str, dict[str, Any]]:
    if args.command == "status":
        return "surface.status", {}
    if args.command == "catalog":
        return "surface.catalog", {}
    if args.command == "compiled-rom":
        if args.compiled_command == "status":
            return "compiled.status", {}
        return "compiled.lookup", {"object_id": args.object_id}
    if args.command == "memory-integrity":
        if args.memory_command == "status":
            return "surface.status", {}
        return "integrity.scan", {}
    if args.command == "timestamp-boundary":
        if args.timestamp_command == "status":
            return "timestamp.status", {}
        return "timestamp.lookup", {"object_id": args.object_id}
    if args.command == "tensor-lattice":
        if args.tensor_command == "status":
            return "tensor.status", {}
        if args.tensor_command == "verify":
            return "tensor.verify", {}
        return "tensor.lookup", {"object_id": args.object_id}
    if args.command == "inventory":
        if args.inventory_command == "status":
            return "inventory.status", {}
        return "inventory.verify", {}
    if args.command == "receipt":
        return "receipt.lookup", {"object_id": args.object_id}
    raise RuntimeError("PASS213_CLI_OPERATION_UNRESOLVED")


def main(
    argv: Sequence[str] | None = None,
    *,
    surface: Pass213GovernedSurface | None = None,
    output: TextIO | None = None,
) -> int:
    stream = output or sys.stdout
    args = build_parser().parse_args(argv)
    authority = surface or get_default_pass213_surface()
    try:
        if args.command == "capability":
            token = authority.capabilities.issue(
                subject=args.subject,
                scopes=args.scope,
                ttl_seconds=args.ttl_seconds,
            )
            _print(
                {
                    "schema": "HHS_PASS_213_LOCAL_CAPABILITY_ISSUANCE_V1",
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
        operation, arguments = _operation(args)
        capability = args.capability or os.environ.get("HHS_PASS213_CAPABILITY")
        _print(
            authority.invoke(
                operation,
                arguments,
                capability=capability,
            ),
            stream,
        )
        return 0
    except Pass213SurfaceError as exc:
        _print(
            {
                "schema": "HHS_PASS_213_GOVERNED_CLI_REJECTION_V1",
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
                "schema": "HHS_PASS_213_GOVERNED_CLI_FAILURE_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
            stream,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
