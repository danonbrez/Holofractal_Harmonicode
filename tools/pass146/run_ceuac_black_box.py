#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "release_artifacts/pass146"
REPORT = ART / "reports/PASS_146_CEUAC_A2_BLACK_BOX.json"
WORK = ART / "reports/ceuac_actor"
DB = WORK / "actor.sqlite3"
DOC = WORK / "actor.txt"


def run(*args: str, input_text: str | None = None) -> dict:
    env = os.environ.copy(); env["PYTHONPATH"] = str(ROOT)
    proc = subprocess.run([str(ROOT / "hhs"), "--db", str(DB), "--format", "json", *args], cwd=ROOT, env=env, input=input_text, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed {args}: {proc.stderr}\n{proc.stdout}")
    return json.loads(proc.stdout)


def main() -> int:
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    DOC.write_text("O denotes the HHS operator. π denotes the circular constant. Boundary contracts construct paths.\n", encoding="utf-8")
    admitted = run("ingest", "file", str(DOC), "--namespace", "ceuac146")
    source_id = admitted["source_id"]
    source = run("source", "show", source_id, "--raw-base64")
    query = run("query", "Show every definition of O", "--namespace", "ceuac146")
    contracts = run("security", "path", "list", "--limit", "50")
    wrapped = [c for c in contracts if c["operation"] == "RUN_CLI_COMMAND"]
    contract_id = wrapped[0]["contract_id"]
    inspected = run("security", "path", "inspect", contract_id)
    replay = run("security", "path", "replay", contract_id)
    # New process invocation proves session and database continuity.
    status_after_restart = run("database", "integrity")
    payload = {
        "schema": "HHS_PASS146_CEUAC_A2_BLACK_BOX_V1",
        "actor_boundary": "PUBLIC_HHS_CLI_ONLY",
        "commands_executed": 7,
        "source_id": source_id,
        "raw_source_preserved": bool(source.get("raw_base64")),
        "query_evidence_count": len(query["answer"]["directly_retrieved_evidence"]),
        "boundary_contract_id": contract_id,
        "boundary_status": inspected["status"],
        "temporary_capabilities_expired": inspected["pathway"]["active_capabilities"] == [],
        "replay_status": replay["status"],
        "restart_integrity": bool(status_after_restart.get("ok")),
        "passed": bool(source.get("raw_base64") and query["answer"]["directly_retrieved_evidence"] and inspected["status"] == "BOUNDARY_CLOSED" and replay["status"] == "REPLAY_VALIDATED" and status_after_restart.get("ok")),
    }
    session = Path(str(DB) + ".pass146-session.json")
    if session.exists():
        session.unlink()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
