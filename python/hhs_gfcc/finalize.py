from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .core import stable, write_json
from .manifest import write_manifests

SUCCESS_TERMINAL = "GOLDEN_FRACTAL_CORRESPONDENCE_CONSTRUCTOR_VERIFIED"
PARTIAL_TERMINAL = "GOLDEN_FRACTAL_CONSTRUCTOR_PARTIAL"


def _read_report(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("HHS_GFCC_INTERNAL_ERROR:validation report is not an object")
    return stable(value)


def _markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# HHS Pass 152 GFCC Validation Report",
            "",
            f"- Contract: `{report['contract_id']}`",
            f"- Positive tests: **{report['positive_tests']['passed']}/{report['positive_tests']['total']}**",
            f"- Negative tests: **{report['negative_tests']['passed']}/{report['negative_tests']['total']}**",
            f"- Replay: **{'MATCH' if report['replay']['match'] else 'MISMATCH'}**",
            f"- Receipt chain: **{'VALID' if report['receipt_audit']['valid'] else 'INVALID'}**",
            f"- Source manifest: **{'VALID' if report['source_manifest_validation']['valid'] else 'INVALID'}**",
            f"- Inherited Pass 152: **{'VALID' if report['inheritance']['valid'] else 'INVALID'}**",
            f"- Artifact manifest: **{'VALID' if report['artifact_manifest']['valid'] else 'INVALID'}**",
            f"- Terminal classification: `{report['terminal_classification']}`",
            f"- Incomplete obligations: `{report['incomplete_obligations']}`",
            "",
        ]
    )


def finalize_report_and_artifacts(repo: Path) -> dict[str, Any]:
    subsystem = repo / "native_projects" / "hhs_gfcc_pass152"
    reports = subsystem / "reports"
    report_path = reports / "HHS_PASS_152_VALIDATION_REPORT.json"
    if not report_path.is_file():
        raise RuntimeError("HHS_GFCC_INTERNAL_ERROR:validation report missing")
    report = _read_report(report_path)
    artifact_info = dict(report.get("artifact_manifest") or {})
    artifact_info.pop("manifest_digest", None)
    report["artifact_manifest"] = {
        "valid": bool(artifact_info.get("valid")),
        "missing_artifacts": list(artifact_info.get("missing_artifacts") or []),
        "digest_location": "HHS_PASS_152_ARTIFACT_MANIFEST.json",
    }
    write_json(report_path, report)
    (reports / "HHS_PASS_152_VALIDATION_REPORT.md").write_text(
        _markdown(report), encoding="utf-8"
    )
    manifests = write_manifests(repo)
    artifact = manifests["artifact_manifest"]
    non_artifact_obligations = {
        key: bool(value)
        for key, value in report.get("obligations", {}).items()
        if key != "artifact_manifest"
    }
    complete = all(non_artifact_obligations.values()) and artifact["valid"] is True
    report["obligations"] = {
        **non_artifact_obligations,
        "artifact_manifest": artifact["valid"] is True,
    }
    report["artifact_manifest"] = {
        "valid": artifact["valid"] is True,
        "missing_artifacts": artifact["missing_artifacts"],
        "digest_location": "HHS_PASS_152_ARTIFACT_MANIFEST.json",
    }
    report["terminal_classification_emitted"] = complete
    report["terminal_classification"] = (
        SUCCESS_TERMINAL if complete else PARTIAL_TERMINAL
    )
    report["incomplete_obligations"] = sorted(
        key for key, value in report["obligations"].items() if not value
    )
    write_json(report_path, report)
    (reports / "HHS_PASS_152_VALIDATION_REPORT.md").write_text(
        _markdown(report), encoding="utf-8"
    )
    final_manifests = write_manifests(repo)
    final_artifact = final_manifests["artifact_manifest"]
    if final_artifact["valid"] is not complete and complete:
        raise RuntimeError(
            "HHS_GFCC_INTERNAL_ERROR:artifact validity changed during finalization"
        )
    write_json(
        subsystem / "HHS_PASS_152_ARTIFACT_MANIFEST.json", final_artifact
    )
    return {
        "report": report,
        "artifact_manifest": final_artifact,
        "source_manifest_validation": final_manifests[
            "source_manifest_validation"
        ],
        "repository_manifest": final_manifests["repository_manifest"],
    }


__all__ = ["finalize_report_and_artifacts"]
