from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any
import json
import os
import sys

from .execution import CompleteInstallationTransaction
from .management import ManagementError, doctor, installation_status, receipt_status, repair, rollback, uninstall
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


def _request_options(parser: ArgumentParser) -> None:
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
    parser.add_argument("--request-json")
    parser.add_argument("--output")


def _home_options(parser: ArgumentParser) -> None:
    parser.add_argument("--hhs-home")
    parser.add_argument("--output")


def parser() -> ArgumentParser:
    root = ArgumentParser(prog="hhs", description="HHS Pass 172 universal installer")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("probe", "plan", "install", "update"):
        _request_options(commands.add_parser(name))
    for name in ("status", "doctor", "verify", "environment", "receipt", "replay-install", "profile", "provider", "model"):
        _home_options(commands.add_parser(name))
    for name in ("repair", "rollback"):
        item = commands.add_parser(name)
        _home_options(item)
        item.add_argument("--authorize", action="store_true")
    item = commands.add_parser("uninstall")
    _home_options(item)
    item.add_argument("--authorize", action="store_true")
    item.add_argument("--delete-user-data", action="store_true")
    return root


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


def _request(args: Namespace) -> InstallationRequest:
    if args.request_json:
        payload = json.loads(Path(args.request_json).read_text(encoding="utf-8"))
        if args.command == "update":
            payload["operation"] = "update"
        return InstallationRequest.from_mapping(payload)
    profile = Profile(args.profile)
    source_kind = SourceKind(args.source_kind)
    network = NetworkPolicy(args.network_policy)
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


def _read_only(command: str, home: Path) -> tuple[dict[str, Any], int]:
    if command == "status":
        return installation_status(home), 0
    if command == "doctor":
        result = doctor(home)
        return result, 0 if not result["repair_required"] else 3
    if command == "verify":
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
        }, 0 if verified else 3
    if command == "environment":
        probe = EnvironmentProbe().run(target=home.parent)
        return {"probe": probe.to_dict(), "host_mutation_performed": False}, 0
    if command == "receipt":
        result = receipt_status(home)
        return result, 0 if result["valid"] else 3
    if command == "replay-install":
        from hhs_verification.pass173.receipt_reconciler import ReceiptReconciler
        result = ReceiptReconciler.verify_receipt_chain(home / "install" / "receipts" / "installation-receipts.jsonl")
        result.update({"schema": "HHS_PASS_173_LOGICAL_INSTALLATION_REPLAY_V1", "mode": "logical-no-host-mutation", "host_mutation_performed": False})
        return result, 0 if result["valid"] else 3
    status = installation_status(home)
    active = status.get("active") or {}
    value = active.get(command) or active.get(f"{command}_state") or "unclassified"
    return {
        "schema": f"HHS_PASS_172_{command.upper()}_STATUS_V1",
        command: value,
        "installation_status_identity": status["status_identity"],
        "host_mutation_performed": False,
    }, 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    output = getattr(args, "output", None)
    try:
        if args.command in {"status", "doctor", "verify", "environment", "receipt", "replay-install", "profile", "provider", "model"}:
            payload, code = _read_only(args.command, _home(args.hhs_home))
            _emit(payload, output)
            return code
        if args.command == "repair":
            payload = repair(_home(args.hhs_home), authorized=bool(args.authorize))
            _emit(payload, output)
            return 0 if payload["status"] == "SUCCESS" else 3
        if args.command == "rollback":
            payload = rollback(_home(args.hhs_home), authorized=bool(args.authorize))
            _emit(payload, output)
            return 0 if payload["status"] == "SUCCESS" else 3
        if args.command == "uninstall":
            payload = uninstall(_home(args.hhs_home), authorized=bool(args.authorize), delete_user_data=bool(args.delete_user_data))
            _emit(payload, output)
            return 0 if payload["status"] == "SUCCESS" else 3

        request = _request(args)
        repository_root = Path(request.source.reference).expanduser().resolve() if request.source.kind is SourceKind.LOCAL else Path.cwd().resolve()
        probe = EnvironmentProbe().run(target=request.resolved_home().parent)
        if args.command == "probe":
            payload = {"request": request.to_dict(), "probe": probe.to_dict(), "host_mutation_performed": False}
            _emit(payload, output)
            return 0 if probe.primary_classification.value != "HHS_ENVIRONMENT_INCOMPATIBLE" else 2
        plan = InstallationPlanner().build(request, probe)
        if args.command == "plan":
            _emit({"probe": probe.to_dict(), "plan": plan.to_dict(), "host_mutation_performed": False}, output)
            return 0
        transaction = CompleteInstallationTransaction(plan, probe, repository_root=repository_root)
        result = transaction.execute()
        _emit({"probe": probe.to_dict(), "plan": plan.to_dict(), "transaction": result}, output)
        return 0 if result["state"] == "RECEIPT_CLOSED" else 3
    except (InstallerSchemaError, ManagementError) as exc:
        _emit({"status": "FAILURE", "error": exc.to_dict()}, output)
        return 2
    except KeyboardInterrupt:
        _emit({"status": "BLOCKED", "classification": "P172_USER_INTERRUPT", "next_action": "rerun the same command; checkpoint state is preserved"}, output)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
