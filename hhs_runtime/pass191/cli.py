"""Pass 191 HARMONICODE-compatible repository hydration CLI."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .repository_hydration import Pass191Error, RepositoryHydrationRuntime


def _authority(path: Optional[str], operation: str) -> Mapping[str, Any]:
    if path:
        return json.loads(Path(path).read_text("utf-8"))
    from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController

    return HHSRuntimeController().authorized_tick(source="HHS_PASS191_CLI:" + operation)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hhs")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--state-root", default=".hhs_runtime_state/pass191")
    roots = parser.add_subparsers(dest="root_command", required=True)

    hydrate = roots.add_parser("hydrate")
    hcmd = hydrate.add_subparsers(dest="operation", required=True)

    repository = hcmd.add_parser("repository")
    repository.add_argument("--commit", default="HEAD")
    repository.add_argument("--since")
    repository.add_argument("--preview", action="store_true")
    repository.add_argument("--authority-json")

    genesis = hcmd.add_parser("genesis")

    hpass = hcmd.add_parser("pass")
    hpass.add_argument("number", type=int)

    obj = hcmd.add_parser("object")
    obj.add_argument("object_id")

    function = hcmd.add_parser("function")
    function.add_argument("operation_id")

    changed = hcmd.add_parser("changed")
    changed.add_argument("--since", required=True)
    changed.add_argument("--commit", default="HEAD")

    status = hcmd.add_parser("status")
    status.add_argument("job_id")

    resume = hcmd.add_parser("resume")
    resume.add_argument("job_id")
    resume.add_argument("--authority-json")

    cancel = hcmd.add_parser("cancel")
    cancel.add_argument("job_id")
    cancel.add_argument("--authority-json")

    verify = hcmd.add_parser("verify")
    verify.add_argument("job_id")

    replay = hcmd.add_parser("replay")
    replay.add_argument("job_id")

    report = hcmd.add_parser("report")
    report.add_argument("job_id")

    receipt = hcmd.add_parser("receipt")
    receipt.add_argument("receipt_hash72")

    registry = roots.add_parser("registry")
    rcmd = registry.add_subparsers(dest="operation", required=True)
    rcmd.add_parser("functions")
    rcmd.add_parser("invariants")
    resolve = rcmd.add_parser("resolve")
    resolve.add_argument("operation_id")

    lineage = roots.add_parser("lineage")
    lcmd = lineage.add_subparsers(dest="operation", required=True)
    lcmd.add_parser("passes")

    symmetry = roots.add_parser("symmetry")
    scmd = symmetry.add_subparsers(dest="operation", required=True)
    scmd.add_parser("verify")

    reciprocal = roots.add_parser("reciprocal")
    rvcmd = reciprocal.add_subparsers(dest="operation", required=True)
    rvcmd.add_parser("verify")
    return parser


def dispatch(namespace: argparse.Namespace) -> Any:
    runtime = RepositoryHydrationRuntime(namespace.repository_root, namespace.state_root)
    root_command = namespace.root_command
    operation = namespace.operation

    if root_command == "hydrate":
        if operation == "repository":
            if namespace.preview:
                return runtime.compact(
                    runtime.preview(commit=namespace.commit, since_commit=namespace.since)
                )
            job = runtime.create_job(
                {"commit": namespace.commit, "since_commit": namespace.since},
                authority_execution=_authority(
                    namespace.authority_json, "P191.Hydrate.Repository"
                ),
            )
            return {
                "job_id": job["job_id"],
                "stage": job["stage"],
                "recovery_action": job["recovery_action"],
            }
        if operation == "genesis":
            return runtime.lineage()["records"][0]
        if operation == "pass":
            if namespace.number < 0 or namespace.number > 190:
                raise Pass191Error("HHS_P191_PASS_NUMBER_INVALID")
            return runtime.lineage()["records"][namespace.number]
        if operation == "object":
            return runtime.object_by_identity(namespace.object_id)
        if operation == "function":
            return runtime.function_by_id(namespace.operation_id)
        if operation == "changed":
            return runtime.compact(
                runtime.preview(commit=namespace.commit, since_commit=namespace.since)
            )
        if operation == "status":
            return runtime.get_job(namespace.job_id)
        if operation == "resume":
            job = runtime.resume_job(
                namespace.job_id,
                authority_execution=_authority(
                    namespace.authority_json, "P191.Hydrate.Resume"
                ),
            )
            return {
                "job_id": job["job_id"],
                "stage": job["stage"],
                "failure_reason": job["failure_reason"],
                "receipt_links": job["receipt_links"],
            }
        if operation == "cancel":
            return runtime.cancel_job(
                namespace.job_id,
                authority_execution=_authority(
                    namespace.authority_json, "P191.Hydrate.Cancel"
                ),
            )
        if operation == "verify":
            return runtime.verify_job(namespace.job_id)
        if operation == "replay":
            return runtime.replay_job(namespace.job_id)
        if operation == "report":
            return runtime.report(namespace.job_id)
        if operation == "receipt":
            return runtime.receipt(namespace.receipt_hash72)

    if root_command == "registry":
        if operation == "functions":
            return runtime._function_registry(runtime.head_commit())
        if operation == "invariants":
            return runtime.invariants()
        if operation == "resolve":
            return runtime.function_by_id(namespace.operation_id)

    if root_command == "lineage" and operation == "passes":
        return runtime.lineage()

    if root_command == "symmetry" and operation == "verify":
        return runtime.invariants()["invariants"][6]["witness"]

    if root_command == "reciprocal" and operation == "verify":
        return runtime.invariants()["invariants"][6]["witness"]["reciprocal_pairs"]

    raise Pass191Error("HHS_P191_CLI_OPERATION_UNKNOWN")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    namespace = parser.parse_args(argv)
    try:
        value = dispatch(namespace)
    except Pass191Error as exc:
        parser.error(exc.classification)
    if isinstance(value, str):
        print(value, end="" if value.endswith("\n") else "\n")
    else:
        print(
            json.dumps(
                value,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
