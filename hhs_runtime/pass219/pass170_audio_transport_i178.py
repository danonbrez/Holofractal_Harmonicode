"""Pass219 I178/I179 executable CLI/Python transports for Pass170 audio.

I178 established HTTP/CLI/Python parity. I179 upgrades those existing public
bindings so all invocation transports reuse the same signed Pass190 admission,
exact native audio/ECC security membrane, and governed internal adapter. Replay
is authenticated, native-revalidated, and non-reexecuting. No parallel token,
VM81, Hash72, Hash216, persistence, or cryptographic authority is created.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from fastapi import HTTPException

from hhs_backend.pass170_audio_language_routes import (
    AUDIO_CAPABILITY_SCOPE,
    AudioLanguageRunRequest,
    enforce_audio_public_admission,
    execute_audio_language_public_replay,
    execute_audio_language_public_request,
)

SCHEMA = "HHS_PASS170_AUDIO_TRANSPORT_I179_V1"
REPLAY_SCHEMA = "HHS_PASS170_AUDIO_REPLAY_TRANSPORT_I179_V1"
OPERATION_ID = "public.audio_language.feedback.run"
CLI_AUTHORIZATION_ENV = "HHS_PASS170_AUDIO_AUTHORIZATION"
CLI_COMMAND = "python -m hhs_runtime.pass219.pass170_audio_transport_i178 invoke"
CLI_REPLAY_COMMAND = "python -m hhs_runtime.pass219.pass170_audio_transport_i178 replay"
PYTHON_BINDING = "hhs_runtime.pass219.pass170_audio_transport_i178.invoke_audio_language_python"
PYTHON_REPLAY_BINDING = "hhs_runtime.pass219.pass170_audio_transport_i178.replay_audio_language_python"


def _request(payload: Mapping[str, Any]) -> AudioLanguageRunRequest:
    if not isinstance(payload, Mapping):
        raise ValueError("audio transport payload must be an object")
    return AudioLanguageRunRequest(**dict(payload))


def invoke_audio_language_python(
    payload: Mapping[str, Any],
    *,
    authorization: str | None,
    capability_secret: str | bytes | None = None,
) -> dict[str, Any]:
    """Execute audio through signed admission + exact native security binding."""
    admission = enforce_audio_public_admission(
        authorization,
        capability_secret=capability_secret,
    )
    result = asyncio.run(
        execute_audio_language_public_request(
            _request(payload),
            capability_admission=admission,
        )
    )
    result["transport"] = {
        "schema": SCHEMA,
        "surface": "python",
        "operation_id": OPERATION_ID,
        "binding": PYTHON_BINDING,
        "required_scope": AUDIO_CAPABILITY_SCOPE,
        "shared_admission_gate": True,
        "shared_internal_adapter": True,
        "native_abi_invoked": True,
        "native_security_binding_present": bool(result.get("native_security_binding")),
        "new_canonical_authority": False,
    }
    return result


def replay_audio_language_python(
    receipt_hash72: str,
    *,
    authorization: str | None,
    capability_secret: str | bytes | None = None,
) -> dict[str, Any]:
    """Replay a stored audio receipt without re-running audio/training writes."""
    admission = enforce_audio_public_admission(
        authorization,
        capability_secret=capability_secret,
    )
    result = execute_audio_language_public_replay(
        receipt_hash72,
        capability_admission=admission,
    )
    result["transport"] = {
        "schema": REPLAY_SCHEMA,
        "surface": "python",
        "operation_id": OPERATION_ID,
        "binding": PYTHON_REPLAY_BINDING,
        "required_scope": AUDIO_CAPABILITY_SCOPE,
        "shared_admission_gate": True,
        "native_replay_abi_invoked": True,
        "reexecuted": False,
        "new_canonical_authority": False,
    }
    return result


def _load_payload(args: argparse.Namespace) -> dict[str, Any]:
    selected = sum(
        value is not None
        for value in (args.payload_json, args.payload_file)
    )
    if selected > 1:
        raise ValueError("choose only one of --payload-json or --payload-file")
    if args.payload_json is not None:
        raw = args.payload_json
    elif args.payload_file is not None:
        raw = Path(args.payload_file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    if not raw.strip():
        raise ValueError("audio CLI requires a JSON payload")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("audio CLI payload must be a JSON object")
    return payload


def _authorization_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--authorization",
        default=None,
        help=os.environ.get(
            "HHS_PASS170_AUDIO_AUTHORIZATION_HELP",
            "HHS-Capability <token>",
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pass170-audio")
    sub = parser.add_subparsers(dest="command", required=True)
    invoke = sub.add_parser("invoke")
    invoke.add_argument("--payload-json")
    invoke.add_argument("--payload-file")
    _authorization_argument(invoke)

    replay = sub.add_parser("replay")
    replay.add_argument("receipt_hash72")
    _authorization_argument(replay)
    return parser


def _error_payload(exc: HTTPException) -> dict[str, Any]:
    return {
        "schema": "HHS_PASS170_AUDIO_CLI_ERROR_I179_V1",
        "ok": False,
        "operation_id": OPERATION_ID,
        "http_status": exc.status_code,
        "detail": exc.detail,
        "required_scope": AUDIO_CAPABILITY_SCOPE,
        "canonical_state_mutated": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    authorization = args.authorization or os.environ.get(CLI_AUTHORIZATION_ENV)
    try:
        if args.command == "invoke":
            result = invoke_audio_language_python(
                _load_payload(args),
                authorization=authorization,
            )
            result["transport"] = {
                **dict(result.get("transport") or {}),
                "surface": "cli",
                "cli_command": CLI_COMMAND,
                "python_binding_reused": PYTHON_BINDING,
            }
        elif args.command == "replay":
            result = replay_audio_language_python(
                args.receipt_hash72,
                authorization=authorization,
            )
            result["transport"] = {
                **dict(result.get("transport") or {}),
                "surface": "cli",
                "cli_command": CLI_REPLAY_COMMAND,
                "python_binding_reused": PYTHON_REPLAY_BINDING,
                "reexecuted": False,
            }
        else:
            raise RuntimeError("unreachable audio CLI command")
    except HTTPException as exc:
        print(json.dumps(_error_payload(exc), sort_keys=True, separators=(",", ":")))
        return 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        error = {
            "schema": "HHS_PASS170_AUDIO_CLI_INPUT_ERROR_I179_V1",
            "ok": False,
            "operation_id": OPERATION_ID,
            "detail": f"{type(exc).__name__}:{exc}",
            "canonical_state_mutated": False,
        }
        print(json.dumps(error, sort_keys=True, separators=(",", ":")))
        return 2

    print(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AUDIO_CAPABILITY_SCOPE",
    "CLI_AUTHORIZATION_ENV",
    "CLI_COMMAND",
    "CLI_REPLAY_COMMAND",
    "OPERATION_ID",
    "PYTHON_BINDING",
    "PYTHON_REPLAY_BINDING",
    "REPLAY_SCHEMA",
    "SCHEMA",
    "build_parser",
    "invoke_audio_language_python",
    "main",
    "replay_audio_language_python",
]
