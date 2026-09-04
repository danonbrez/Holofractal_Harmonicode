"""Pass169 CLI surface using the shared Pass169AlgebraService."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .public_service import Pass169AlgebraService, Pass169PublicSurfaceError

CLI_EQUIVALENTS = (
    "hhs algebra status",
    "hhs algebra source",
    "hhs algebra tokens",
    "hhs algebra ast",
    "hhs algebra symbols",
    "hhs algebra constraints",
    "hhs algebra inspect <node>",
    "hhs algebra typecheck",
    "hhs algebra normalize",
    "hhs algebra prove",
    "hhs algebra prove --constraint <id>",
    "hhs algebra evaluate --candidate",
    "hhs algebra admit <candidate-id>",
    "hhs algebra commit <candidate-id>",
    "hhs algebra receipt <transition-id>",
    "hhs algebra replay <transition-id>",
    "hhs algebra reverse <transition-id>",
    "hhs algebra divergence <transition-id>",
    "hhs algebra export-proof <transition-id>",
    "hhs algebra validate",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hhs")
    top = parser.add_subparsers(dest="namespace", required=True)
    algebra = top.add_parser("algebra")
    sub = algebra.add_subparsers(dest="operation", required=True)

    sub.add_parser("status")
    source = sub.add_parser("source")
    source.add_argument("source_id", nargs="?")
    for name in ("tokens", "ast", "symbols", "constraints", "typecheck", "normalize", "validate"):
        p = sub.add_parser(name)
        p.add_argument("--source-id")
    inspect = sub.add_parser("inspect")
    inspect.add_argument("node")
    inspect.add_argument("--source-id")
    prove = sub.add_parser("prove")
    prove.add_argument("--constraint")
    prove.add_argument("--source-id")
    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--candidate", action="store_true")
    evaluate.add_argument("--source-id")
    for name in ("admit", "commit"):
        p = sub.add_parser(name)
        p.add_argument("candidate_id")
    for name in ("receipt", "replay", "reverse", "divergence", "export-proof"):
        p = sub.add_parser(name)
        p.add_argument("transition_id")
    return parser


def _dispatch(service: Pass169AlgebraService, args: argparse.Namespace) -> dict:
    op = args.operation
    data = vars(args)
    if op == "prove" and data.get("constraint"):
        return service.dispatch("prove-constraint", constraint_id=data["constraint"], source_id=data.get("source_id"))
    if op == "evaluate":
        if not data.get("candidate"):
            raise Pass169PublicSurfaceError("PASS169_EVALUATE_REQUIRES_CANDIDATE_FLAG", http_status=400)
        return service.dispatch("evaluate-candidate", source_id=data.get("source_id"))
    if op in {"admit", "commit"}:
        return service.dispatch(op, candidate_id=data["candidate_id"])
    if op in {"receipt", "replay", "reverse", "divergence", "export-proof"}:
        return service.dispatch(op, transition_id=data["transition_id"])
    if op == "inspect":
        return service.dispatch(op, node=data["node"], source_id=data.get("source_id"))
    if op == "source":
        return service.dispatch(op, source_id=data.get("source_id"))
    return service.dispatch(op, source_id=data.get("source_id"))


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = Pass169AlgebraService()
    try:
        payload = _dispatch(service, args)
        code = 0
    except Pass169PublicSurfaceError as exc:
        payload = exc.to_dict()
        code = 2
    print(json.dumps(payload, sort_keys=True, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
