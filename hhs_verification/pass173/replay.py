from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import json

from hhs_installer.canonical import hash216, stable
from hhs_installer.receipts import ReceiptChain, ReceiptError


@dataclass(frozen=True)
class ReplayResult:
    mode: str
    matched: bool
    classification: str
    input_identity: str
    reconstructed_identity: str
    claimed_identity: str | None
    receipt_tip: str | None
    details: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class InstallationReplay:
    @staticmethod
    def logical(
        *,
        request: Mapping[str, Any],
        probe: Mapping[str, Any],
        plan: Mapping[str, Any],
        artifacts: Mapping[str, Any],
        validation: Mapping[str, Any],
        receipt_path: str | Path | None = None,
        claimed_identity: str | None = None,
    ) -> ReplayResult:
        payload = {
            "request": stable(request),
            "probe": stable(probe),
            "plan": stable(plan),
            "artifacts": stable(artifacts),
            "validation": stable(validation),
        }
        input_identity = hash216(payload, domain="HHS-P173-LOGICAL-REPLAY-INPUT-V1")
        reconstructed = hash216(
            {
                "source": artifacts.get("source"),
                "profile": plan.get("resolved_profile"),
                "platform": probe.get("platform"),
                "architecture": probe.get("architecture"),
                "dependencies": artifacts.get("dependencies"),
                "native": artifacts.get("native"),
                "frontend": artifacts.get("frontend"),
                "provider": artifacts.get("provider"),
                "model": artifacts.get("model"),
                "evidence": validation,
            },
            domain="HHS-P173-LOGICAL-REPLAY-RESULT-V1",
        )
        receipt_tip: str | None = None
        receipt_valid = True
        receipt_error: str | None = None
        if receipt_path is not None:
            try:
                chain = ReceiptChain(receipt_path)
                receipt_tip = chain.tip
            except ReceiptError as exc:
                receipt_valid = False
                receipt_error = str(exc)
        matched = receipt_valid and (claimed_identity is None or claimed_identity == reconstructed)
        return ReplayResult(
            mode="logical",
            matched=matched,
            classification="P173_LOGICAL_REPLAY_MATCH" if matched else "P173_LOGICAL_REPLAY_DIVERGENCE",
            input_identity=input_identity,
            reconstructed_identity=reconstructed,
            claimed_identity=claimed_identity,
            receipt_tip=receipt_tip,
            details={"receipt_valid": receipt_valid, "receipt_error": receipt_error},
        )

    @staticmethod
    def compare_clean_runs(first: Mapping[str, Any], second: Mapping[str, Any], *, platform_bound_fields: Iterable[str] = ()) -> ReplayResult:
        ignored = set(platform_bound_fields)
        first_stable = {key: value for key, value in stable(first).items() if key not in ignored}
        second_stable = {key: value for key, value in stable(second).items() if key not in ignored}
        first_identity = hash216(first_stable, domain="HHS-P173-CLEAN-REPLAY-CANONICAL-V1")
        second_identity = hash216(second_stable, domain="HHS-P173-CLEAN-REPLAY-CANONICAL-V1")
        matched = first_identity == second_identity
        return ReplayResult(
            mode="full-clean-environment-compare",
            matched=matched,
            classification="P173_FINAL_CLEAN_REPLAY_MATCH" if matched else "P173_FINAL_CLEAN_REPLAY_DIVERGENCE",
            input_identity=hash216({"first": first, "second": second}, domain="HHS-P173-CLEAN-REPLAY-INPUT-V1"),
            reconstructed_identity=second_identity,
            claimed_identity=first_identity,
            receipt_tip=None,
            details={"ignored_platform_bound_fields": sorted(ignored)},
        )

    @staticmethod
    def load_capsule(path: str | Path) -> dict[str, Any]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        required = {"request", "probe", "plan", "artifacts", "validation"}
        missing = sorted(required - set(payload))
        if missing:
            raise ValueError(f"P173_REPLAY_CAPSULE_FIELDS_MISSING:{','.join(missing)}")
        return payload
