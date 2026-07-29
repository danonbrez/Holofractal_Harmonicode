from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any
import json
import os
import sys

from .planner import InstallationPlanner
from .probe import EnvironmentProbe
from .schema import (
    InstallMode,
    InstallationRequest,
    InstallerSchemaError,
    ModelPolicy,
    NetworkPolicy,
    PrivilegePolicy,
    Profile,
    ProviderPolicy,
    SourceKind,
    SourceSpec,
)
from .transaction import InstallationTransaction


def _parser() -> ArgumentParser:
    parser = ArgumentParser(prog="hhs", description="HHS Pass 172 universal installer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("probe", "plan", "install"):
        item = subparsers.add_parser(command)
        item.add_argument("--profile", choices=[value.value for value in Profile], default="auto")
        item.add_argument("--source-kind", choices=[value.value for value in SourceKind], default="local")
        item.add_argument("--source", default=".")
        item.add_argument("--expected-identity")
        item.add_argument("--install-mode", choices=[value.value for value in InstallMode], default="user")
        item.add_argument("--network-policy", choices=[value.value for value in NetworkPolicy], default="online")
        item.add_argument("--privilege-policy", choices=[value.value for value in PrivilegePolicy], default="prompt")
        item.add_argument("--provider-policy", choices=[value.value for value in ProviderPolicy], default="auto")
        item.add_argument("--model-policy", choices=[value.value for value in ModelPolicy], default="auto")
        item.add_argument("--hhs-home")
        item.add_argument("--timeout", type=int, default=900)
        item.add_argument("--start", action="store_true")
        item.add_argument("--noninteractive", action="store_true")
        item.add_argument("--request-json", help="read the canonical request from a JSON file")
        item.add_argument("--output", help="write canonical JSON output to this file")

    status = subparsers.add_parser("status")
    status.add_argument("--hhs-home")
    status.add_argument("--output")
    subparsers.add_parser("doctor").add_argument("--hhs-home")
    return parser


def _request_from_args(args: Namespace) -> InstallationRequest:
    if getattr(args, "request_json", None):
        payload = json.loads(Path(args.request_json).read_text(encoding="utf-8"))
        return InstallationRequest.from_mapping(payload)
    network = NetworkPolicy(args.network_policy)
    profile = Profile(args.profile)
    source_kind = SourceKind(args.source_kind)
    if profile is Profile.OFFLINE or source_kind is SourceKind.OFFLINE_BUNDLE:
        network = NetworkPolicy.OFFLINE
    return InstallationRequest(
        operation=args.command,
        source=SourceSpec(source_kind, args.source, args.expected_identity),
        profile=profile,
        install_mode=InstallMode(args.install_mode),
        start_after_install=bool(args.start),
        network_policy=network,
        privilege_policy=PrivilegePolicy(args.privilege_policy),
        provider_policy=ProviderPolicy(args.provider_policy),
        model_policy=ModelPolicy(args.model_policy),
        preserve_user_data=True,
        noninteractive=bool(args.noninteractive),
        hhs_home=args.hhs_home,
        timeout_seconds=args.timeout,
    )


def _emit(payload: Any, output: str | None) -> None:
    text = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def _status(home_value: str | None) -> dict[str, Any]:
    home = Path(home_value).expanduser() if home_value else Path(os.environ.get("HHS_HOME", Path.home() / ".hhs")).expanduser()
    pointer = home / "current.json"
    receipt_path = home / "install" / "receipts" / "installation-receipts.jsonl"
    active: dict[str, Any] | None = None
    if pointer.exists():
        try:
            active = json.loads(pointer.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            active = {"classification": "HHS_ENVIRONMENT_REPAIRABLE", "error": "active pointer unreadable"}
    return {
        "schema": "HHS_PASS_172_INSTALLATION_STATUS_V1",
        "hhs_home": str(home),
        "installed": bool(active),
        "active": active,
        "receipt_chain_present": receipt_path.is_file(),
        "host_mutation_performed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command in {"status", "doctor"}:
            payload = _status(args.hhs_home)
            if args.command == "doctor":
                payload["doctor_mode"] = "read_only"
                payload["repair_required"] = not payload["installed"] or bool(payload.get("active", {}).get("error") if isinstance(payload.get("active"), dict) else False)
            _emit(payload, getattr(args, "output", None))
            return 0

        request = _request_from_args(args)
        repository_root = Path(request.source.reference).expanduser().resolve() if request.source.kind is SourceKind.LOCAL else Path.cwd().resolve()
        probe = EnvironmentProbe().run(target=request.resolved_home().parent)
        if args.command == "probe":
            _emit({"request": request.to_dict(), "probe": probe.to_dict()}, args.output)
            return 0 if probe.primary_classification.value != "HHS_ENVIRONMENT_INCOMPATIBLE" else 2

        plan = InstallationPlanner().build(request, probe)
        if args.command == "plan":
            _emit({"probe": probe.to_dict(), "plan": plan.to_dict(), "host_mutation_performed": False}, args.output)
            return 0

        transaction = InstallationTransaction(plan, probe, repository_root=repository_root)
        result = transaction.execute()
        _emit({"probe": probe.to_dict(), "plan": plan.to_dict(), "transaction": result}, args.output)
        return 0 if result["state"] == "RECEIPT_CLOSED" else 3
    except InstallerSchemaError as exc:
        _emit({"status": "FAILURE", "error": exc.to_dict()}, getattr(args, "output", None))
        return 2
    except KeyboardInterrupt:
        _emit({"status": "BLOCKED", "classification": "P172_USER_INTERRUPT", "next_action": "rerun the same command; transaction checkpoint is preserved"}, getattr(args, "output", None))
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
