from copy import deepcopy

import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass112_pass_safe_resume_exit_v1 import PassSafeExitEngine
from hhs_runtime.hhs_pass113_safe_lossless_archive_v1 import (
    ArchiveError,
    ArchivePolicy,
    RecoveryContract,
    SafeLosslessArchiveEngine,
    _build_pass112_bundles,
    pass113_self_test,
)


@pytest.fixture(scope="module")
def result():
    return pass113_self_test()


def _roots():
    return {
        "authority": _hash("test_authority", {"v": 1}),
        "dependency": _hash("test_dependency", {"v": 1}),
        "security": _hash("test_security", {"v": 1}),
        "provenance": _hash("test_provenance", {"v": 1}),
    }


def _contract(**updates):
    values = dict(maximum_recovery_memory_bytes=2_000_000, maximum_recovery_work_units=5_000_000,
                  maximum_expansion_ratio_numerator=100, maximum_chunk_count=4096)
    values.update(updates)
    return RecoveryContract(**values)


def _archive(source=None, policy=None, contract=None):
    completed, _ = _build_pass112_bundles()
    source = source or completed
    roots = _roots()
    engine = SafeLosslessArchiveEngine(policy or ArchivePolicy(chunk_size_bytes=512))
    bundle = engine.archive(source, source_class="VM_PASS112_EXIT", recovery_contract=contract or _contract(),
                            authority_root_hash72=roots["authority"], dependency_root_hash72=roots["dependency"],
                            security_policy_root_hash72=roots["security"], provenance_root_hash72=roots["provenance"])
    return engine, bundle, roots


def test_pass113_round_trip_and_pass112_reconstruction(result):
    assert result["status"] == "PASS"
    assert result["completed_recovery"]["recovered_state"] == result["completed_exit_reconstruction"] or result["completed_exit_reconstruction"]["reconstruction_status"] == "RECONSTRUCTED"
    assert result["deferred_exit_reconstruction"]["reconstruction_status"] == "RECONSTRUCTED"


def test_pass113_uses_exact_rational_compression_ratio(result):
    ratio = result["completed_archive"]["compression_receipt"]["compression_ratio"]
    assert set(ratio) == {"numerator", "denominator"}
    assert isinstance(ratio["numerator"], int)
    assert isinstance(ratio["denominator"], int)
    assert ratio["denominator"] > 0


def test_pass113_manifest_contains_bounded_recovery_contract(result):
    manifest = result["completed_archive"]["archive"]["manifest"]
    assert manifest["maximum_recovery_work"] > 0
    assert manifest["maximum_recovery_memory_bytes"] > 0
    assert manifest["recovery_contract_root_hash72"]
    assert manifest["compression_algorithm_root_hash72"]


def test_pass113_selects_from_real_stdlib_codecs(result):
    manifest = result["completed_archive"]["archive"]["manifest"]
    assert manifest["compression_algorithm"] in {"raw", "zlib", "lzma"}
    assert len(manifest["codec_observations"]) == 3


def test_pass113_rejects_corrupted_chunk():
    engine, bundle, roots = _archive()
    corrupted = deepcopy(bundle["archive"])
    corrupted["chunks"][0]["payload_hex"] = ("00" if corrupted["chunks"][0]["payload_hex"][:2] != "00" else "01") + corrupted["chunks"][0]["payload_hex"][2:]
    corrupted["archive_root_hash72"] = _hash("hhs_pass113_archive_v1", {k: deepcopy(v) for k, v in corrupted.items() if k != "archive_root_hash72"})
    with pytest.raises(ArchiveError) as exc:
        engine.recover(corrupted, available_memory_bytes=2_000_000, available_work_units=5_000_000,
                       revalidate_authority_root_hash72=roots["authority"])
    assert exc.value.code == "REJECT_CORRUPTED_ARCHIVE_CHUNK"


def test_pass113_rejects_manifest_tampering():
    engine, bundle, roots = _archive()
    tampered = deepcopy(bundle["archive"])
    tampered["manifest"]["uncompressed_size_bytes"] += 1
    with pytest.raises(ArchiveError) as exc:
        engine.recover(tampered, available_memory_bytes=2_000_000, available_work_units=5_000_000,
                       revalidate_authority_root_hash72=roots["authority"])
    assert exc.value.code in {"REJECT_ARCHIVE_ROOT_MISMATCH", "REJECT_ARCHIVE_MANIFEST_ROOT_MISMATCH"}


def test_pass113_rejects_stale_authority_on_recovery():
    engine, bundle, _ = _archive()
    with pytest.raises(ArchiveError) as exc:
        engine.recover(bundle["archive"], available_memory_bytes=2_000_000, available_work_units=5_000_000,
                       revalidate_authority_root_hash72="changed")
    assert exc.value.code == "REJECT_AUTHORITY_REACTIVATION_WITHOUT_REVALIDATION"


