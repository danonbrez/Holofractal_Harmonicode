"""Bash-friendly CLI for the Pass 220 Ubuntu application VM."""
from __future__ import annotations

import argparse
import json
import os
import shlex
from pathlib import Path
from typing import Any, Sequence

from hhs_runtime.pass220.application_vm_control_plane import (
    ApplicationVMControlPlane,
    ApplicationVMError,
)


def _load_env_file(path: str | None) -> None:
    if not path:
        return
    source = Path(path).expanduser()
    if not source.is_file():
        raise ApplicationVMError(f"HHS_APPLICATION_VM_ENV_FILE_NOT_FOUND:{source}")
    for raw in source.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def _emit(value: Any, *, pretty: bool) -> None:
    if pretty:
        text = json.dumps(
            value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False
        )
    else:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    print(text)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="hhs-vm",
        description="HHS Ubuntu application VM backend control plane",
    )
    root.add_argument("--env-file")
    root.add_argument("--repository-root")
    root.add_argument("--state-root")
    root.add_argument("--database")
    root.add_argument("--capability-token")
    root.add_argument("--pretty", action="store_true")
    commands = root.add_subparsers(dest="command", required=True)

    commands.add_parser("health")
    commands.add_parser("status")
    commands.add_parser("doctor")
    commands.add_parser("capabilities")

    shell = commands.add_parser("shell")
    shell.add_argument("shell_command", nargs=argparse.REMAINDER)

    invoke = commands.add_parser("invoke")
    invoke.add_argument("operation_id")
    invoke.add_argument("arguments_json")

    harmonicode = commands.add_parser("harmonicode")
    harmonicode.add_argument("expression")

    receipts = commands.add_parser("receipts")
    receipts.add_argument("--after", type=int, default=0)
    receipts.add_argument("--limit", type=int, default=100)

    replay = commands.add_parser("replay")
    replay.add_argument("receipt_hash72")

    token = commands.add_parser("token")
    token_sub = token.add_subparsers(dest="token_command", required=True)
    issue = token_sub.add_parser("issue")
    issue.add_argument("--principal", required=True)
    issue.add_argument("--scope", action="append", required=True)
    issue.add_argument("--ttl", type=int, default=900)

    return root


def _control_plane(args: argparse.Namespace) -> ApplicationVMControlPlane:
    _load_env_file(args.env_file)
    if args.repository_root:
        os.environ["HHS_APPLICATION_VM_REPOSITORY_ROOT"] = args.repository_root
    if args.state_root:
        os.environ["HHS_APPLICATION_VM_STATE_ROOT"] = args.state_root
    if args.database:
        os.environ["HHS_PASS190_DATABASE"] = args.database
    return ApplicationVMControlPlane.from_environment()


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        control = _control_plane(args)
        token = args.capability_token or os.environ.get(
            "HHS_APPLICATION_VM_CAPABILITY_TOKEN"
        )

        if args.command == "health":
            result = control.health()
        elif args.command == "status":
            result = control.status()
        elif args.command == "doctor":
            result = control.doctor()
        elif args.command == "capabilities":
            result = control.capabilities()
        elif args.command == "shell":
            words = list(args.shell_command)
            if words and words[0] == "--":
                words = words[1:]
            if not words:
                raise ApplicationVMError("HHS_APPLICATION_VM_SHELL_COMMAND_REQUIRED")
            result = control.shell(
                shlex.join(words),
                authorization_token=token,
            )
        elif args.command == "invoke":
            arguments = json.loads(args.arguments_json)
            if not isinstance(arguments, dict):
                raise ApplicationVMError("HHS_APPLICATION_VM_ARGUMENT_OBJECT_REQUIRED")
            result = control.invoke(
                args.operation_id,
                arguments,
                authorization_token=token,
            )
        elif args.command == "harmonicode":
            result = control.harmonicode(
                args.expression,
                authorization_token=token,
            )
        elif args.command == "receipts":
            result = control.receipts(after=args.after, limit=args.limit)
        elif args.command == "replay":
            result = control.replay(args.receipt_hash72)
        elif args.command == "token" and args.token_command == "issue":
            issued = control.issue_token(
                principal=args.principal,
                scopes=args.scope,
                ttl_seconds=args.ttl,
            )
            result = {
                "schema": "HHS_PASS_220_APPLICATION_VM_LOCAL_TOKEN_ISSUE_V1",
                "authorization_scheme": "HHS-Capability",
                "token": issued,
                "principal": args.principal,
                "scopes": sorted(set(args.scope)),
                "ttl_seconds": args.ttl,
                "remote_issuance": False,
            }
        else:
            raise ApplicationVMError("HHS_APPLICATION_VM_COMMAND_UNREACHABLE")

        _emit(result, pretty=args.pretty)
        return 0
    except (ApplicationVMError, ValueError, json.JSONDecodeError) as exc:
        _emit(
            {
                "schema": "HHS_PASS_220_APPLICATION_VM_CLI_ERROR_V1",
                "ok": False,
                "error": f"{type(exc).__name__}:{exc}",
            },
            pretty=True,
        )
        return 2
    except Exception as exc:
        _emit(
            {
                "schema": "HHS_PASS_220_APPLICATION_VM_CLI_ERROR_V1",
                "ok": False,
                "error": f"{type(exc).__name__}:{exc}",
            },
            pretty=True,
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
