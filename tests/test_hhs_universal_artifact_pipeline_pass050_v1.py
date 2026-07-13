from hhs_backend.runtime.hhs_modality_reconstruction_recipe_v1 import modality_reconstruction_recipe_self_test
from hhs_backend.runtime.hhs_cross_modal_transformation_plan_v1 import cross_modal_transformation_plan_self_test
from hhs_backend.runtime.hhs_derived_artifact_pipeline_v1 import derived_artifact_pipeline_self_test
from hhs_backend.runtime.hhs_artifact_lineage_registry_v1 import artifact_lineage_registry_self_test
from hhs_backend.runtime.hhs_modality_adapter_capability_map_v1 import modality_adapter_capability_map_self_test
from hhs_backend.runtime.hhs_universal_artifact_pipeline_v1 import universal_artifact_pipeline_self_test, run_universal_artifact_pipeline


def test_reconstruction_recipe_compacts_expanded_metadata():
    result = modality_reconstruction_recipe_self_test()
    assert result["ok"]
    assert "REJECT_WORKSPACE_PERSISTENCE_EXPANDED_METADATA" in result["rejected"]["reasons"]


def test_cross_modal_plan_requires_reconstruction():
    result = cross_modal_transformation_plan_self_test()
    assert result["ok"]
    assert "REJECT_CROSS_MODAL_PLAN_WITHOUT_RECONSTRUCTION" in result["reconstruction_rejection"]["reasons"]


def test_derived_artifact_does_not_infer_execution_authority():
    result = derived_artifact_pipeline_self_test()
    assert result["ok"]
    assert result["artifact"]["execution_authorized"] is False
    assert "REJECT_ARTIFACT_EXECUTION_AUTHORITY_INFERRED" in result["execution_authority_rejection"]["reasons"]


def test_artifact_lineage_keeps_source_projection_artifact_separate():
    result = artifact_lineage_registry_self_test()
    assert result["ok"]
    assert result["lineage"]["source_not_replaced_by_projection"] is True
    assert "REJECT_PROJECTION_REPLACES_SOURCE" in result["projection_replace_rejection"]["reasons"]


def test_adapter_capability_map_covers_all_modalities():
    result = modality_adapter_capability_map_self_test()
    assert result["ok"]
    capability_map = result["capability_map"]
    assert capability_map["shared_contract"] == "HHS_UNIVERSAL_MODALITY_ADAPTER_V1"
    assert "VIDEO" in capability_map["supported_modalities"]
    assert "AUDIO" in capability_map["supported_modalities"]


def test_universal_artifact_pipeline_vertical_slice():
    result = universal_artifact_pipeline_self_test()
    assert result["ok"]
    for run in result["pipeline_runs"]:
        assert run["ok"]
        assert run["artifact"]["execution_authorized"] is False
        assert run["lineage"]["source_not_replaced_by_projection"] is True
        assert run["source_projection_artifact_separation"] == "source != projection != artifact != execution_authority"


def test_universal_pipeline_rejects_no_private_truth_stack():
    run = run_universal_artifact_pipeline(
        project_id="project:test",
        source_name="clip.mp4",
        payload="video",
        source_modality="VIDEO",
        projection_type="TEMPORAL_SCENE_PROJECTION",
        target_modality="GRAPH_OBJECT",
        target_artifact_type="VIDEO_SCENE_GRAPH",
    )
    assert run["ok"]
    assert run["adaptation"]["adapter_contract"]["private_truth_pipeline_allowed"] is False
