from hhs_backend.runtime.hhs_document_structure_fusion_v1 import fuse_document_observations, validate_document_fusion
from hhs_backend.runtime.hhs_document_projection_bundle_v1 import build_document_projection_bundle, validate_document_projection_bundle
from hhs_backend.runtime.hhs_document_perception_receipt_v1 import build_document_perception_receipt, validate_document_perception_receipt
from hhs_backend.runtime.hhs_document_reconstruction_plan_v1 import build_document_reconstruction_plan, validate_document_reconstruction_plan
from hhs_backend.runtime.hhs_deep_document_perception_pipeline_v1 import (
    run_deep_document_perception,
    validate_deep_document_perception_run,
    deep_document_perception_pipeline_self_test,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72


def test_document_fusion_preserves_disagreement():
    source = {"source_root_hash72": hash72("SOURCE", "doc")}
    native = {"projection_type": "PDF_NATIVE_TEXT_PROJECTION", "observation_root_hash72": hash72("OBS", "native"), "extracted_text_root_hash72": hash72("TEXT", "native")}
    ocr = {"projection_type": "OCR_TEXT_PROJECTION", "observation_root_hash72": hash72("OBS", "ocr"), "ocr_region_projections": [{"ocr_text_root_hash72": hash72("TEXT", "ocr")}]}
    fusion = fuse_document_observations(source_commitment=source, observations=[native, ocr])
    assert fusion["fusion_state"] == "OBSERVATION_DISAGREEMENT"
    assert fusion["provider_disagreement_collapsed_silently"] is False
    assert validate_document_fusion(fusion)["ok"]
    bad = dict(fusion, provider_disagreement_collapsed_silently=True)
    assert not validate_document_fusion(bad)["ok"]


def test_projection_bundle_receipt_and_reconstruction_keep_source_distinct():
    source = {"source_root_hash72": hash72("SOURCE", "doc")}
    obs = {"projection_type": "PDF_NATIVE_TEXT_PROJECTION", "observation_root_hash72": hash72("OBS", "native"), "provider_id": "provider:pdf-native-text", "loss_profile": "DECLARED"}
    fusion = {"fusion_root_hash72": hash72("FUSION", "f")}
    bundle = build_document_projection_bundle(source_commitment=source, observations=[obs], fusion_record=fusion)
    assert validate_document_projection_bundle(bundle)["ok"]
    receipt = build_document_perception_receipt(source_commitment=source, projection_bundle=bundle, fusion_record=fusion)
    assert validate_document_perception_receipt(receipt)["ok"]
    plan = build_document_reconstruction_plan(source_commitment=source, projection_bundle=bundle, perception_receipt=receipt, observation_roots=[obs["observation_root_hash72"]])
    assert validate_document_reconstruction_plan(plan)["ok"]
    assert plan["expanded_metadata_retained"] is False


def test_deep_document_perception_pipeline_runs_pdf_and_image():
    pdf = run_deep_document_perception(project_id="project:test", source_name="spec.pdf", payload="%PDF BT (native HHS) ET", declared_modality="PDF", ocr_text_hint="native HHS")
    assert pdf["ok"]
    assert validate_deep_document_perception_run(pdf)["ok"]
    assert pdf["provider_result_ingress"]["ok"]
    assert pdf["universal_artifact_pipeline"]["ok"]
    assert pdf["critical_doctrine"]["ocr_text_ne_page_image"] is True
    image = run_deep_document_perception(project_id="project:test", source_name="scan.png", payload="scan HHS", declared_modality="IMAGE", ocr_text_hint="scan HHS")
    assert image["ok"]


def test_reject_private_document_truth_pipeline():
    run = run_deep_document_perception(project_id="project:test", source_name="spec.pdf", payload="%PDF", declared_modality="PDF")
    bad = dict(run, private_document_truth_pipeline_allowed=True)
    rejected = validate_deep_document_perception_run(bad)
    assert not rejected["ok"]
    assert "REJECT_PROVIDER_PRIVATE_TRUTH_PIPELINE" in rejected["reasons"]


def test_pipeline_self_test():
    assert deep_document_perception_pipeline_self_test()["ok"]
