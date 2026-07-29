from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping
import os
import shutil
import tempfile

from hhs_installer.canonical import hash216, stable


@dataclass(frozen=True)
class FaultCase:
    fault_id: str
    family: str
    description: str
    expected_classification: str
    mutation_scope: tuple[str, ...]
    reversible: bool = True

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


@dataclass(frozen=True)
class FaultResult:
    fault_id: str
    detected: bool
    observed_classification: str
    expected_classification: str
    user_data_preserved: bool
    rollback_completed: bool
    evidence_identity: str
    details: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


CATALOG: tuple[FaultCase, ...] = (
    FaultCase("missing-python", "P173_ENVIRONMENT", "Python executable absent", "P173_ENVIRONMENT_PYTHON_MISSING", ("probe",)),
    FaultCase("wrong-python", "P173_ENVIRONMENT", "Python below minimum", "P173_ENVIRONMENT_PYTHON_UNSUPPORTED", ("probe",)),
    FaultCase("missing-compiler", "P173_NATIVE", "C11 compiler absent", "P173_NATIVE_COMPILER_MISSING", ("probe", "native")),
    FaultCase("source-digest", "P173_SOURCE", "source digest mismatch", "P173_SOURCE_DIGEST_MISMATCH", ("staging/source",)),
    FaultCase("archive-traversal", "P173_SECURITY", "archive contains traversal entry", "P173_SECURITY_ARCHIVE_TRAVERSAL", ("staging/source",)),
    FaultCase("dependency-lock", "P173_DEPENDENCY", "dependency lock mismatch", "P173_DEPENDENCY_LOCK_MISMATCH", ("runtime/python",)),
    FaultCase("partial-venv", "P173_DEPENDENCY", "partial virtual environment", "P173_DEPENDENCY_PYTHON_ENVIRONMENT_INCOMPLETE", ("runtime/python",)),
    FaultCase("native-symbol", "P173_NATIVE", "required native symbol missing", "P173_NATIVE_SYMBOL_MISSING", ("runtime/native",)),
    FaultCase("api-port", "P173_PORT", "API port occupied", "P173_PORT_API_OCCUPIED", ("runtime/config",)),
    FaultCase("provider-port", "P173_PORT", "provider port occupied", "P173_PORT_PROVIDER_OCCUPIED", ("runtime/config",)),
    FaultCase("stale-lock", "P173_TRANSACTION", "stale installation lock", "P173_TRANSACTION_STALE_LOCK", ("install/locks",)),
    FaultCase("activation-interrupt", "P173_TRANSACTION", "activation interrupted", "P173_TRANSACTION_ACTIVATION_INTERRUPTED", ("current",)),
    FaultCase("receipt-forgery", "P173_VALIDATION", "receipt field altered", "P173_VALIDATION_HASH72_RECEIPT_FORGED", ("install/receipts",)),
    FaultCase("offline-network", "P173_SECURITY", "network attempted in offline mode", "P173_OFFLINE_NETWORK_POLICY_VIOLATION", ("offline",)),
    FaultCase("uninstall-data-loss", "P173_UNINSTALL", "protected user data selected for deletion", "P173_UNINSTALL_PRESERVATION_VIOLATION", ("state",)),
)


class FaultInjector:
    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    def run_file_fault(
        self,
        case: FaultCase,
        *,
        relative_path: str,
        verifier: Callable[[Path], str],
        corrupt: bytes = b"P173_FAULT\n",
    ) -> FaultResult:
        target = (self.workspace / relative_path).resolve()
        if self.workspace not in target.parents and target != self.workspace:
            raise ValueError("P173_FAULT_SCOPE_ESCAPE")
        target.parent.mkdir(parents=True, exist_ok=True)
        original_exists = target.exists()
        original = target.read_bytes() if original_exists else None
        protected_state = self.workspace / "state"
        protected_before = self._tree_identity(protected_state)
        try:
            target.write_bytes(corrupt)
            observed = verifier(target)
            detected = observed == case.expected_classification
        finally:
            if original_exists and original is not None:
                target.write_bytes(original)
            else:
                target.unlink(missing_ok=True)
        protected_after = self._tree_identity(protected_state)
        details = {
            "target": str(target.relative_to(self.workspace)),
            "reversible": case.reversible,
            "protected_before": protected_before,
            "protected_after": protected_after,
        }
        identity = hash216({"case": case.to_dict(), "details": details, "observed": observed}, domain="HHS-P173-FAULT-EVIDENCE-V1")
        return FaultResult(
            fault_id=case.fault_id,
            detected=detected,
            observed_classification=observed,
            expected_classification=case.expected_classification,
            user_data_preserved=protected_before == protected_after,
            rollback_completed=not target.exists() if not original_exists else target.read_bytes() == original,
            evidence_identity=identity,
            details=details,
        )

    @staticmethod
    def isolated_workspace() -> tempfile.TemporaryDirectory[str]:
        return tempfile.TemporaryDirectory(prefix="hhs-pass173-fault-")

    @staticmethod
    def _tree_identity(path: Path) -> str:
        if not path.exists():
            return hash216([], domain="HHS-P173-PROTECTED-TREE-V1")
        records: list[dict[str, Any]] = []
        for item in sorted(path.rglob("*")):
            if item.is_file():
                records.append({"path": str(item.relative_to(path)).replace("\\", "/"), "bytes": item.read_bytes()})
        return hash216(records, domain="HHS-P173-PROTECTED-TREE-V1")
