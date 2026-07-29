from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any
import json
import os
import sys

from .management import (
    ManagementError,
    doctor,
    installation_status,
    receipt_status,
    repair,
    rollback,
    uninstall,
)
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


def _add_request_options(parser: ArgumentParser) -> None:
    parser.add_argument("--profile", choices=[value.value for value in Profile], default="auto")
    parser.add_argument("--source-kind", choices=[value.value for value in SourceKind], default="local")
    parser.add_argument("--source", default=".")
    parser.add_argument("--expected-identity")
    parser.add_argument("--install-mode", choices=[value.value for value in InstallMode], default="user")
    parser.add_argument("--network-policy", choices=[value.value for value in NetworkPolicy], default="online")
    parser.add_argument("--privilege-policy", choices=[value.value for value in PrivilegePolicy], default="prompt")
    parser.add_argument("--provider-policy", choices=[value.value for value in ProviderPolicy], default="auto")
    parser.add_argument("--model-policy", choices=[value.value for value in ModelPolicy], default="auto")
    parser.add_argument("--hhs-home")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--noninteractive", action="store_true")
    parser.add_argument("--request-json", help="read the canonical request from a JSON file")
    parser.add_argument("--output", help="write canonical JSON output to this file")


def _add_home_output(parser: ArgumentParser) -> None:
    parser.add_argument("--hhs-home")
    parser.add_argument("--output")