def test_pass113_predicts_insufficient_recovery_resources():
    engine, bundle, _ = _archive()
    status = engine.inspect_recovery(bundle["archive"], available_memory_bytes=1, available_work_units=1)
    assert status["status"] == "INSUFFICIENT_RECOVERY_RESOURCES"


def test_pass113_rejects_unstable_pass112_checkpoint():
    completed, _ = _build_pass112_bundles()
    completed["exit_checkpoint"]["checkpoint_status"] = "OPEN"
    roots = _roots()
    engine = SafeLosslessArchiveEngine()
    with pytest.raises(ArchiveError) as exc:
        engine.archive(completed, source_class="VM_PASS112_EXIT", recovery_contract=_contract(),
                       authority_root_hash72=roots["authority"], dependency_root_hash72=roots["dependency"],
                       security_policy_root_hash72=roots["security"], provenance_root_hash72=roots["provenance"])
    assert exc.value.code == "REJECT_VM_SNAPSHOT_AT_UNSTABLE_COORDINATE"


def test_pass113_rejects_recovery_work_debt_before_archive():
    completed, _ = _build_pass112_bundles()
    roots = _roots()
    engine = SafeLosslessArchiveEngine()
    with pytest.raises(ArchiveError) as exc:
        engine.archive(completed, source_class="VM_PASS112_EXIT", recovery_contract=_contract(maximum_recovery_work_units=1),
                       authority_root_hash72=roots["authority"], dependency_root_hash72=roots["dependency"],
                       security_policy_root_hash72=roots["security"], provenance_root_hash72=roots["provenance"])
    assert exc.value.code == "REJECT_UNBOUNDED_RECOVERY_WORK"


def test_pass113_rejects_recovery_memory_debt_before_archive():
    completed, _ = _build_pass112_bundles()
    roots = _roots()
    engine = SafeLosslessArchiveEngine()
    with pytest.raises(ArchiveError) as exc:
        engine.archive(completed, source_class="VM_PASS112_EXIT", recovery_contract=_contract(maximum_recovery_memory_bytes=1),
                       authority_root_hash72=roots["authority"], dependency_root_hash72=roots["dependency"],
                       security_policy_root_hash72=roots["security"], provenance_root_hash72=roots["provenance"])
    assert exc.value.code == "REJECT_UNBOUNDED_RECOVERY_MEMORY"


def test_pass113_rejects_expansion_ratio_bomb():
    engine, bundle, roots = _archive(contract=_contract(maximum_expansion_ratio_numerator=100))
    bomb = deepcopy(bundle["archive"])
    bomb["recovery_contract"]["maximum_expansion_ratio_numerator"] = 1
    bomb["recovery_contract"]["maximum_expansion_ratio_denominator"] = 100
    bomb["recovery_contract"]["recovery_contract_root_hash72"] = _hash("hhs_pass113_recovery_contract_v1", {k: v for k, v in bomb["recovery_contract"].items() if k not in {"schema", "recovery_contract_root_hash72"}})
    bomb["archive_root_hash72"] = _hash("hhs_pass113_archive_v1", {k: deepcopy(v) for k, v in bomb.items() if k != "archive_root_hash72"})
    with pytest.raises(ArchiveError) as exc:
        engine.recover(bomb, available_memory_bytes=2_000_000, available_work_units=5_000_000,
                       revalidate_authority_root_hash72=roots["authority"])
    assert exc.value.code == "REJECT_ARCHIVE_EXPANSION_RATIO_EXCEEDED"


def test_pass113_migration_preserves_source_root(result):
    migration = result["migration"]
    assert migration["migration_relation"]["equivalence_valid"] is True
    assert migration["migration_relation"]["old_archive_retained"] is True
    assert migration["archive"]["manifest"]["source_state_root_hash72"] == migration["migration_relation"]["source_state_root_hash72"]


def test_pass113_recovered_exit_is_execution_equivalent():
    engine, bundle, roots = _archive()
    recovered = engine.recover(bundle["archive"], available_memory_bytes=2_000_000, available_work_units=5_000_000,
                               revalidate_authority_root_hash72=roots["authority"])
    reconstructed = PassSafeExitEngine.reconstruct_exit(recovered["recovered_state"])
    assert reconstructed["reconstruction_status"] == "RECONSTRUCTED"


def test_pass113_service_registered_and_conformance_derived():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    registry = make_default_service_registry()
    service = next(x for x in registry.services() if x["name"] == "runtime.safe_lossless_archive.pass113")
    assert service["conformance_decision"]["derivation_complete"] is True
    assert "bounded_recovery_contract_required" in service["guards"]
    assert "zero_bypass_runtime_interposer" in service["guards"]
