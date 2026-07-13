from hhs_backend.runtime.hhs_modality_source_commitment_v1 import modality_source_commitment_self_test, build_source_commitment
from hhs_backend.runtime.hhs_universal_modality_adapter_v1 import universal_modality_adapter_self_test, list_default_adapter_contracts, validate_adapter_contract
from hhs_backend.runtime.hhs_modality_projection_registry_v1 import modality_projection_registry_self_test


def test_source_commitment_preserves_original_identity():
    result = modality_source_commitment_self_test()
    assert result["ok"]
    assert result["rejected"]["reasons"] == ["REJECT_PROJECTION_REPLACES_SOURCE"]


def test_all_modalities_share_universal_adapter_contract():
    result = universal_modality_adapter_self_test()
    assert result["ok"]
    assert result["adapter_count"] >= 18
    assert "VIDEO" in result["modalities"]
    assert "AUDIO" in result["modalities"]
    assert result["private_truth_pipeline_rejection"]["reasons"] == ["REJECT_ADAPTER_PRIVATE_TRUTH_PIPELINE"]


def test_adapter_contract_rejects_source_replacement():
    contract = list_default_adapter_contracts()[0]
    bad = dict(contract, projection_replaces_source=True)
    validation = validate_adapter_contract(bad)
    assert not validation["ok"]
    assert "REJECT_PROJECTION_REPLACES_SOURCE" in validation["reasons"]


def test_projection_registry_marks_lossy_projection():
    result = modality_projection_registry_self_test()
    assert result["ok"]
    assert result["projection"]["lossy_projection"] is True
    assert "REJECT_LOSSY_PROJECTION_UNMARKED" in result["lossy_unmarked_rejection"]["reasons"]