def _parser() -> ArgumentParser:
    parser = ArgumentParser(prog="hhs", description="HHS Pass 172 universal installer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("probe", "plan", "install", "update"):
        item = subparsers.add_parser(command)
        _add_request_options(item)

    for command in ("status", "doctor", "verify", "environment", "receipt", "replay-install"):
        item = subparsers.add_parser(command)
        _add_home_output(item)

    repair_parser = subparsers.add_parser("repair")
    _add_home_output(repair_parser)
    repair_parser.add_argument("--authorize", action="store_true")

    rollback_parser = subparsers.add_parser("rollback")
    _add_home_output(rollback_parser)
    rollback_parser.add_argument("--authorize", action="store_true")

    uninstall_parser = subparsers.add_parser("uninstall")
    _add_home_output(uninstall_parser)
    uninstall_parser.add_argument("--authorize", action="store_true")
    uninstall_parser.add_argument("--delete-user-data", action="store_true")

    for command in ("profile", "provider", "model"):
        item = subparsers.add_parser(command)
        _add_home_output(item)

    return parser


def _request_from_args(args: Namespace) -> InstallationRequest:
    if getattr(args, "request_json", None):
        payload = json.loads(Path(args.request_json).read_text(encoding="utf-8"))
        request = InstallationRequest.from_mapping(payload)
        if args.command == "update" and request.operation == "install":
            payload = request.to_dict()
            payload["operation"] = "update"
            request = InstallationRequest.from_mapping(payload)
        return request
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


def _home(value: str | None) -> Path:
    raw = value or os.environ.get("HHS_HOME")
    return Path(raw).expanduser().resolve() if raw else (Path.home() / ".hhs").resolve()


def _emit(payload: Any, output: str | None) -> None:
    text = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def _verify(home: Path) -> dict[str, Any]:
    status = installation_status(home)
    receipts = receipt_status(home)
    verified = bool(status["installed"] and receipts["valid"])
    return {
        "schema": "HHS_PASS_172_INSTALLATION_VERIFY_V1",
        "verified": verified,
        "classification": "P172_ACTIVE_INSTALLATION_VERIFIED" if verified else "P172_INSTALLATION_VERIFICATION_FAILED",
        "status": status,
        "receipts": receipts,
        "host_mutation_performed": False,
    }


def _replay(home: Path) -> dict[str, Any]:
    from hhs_verification.pass173.receipt_reconciler import ReceiptReconciler

    path = home / "install" / "receipts" / "installation-receipts.jsonl"
    result = ReceiptReconciler.verify_receipt_chain(path)
    result.update(
        {
            "schema": "HHS_PASS_173_LOGICAL_INSTALLATION_REPLAY_V1",
            "mode": "logical-no-host-mutation",
            "host_mutation_performed": False,
        }
    )
    return result


def _classification_view(command: str, home: Path) -> dict[str, Any]:
    status = installation_status(home)
    active = status.get("active") or {}
    if command == "profile":
        value = active.get("profile") or active.get("resolved_profile")
    elif command == "provider":
        value = active.get("provider") or "unclassified"
    else:
        value = active.get("model") or "not-installed"
    return {
        "schema": f"HHS_PASS_172_{command.upper()}_STATUS_V1",
        command: value,
        "installation_status_identity": status["status_identity"],
        "host_mutation_performed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    output = getattr(args, "output", None)
    try:
        if args.command == "status":
            _emit(installation_status(_home(args.hhs_home)), output)
            return 0
        if args.command == "doctor":
            payload = doctor(_home(args.hhs_home))
            _emit(payload, output)
            return 0 if not payload["repair_required"] else 3
        if args.command == "verify":
            payload = _verify(_home(args.hhs_home))
            _emit(payload, output)
            return 0 if payload["verified"] else 3
        if args.command == "environment":
            probe = EnvironmentProbe().run(target=_home(args.hhs_home).parent)
            _emit({"probe": probe.to_dict(), "host_mutation_performed": False}, output)
            return 0
        if args.command == "receipt":
            payload = receipt_status(_home(args.hhs_home))
            _emit(payload, output)
            return 0 if payload["valid"] else 3
        if args.command == "replay-install":
            payload = _replay(_home(args.hhs_home))
            _emit(payload, output)
            return 0 if payload["valid"] else 3
        if args.command == "repair":
            payload = repair(_home(args.hhs_home), authorized=bool(args.authorize))
            _emit(payload, output)
            return 0 if payload["status"] == "SUCCESS" else 3
        if args.command == "rollback":
            payload = rollback(_home(args.hhs_home), authorized=bool(args.authorize))
            _emit(payload, output)
            return 0 if payload["status"] == "SUCCESS" else 3
        if args.command == "uninstall":
            payload = uninstall(
                _home(args.hhs_home),
                authorized=bool(args.authorize),
                delete_user_data=bool(args.delete_user_data),
            )
            _emit(payload, output)
            return 0 if payload["status"] == "SUCCESS" else 3
        if args.command in {"profile", "provider", "model"}:
            _emit(_classification_view(args.command, _home(args.hhs_home)), output)
            return 0

        request = _request_from_args(args)
        repository_root = (
            Path(request.source.reference).expanduser().resolve()
            if request.source.kind is SourceKind.LOCAL
            else Path.cwd().resolve()
        )
        probe = EnvironmentProbe().run(target=request.resolved_home().parent)
        if args.command == "probe":
            payload = {"request": request.to_dict(), "probe": probe.to_dict(), "host_mutation_performed": False}
            _emit(payload, output)
            return 0 if probe.primary_classification.value != "HHS_ENVIRONMENT_INCOMPATIBLE" else 2

        plan = InstallationPlanner().build(request, probe)
        if args.command == "plan":
            _emit({"probe": probe.to_dict(), "plan": plan.to_dict(), "host_mutation_performed": False}, output)
            return 0

        transaction = InstallationTransaction(plan, probe, repository_root=repository_root)
        result = transaction.execute()
        _emit({"probe": probe.to_dict(), "plan": plan.to_dict(), "transaction": result}, output)
        return 0 if result["state"] == "RECEIPT_CLOSED" else 3
    except (InstallerSchemaError, ManagementError) as exc:
        _emit({"status": "FAILURE", "error": exc.to_dict()}, output)
        return 2
    except KeyboardInterrupt:
        _emit(
            {
                "status": "BLOCKED",
                "classification": "P172_USER_INTERRUPT",
                "next_action": "rerun the same command; repository-visible or installation-local checkpoint state is preserved",
            },
            output,
        )
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
