"""Pass 192 shell-compatible command grammar.

The repository does not currently install a root ``hhs`` console entry point,
so this module exposes the exact required grammar through ``main(argv)`` and
``python -m hhs_runtime.pass192.cli``. Its tokens are intentionally identical
to the Pass 192 shell contract: ``hhs tensor fibonacci ...``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .runtime import Pass192Error, Pass192Runtime


def _cell(value: str) -> tuple[int, int]:
    try:
        left, right = value.split(",", 1)
        return int(left), int(right)
    except Exception as exc:
        raise argparse.ArgumentTypeError("cell must be ROW,COLUMN") from exc


def _authority(path: Optional[str], operation: str) -> Mapping[str, Any]:
    if path:
        return json.loads(Path(path).read_text("utf-8"))
    from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
    return HHSRuntimeController().authorized_tick(source="HHS_PASS192_CLI:" + operation)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hhs")
    parser.add_argument("--runtime-root", default=".hhs_runtime_state/pass192")
    tensor = parser.add_subparsers(dest="root_command", required=True).add_parser("tensor")
    fibonacci = tensor.add_subparsers(dest="tensor_command", required=True).add_parser("fibonacci")
    commands = fibonacci.add_subparsers(dest="operation", required=True)

    create = commands.add_parser("create")
    create.add_argument("--cell", required=True, type=_cell)
    create.add_argument("--authority-json")

    inspect = commands.add_parser("inspect")
    inspect.add_argument("tensor_id")

    materialize = commands.add_parser("materialize")
    materialize.add_argument("tensor_id")
    materialize.add_argument("--depth", required=True, type=int)
    materialize.add_argument("--authority-json")

    validate = commands.add_parser("validate")
    validate.add_argument("tensor_id")

    replay = commands.add_parser("replay")
    replay.add_argument("identity", nargs="?")
    return parser


def dispatch(namespace: argparse.Namespace) -> dict[str, Any]:
    runtime = Pass192Runtime(namespace.runtime_root)
    operation = namespace.operation
    if operation == "create":
        row, column = namespace.cell
        return runtime.create_tensor(
            row,
            column,
            authority_execution=_authority(namespace.authority_json, "P192.CellularFibonacciTensor"),
        )
    if operation == "inspect":
        return runtime.get_tensor(namespace.tensor_id)
    if operation == "materialize":
        return runtime.materialize_prefix(
            namespace.tensor_id,
            namespace.depth,
            authority_execution=_authority(namespace.authority_json, "P192.MaterializeTensorPrefix"),
        )
    if operation == "validate":
        return runtime.validate_tensor(namespace.tensor_id)
    if operation == "replay":
        return runtime.replay(namespace.identity)
    raise Pass192Error("HHS_P192_CLI_OPERATION_UNKNOWN")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = dispatch(args)
    except Pass192Error as exc:
        parser.error(exc.classification)
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
