from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from hhs_installer.canonical import hash216, stable


REPAIR_CLASSES = {
    "MANIFEST_REPAIR",
    "LOCKFILE_REPAIR",
    "PROFILE_MEMBERSHIP_REPAIR",
    "PLATFORM_ADAPTER_REPAIR",
    "PATH_ADAPTER_REPAIR",
    "NOEXEC_FALLBACK_REPAIR",
    "NATIVE_BUILD_REPAIR",
    "SYMBOL_EXPORT_REPAIR",
    "PYTHON_ENVIRONMENT_REPAIR",
    "FRONTEND_DEPENDENCY_REPAIR",
    "PORT_SELECTION_REPAIR",
    "PROVIDER_CLASSIFICATION_REPAIR",
    "MODEL_IMPORT_REPAIR",
    "RECEIPT_COUNT_REPAIR",
    "TEST_CONFIGURATION_REPAIR",
    "INTERRUPTION_RECOVERY_REPAIR",
    "ROLLBACK_REPAIR",
    "UNINSTALL_PRESERVATION_REPAIR",
    "DOCUMENTATION_REPAIR",
}


@dataclass(frozen=True)
class Defect:
    defect_id: str
    classification: str
    affected_paths: tuple[str, ...]
    affected_requirements: tuple[str, ...]
    evidence: tuple[str, ...]
    authority_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


@dataclass(frozen=True)
class RepairPlan:
    defect_id: str
    repair_class: str
    implementation_paths: tuple[str, ...]
    unit_tests: tuple[str, ...]
    integration_tests: tuple[str, ...]
    prohibited_changes: tuple[str, ...]
    expected_receipts: tuple[str, ...]
    plan_identity: str = ""

    def __post_init__(self) -> None:
        if self.repair_class not in REPAIR_CLASSES:
            raise ValueError("P173_REPAIR_CLASS_INVALID")
        if not self.plan_identity:
            object.__setattr__(self, "plan_identity", hash216(self.to_dict(include_identity=False), domain="HHS-P173-REPAIR-PLAN-V1"))

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        result = asdict(self)
        if not include_identity:
            result.pop("plan_identity", None)
        return stable(result)


class RepairPlanner:
    CLASS_MAP: Mapping[str, str] = {
        "P173_SOURCE": "MANIFEST_REPAIR",
        "P173_DEPENDENCY_LOCK": "LOCKFILE_REPAIR",
        "P173_DEPENDENCY_PROFILE": "PROFILE_MEMBERSHIP_REPAIR",
        "P173_ENVIRONMENT_PLATFORM": "PLATFORM_ADAPTER_REPAIR",
        "P173_ENVIRONMENT_PATH": "PATH_ADAPTER_REPAIR",
        "P173_ENVIRONMENT_NOEXEC": "NOEXEC_FALLBACK_REPAIR",
        "P173_NATIVE_BUILD": "NATIVE_BUILD_REPAIR",
        "P173_NATIVE_SYMBOL": "SYMBOL_EXPORT_REPAIR",
        "P173_DEPENDENCY_PYTHON": "PYTHON_ENVIRONMENT_REPAIR",
        "P173_FRONTEND": "FRONTEND_DEPENDENCY_REPAIR",
        "P173_PORT": "PORT_SELECTION_REPAIR",
        "P173_PROVIDER": "PROVIDER_CLASSIFICATION_REPAIR",
        "P173_MODEL": "MODEL_IMPORT_REPAIR",
        "P173_RECEIPT": "RECEIPT_COUNT_REPAIR",
        "P173_VALIDATION_CONFIG": "TEST_CONFIGURATION_REPAIR",
        "P173_TRANSACTION": "INTERRUPTION_RECOVERY_REPAIR",
        "P173_ROLLBACK": "ROLLBACK_REPAIR",
        "P173_UNINSTALL": "UNINSTALL_PRESERVATION_REPAIR",
    }

    def choose_class(self, defect: Defect) -> str:
        for prefix, repair_class in sorted(self.CLASS_MAP.items(), key=lambda item: len(item[0]), reverse=True):
            if defect.classification.startswith(prefix):
                return repair_class
        return "DOCUMENTATION_REPAIR" if not defect.affected_paths else "PLATFORM_ADAPTER_REPAIR"

    def build(
        self,
        defect: Defect,
        *,
        dependency_graph: Mapping[str, Iterable[str]],
        test_graph: Mapping[str, Iterable[str]],
    ) -> RepairPlan:
        implementation_paths = tuple(sorted(set(defect.affected_paths)))
        impacted_requirements = set(defect.affected_requirements)
        expanded_paths = set(implementation_paths)
        for path in implementation_paths:
            expanded_paths.update(str(item) for item in dependency_graph.get(path, ()))
        unit_tests: set[str] = set()
        integration_tests: set[str] = set()
        for path in sorted(expanded_paths):
            for test in test_graph.get(path, ()):
                test_name = str(test)
                if "/integration/" in test_name or test_name.endswith("_integration.py"):
                    integration_tests.add(test_name)
                else:
                    unit_tests.add(test_name)
        if not unit_tests and not integration_tests:
            raise ValueError("P173_REPAIR_HAS_NO_REVALIDATION_SCOPE")
        return RepairPlan(
            defect_id=defect.defect_id,
            repair_class=self.choose_class(defect),
            implementation_paths=tuple(sorted(expanded_paths)),
            unit_tests=tuple(sorted(unit_tests)),
            integration_tests=tuple(sorted(integration_tests)),
            prohibited_changes=(
                "contract source modification",
                "test deletion or weakening",
                "strict compiler flag weakening",
                "profile reclassification without evidence",
                "alternate VM81, Hash72, Hash216, installer, or receipt authority",
                "historical evidence deletion",
            ),
            expected_receipts=("P173_REPAIR_PLAN_RECEIPT", "P173_DEPENDENCY_SCOPE_REVALIDATION_RECEIPT"),
        )
