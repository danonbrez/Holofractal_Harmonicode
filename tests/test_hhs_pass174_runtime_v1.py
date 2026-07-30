from dataclasses import replace
from pathlib import Path

import pytest

from hhs_runtime.pass174 import (
    EncryptedVectorStore,
    Hash216Array,
    LegacyInheritanceError,
    Pass174Error,
    Pass174Runtime,
    PhaseCoordinate,
    build_legacy_manifest,
)


def _foundation(tmp_path: Path):
    (tmp_path / "HHS_PASS_001_GENESIS.md").write_text("pass 1\n")
    (tmp_path / "HHS_PASS_042_INVARIANTS.md").write_text("pass 42\n")
    (tmp_path / "HHS_PASS_150_HASH216.md").write_text("pass 150\n")
    (tmp_path / "HHS_PASS_163_VMRC.md").write_text("pass 163\n")
    (tmp_path / "HHS_PASS_173_INSTALL_VERIFY.md").write_text("pass 173\n")
    return build_legacy_manifest(tmp_path)


def test_legacy_specs_are_append_only_minimum_foundation(tmp_path):
    manifest = _foundation(tmp_path)
    assert manifest.maximum_inherited_pass == 173
    assert manifest.pass_numbers_present == (1, 42, 150, 163, 173)
    assert manifest.specification_count == 5
    assert len(manifest.aggregate_root_sha256) == 64
    (tmp_path / "HHS_PASS_174_NEW.md").write_text("pass 174 is not part of inherited root\n")
    observed = build_legacy_manifest(tmp_path)
    assert observed.aggregate_root_sha256 == manifest.aggregate_root_sha256


def test_pass173_is_required(tmp_path):
    (tmp_path / "HHS_PASS_001_GENESIS.md").write_text("pass 1\n")
    with pytest.raises(LegacyInheritanceError, match="HHS_P174_PASS_173_FOUNDATION_REQUIRED"):
        build_legacy_manifest(tmp_path)


def test_phase_gears_lock_at_5184_without_implying_state_reset():
    before = PhaseCoordinate.at(5183)
    closure = PhaseCoordinate.at(5184)
    assert before.full_phase_lock is False
    assert closure.full_phase_lock is True
    assert (closure.phase64, closure.phase72, closure.phase81, closure.phase5184) == (0, 0, 0, 0)


def test_hash216_has_three_ordered_lanes_and_216_indexes(tmp_path):
    runtime = Pass174Runtime(repository_root=tmp_path, legacy_manifest=_foundation(tmp_path))
    first = runtime.vmrc.state_hash72
    array = Hash216Array.build(
        first,
        first,
        first,
        genesis_identity=runtime.genesis_identity,
        logical_step=0,
        operation_identity="1" * 64,
        legacy_foundation_root=runtime.legacy_foundation_root,
    )
    assert len(array.combined) == 216
    assert len(array.character_indexes_sha256) == 216
    assert len(set(array.character_indexes_sha256)) == 216
    array.verify()


def test_direct_execution_admits_encrypted_vector_and_replay(tmp_path):
    runtime = Pass174Runtime(legacy_manifest=_foundation(tmp_path))
    result = runtime.execute(thread=7, writes={0: 1, 8: 1, 80: -1})
    assert result["path"] == "DIRECT_RUNTIME"
    assert result["object"]["plaintext_exposed"] is False
    assert len(result["object"]["hash216"]["combined"]) == 216
    assert len(result["object"]["hash216"]["character_indexes_sha256"]) == 216
    assert runtime.vmrc.snapshot().get(0, 7) == 1
    assert runtime.replay()["receipt_chain_valid"] is True


def test_validated_retrieval_commits_one_whole_frame(tmp_path):
    manifest = _foundation(tmp_path)
    store = EncryptedVectorStore(key=b"k" * 32)
    producer = Pass174Runtime(legacy_manifest=manifest, vector_store=store)
    direct = producer.execute(thread=3, writes={1: 1, 2: 1})
    consumer = Pass174Runtime(legacy_manifest=manifest, vector_store=store)
    retrieved = consumer.execute(thread=3, writes={1: 1, 2: 1}, prefer_retrieval=True)
    assert direct["path"] == "DIRECT_RUNTIME"
    assert retrieved["path"] == "RETRIEVAL"
    assert consumer.vmrc.epoch == 1
    assert consumer.vmrc.state_hash72 == producer.vmrc.state_hash72
    assert consumer.vmrc.snapshot().to_bytes() == producer.vmrc.snapshot().to_bytes()
    assert consumer.replay()["inherited_vmrc_replay"]["retrieved_frame_events_supported"] is True


def test_ciphertext_tamper_is_rejected_and_never_admitted(tmp_path):
    manifest = _foundation(tmp_path)
    store = EncryptedVectorStore(key=b"z" * 32)
    runtime = Pass174Runtime(legacy_manifest=manifest, vector_store=store)
    result = runtime.execute(thread=0, writes={4: 1})
    object_id = result["object"]["object_id"]
    obj = store._objects[object_id]
    damaged = obj.ciphertext_b64[:-2] + ("AA" if obj.ciphertext_b64[-2:] != "AA" else "BB")
    store._objects[object_id] = replace(obj, ciphertext_b64=damaged)
    fresh = Pass174Runtime(legacy_manifest=manifest, vector_store=store)
    with pytest.raises(Pass174Error, match="HHS_P174_VECTOR_AUTHENTICATION_FAILED"):
        fresh.execute(thread=0, writes={4: 1}, prefer_retrieval=True)
    assert fresh.vmrc.epoch == 0


def test_3_by_144_controller_and_exact_harmonic_gate(tmp_path):
    runtime = Pass174Runtime(legacy_manifest=_foundation(tmp_path))
    controller = runtime.phase_controller()
    assert controller["planes_count"] == 3
    assert controller["directed_relationships_per_plane"] == 144
    assert controller["total_directed_relationships"] == 432
    compiled = runtime.register_harmonic_gate(
        connectors=["+", "*", "Or", "=="],
        phase_offsets=[0, 8, 9, 36],
        exact_weights=["1/4", "1/4", "1/4", "1/4"],
    )
    assert compiled["gate"]["additive_endpoint"] == "x+y"
    assert compiled["gate"]["multiplicative_endpoint"] == "xy"
    assert compiled["gate"]["operator_order_preserved"] is True


def test_audit_binds_genesis_legacy_root_and_vector_frontier(tmp_path):
    runtime = Pass174Runtime(legacy_manifest=_foundation(tmp_path))
    runtime.execute(thread=1, writes={2: 1})
    audit = runtime.audit(challenge="unit-test-unpredictable-after-seal", deep=True)
    assert audit["classification"] == "HHS_PASS_174_AUDIT_PASS"
    assert audit["sample_count"] == 1
    assert audit["vector_store_root"] == runtime.vector_store.root()
