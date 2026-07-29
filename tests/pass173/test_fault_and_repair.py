from __future__ import annotations

from pathlib import Path

from hhs_verification.pass173.fault_injection import CATALOG, FaultInjector
from hhs_verification.pass173.repair_planner import Defect, RepairPlanner


def test_fault_injection_restores_original_and_preserves_state(tmp_path: Path) -> None:
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "user.db").write_bytes(b"user-state")
    target = tmp_path / "runtime" / "native" / "artifact.bin"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"valid")
    case = next(item for item in CATALOG if item.fault_id == "native-symbol")

    def verifier(path: Path) -> str:
        return case.expected_classification if path.read_bytes() == b"corrupt" else "UNEXPECTED"

    result = FaultInjector(tmp_path).run_file_fault(
        case,
        relative_path="runtime/native/artifact.bin",
        verifier=verifier,
        corrupt=b"corrupt",
    )
    assert result.detected is True
    assert result.rollback_completed is True
    assert result.user_data_preserved is True
    assert target.read_bytes() == b"valid"


def test_repair_plan_is_dependency_scoped() -> None:
    defect = Defect(
        defect_id="D1",
        classification="P173_NATIVE_SYMBOL_MISSING",
        affected_paths=("hhs_installer/native_builder.py",),
        affected_requirements=("P172-PLATFORM-001",),
        evidence=("evidence/native/symbols.json",),
        authority_boundary="Pass 172 native builder",
    )
    plan = RepairPlanner().build(
        defect,
        dependency_graph={"hhs_installer/native_builder.py": ["manifests/pass172/native_targets.json"]},
        test_graph={
            "hhs_installer/native_builder.py": ["tests/pass172/test_native_builder.py"],
            "manifests/pass172/native_targets.json": ["tests/pass172/integration/test_native_matrix.py"],
        },
    )
    assert plan.repair_class == "SYMBOL_EXPORT_REPAIR"
    assert plan.unit_tests == ("tests/pass172/test_native_builder.py",)
    assert plan.integration_tests == ("tests/pass172/integration/test_native_matrix.py",)
    assert "contract source modification" in plan.prohibited_changes
