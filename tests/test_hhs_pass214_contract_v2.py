from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts/pass214/PASS_214_CONTRACT.json"
SCHEMA = ROOT / "contracts/pass214/PASS_214_BENCHMARK_RECORD.schema.json"
SPEC = ROOT / "HHS_PASS_214_REPOSITORY_WIDE_COMPOUND_OPTIMIZATION_BENCHMARK_AUTHORITY.md"
README = ROOT / "docs/pass214/README.md"
RESTART = ROOT / "docs/pass214/RESTART_RECORD.md"
PLAN = ROOT / "evidence/pass214/PASS_214_ITERATION_1_REPOSITORY_SCAN_PLAN.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_required_files_exist() -> None:
    for path in (CONTRACT, SCHEMA, SPEC, README, RESTART, PLAN):
        assert path.is_file(), path


def test_contract_identity_and_foundation() -> None:
    contract = load_json(CONTRACT)
    assert contract["pass"] == 214
    assert contract["classification"] == "HHS_PASS_214_REPOSITORY_WIDE_COMPOUND_OPTIMIZATION_BENCHMARK_CONTRACT_FROZEN"
    assert contract["pass213_foundation"]["authoritative_merge"] == "86ec461818682fc87232740758769602e8f9fe05"
    assert contract["contract_baseline"] == "ff7363ea5e35d659be5866ebb684620bc55ca967"
    assert "complete_pre_pass_foundation" in contract["inherits"]


def test_pass215_boundary_is_frozen() -> None:
    contract = load_json(CONTRACT)
    successor = contract["successor"]
    assert successor["pass"] == 215
    assert "NATIVE-TRANSFORMER-SYMBOLIC-INGESTION" in successor["contract"]
    assert "PASS214_AUTHORITY_ROOT_HASH216" in contract["terminal_roots"]
    assert "PASS215_BENCHMARK_PROFILE_ROOT_HASH216" in contract["terminal_roots"]


def test_repository_scan_is_complete_by_contract() -> None:
    contract = load_json(CONTRACT)
    scan = contract["repository_scan"]
    assert scan["tree_manifest_required"] is True
    assert "SCANNED_CALLABLE" in scan["dispositions"]
    assert "SCANNED_CONTRACT_ONLY" in scan["dispositions"]
    assert "CONFLICTING_AUTHORITY" in scan["relation_classes"]
    assert "entrypoint" in scan["symbol_record_fields"]


def test_multimodal_machine_learning_is_first_class() -> None:
    contract = load_json(CONTRACT)
    assert "multimodal_machine_learning" in contract["optimization_families"]
    layers = set(contract["required_known_layers"])
    assert "residual_novelty_contradiction" in layers
    assert "bounded_backpropagation" in layers
    assert "dataset_and_checkpoint_lineage" in layers
    assert "pass213_compiled_rom" in layers


def test_compound_and_ablation_stages_are_frozen() -> None:
    contract = load_json(CONTRACT)
    stages = contract["benchmark_stages"]
    assert list(stages) == [f"A{i}" for i in range(10)]
    assert stages["A4"] == "complete_inherited_hhs_stack"
    assert stages["A5"] == "full_stack_one_layer_disabled"
    assert "semantic_composition_cache" in contract["mandatory_ablations"]
    assert "multimodal_cross_alignment" in contract["mandatory_ablations"]
    assert "native_dispatch" in contract["mandatory_ablations"]


def test_semantic_and_observational_identity_are_separate() -> None:
    contract = load_json(CONTRACT)
    separation = contract["semantic_observational_separation"]
    assert "Exact canonical" in separation["semantic"]
    assert "Hardware timing" in separation["observational"]
    assert "shall not redefine semantic identity" in separation["rule"]


def test_schema_requires_root_bound_semantic_and_observational_results() -> None:
    schema = load_json(SCHEMA)
    required = set(schema["required"])
    assert "repository_tree_root_hash216" in required
    assert "optimization_registry_root_hash216" in required
    assert "compatibility_graph_root_hash216" in required
    assert "semantic_result" in required
    assert "observational_result" in required
    assert "receipt_hash72" in required


def test_scan_plan_makes_no_false_completion_claim() -> None:
    plan = load_json(PLAN)
    assert plan["classification"] == "PLAN_ONLY_NO_SCAN_COMPLETION_CLAIM"
    assert any("No complete repository scan" in item for item in plan["nonclaims"])
    assert "optimization_registry.json" in " ".join(plan["required_outputs"])


def test_formal_spec_preserves_old_compression_work_as_subbenchmark() -> None:
    text = SPEC.read_text(encoding="utf-8")
    assert "Pass 213 authoritative closure" in text
    assert "pre-pass foundation" in text
    assert "multimodal machine-learning optimization" in text
    assert "prior Pass 214 operating-compression-gradient draft" in text
    assert "It no longer defines the whole pass" in text
    assert "Pass 215 SHALL bind" in text
    assert "CONTRACT_AUTHORIZED — FULL IMPLEMENTATION REQUIRED" in text
