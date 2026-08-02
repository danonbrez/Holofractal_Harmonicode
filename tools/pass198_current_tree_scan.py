#!/usr/bin/env python3
"""Run a bounded Pass 196 scan and emit a concise current-tree integration report."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from hhs_backend.runtime.hhs_pass196_integrated_environment_v1 import Pass196IntegratedEnvironment
from hhs_backend.runtime.pass197_exact_v1 import canonical_json, hash72

SCHEMA = "HHS_PASS_198_CURRENT_TREE_INTEGRATION_SCAN_V1"


def build_report(repository_root: Path, state_root: Path) -> dict:
    runtime = Pass196IntegratedEnvironment(
        repository_root=repository_root,
        state_root=state_root,
        workers=4,
    )
    status = runtime.scan(
        vm81_receipt_hash72=None,
        persist_vector=False,
    )
    gaps = runtime.gaps()
    manifest = status["manifest"]
    unresolved = [
        {
            "pass_number": item["pass_number"],
            "state": item["state"],
            "artifact_count": item["artifact_count"],
            "surfaces": item["surfaces"],
            "contracts": item["contracts"],
            "artifact_root_hash72": item["artifact_root_hash72"],
        }
        for item in gaps["unresolved_passes"]
    ]
    body = {
        "schema": SCHEMA,
        "manifest_hash72": status["manifest_hash72"],
        "manifest_hash216": status["manifest_hash216"],
        "phase": status["phase"],
        "scanned": status["scanned"],
        "integration_closed": status["integration_closed"],
        "operational_surfaces": status["operational"],
        "file_count": status["file_count"],
        "byte_count": status["byte_count"],
        "maximum_discovered_pass": status["maximum_discovered_pass"],
        "pass_state_counts": status["pass_state_counts"],
        "surface_counts": status["surface_matrix"]["counts"],
        "missing_mandatory_surfaces": status["surface_matrix"]["missing_mandatory_surfaces"],
        "unresolved_pass_count": gaps["unresolved_pass_count"],
        "unresolved_passes": unresolved,
        "pass198": next(
            (item for item in manifest["pass_matrix"] if item["pass_number"] == 198),
            None,
        ),
        "authority": manifest["authority"],
        "claim_boundary": {
            "scan_is_repository_observation": True,
            "scan_grants_runtime_authority": False,
            "persisted_encrypted_vector": False,
            "live_digitalocean_acceptance": False,
        },
    }
    return {**body, "scan_report_hash72": hash72("pass198.current.tree.scan", body)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output", required=True)
    parser.add_argument("--state-root")
    args = parser.parse_args()
    repository_root = Path(args.repository_root).resolve()
    output = Path(args.output).resolve()
    if args.state_root:
        report = build_report(repository_root, Path(args.state_root).resolve())
    else:
        with tempfile.TemporaryDirectory() as temporary:
            report = build_report(repository_root, Path(temporary))
    if not report["scanned"]:
        raise SystemExit("Pass 196 did not complete repository observation")
    if report["maximum_discovered_pass"] < 198:
        raise SystemExit("Pass 198 was not discovered in current-tree scan")
    if report["pass198"] is None:
        raise SystemExit("Pass 198 classification is missing")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(report) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
