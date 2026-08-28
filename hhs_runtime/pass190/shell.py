"""Pass 190 Bash-like shell lowering.

The shell is a projection over Pass190CompletionContext. It never owns an
operation implementation. Commands outside the currently registered semantic
nucleus fail explicitly rather than fabricating success.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
from typing import Any, Optional, Sequence

from .completion import Pass190CompletionContext, Pass190CompletionError


REQUIRED_COMMAND_FAMILIES = (
    "status",
    "doctor",
    "login",
    "profile",
    "new",
    "open",
    "list",
    "files",
    "edit",
    "build",
    "run",
    "test",
    "install",
    "add",
    "remove",
    "assistant",
    "jobs",
    "artifacts",
    "export",
    "receipts",
    "replay",
    "config",
    "shell",
    "completion",
    "eval",
    "explain",
)

_IMPLEMENTED_META = {
    "status",
    "doctor",
    "operations",
    "python-census",
    "hydrate-preview",
    "eval",
    "invoke",
    "replay",
    "completion",
}


class ShellUnsupported(Pass190CompletionError):
    pass


def lower_shell_command(
    context: Pass190CompletionContext,
    command_line: str,
    *,
    authorization_token: str | None = None,
) -> dict[str, Any]:
    tokens = shlex.split(command_line)
    if not tokens:
        raise Pass190CompletionError("HHS_P190_SHELL_EMPTY")
    if tokens[0] != "hhs":
        return context.invoke_constructor(
            command_line,
            authorization_token=authorization_token,
        )
    if len(tokens) == 1:
        return {
            "mode": "INTERACTIVE_REPL_AVAILABLE",
            "commands": list(REQUIRED_COMMAND_FAMILIES),
        }

    command = tokens[1]
    if command == "status":
        return context.invoke(
            "system.status",
            {},
            surface="shell",
            authorization_token=authorization_token,
        )
    if command == "doctor":
        status = context.status()
        hydration = context.hydration_preview()
        return {
            "ok": hydration["blocker_count"] == 0,
            "runtime_mode": status["runtime_mode"],
            "governed_operation_count": status["governed_operation_count"],
            "python_public_callable_count": status["python_compatibility"][
                "public_callable_record_count"
            ],
            "hydration_blockers": hydration["blocker_count"],
            "hydrated_repository_root_hash216": hydration["topology"][
                "hydrated_repository_root_hash216"
            ],
        }
    if command == "operations":
        return {
            "operations": [
                {
                    "operation_id": item["operation_id"],
                    "constructor": item["harmonicode_constructor"],
                    "effect_class": item["effect_class"],
                    "capability_scope": item["capability_scope"],
                }
                for item in context.operations()
            ]
        }
    if command == "python-census":
        return context.compatibility_registry()
    if command == "hydrate-preview":
        since = None
        commit = "HEAD"
        index = 2
        while index < len(tokens):
            if tokens[index] == "--since" and index + 1 < len(tokens):
                since = tokens[index + 1]
                index += 2
            elif tokens[index] == "--commit" and index + 1 < len(tokens):
                commit = tokens[index + 1]
                index += 2
            else:
                raise Pass190CompletionError("HHS_P190_SHELL_ARGUMENT_INVALID")
        return context.hydration_preview(commit=commit, since_commit=since)
    if command == "eval":
        if len(tokens) != 3:
            raise Pass190CompletionError("HHS_P190_SHELL_EVAL_USAGE")
        return context.invoke_constructor(
            tokens[2],
            authorization_token=authorization_token,
        )
    if command == "invoke":
        if len(tokens) != 4:
            raise Pass190CompletionError("HHS_P190_SHELL_INVOKE_USAGE")
        arguments = json.loads(tokens[3])
        if not isinstance(arguments, dict):
            raise Pass190CompletionError("HHS_P190_SHELL_ARGUMENT_OBJECT_REQUIRED")
        return context.invoke(
            tokens[2],
            arguments,
            surface="shell",
            authorization_token=authorization_token,
        )
    if command == "replay":
        if len(tokens) != 3:
            raise Pass190CompletionError("HHS_P190_SHELL_REPLAY_USAGE")
        return context.replay(tokens[2])
    if command == "completion":
        return {
            "commands": sorted(
                set(REQUIRED_COMMAND_FAMILIES)
                | set(context.registry.by_shell)
                | _IMPLEMENTED_META
            )
        }

    if command in context.registry.by_shell:
        if len(tokens) != 3:
            raise Pass190CompletionError(
                f"HHS_P190_SHELL_REGISTERED_ARGUMENT_USAGE:{command}"
            )
        arguments = json.loads(tokens[2])
        if not isinstance(arguments, dict):
            raise Pass190CompletionError("HHS_P190_SHELL_ARGUMENT_OBJECT_REQUIRED")
        record = context.registry.by_shell[command]
        return context.invoke(
            record.operation_id,
            arguments,
            surface="shell",
            authorization_token=authorization_token,
        )

    if command in REQUIRED_COMMAND_FAMILIES:
        raise ShellUnsupported(
            f"HHS_P190_ACCEPTANCE_COMMAND_NOT_YET_BOUND:{command}"
        )
    suggestions = sorted(
        name
        for name in set(REQUIRED_COMMAND_FAMILIES) | set(context.registry.by_shell)
        if name.startswith(command[:1])
    )[:8]
    raise ShellUnsupported(
        f"HHS_P190_UNKNOWN_COMMAND:{command}:suggestions={suggestions}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hhs")
    parser.add_argument(
        "--database",
        default=".hhs_runtime_state/pass190/pass190-authority.sqlite3",
    )
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--capability-token")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    namespace = build_parser().parse_args(argv)
    context = Pass190CompletionContext(
        database_path=namespace.database,
        repository_root=namespace.repository_root,
        capability_secret=None,
    )
    line = "hhs " + " ".join(namespace.command)
    result = lower_shell_command(
        context,
        line,
        authorization_token=namespace.capability_token,
    )
    print(
        json.dumps(
            result,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
