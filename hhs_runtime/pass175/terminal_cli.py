"""CLI for terminal Pass 175 hydration, firmware, devices, and verification."""
from __future__ import annotations

import argparse
from base64 import b64decode
import json
import os
from pathlib import Path
from typing import Any, Sequence

from hhs_runtime.pass174 import Pass174Runtime
from .runtime import HydratedMicrocodeStore, Pass175Runtime
from .secure_store import EncryptedHash216Store
from .terminal import TerminalInstructionRequest, TerminalPass175Runtime


def _runtime() -> TerminalPass175Runtime:
    state_root = Path(os.environ.get("HHS_PASS175_STATE_DIR", ".hhs/pass175")).resolve()
    state_root.mkdir(parents=True, exist_ok=True)
    base = Pass175Runtime(
        authority=Pass174Runtime(repository_root=Path.cwd()),
        microcode_store=HydratedMicrocodeStore(state_root / "hash216_microcode.jsonl"),
    )
    return TerminalPass175Runtime(
        base_runtime=base,
        secure_store=EncryptedHash216Store(
            state_root / "hash216_microcode.sqlite3",
            key_path=state_root / "hash216_microcode.key",
        ),
        repository_root=Path.cwd(),
    )


def _print(value: Any) -> int:
    print(json.dumps(value, sort_keys=True, indent=2, default=str))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="hhs-pass175-terminal",
        description="Terminal Pass 175 Hash216-hydrated VM5184 × G243 processor",
    )
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    hydrate = commands.add_parser("hydrate")
    hydrate.add_argument("--no-seal", action="store_true")
    commands.add_parser("boot")
    decode = commands.add_parser("decode")
    decode.add_argument("exact_bytes_b64")
    decode.add_argument("--mode", default="LONG_64")
    execute = commands.add_parser("execute")
    execute.add_argument("exact_bytes_b64")
    execute.add_argument("--mode", default="LONG_64")
    execute.add_argument("--sequence", type=int, default=0)
    execute.add_argument("--thread", type=int, default=0)
    execute.add_argument("--allow-privileged", action="store_true")
    execute.add_argument("--delta", nargs="*", default=[])
    device = commands.add_parser("device")
    device.add_argument("device")
    device.add_argument("operation")
    device.add_argument("--payload", default="{}")
    commands.add_parser("replay")
    verify = commands.add_parser("verify")
    verify.add_argument("--native-root")
    verify.add_argument("--no-boot", action="store_true")
    backup = commands.add_parser("backup-store")
    backup.add_argument("destination")
    return root


def _delta(items: Sequence[str]) -> tuple[tuple[int, int], ...]:
    result = []
    for item in items:
        position, value = item.split("=", 1)
        result.append((int(position), int(value)))
    return tuple(result)


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    runtime = _runtime()
    try:
        if args.command == "status":
            return _print(runtime.status(native_root=os.environ.get("HHS_PASS175_NATIVE_ARTIFACT_DIR")))
        if args.command == "hydrate":
            return _print(runtime.cold_hydrate_terminal(seal=not args.no_seal))
        if args.command == "boot":
            if not runtime.secure_store.sealed:
                runtime.cold_hydrate_terminal(seal=True)
            return _print(runtime.boot_firmware())
        if args.command == "decode":
            record = runtime.decoder.decode(
                b64decode(args.exact_bytes_b64, validate=True),
                decoder_mode=args.mode,
            )
            return _print(record.to_dict())
        if args.command == "execute":
            return _print(runtime.execute_batch([
                TerminalInstructionRequest(
                    exact_bytes=b64decode(args.exact_bytes_b64, validate=True),
                    decoder_mode=args.mode,
                    sequence=args.sequence,
                    thread_id=args.thread,
                    allow_privileged=args.allow_privileged,
                    explicit_delta=_delta(args.delta),
                )
            ]))
        if args.command == "device":
            payload = json.loads(args.payload)
            return _print(runtime.execute_batch([
                TerminalInstructionRequest(
                    exact_bytes=b"\x90",
                    device=args.device,
                    device_operation=args.operation,
                    device_payload=payload,
                )
            ], max_workers=1))
        if args.command == "replay":
            return _print(runtime.replay())
        if args.command == "verify":
            if not runtime.secure_store.sealed:
                runtime.cold_hydrate_terminal(seal=True)
            return _print(runtime.terminal_verification(
                native_root=args.native_root,
                require_boot=not args.no_boot,
            ))
        if args.command == "backup-store":
            return _print(runtime.secure_store.backup(args.destination))
    except Exception as exc:
        _print({
            "schema": "HHS_PASS_175_TERMINAL_CLI_REJECTION_V1",
            "classification": getattr(exc, "classification", type(exc).__name__),
            "detail": getattr(exc, "detail", str(exc)),
        })
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
