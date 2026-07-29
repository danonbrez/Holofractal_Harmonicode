from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json

from hhs_installer.canonical import hash216, stable
from hhs_installer.journal import atomic_write_json
from .verdicts import VerdictEngine, VerdictInput


class VerificationReportBuilder:
    def build(
        self,
        *,
        requirement_scan: Mapping[str, Any],
        dependency_scan: Mapping[str, Any],
        coverage: Mapping[str, Any],
        environments: Mapping[str, Any],
        profiles: Mapping[str, Any],
        receipts: Mapping[str, Any],
        replay: Mapping[str, Any],
        defects: Mapping[str, Any],
        verdict_input: VerdictInput,
    ) -> dict[str, Any]:
        verdict = VerdictEngine.classify(verdict_input)
        payload = {
            "schema": "HHS_PASS_173_FINAL_VERIFICATION_REPORT_V1",
            "contract_id": "HHS-P173-UIFCRV-CRRCR",
            "requirement_scan": stable(requirement_scan),
            "dependency_scan": stable(dependency_scan),
            "coverage": stable(coverage),
            "environments": stable(environments),
            "profiles": stable(profiles),
            "receipts": stable(receipts),
            "replay": stable(replay),
            "defects": stable(defects),
            "verdict": verdict.to_dict(),
            "honest_nonclaims": [
                "No unavailable platform, architecture, physical GPU, provider, model, Android build, or offline bundle is classified verified.",
                "Static inspection is not represented as clean-install execution.",
                "Mock provider responses are not represented as real provider support.",
                "A generated receipt is not evidence that an unexecuted operation ran.",
                "Pass 172 and Pass 173 remain nonterminal unless the verdict is A+ with omega_173=true.",
            ],
        }
        payload["report_identity"] = hash216(payload, domain="HHS-P173-FINAL-REPORT-V1")
        return stable(payload)

    def write(self, path: str | Path, report: Mapping[str, Any]) -> None:
        atomic_write_json(path, report)

    @staticmethod
    def write_markdown(path: str | Path, report: Mapping[str, Any]) -> None:
        verdict = report["verdict"]
        lines = [
            "# HHS Pass 173 verification report",
            "",
            f"- Verdict: `{verdict['verdict']}`",
            f"- Terminal: `{str(verdict['terminal']).lower()}`",
            f"- Omega 173: `{str(verdict['omega_173']).lower()}`",
            f"- Report identity: `{report['report_identity']}`",
            "",
            "## Blockers",
            "",
        ]
        blockers = verdict.get("blockers", [])
        lines.extend(f"- `{blocker}`" for blocker in blockers)
        if not blockers:
            lines.append("- None")
        lines.extend(["", "## Honest nonclaims", ""])
        lines.extend(f"- {item}" for item in report.get("honest_nonclaims", []))
        Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
