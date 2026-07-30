"""Command-line authority surface for Pass 174."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Any

from .runtime import Pass174Error, Pass174Runtime
from .storage import PersistentEncryptedVectorStore


def _runtime(args: argparse.Namespace) -> Pass174Runtime:
    repository_root = Path(args.repository_root).resolve()
    state_root = Path(args.state_dir).resolve() if args.state_dir else repository_root / ".hhs" / "pass174"
    store = PersistentEncryptedVectorStore(
        state_root / "hash216_vectors.sqlite3",
        key_path=state_root / "hash216_vectors.key",
        active_suffix_limit=args.active_suffix_limit,
    )
    return Pass174Runtime(repository_root=repository_root, vector_store=store)


def _writes(raw: str) -> dict[int, int]:
    result: dict[int, int] = {}
    if not raw:
        return result
    for token in raw.split(","):
        position, value = token.split("=", 1)
        result[int(position)] = int(value)
    return result


def _emit(payload: Any) -> int:
    print(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False, default=str))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hhs-pass174", description="Pass 174 harmonic Hash216 VM81 authority")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--state-dir")
    parser.add_argument("--active-suffix-limit", type=int, default=72)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status")
    sub.add_parser("frame")
    sub.add_parser("phase")
    sub.add_parser("controller")
    sub.add_parser("efficiency")
    sub.add_parser("replay")
    sub.add_parser("legacy-foundation")

    execute = sub.add_parser("execute")
    execute.add_argument("--thread", type=int, default=0)
    execute.add_argument("--writes", default="0=1,8=1,72=1")
    execute.add_argument("--operation", default="VMRC_COMMIT")
    execute.add_argument("--capability-scope", default="P174_WHOLE_FRAME_STATE_WRITE")
    execute.add_argument("--no-retrieval", action="store_true")

    harmonic = sub.add_parser("harmonic-compile")
    harmonic.add_argument("--connectors", default="+,*,Or,==")
    harmonic.add_argument("--phase-offsets", default="0,8,9,36")
    harmonic.add_argument("--weights", default="1/4,1/4,1/4,1/4")
    harmonic.add_argument("--additive-endpoint", default="x+y")
    harmonic.add_argument("--multiplicative-endpoint", default="xy")

    audit = sub.add_parser("audit")
    audit.add_argument("--challenge", required=True)
    audit.add_argument("--sample-limit", type=int, default=16)
    audit.add_argument("--deep", action="store_true")

    query = sub.add_parser("query")
    query.add_argument("operation_key")
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        runtime = _runtime(args)
        if args.command == "status":
            payload = runtime.status()
            payload["persistent_vector_store"] = runtime.vector_store.storage_status()
            return _emit(payload)
        if args.command == "frame":
            snapshot = runtime.vmrc.snapshot()
            return _emit({
                "schema": "HHS_P174_FRAME_5184_V1",
                "snapshot_b64": snapshot.base64(),
                "frame_bytes": len(snapshot.to_bytes()),
                "frame_bits": len(snapshot.to_bytes()) * 8,
                "snapshot_hash72": runtime.vmrc.snapshot_hash72,
                "state_hash72": runtime.vmrc.state_hash72,
                "phase": asdict(runtime.phase),
            })
        if args.command == "phase":
            return _emit(asdict(runtime.phase))
        if args.command == "controller":
            return _emit(runtime.phase_controller())
        if args.command == "efficiency":
            return _emit(runtime.efficiency_report())
        if args.command == "replay":
            return _emit(runtime.replay())
        if args.command == "legacy-foundation":
            return _emit(runtime.legacy_manifest.to_dict())
        if args.command == "execute":
            return _emit(runtime.execute(
                thread=args.thread,
                writes=_writes(args.writes),
                operation=args.operation,
                capability_scope=args.capability_scope,
                prefer_retrieval=not args.no_retrieval,
            ))
        if args.command == "harmonic-compile":
            return _emit(runtime.register_harmonic_gate(
                connectors=args.connectors.split(","),
                phase_offsets=[int(item) for item in args.phase_offsets.split(",")],
                exact_weights=args.weights.split(","),
                additive_endpoint=args.additive_endpoint,
                multiplicative_endpoint=args.multiplicative_endpoint,
            ))
        if args.command == "audit":
            return _emit(runtime.audit(challenge=args.challenge, sample_limit=args.sample_limit, deep=args.deep))
        if args.command == "query":
            return _emit(runtime.query(args.operation_key))
        parser.error(f"unknown command {args.command}")
    except (Pass174Error, ValueError, OSError) as exc:
        print(json.dumps({
            "schema": "HHS_P174_CLI_REJECTION_V1",
            "classification": getattr(exc, "classification", type(exc).__name__),
            "detail": getattr(exc, "detail", str(exc)),
        }, sort_keys=True), file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(run())
