from __future__ import annotations

import importlib.util
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "hhs_optimization_control_v1.py"
CONTRACT = ROOT / "contracts" / "pass219" / "PASS_219_NORMALIZED_OPTIMIZATION_CONTROL_V1.md"
APPENDIX = ROOT / "docs" / "whitepapers" / "HHS_PRACTICAL_APPLICATIONS_AND_VON_NEUMANN_COMPARISON_APPENDIX_V1.md"
TUTORIAL = ROOT / "docs" / "tutorials" / "HHS_LANE5_OPTIMIZATION_CONTROL_TUTORIAL_V1.md"
MANUAL = ROOT / "docs" / "manuals" / "HHS_OPTIMIZATION_AND_PERFORMANCE_MANUAL_V1.md"
DOCS_README = ROOT / "docs" / "README.md"
TUTORIALS_README = ROOT / "docs" / "tutorials" / "README.md"

spec = importlib.util.spec_from_file_location("hhs_opt_control", TOOL)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def qinfo(rate: int = 323557) -> dict:
    return {
        "result": "PASS",
        "physical_runner_observation": {
            "candidate_count": 1_000_000,
            "candidate_rate_floor_per_second": rate,
        },
        "logical_state_space": {
            "binary_embedding_bits": 445,
            "native_address_bytes": 56,
        },
        "authority": {
            "observational_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        },
        "hardware_normalization": {
            "runner_label": "ubuntu-24.04",
            "provider_declared_vcpu": 4,
        },
    }


def test_frozen_reference_math() -> None:
    assert mod.R_REF == Decimal(323557)
    assert mod.H_ADDR == Decimal(
        "444.23460010384649012933840792848557726141327470771727270562838225391814480238763"
    )
    m = mod.metrics(qinfo())
    assert m["basis"] == mod.GAMMA_BASIS_REF
    assert m["route"] == mod.GAMMA_ROUTE_REF
    assert m["qudit"] == mod.GAMMA_QUDIT_REF
    assert m["vm5184"] == mod.GAMMA_VM_REF


def test_exact_membrane_rejects_authority_drift() -> None:
    value = qinfo()
    assert mod.exact_membrane_ok(value)
    value["authority"]["canonical_hash216_authority"] = True
    assert not mod.exact_membrane_ok(value)


def test_paired_jitter_floor() -> None:
    control = mod.metrics(qinfo(100_000))
    candidate_pass = mod.metrics(qinfo(95_000))
    candidate_fail = mod.metrics(qinfo(94_999))
    assert mod.ratio(candidate_pass["shot"], control["shot"]) == Decimal("0.95")
    assert mod.ratio(candidate_fail["shot"], control["shot"]) < mod.DEFAULT_PAIRED_FLOOR


def test_documents_publish_control_and_practical_translation() -> None:
    required_paths = (CONTRACT, APPENDIX, TUTORIAL, MANUAL, DOCS_README, TUTORIALS_README)
    for path in required_paths:
        assert path.is_file(), path
    combined = "\n".join(path.read_text(encoding="utf-8") for path in required_paths)
    for needle in (
        "323,557",
        "143.735",
        "574.941",
        "568 bytes",
        "14,336,000,000 bytes",
        "von Neumann",
        "paired",
        "replay",
        "AI/ML inference orchestration",
    ):
        assert needle.lower() in combined.lower(), needle
