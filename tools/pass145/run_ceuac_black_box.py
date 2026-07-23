#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HHS = ROOT / "hhs"


def invoke(db: Path, *args: str) -> tuple[int, dict, str]:
    proc = subprocess.run(
        [str(HHS), "--db", str(db), "--format", "json", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    stream = proc.stdout if proc.returncode == 0 else proc.stderr
    try:
        payload = json.loads(stream)
    except json.JSONDecodeError:
        payload = {"raw": stream}
    return proc.returncode, payload, proc.stderr


def main() -> int:
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "release_artifacts/pass145/reports/PASS_145_CEUAC_A2_BLACK_BOX.json"
    with tempfile.TemporaryDirectory(prefix="hhs145_a2_") as td:
        td = Path(td)
        db = td / "knowledge.sqlite3"
        source_path = td / "evidence.md"
        source_bytes = (
            "# External capability evidence\n"
            "O denotes the HHS operator.\n"
            "π denotes the circular constant.\n"
            "Hash72 denotes the receipt ancestry witness.\n"
        ).encode("utf-8")
        source_path.write_bytes(source_bytes)
        steps = []

        rc, ingest, err = invoke(db, "ingest", "file", str(source_path), "--namespace", "ceuac-a2")
        steps.append({"step": "import_document", "returncode": rc, "result": ingest})
        source_id = ingest.get("source_id", "")
        receipt_id = ingest.get("receipt_id", "")

        rc, source, err = invoke(db, "source", "show", source_id, "--raw-base64")
        raw_equal = False
        if source.get("raw_base64"):
            raw_equal = base64.b64decode(source["raw_base64"]) == source_bytes
        steps.append({"step": "inspect_preserved_source", "returncode": rc, "raw_bytes_equal": raw_equal, "source_root_hash72": source.get("source_root_hash72")})

        rc, query, err = invoke(db, "query", "Show every definition of the symbol O", "--namespace", "ceuac-a2")
        steps.append({"step": "query_contents", "returncode": rc, "result_count": query.get("answer", {}).get("deterministic_calculations", {}).get("result_count"), "database_root_unchanged": query.get("database_root_unchanged")})

        rc, validation, err = invoke(db, "validate", "source", source_id)
        steps.append({"step": "inspect_validation", "returncode": rc, "outcome": validation.get("outcome"), "validators_executed": validation.get("validators_executed", [])})

        rc, receipt, err = invoke(db, "receipt", "show", receipt_id)
        steps.append({"step": "export_receipt", "returncode": rc, "receipt_id": receipt.get("receipt_id"), "receipt_hash72": receipt.get("receipt_hash72")})

        # Each CLI invocation creates a fresh process; this status call is the explicit restart boundary.
        rc, status, err = invoke(db, "status")
        steps.append({"step": "restart_and_verify_continuity", "returncode": rc, "ok": status.get("ok"), "source_count": status.get("counts", {}).get("sources")})

        rc, replay, err = invoke(db, "replay", "ingestion", source_id)
        steps.append({"step": "replay_ingestion", "returncode": rc, "status": replay.get("status"), "comparison": replay.get("comparison")})

        passed = (
            all(step["returncode"] == 0 for step in steps)
            and raw_equal
            and validation.get("outcome") == "VALIDATED"
            and replay.get("status") == "REPLAY_VALIDATED"
            and status.get("ok") is True
            and status.get("counts", {}).get("sources") == 1
            and query.get("database_root_unchanged") is True
        )
        report = {
            "schema": "HHS_PASS145_CEUAC_A2_BLACK_BOX_V1",
            "authority_level": "A2",
            "actor_boundary": "PUBLIC_HHS_CLI_ONLY",
            "process_restart_boundary_exercised": True,
            "steps": steps,
            "passed": passed,
            "apk_surface_exercised": False,
            "apk_surface_status": "NOT_EXPOSED",
            "conclusion": "HOST_CLI_EXTERNAL_CAPABILITY_OBSERVED" if passed else "HOST_CLI_EXTERNAL_CAPABILITY_FAILED",
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
