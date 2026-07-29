from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Iterable, Mapping

from hhs_installer.canonical import hash216, stable


class Verdict(str, Enum):
    H = "H. INSUFFICIENT_EVIDENCE"
    G = "G. STATICALLY_MAPPED"
    F = "F. PARTIALLY_EXECUTED"
    E = "E. DEFECT_CONFIRMED"
    D = "D. REPAIR_IMPLEMENTED"
    C = "C. DEPENDENCY_SCOPE_REVALIDATED"
    B = "B. FULL_MATRIX_EXECUTED"
    A = "A. REDUNDANTLY_VERIFIED"
    A_PLUS = "A+. CALIBRATED_REPAIR_REPLAY_CLOSED"


@dataclass(frozen=True)
class VerdictInput:
    contract_fully_mapped: bool = False
    executed_cases: int = 0
    required_cases: int = 0
    confirmed_defects: int = 0
    repairs_implemented: int = 0
    affected_scopes_revalidated: bool = False
    full_matrix_executed: bool = False
    redundant_lane_agreement: bool = False
    calibration_passed: bool = False
    final_replay_match: bool = False
    receipt_mismatches: int = 0
    authority_bypasses: int = 0
    data_loss_events: int = 0
    unrepaired_defects: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerdictResult:
    verdict: Verdict
    terminal: bool
    omega_173: bool
    blockers: tuple[str, ...]
    result_identity: str

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["verdict"] = self.verdict.value
        return stable(result)


class VerdictEngine:
    @staticmethod
    def classify(value: VerdictInput) -> VerdictResult:
        blockers: list[str] = []
        terminal_requirements = {
            "contract_fully_mapped": value.contract_fully_mapped,
            "all_required_cases_executed": value.required_cases > 0 and value.executed_cases >= value.required_cases,
            "full_matrix_executed": value.full_matrix_executed,
            "redundant_lane_agreement": value.redundant_lane_agreement,
            "calibration_passed": value.calibration_passed,
            "final_replay_match": value.final_replay_match,
            "receipt_mismatches_zero": value.receipt_mismatches == 0,
            "authority_bypasses_zero": value.authority_bypasses == 0,
            "data_loss_events_zero": value.data_loss_events == 0,
            "unrepaired_defects_zero": value.unrepaired_defects == 0,
        }
        blockers.extend(key for key, passed in terminal_requirements.items() if not passed)
        if all(terminal_requirements.values()):
            verdict = Verdict.A_PLUS
        elif value.redundant_lane_agreement:
            verdict = Verdict.A
        elif value.full_matrix_executed:
            verdict = Verdict.B
        elif value.affected_scopes_revalidated:
            verdict = Verdict.C
        elif value.repairs_implemented > 0:
            verdict = Verdict.D
        elif value.confirmed_defects > 0:
            verdict = Verdict.E
        elif value.executed_cases > 0:
            verdict = Verdict.F
        elif value.contract_fully_mapped:
            verdict = Verdict.G
        else:
            verdict = Verdict.H
        terminal = verdict is Verdict.A_PLUS
        payload = {"input": value.to_dict(), "verdict": verdict.value, "terminal": terminal, "blockers": blockers}
        return VerdictResult(
            verdict=verdict,
            terminal=terminal,
            omega_173=terminal,
            blockers=tuple(blockers),
            result_identity=hash216(payload, domain="HHS-P173-VERDICT-V1"),
        )
