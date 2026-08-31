"""Human-readable Pass 184 command surface."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence

from .runtime import (
    HEALTH_PATH,
    PROFILE_SEEDS,
    Pass184Error,
    PortableRuntimeAuthority,
)


def _emit(payload: dict[str, Any], *, json_mode: bool) -> None:
    if json_mode:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    classification = payload.get("classification") or payload.get("status") or "HHS_PASS_184_RESULT"
    print(classification)
    for key in (
        "profile",
        "install_root",
        "plan_identity",
        "manifest_identity",
        "host",
        "port",
        "ready",
        "verified_file_count",
        "message",
    ):
        if key in payload:
            print(f"{key.replace('_', ' ').title()}: {payload[key]}")
    components = payload.get("components")
    if components:
        print("Components:")
        for component in components:
            print(f"  - {component}")
    verification = payload.get("verification")
    if isinstance(verification, dict):
        print(f"Verified files: {verification.get('verified_file_count', 0)}")


def _add_plan_arguments(parser: argparse.ArgumentParser, *, require_install: bool = True) -> None:
    parser.add_argument("--profile", choices=sorted(PROFILE_SEEDS), default="full")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--install-root", required=require_install)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hhs-pass184",
        description="Build, verify, and supervise portable HHS runtime packages.",
    )
    parser.add_argument("--json", action="store_true", dest="json_mode", help="emit machine-readable JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    detect = subparsers.add_parser("detect", help="inspect the current installation environment")
    detect.add_argument("--repository-root", default=".")
    detect.add_argument("--writable-root")

    plan = subparsers.add_parser("plan", help="resolve a deterministic package plan")
    _add_plan_arguments(plan)

    build = subparsers.add_parser("build", help="materialize and verify a runtime package")
    _add_plan_arguments(build)
    build.add_argument("--clean", action="store_true")

    verify = subparsers.add_parser("verify", help="verify a generated package manifest")
    verify.add_argument("--install-root", required=True)

    probe = subparsers.add_parser("probe", help="verify TCP and HTTP health readiness")
    probe.add_argument("--host", default="127.0.0.1")
    probe.add_argument("--port", type=int, default=8080)
    probe.add_argument("--health-path", default=HEALTH_PATH)
    probe.add_argument("--timeout", type=float, default=2.0)

    serve = subparsers.add_parser("serve", help="start and supervise the full HHS application IDE")
    serve.add_argument("--repository-root", default=".")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8080)
    serve.add_argument("--timeout", type=float, default=60.0)
    serve.add_argument("--python-bin")

    subparsers.add_parser("status", help="show Pass 184 authority and profile status")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(list(argv) if argv is not None else None)
    authority = PortableRuntimeAuthority()
    try:
        if arguments.command == "detect":
            result = authority.detect(
                repository_root=arguments.repository_root,
                writable_root=arguments.writable_root,
            )
            result["classification"] = "HHS_PASS_184_ENVIRONMENT_DETECTION_VERIFIED"
        elif arguments.command == "plan":
            plan = authority.plan(
                profile=arguments.profile,
                install_root=arguments.install_root,
                repository_root=arguments.repository_root,
                host=arguments.host,
                port=arguments.port,
            )
            result = plan.to_dict()
            result["classification"] = "HHS_PASS_184_DETERMINISTIC_PACKAGE_PLAN_VERIFIED"
        elif arguments.command == "build":
            plan = authority.plan(
                profile=arguments.profile,
                install_root=arguments.install_root,
                repository_root=arguments.repository_root,
                host=arguments.host,
                port=arguments.port,
            )
            result = authority.build(plan, clean=arguments.clean)
        elif arguments.command == "verify":
            result = authority.verify(arguments.install_root)
        elif arguments.command == "probe":
            result = authority.probe(
                host=arguments.host,
                port=arguments.port,
                health_path=arguments.health_path,
                timeout=arguments.timeout,
            )
        elif arguments.command == "serve":
            return authority.serve(
                repository_root=arguments.repository_root,
                host=arguments.host,
                port=arguments.port,
                timeout=arguments.timeout,
                python_bin=arguments.python_bin,
            )
        elif arguments.command == "status":
            result = authority.status()
        else:  # pragma: no cover - argparse enforces a command
            raise Pass184Error("P184_REJECT_COMMAND", "unknown command")
        _emit(result, json_mode=arguments.json_mode)
        return 0
    except Pass184Error as error:
        payload = error.to_dict()
        if arguments.json_mode:
            print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
        else:
            print(f"{error.status}: {error.message}", file=sys.stderr)
            for key, value in error.details.items():
                print(f"{key}: {value}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
