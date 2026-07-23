from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def run_cli(root: Path, db: Path, args: list[str], *, expect: int = 0, stdin: str | None = None) -> dict[str, Any]:
    proc = subprocess.run([str(root / "hhs"), "--db", str(db), "--format", "json", *args], input=stdin, text=True, capture_output=True, cwd=root)
    if proc.returncode != expect:
        raise RuntimeError(json.dumps({"args": args, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}, indent=2))
    payload = json.loads(proc.stdout if proc.stdout.strip() else proc.stderr)
    return payload


def agent_cli(root: Path, db: Path, creds: dict[str, str], args: list[str], *, stdin_text: str | None = None) -> dict[str, Any]:
    command = ["agent", "execute", "--identity", creds["identity_id"], "--grant", creds["grant_id"], "--token", creds["token"]]
    if stdin_text is not None:
        command += ["--stdin-text", stdin_text]
    command += ["--", *args]
    return run_cli(root, db, command)


def target_result(agent_response: dict[str, Any]) -> Any:
    return agent_response["execution"]["result"]


def transaction_result(agent_response: dict[str, Any]) -> Any:
    value = target_result(agent_response)
    return value.get("result", value) if isinstance(value, dict) else value


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    out_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / "release_artifacts/pass147/reference/external_actor"
    out_root.mkdir(parents=True, exist_ok=True)
    db = out_root / "PASS_147_EXTERNAL_ACTOR.sqlite3"
    for candidate in (db, Path(str(db) + "-wal"), Path(str(db) + "-shm"), db.with_name(db.name + ".pass146-session.json")):
        candidate.unlink(missing_ok=True)

    trace: list[dict[str, Any]] = []

    secret_keys = {"authentication_token", "identity_token", "token", "api_token", "secret", "private_key"}

    def redact(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: ("[REDACTED]" if key.casefold() in secret_keys else redact(item)) for key, item in value.items()}
        if isinstance(value, list):
            return [redact(item) for item in value]
        if isinstance(value, tuple):
            return [redact(item) for item in value]
        return value

    def record(step: str, result: Any) -> Any:
        # Persist evidence without one-time credentials or protected secret values.
        trace.append({"ordinal": len(trace), "step": step, "result": redact(result)})
        print(f"PASS147_ACTOR_STEP {len(trace)-1} {step}", file=sys.stderr, flush=True)
        return result

    record("VERSION", run_cli(root, db, ["version"]))
    record("PUBLIC_DOCUMENTATION_INSTALL", run_cli(root, db, ["docs", "install"]))
    bootstrap = record("EXTERNAL_AGENT_BOOTSTRAP", run_cli(root, db, ["agent", "bootstrap", "CEUAC External Actor"]))
    creds = {"identity_id": bootstrap["profile"]["identity_id"], "grant_id": bootstrap["profile"]["grant_id"], "token": bootstrap["authentication_token"]}

    surface = record("CAPABILITY_DISCOVERY", agent_cli(root, db, creds, ["surface", "audit"]))
    command = record("COMMAND_SCHEMA_INSPECTION", agent_cli(root, db, creds, ["command", "describe", "script", "import"]))
    api = record("API_SCHEMA_INSPECTION", agent_cli(root, db, creds, ["api-contract", "describe", "/api/v1/query"]))
    docs = record("DOCUMENTATION_QUERY", agent_cli(root, db, creds, ["docs", "query", "external-agent", "opacity"]))

    env_response = record("KNOWLEDGE_ENVIRONMENT_CREATE", agent_cli(root, db, creds, ["env", "create", "External Actor Lab", "--namespace", "actor-lab"]))
    environment_id = transaction_result(env_response)["environment_id"]

    source_path = out_root / "actor_source.md"
    source_path.write_text("# Actor Source\n\nO is a distinct HHS operator. π is the ordinary circular constant. O != π.\n\nPublic operations require boundary construction and replayable receipts.\n", encoding="utf-8")
    ingest_response = record("DOCUMENT_INGESTION", agent_cli(root, db, creds, ["ingest", "file", str(source_path), "--namespace", "actor-lab"]))
    source_id = target_result(ingest_response)["source_id"]
    record("KNOWLEDGE_QUERY", agent_cli(root, db, creds, ["query", "What is distinct from pi?", "--namespace", "actor-lab"]))

    bad_script = out_root / "bad_workflow.hhs"
    bad_script.write_text("kernel execute\n", encoding="utf-8")
    bad_import = record("BAD_SCRIPT_IMPORT", agent_cli(root, db, creds, ["script", "import", str(bad_script), "--name", "Bad Workflow", "--language", "HHS_COMMAND", "--environment", environment_id, "--capability", "DATABASE_READ"]))
    bad_script_id = transaction_result(bad_import)["script_id"]
    bad_validation = record("DELIBERATE_FAILURE", agent_cli(root, db, creds, ["script", "validate", bad_script_id]))
    bad_state = transaction_result(bad_validation)["validation_state"]
    if bad_state != "RUNTIME_REJECTED":
        raise RuntimeError(f"expected bad script rejection, observed {bad_state}")
    record("FAILURE_DIAGNOSIS", agent_cli(root, db, creds, ["error", "explain", "SCRIPT_COMMAND_REJECTED"]))

    good_script = out_root / "good_workflow.hhs"
    good_script.write_text("query What is external-agent opacity?\n", encoding="utf-8")
    good_import = record("REPAIRED_SCRIPT_IMPORT", agent_cli(root, db, creds, ["script", "import", str(good_script), "--name", "Opacity Query", "--language", "HHS_COMMAND", "--environment", environment_id, "--capability", "DATABASE_READ"]))
    script_id = transaction_result(good_import)["script_id"]
    good_validation = record("REPAIRED_SCRIPT_VALIDATE", agent_cli(root, db, creds, ["script", "validate", script_id]))
    if transaction_result(good_validation)["validation_state"] != "VALIDATED":
        raise RuntimeError("repaired script did not validate")
    script_run = record("SCRIPT_EXECUTE", agent_cli(root, db, creds, ["script", "run", script_id]))
    script_execution_id = transaction_result(script_run)["execution_id"]
    record("SCRIPT_STATE_INSPECT", agent_cli(root, db, creds, ["script", "inspect", script_id]))

    manifest_path = out_root / "opacity_lvm.json"
    manifest = {
        "name": "Opacity Query LVM",
        "version": 1,
        "components": [{"id": "query_script", "type": "SCRIPT", "script_id": script_id, "input": "$input"}],
        "edges": [],
        "outputs": {"result": "$query_script"},
        "resource_policy": {"max_recursive_depth": 8},
        "failure_policy": "HALT_AND_RECEIPT",
        "replay_policy": "DETERMINISTIC",
        "capabilities": ["NATIVE_RUNTIME", "DATABASE_READ", "DATABASE_WRITE"]
    }
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2), encoding="utf-8")
    lvm_create = record("LVM_CREATE", agent_cli(root, db, creds, ["lvm", "create", str(manifest_path), "--environment", environment_id]))
    lvm_id = transaction_result(lvm_create)["lvm_id"]
    lvm_run = record("LVM_EXECUTE", agent_cli(root, db, creds, ["lvm", "run", lvm_id, "--input-json", "{}"] ))
    lvm_execution_id = transaction_result(lvm_run)["execution_id"]
    record("LVM_INSPECT", agent_cli(root, db, creds, ["lvm", "inspect", lvm_id]))
    replay = record("LVM_REPLAY", agent_cli(root, db, creds, ["lvm", "replay", lvm_execution_id]))
    if target_result(replay)["status"] != "REPLAY_VALIDATED":
        raise RuntimeError("LVM replay did not validate")

    workspace_create = record("WORKSPACE_CREATE", agent_cli(root, db, creds, ["workspace", "create", "External Actor Project", "--active-environment", environment_id]))
    workspace_id = transaction_result(workspace_create)["workspace_id"]
    record("WORKSPACE_ADD_SCRIPT", agent_cli(root, db, creds, ["workspace", "add", workspace_id, "SCRIPT", script_id]))
    record("WORKSPACE_ADD_LVM", agent_cli(root, db, creds, ["workspace", "add", workspace_id, "LVM", lvm_id]))
    record("RECEIPT_CHAIN_VERIFY", agent_cli(root, db, creds, ["validate", "receipt"]))
    record("SOURCE_REPLAY", agent_cli(root, db, creds, ["replay", "ingestion", source_id]))
    export_path = out_root / "external_actor_project.json"
    export_result = record("PROJECT_EXPORT", agent_cli(root, db, creds, ["workspace", "export", workspace_id, str(export_path)]))

    audit = target_result(surface)
    receipt_check = target_result(trace[-3]["result"])
    result = {
        "schema": "HHS_PASS147_CEUAC_EXTERNAL_ACTOR_WORKFLOW_V1",
        "status": "EXTERNAL_ACTOR_WORKFLOW_COMPLETED",
        "actor_used_public_cli_only": True,
        "direct_repository_imports": False,
        "direct_database_access": False,
        "privileged_internal_access": 0,
        "potential_capability_complete": audit["potential_capability_complete"],
        "public_surface_closed": audit["closed"],
        "environment_id": environment_id,
        "source_id": source_id,
        "script_id": script_id,
        "script_execution_id": script_execution_id,
        "lvm_id": lvm_id,
        "lvm_execution_id": lvm_execution_id,
        "workspace_id": workspace_id,
        "project_export": str(export_path),
        "project_export_exists": export_path.is_file(),
        "receipt_chain_valid": bool(receipt_check.get("ok")),
        "trace_count": len(trace),
        "trace": trace,
    }
    (out_root / "PASS_147_EXTERNAL_ACTOR_WORKFLOW.json").write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
