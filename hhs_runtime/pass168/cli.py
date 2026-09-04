from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .public_service import Pass168ParameterCircuitError, Pass168ParameterCircuitService

REQUIRED_CLI_OPERATIONS = (
    "status", "inspect", "source", "map", "threads", "banks", "parameters", "get", "set",
    "evaluate", "evaluate-upper", "evaluate-lower", "compare", "dependencies", "affected-cells",
    "commit", "rollback", "replay", "receipt", "validate", "benchmark",
)


def _exact_value(text: str) -> dict[str, int]:
    token = text.strip()
    if "/" in token:
        left, right = token.split("/", 1)
        numerator = int(left)
        denominator = int(right)
    else:
        numerator = int(token)
        denominator = 1
    if denominator <= 0:
        raise argparse.ArgumentTypeError("exact rational denominator must be positive")
    return {"numerator": numerator, "denominator": denominator}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hhs")
    root = parser.add_subparsers(dest="surface", required=True)
    circuit = root.add_parser("parameter-circuit")
    circuit.add_argument("--state-dir")
    circuit.add_argument("--output", choices=("text", "json", "jsonl"), default="json")
    operations = circuit.add_subparsers(dest="operation", required=True)

    for name in ("status", "inspect", "source", "map", "threads", "banks", "parameters", "validate"):
        operations.add_parser(name)

    get = operations.add_parser("get")
    get.add_argument("parameter_id")

    set_cmd = operations.add_parser("set")
    set_cmd.add_argument("parameter_id")
    set_cmd.add_argument("value", type=_exact_value)

    evaluate = operations.add_parser("evaluate")
    evaluate.add_argument("--candidate-id")
    evaluate.add_argument("--lane", choices=("upper", "lower", "successor"))

    compare = operations.add_parser("compare")
    compare.add_argument("comparator_id")

    dependencies = operations.add_parser("dependencies")
    dependencies.add_argument("parameter_id")

    affected = operations.add_parser("affected-cells")
    affected.add_argument("parameter_id")

    commit = operations.add_parser("commit")
    commit.add_argument("candidate_id", nargs="?")

    for name in ("rollback", "replay", "receipt"):
        command = operations.add_parser(name)
        command.add_argument("transition_id")

    benchmark = operations.add_parser("benchmark")
    benchmark.add_argument("--repeats", type=int, default=12)
    return parser


def _select_single_candidate(service: Pass168ParameterCircuitService, explicit: str | None) -> str:
    if explicit:
        return explicit
    candidates = service.list_candidate_ids()
    if len(candidates) != 1:
        raise Pass168ParameterCircuitError(
            "PASS168_CANDIDATE_AMBIGUOUS",
            "operation requires --candidate-id unless exactly one durable candidate exists",
            details={"candidate_ids": candidates},
        )
    return candidates[0]


def _execute(args: argparse.Namespace) -> dict[str, Any]:
    service = Pass168ParameterCircuitService(args.state_dir)
    op = args.operation
    if op in {"status", "inspect", "source", "map", "threads", "banks", "parameters", "validate"}:
        return service.dispatch(op)
    if op == "get":
        return service.dispatch(op, parameter_id=args.parameter_id)
    if op == "set":
        return service.dispatch(op, parameter_id=args.parameter_id, value=args.value)
    if op == "evaluate":
        candidate_id = _select_single_candidate(service, args.candidate_id)
        result = service.evaluate_candidate(candidate_id)
        if args.lane:
            result = {
                "candidate_id": candidate_id,
                "lane": args.lane,
                "matrix": result["candidate_state"][args.lane],
                "canonical_state_mutated": False,
            }
        return result
    if op == "compare":
        return service.dispatch(op, comparator_id=args.comparator_id)
    if op in {"dependencies", "affected-cells"}:
        return service.dispatch(op, parameter_id=args.parameter_id)
    if op == "commit":
        return service.dispatch(op, candidate_id=args.candidate_id)
    if op in {"rollback", "replay", "receipt"}:
        return service.dispatch(op, transition_id=args.transition_id)
    if op == "benchmark":
        return service.dispatch(op, repeats=args.repeats)
    raise AssertionError(op)


def _render(value: dict[str, Any], profile: str) -> str:
    if profile == "json":
        return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)
    if profile == "jsonl":
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    lines = [f"{key}: {json.dumps(item, sort_keys=True, ensure_ascii=False)}" for key, item in value.items()]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = _execute(args)
    except Pass168ParameterCircuitError as exc:
        print(_render(exc.as_dict(), args.output))
        return 2
    except Exception as exc:
        error = {
            "ok": False,
            "error": "PASS168_UNHANDLED_RUNTIME_ERROR",
            "message": f"{type(exc).__name__}:{exc}",
            "floating_point_canonical_authority": False,
        }
        print(_render(error, args.output))
        return 3
    print(_render(result, args.output))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
