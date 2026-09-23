"""Host CLI for the Pass 220 I043 Ubuntu guest runtime."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
import time
from typing import Any, Sequence

from hhs_runtime.pass220.ubuntu_guest_runtime import (
    GuestRuntimeConfig,
    GuestRuntimeError,
    UbuntuGuestRuntime,
)


def _emit(value: Any, *, pretty: bool) -> None:
    print(
        json.dumps(
            value,
            sort_keys=True,
            indent=2 if pretty else None,
            separators=None if pretty else (",", ":"),
            ensure_ascii=False,
        )
    )


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="hhs-guest",
        description="Host-side Ubuntu guest lifecycle and PTY transport",
    )
    root.add_argument("--pretty", action="store_true")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("verify", "prepare", "start", "status", "stop", "restart"):
        commands.add_parser(name)

    pty_exec = commands.add_parser("pty-exec")
    pty_exec.add_argument("--rows", type=int, default=24)
    pty_exec.add_argument("--cols", type=int, default=80)
    pty_exec.add_argument("--timeout", type=float, default=60.0)
    pty_exec.add_argument("remote_command", nargs=argparse.REMAINDER)
    return root


def _runtime() -> UbuntuGuestRuntime:
    return UbuntuGuestRuntime(GuestRuntimeConfig.from_environment())


def _pty_exec(
    runtime: UbuntuGuestRuntime,
    words: Sequence[str],
    *,
    rows: int,
    cols: int,
    timeout: float,
) -> dict[str, Any]:
    command = list(words)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise GuestRuntimeError("HHS_GUEST_PTY_COMMAND_REQUIRED")
    if timeout <= 0 or timeout > 86400:
        raise GuestRuntimeError("HHS_GUEST_PTY_TIMEOUT_INVALID")

    collected = bytearray()
    deadline = time.monotonic() + timeout
    with runtime.open_pty(command, rows=rows, cols=cols) as session:
        while True:
            chunk = session.read(timeout=0.05)
            if chunk:
                collected.extend(chunk)
            code = session.process.poll()
            if code is not None:
                while True:
                    tail = session.read(timeout=0.0)
                    if not tail:
                        break
                    collected.extend(tail)
                return {
                    **session.snapshot(),
                    "exit_status": code,
                    "remote_command": shlex.join(command),
                    "output_utf8": collected.decode("utf-8", errors="replace"),
                    "canonical_state_authority": False,
                }
            if time.monotonic() >= deadline:
                session.send_signal(15)
                raise GuestRuntimeError("HHS_GUEST_PTY_EXEC_TIMEOUT")


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        runtime = _runtime()
        if args.command == "verify":
            result = {
                "schema": "HHS_PASS_220_I043_GUEST_IMAGE_VERIFY_V1",
                "base": runtime.verify_base_image(),
                "canonical_state_authority": False,
            }
        elif args.command == "prepare":
            result = runtime.prepare_overlay()
        elif args.command == "start":
            result = runtime.start()
        elif args.command == "status":
            result = runtime.status()
        elif args.command == "stop":
            result = runtime.stop()
        elif args.command == "restart":
            result = runtime.restart()
        elif args.command == "pty-exec":
            result = _pty_exec(
                runtime,
                args.remote_command,
                rows=args.rows,
                cols=args.cols,
                timeout=args.timeout,
            )
        else:
            raise GuestRuntimeError("HHS_GUEST_COMMAND_UNREACHABLE")
        _emit(result, pretty=args.pretty)
        return 0
    except (GuestRuntimeError, ValueError, OSError) as exc:
        _emit(
            {
                "schema": "HHS_PASS_220_I043_GUEST_CLI_ERROR_V1",
                "ok": False,
                "error": f"{type(exc).__name__}:{exc}",
            },
            pretty=True,
        )
        return 2
    except Exception as exc:
        _emit(
            {
                "schema": "HHS_PASS_220_I043_GUEST_CLI_ERROR_V1",
                "ok": False,
                "error": f"{type(exc).__name__}:{exc}",
            },
            pretty=True,
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
