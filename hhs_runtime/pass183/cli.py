"""Human-readable command surface for Pass 183 probability hydration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from . import ADAPTER_EQUATIONS, GLOBAL_MODULUS, Pass183Error, ProbabilityHydrationRuntime


def _load_manifest(value: str | None) -> dict[str, Any]:
    if value is None:
        return {}
    path = Path(value)
    text = path.read_text(encoding="utf-8") if path.is_file() else value
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise Pass183Error("P183_REJECT_PARSE", "manifest")
    return parsed


def _equation(args: argparse.Namespace) -> str:
    if args.equation_file:
        return Path(args.equation_file).read_text(encoding="utf-8").strip()
    if args.equation:
        return args.equation
    try:
        return ADAPTER_EQUATIONS[args.adapter]
    except KeyError as exc:
        raise Pass183Error("P183_REJECT_PARSE", "adapter") from exc


def _emit(value: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=2, sort_keys=True, default=str))
        return
    classification = value.get("classification", "P183_RESULT")
    print(f"Status: {classification}")
    if "evaluation" in value:
        evaluation = value["evaluation"]
        print(f"Adapter: {evaluation['adapter']}")
        print(f"Equation valid: {evaluation['source_equation_true']}")
        print(f"Domain valid: {evaluation['probability_domain_valid']}")
        print(f"Membranes: {len(evaluation['membranes'])}")
        print(f"Exact result: {evaluation['result_exact']}")
        print(f"Zero bypass: {evaluation['typed_zero_bypass']}")
        print(f"u^72 closure: {evaluation['closure_exact']}")
        residue = evaluation["outer_modulus"]
        print(f"Outer residue: {residue.get('residue', residue['classification'])}")
        print(f"Hash216: {evaluation['hash216']['logical_identity_sha256']}")
        if "receipt" in value:
            print(f"Hash72 receipt: {value['receipt']['receipt_hash72']}")
    elif "membranes" in value:
        print(f"Adapter: {value['adapter']}")
        print(f"Equation identity: {value['equation_sha256']}")
        print(f"Membranes: {value['membrane_count']}")
        for membrane in value["membranes"]:
            print(
                f"  depth {membrane['depth_n']}: {membrane['boundary_residue_n']} MOD "
                f"{membrane['boundary_modulus_n_plus_1']} · span "
                f"{membrane['source_span_start']}..{membrane['source_span_end']}"
            )
    else:
        for key, item in value.items():
            if key != "classification":
                print(f"{key}: {item}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hhs probability", description="Pass 183 exact probability hydration")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in (
        "parse", "inspect", "validate", "membranes", "hydrate", "execute",
        "close", "residue", "zero-bypass", "receipt", "verify",
    ):
        child = subparsers.add_parser(command)
        child.add_argument("--adapter", required=True, choices=sorted(ADAPTER_EQUATIONS))
        child.add_argument("--equation")
        child.add_argument("--equation-file")
        child.add_argument("--manifest", help="JSON object or path to JSON object")
        child.add_argument("--seed")
        child.add_argument("--seed-class", default="DETERMINISTIC_ENUMERATION")
        child.add_argument("--timeout", type=int, default=30_000)
        child.add_argument("--json", action="store_true")
        child.add_argument("--explain", action="store_true")
    replay = subparsers.add_parser("replay")
    replay.add_argument("--json", action="store_true")
    status = subparsers.add_parser("test")
    status.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        runtime = ProbabilityHydrationRuntime()
        if args.command == "replay":
            _emit(runtime.replay(), as_json=args.json)
            return 0
        if args.command == "test":
            _emit(runtime.status(), as_json=args.json)
            return 0
        equation = _equation(args)
        manifest = _load_manifest(args.manifest)
        if args.command in {"parse", "inspect", "membranes"}:
            _emit(runtime.inspect(adapter=args.adapter, equation=equation), as_json=args.json)
            return 0
        if args.command == "validate":
            evaluation = runtime.execute(
                adapter=args.adapter,
                equation=equation,
                manifest=manifest,
                seed_class=args.seed_class,
                seed=args.seed,
                commit=False,
            )
            _emit({"classification": "HHS_PASS_183_DOMAIN_AND_EQUATION_VALID", "evaluation": evaluation}, as_json=args.json)
            return 0
        result = runtime.execute(
            adapter=args.adapter,
            equation=equation,
            manifest=manifest,
            seed_class=args.seed_class,
            seed=args.seed,
            modulus=GLOBAL_MODULUS,
        )
        _emit(result, as_json=args.json)
        return 0
    except (Pass183Error, json.JSONDecodeError, OSError) as exc:
        classification = getattr(exc, "classification", "P183_REJECT_PARSE")
        detail = getattr(exc, "detail", str(exc))
        print(f"Status: {classification}", file=sys.stderr)
        if detail:
            print(f"Reason: {detail}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
