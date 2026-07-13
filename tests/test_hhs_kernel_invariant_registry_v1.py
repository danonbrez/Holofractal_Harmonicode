import pytest

from hhs_runtime.hhs_kernel_invariant_registry_v1 import (
    HHSInvariantRegistryError,
    HHSKernelInvariantRegistry,
    build_default_invariant_registry,
    validate_invariant_registry,
    resolve_invariant_dependencies,
)


def test_default_registry_has_kernel_invariants():
    registry = build_default_invariant_registry()
    validation = registry.validate_invariant_registry()
    assert validation["ok"] is True
    assert validation["invariant_count"] >= 16
    assert validation["registry_root_hash72"]


def test_registry_rejects_duplicate_conflicting_invariant():
    registry = HHSKernelInvariantRegistry()
    record = {
        "invariant_id": "HHS-X001",
        "name": "Test Invariant",
        "statement": "A",
        "required_witnesses": ["W"],
        "required_validators": ["V"],
        "rejection_codes": ["R"],
    }
    registry.register_invariant(record)
    changed = dict(record)
    changed["statement"] = "B"
    with pytest.raises(HHSInvariantRegistryError):
        registry.register_invariant(changed)


def test_registry_rejects_unknown_dependency():
    registry = HHSKernelInvariantRegistry()
    registry.register_invariant({
        "invariant_id": "HHS-X002",
        "name": "Dependent",
        "statement": "Depends on missing invariant.",
        "depends_on": ["HHS-MISSING"],
        "required_witnesses": ["W"],
        "required_validators": ["V"],
        "rejection_codes": ["R"],
    })
    validation = registry.validate_invariant_registry()
    assert validation["ok"] is False
    assert any("HHS-MISSING" in reason for reason in validation["reasons"])


def test_dependency_resolution_is_deterministic():
    deps = resolve_invariant_dependencies("HHS-I015")
    assert deps[-1] == "HHS-I015"
    assert "HHS-I011" in deps
    assert "HHS-I014" in deps
