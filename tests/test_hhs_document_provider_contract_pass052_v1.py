from hhs_backend.runtime.hhs_document_provider_contract_v1 import (
    build_document_provider_contract,
    validate_document_provider_contract,
    build_document_provider_admission,
    document_provider_contract_self_test,
)
from hhs_backend.runtime.hhs_pdf_native_text_provider_v1 import extract_pdf_native_text, validate_pdf_native_text_observation
from hhs_backend.runtime.hhs_pdf_page_geometry_provider_v1 import observe_pdf_page_geometry, validate_pdf_page_geometry_observation
from hhs_backend.runtime.hhs_document_image_region_provider_v1 import observe_document_image_regions, validate_document_image_region_observation
from hhs_backend.runtime.hhs_ocr_provider_v1 import run_ocr_on_regions, validate_ocr_observation
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72


def test_document_provider_contract_rejects_provider_authority():
    contract = build_document_provider_contract(provider_id="provider:test", capability_class="OCR")
    assert validate_document_provider_contract(contract)["ok"]
    bad = dict(contract, provider_is_canonical_authority=True)
    decision = validate_document_provider_contract(bad)
    assert not decision["ok"]
    assert "REJECT_DOCUMENT_PROVIDER_AS_AUTHORITY" in decision["reasons"]


def test_document_provider_admission_uses_capability_policy_chain():
    contract = build_document_provider_contract(provider_id="provider:pdf-native-text", capability_class="DOCUMENT_EXTRACTION")
    admission = build_document_provider_admission(contract=contract, project_id="project:test", input_payload="%PDF")
    assert admission["ok"]
    assert admission["provider_never_becomes_canonical_authority"] is True
    assert admission["runtime_admission"]["ok"]


def test_pdf_native_text_is_not_complete_document():
    source = {"source_root_hash72": hash72("SOURCE", "%PDF BT (hello) ET")}
    observation = extract_pdf_native_text(source_commitment=source, payload="%PDF BT (hello) ET")
    assert validate_pdf_native_text_observation(observation)["ok"]
    bad = dict(observation, pdf_parser_output_is_complete_document=True)
    rejected = validate_pdf_native_text_observation(bad)
    assert not rejected["ok"]
    assert "REJECT_PDF_TEXT_AS_COMPLETE_DOCUMENT" in rejected["reasons"]


def test_page_geometry_and_image_region_are_projections():
    source = {"source_root_hash72": hash72("SOURCE", "image")}
    geometry = observe_pdf_page_geometry(source_commitment=source, payload="%PDF", page_count_hint=2)
    assert validate_pdf_page_geometry_observation(geometry)["ok"]
    regions = observe_document_image_regions(source_commitment=source, payload="scan", page_geometry=geometry)
    assert validate_document_image_region_observation(regions)["ok"]
    bad_regions = dict(regions, regions=[dict(regions["regions"][0], region_is_document_identity=True)])
    assert not validate_document_image_region_observation(bad_regions)["ok"]


def test_ocr_text_is_projection_not_source():
    source = {"source_root_hash72": hash72("SOURCE", "image")}
    regions = {"observation_root_hash72": hash72("REGIONS", "r"), "regions": [{"region_id": "region:0", "page_index": 0, "region_root_hash72": hash72("REGION", "r")}]} 
    observation = run_ocr_on_regions(source_commitment=source, image_regions=regions, payload="HHS OCR")
    assert validate_ocr_observation(observation)["ok"]
    bad = dict(observation, ocr_text_is_document_source=True)
    rejected = validate_ocr_observation(bad)
    assert not rejected["ok"]
    assert "REJECT_OCR_TEXT_AS_DOCUMENT_SOURCE" in rejected["reasons"]


def test_document_provider_contract_self_test():
    assert document_provider_contract_self_test()["ok"]
