from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts/pass214/PASS_214_CONTRACT.json"
SCHEMA_PATH = ROOT / "contracts/pass214/PASS_214_MEASUREMENT_RECORD.schema.json"
PLAN_PATH = ROOT / "evidence/pass214/PASS_214_ITERATION_1_MEASUREMENT_PLAN.json"
DOC_PATH = ROOT / "HHS_PASS_214_OPERATING_COMPRESSION_GRADIENT_ADMISSION_INCIDENCE_CALIBRATION.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_identity_and_sequence() -> None:
    contract = load(CONTRACT_PATH)
    assert contract["pass"] == 214
    assert contract["schema"] == "HHS_PASS_214_CONTRACT_V1"
    assert contract["predecessor"]["pass"] == 213
    assert contract["predecessor"]["development_branch"] == "agent/pass213-compiled-rom-integrity"
    assert "authoritative Pass 213 closure" in contract["predecessor"]["activation_rule"]


def test_full_hydration_arithmetic_is_exact() -> None:
    fixed = load(CONTRACT_PATH)["fixed_dimensions"]
    assert fixed["local_leaf_bits"] == 81 * 64 == 5184
    assert fixed["hydration_lanes"] == 8 * 5 == 40
    assert fixed["full_leaf_count"] == 243 * 40 == 9720
    assert fixed["full_hydration_bits"] == 5184 * 243 * 40 == 50_388_480
    assert fixed["full_hydration_bytes"] == fixed["full_hydration_bits"] // 8 == 6_298_560
    assert fixed["pure_generator_seed_bits"] == 9720 * 2 == 19_440
    assert fixed["pure_generator_seed_bytes"] == 2_430
    assert fixed["raw_protected_bytes"] == 6_298_560 + 51_840 == 6_350_400


def test_reference_ratios_remain_reference_only() -> None:
    contract = load(CONTRACT_PATH)
    fixed = contract["fixed_dimensions"]
    assert Fraction(fixed["tier1_reference_ratio"]) == Fraction(6_298_560, 2_473)
    assert Fraction(fixed["tier2_reference_ratio"]) == Fraction(6_298_560, 10_665)
    assert any("remain Pass 212 reference vectors" in item for item in contract["iteration_1_nonclaims"])
    assert contract["validation"]["status"].startswith("CONTRACT_ONLY")


def test_operating_denominator_is_complete() -> None:
    required = {
        "generator_seeds",
        "exception_positions",
        "exception_values",
        "raw_fallback_payloads",
        "gf256_parity",
        "package_manifests",
        "framing",
        "hash72_receipts",
        "hash216_identities",
        "retrieval_indexes",
        "reconstruction_indexes",
        "required_alignment_and_padding",
    }
    assert required == set(load(CONTRACT_PATH)["operating_ratio_denominator_must_include"])


def test_all_incidence_and_transition_views_are_required() -> None:
    contract = load(CONTRACT_PATH)
    metrics = contract["primary_metrics"]
    for key in (
        "snapshot_incidence",
        "byte_weighted_incidence",
        "transition_incidence",
        "dwell_time_incidence",
        "structured_snapshot_incidence",
        "structured_byte_incidence",
        "operating_ratio",
    ):
        assert key in metrics
    assert len(contract["transition_matrix"]["required_cells"]) == 9
    assert set(contract["transition_matrix"]["tiers"]) == {1, 2, 3}


def test_tier_admission_is_honest_and_size_aware() -> None:
    contract = load(CONTRACT_PATH)
    policy = contract["admission_policy"]
    assert "smallest complete protected representation" in policy["selection"]
    assert "strictly less than tier 3" in policy["tier2_requirement"]
    assert "Reference ratios are ceilings" in policy["no_reference_vector_substitution"]
    assert contract["acceptance"]["allowed_false_compression_claims"] == 0


def test_measurement_schema_carries_required_authority_fields() -> None:
    schema = load(SCHEMA_PATH)
    required = set(schema["required"])
    for field in (
        "selected_tier",
        "canonical_state_bytes",
        "protected_physical_bytes",
        "exception_count",
        "state_hash216",
        "package_hash216",
        "hash72_receipt",
        "exact_decode_verified",
        "deterministic_replay_verified",
        "recovery_drill",
    ):
        assert field in required
    assert schema["properties"]["exception_density_denominator"]["const"] == 50_388_480
    assert schema["properties"]["selected_tier"]["enum"] == [1, 2, 3]


def test_iteration_one_plan_matches_contract() -> None:
    contract = load(CONTRACT_PATH)
    plan = load(PLAN_PATH)
    assert plan["contract"] == contract["contract"]
    assert plan["pass"] == 214
    assert plan["status"] == "CONTRACT_ONLY_NO_WORKLOAD_RESULT_CLAIM"
    assert plan["required_workload_classes"] == contract["workload_classes"]
    assert plan["required_transition_cells"] == contract["transition_matrix"]["required_cells"]
    assert plan["fixed_arithmetic"]["raw_parity_fraction"] == "51840/6298560"


def test_document_states_sequence_and_nonclaim_boundaries() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "Pass 213 is already reserved" in text
    assert "must not merge ahead" in text
    assert "No payload-only ratio" in text
    assert "does **not** claim workload incidence" in text
