from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .runtime import UniversalHydrationCompiler, supported_modality_families


COMMANDS = (
    "doctor", "detect", "plan", "build", "install", "ingest", "reconstruct", "compare",
    "optimize", "promote", "freeze", "replay", "verify", "package", "deploy", "status",
)
TREE_COMMANDS = ("snapshot", "enumerate", "ingest", "trace", "graph", "residuals", "verify", "replay", "freeze", "report")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hhs-hydrate")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in COMMANDS:
        item = sub.add_parser(name)
        item.add_argument("--source", default=".")
        item.add_argument("--output")
        item.add_argument("--profile", default="multimodal")
    tree = sub.add_parser("tree")
    tree_sub = tree.add_subparsers(dest="tree_command", required=True)
    for name in TREE_COMMANDS:
        item = tree_sub.add_parser(name)
        item.add_argument("--source", default=".")
        item.add_argument("--output")
    return parser


def _write_or_print(value: Any, output: str | None) -> None:
    text = json.dumps(value, sort_keys=True, indent=2) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def _tree(compiler: UniversalHydrationCompiler, name: str, source: str) -> dict[str, Any]:
    snapshot = compiler.snapshot_tree(source)
    if name in {"snapshot", "enumerate", "ingest", "verify", "freeze", "report"}:
        return snapshot
    if name == "trace":
        return compiler.sandbox_dynamic_trace(source)
    if name == "graph":
        return compiler.build_logic_graph(source, snapshot)
    if name == "residuals":
        return {"residuals": compiler.build_logic_graph(source, snapshot)["residuals"]}
    if name == "replay":
        return compiler.replay_snapshot(source, snapshot)
    raise SystemExit(f"unsupported tree command: {name}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    compiler = UniversalHydrationCompiler()
    if args.command == "tree":
        result = _tree(compiler, args.tree_command, args.source)
        _write_or_print(result, args.output)
        return 0

    snapshot = compiler.snapshot_tree(args.source)
    if args.command in {"doctor", "detect", "status"}:
        result = {
            "contract": "HHS-P182-UMHC-ROTR-VM81-H72-H216",
            "source_read_only": True,
            "modalities": list(supported_modality_families()),
            "entry_count": snapshot["entry_count"],
            "tree_root_hash216": snapshot["tree_root_hash216"],
        }
    elif args.command in {"plan", "ingest", "reconstruct", "compare", "optimize", "freeze", "verify"}:
        result = {
            "snapshot": snapshot,
            "ir": compiler.build_ir(snapshot),
            "graph": compiler.build_logic_graph(args.source, snapshot),
            "adapters": compiler.modality_reference_adapters(snapshot),
        }
    elif args.command == "replay":
        result = compiler.replay_snapshot(args.source, snapshot)
    elif args.command in {"build", "install", "package", "deploy"}:
        if not args.output:
            raise SystemExit("--output is required for package/build/install/deploy")
        result = compiler.build_portable_package(args.output, profile=args.profile, source_snapshot=snapshot)
        result["cold_start"] = compiler.verify_cold_start(args.output)
    elif args.command == "promote":
        result = {
            "classification": "PASS182_PROMOTION_REQUIRES_VM81_CALLBACK",
            "direct_cli_promotion_authority": False,
            "instruction": "Use UniversalHydrationCompiler.promote_constraint with inherited VM81 admission.",
        }
    else:
        raise SystemExit(f"unsupported command: {args.command}")
    _write_or_print(result, args.output if args.command not in {"build", "install", "package", "deploy"} else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
