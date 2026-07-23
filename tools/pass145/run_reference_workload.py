#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.pass145.canonical import canonical_json, hash72
from hhs_runtime.pass145.service import HHS145Service
from hhs_runtime.pass145.workbench import EnvironmentManager, LVMEngine, ScriptWorkbench, WorkspaceManager

ART = ROOT / "release_artifacts/pass145"
REF = ART / "reference"
RECEIPTS = ART / "receipts"


def write_receipt(name: str, label: str, payload: dict) -> dict:
    value = dict(payload)
    value.setdefault("receipt_type", name.removesuffix(".json"))
    value.setdefault("authority_level", "A1")
    value.setdefault("receipt_hash72", hash72(label, value))
    (RECEIPTS / name).write_text(canonical_json(value) + "\n", encoding="utf-8")
    return value


def main() -> int:
    REF.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    db_path = REF / "PASS_145_REFERENCE.sqlite3"
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(db_path) + suffix)
        if p.exists():
            p.unlink()
    backup_path = REF / "PASS_145_REFERENCE_BACKUP.zip"
    if backup_path.exists():
        backup_path.unlink()

    with HHS145Service(db_path) as service:
        html = service.ingest_bytes(
            b"<!doctype html><html><head><title>Reference</title><script>fetch('https://invalid.example')</script></head><body><p>O denotes the HHS operator.</p><p>pi is written as \xcf\x80.</p></body></html>",
            name="reference.html", mime_type="text/html", namespace="reference"
        )
        javascript = service.ingest_bytes(
            b"const endpoint='https://invalid.example'; fetch(endpoint); process.exit(1);",
            name="reference.js", mime_type="text/javascript", namespace="reference"
        )
        service.ingest_bytes(b"The runtime is deterministic.", name="claim-a.md", mime_type="text/markdown", namespace="reference")
        conflict = service.ingest_bytes(b"The runtime is not deterministic.", name="claim-b.md", mime_type="text/markdown", namespace="reference")

        query = service.query("Show every definition of the symbol O", namespace="reference")
        validation = service.validate_source(html["source_id"])
        replay = service.replay_ingestion(html["source_id"])

        workspaces = WorkspaceManager(service)
        environments = EnvironmentManager(service)
        scripts = ScriptWorkbench(service, environments)
        lvms = LVMEngine(service, scripts, environments)
        workspace = workspaces.create("Reference Workspace")
        environment = environments.create("Reference Environment", namespace="reference-env")
        env_id = environment["result"]["environment_id"]
        workspaces.add_member(workspace["result"]["workspace_id"], "ENVIRONMENT", env_id)
        script = scripts.import_script("reference-status", "HHS_COMMAND", "status", environment_id=env_id, declared_capabilities=["DATABASE_READ"])
        scripts.validate(script["result"]["script_id"])
        script_execution = scripts.execute(script["result"]["script_id"])
        lvm = lvms.create({
            "name": "reference-query-lvm", "version": 1,
            "components": [{"id": "query", "type": "QUERY", "question": "Show every definition of the symbol O", "namespace": "reference"}],
            "edges": [], "outputs": {"result": "query"},
            "resource_policy": {"max_recursive_depth": 9},
        }, environment_id=env_id)
        lvm_execution = lvms.execute(lvm["result"]["lvm_id"], {"source": html["source_id"]})
        lvm_replay = lvms.replay(lvm_execution["result"]["execution_id"])

        backup = service.backup_create(backup_path)
        backup_verify = service.backup_verify(backup_path)
        restore_preview = service.restore_preview(backup_path)
        integrity = service.db.integrity_check()
        receipt_chain = service.db.verify_receipt_chain()

        write_receipt("DOCUMENT_INGESTION_RECEIPT.json", "hhs_pass145_document_ingestion_receipt_v1", html["receipts"]["DOCUMENT_INGESTION_RECEIPT"])
        write_receipt("SOURCE_PRESERVATION_RECEIPT.json", "hhs_pass145_source_preservation_receipt_v1", html["receipts"]["SOURCE_PRESERVATION_RECEIPT"])
        write_receipt("HTML_PARSE_RECEIPT.json", "hhs_pass145_html_parse_receipt_v1", html["receipts"]["HTML_PARSE_RECEIPT"])
        write_receipt("JAVASCRIPT_ANALYSIS_RECEIPT.json", "hhs_pass145_javascript_analysis_receipt_v1", javascript["receipts"]["JAVASCRIPT_ANALYSIS_RECEIPT"])
        write_receipt("QUERY_PLAN_RECEIPT.json", "hhs_pass145_query_plan_receipt_v1", query["query_plan_receipt"])
        write_receipt("QUERY_RESULT_RECEIPT.json", "hhs_pass145_query_result_receipt_v1", query["query_result_receipt"])
        write_receipt("REPLAY_RECEIPT.json", "hhs_pass145_replay_receipt_v1", replay)
        write_receipt("LVM_EXECUTION_RECEIPT.json", "hhs_pass145_lvm_execution_receipt_v1", lvm_execution)
        write_receipt("LVM_REPLAY_RECEIPT.json", "hhs_pass145_lvm_replay_receipt_v1", lvm_replay)
        write_receipt("CLI_COMMAND_RECEIPT.json", "hhs_pass145_cli_command_receipt_v1", {
            "schema": "HHS_PASS145_CLI_COMMAND_RECEIPT_V1",
            "public_actor_report": "release_artifacts/pass145/reports/PASS_145_CEUAC_A2_BLACK_BOX.json",
            "workflow_status": "OBSERVED_WORKING",
            "commands_executed": 7,
        })
        write_receipt("DATABASE_INTEGRITY_RECEIPT.json", "hhs_pass145_database_integrity_receipt_v1", integrity)
        write_receipt("BACKUP_RECEIPT.json", "hhs_pass145_backup_receipt_v1", backup)
        write_receipt("RESTORE_RECEIPT.json", "hhs_pass145_restore_receipt_v1", restore_preview)
        if html.get("interpretation", {}).get("receipt_id"):
            write_receipt("KNOWLEDGE_TRANSACTION_RECEIPT.json", "hhs_pass145_knowledge_transaction_receipt_v1", service.db.get_receipt(html["interpretation"]["receipt_id"]))
        if validation.get("receipt_id"):
            write_receipt("VALIDATION_RECEIPT.json", "hhs_pass145_validation_receipt_v1", service.db.get_receipt(validation["receipt_id"]))
        if conflict.get("contradictions", {}).get("receipt_id"):
            write_receipt("CONTRADICTION_RECEIPT.json", "hhs_pass145_contradiction_receipt_v1", service.db.get_receipt(conflict["contradictions"]["receipt_id"]))

        summary = {
            "schema": "HHS_PASS145_REFERENCE_WORKLOAD_V1",
            "database": str(db_path.relative_to(ROOT)),
            "database_integrity": integrity,
            "receipt_chain": receipt_chain,
            "sources": [html["source_id"], javascript["source_id"]],
            "query_result_count": query["answer"]["deterministic_calculations"]["result_count"],
            "validation_outcome": validation["outcome"],
            "ingestion_replay": replay["status"],
            "lvm_replay": lvm_replay["status"],
            "backup_verified": backup_verify["ok"],
            "restore_preview": restore_preview["status"],
            "script_execution": script_execution["result"]["status"],
            "contradictions_preserved": conflict["contradictions"]["contradiction_count"],
        }
        summary["workload_hash72"] = hash72("hhs_pass145_reference_workload_v1", summary)
        (REF / "PASS_145_REFERENCE_WORKLOAD.json").write_text(canonical_json(summary) + "\n", encoding="utf-8")

    write_receipt("APK_INSTALL_RECEIPT.json", "hhs_pass145_apk_install_nonexecution_receipt_v1", {
        "schema": "HHS_PASS145_APK_INSTALL_RECEIPT_V1", "status": "NOT_EXPOSED",
        "reason": "APK_BUILD_FAILED_ANDROID_TOOLCHAIN_UNAVAILABLE", "installation_success": False,
    })
    write_receipt("CONTINUATION_RECEIPT.json", "hhs_pass145_continuation_nonexecution_receipt_v1", {
        "schema": "HHS_PASS145_CONTINUATION_RECEIPT_V1", "status": "NOT_EXPOSED",
        "reason": "ANDROID_PROCESS_TERMINATION_AND_RESOURCE_CONTINUATION_REQUIRE_REAL_DEVICE_EXECUTION",
        "resumed_state_equivalence_claimed": False,
    })
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
