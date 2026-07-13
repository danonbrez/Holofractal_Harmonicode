"""HHS Deep Deterministic Document Perception Pipeline v1."""
from __future__ import annotations
from typing import Any, Dict, Mapping
import time, uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_modality_source_commitment_v1 import build_source_commitment
from hhs_backend.runtime.hhs_pdf_native_text_provider_v1 import extract_pdf_native_text, validate_pdf_native_text_observation
from hhs_backend.runtime.hhs_pdf_page_geometry_provider_v1 import observe_pdf_page_geometry, validate_pdf_page_geometry_observation
from hhs_backend.runtime.hhs_document_image_region_provider_v1 import observe_document_image_regions, validate_document_image_region_observation
from hhs_backend.runtime.hhs_ocr_provider_v1 import run_ocr_on_regions, validate_ocr_observation
from hhs_backend.runtime.hhs_document_structure_fusion_v1 import fuse_document_observations, validate_document_fusion
from hhs_backend.runtime.hhs_document_projection_bundle_v1 import build_document_projection_bundle, validate_document_projection_bundle
from hhs_backend.runtime.hhs_document_perception_receipt_v1 import build_document_perception_receipt, validate_document_perception_receipt
from hhs_backend.runtime.hhs_document_reconstruction_plan_v1 import build_document_reconstruction_plan, validate_document_reconstruction_plan
from hhs_backend.runtime.hhs_provider_result_ingress_v1 import ingress_provider_result
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import build_provider_execution_proposal
from hhs_backend.runtime.hhs_provider_invocation_receipt_v1 import invoke_provider_with_receipt
from hhs_backend.runtime.hhs_universal_artifact_pipeline_v1 import run_universal_artifact_pipeline
from hhs_backend.runtime.hhs_document_provider_contract_v1 import VERSION, AUTHORITY
SCHEMA="HHS_DEEP_DOCUMENT_PERCEPTION_PIPELINE_RUN_V1"
def _unique(prefix:str)->str: return f"{prefix}:{uuid.uuid4().hex}"
def _now_ms()->int: return int(time.time()*1000)

def run_deep_document_perception(*, project_id:str, source_name:str, payload:Any, declared_modality:str="PDF", page_count_hint:int=1, ocr_text_hint:str="") -> Dict[str,Any]:
    source=build_source_commitment(project_id=project_id, source_name=source_name, payload=payload, modality=declared_modality)
    native=extract_pdf_native_text(source_commitment=source, payload=payload, page_count_hint=page_count_hint)
    geometry=observe_pdf_page_geometry(source_commitment=source, payload=payload, page_count_hint=page_count_hint)
    regions=observe_document_image_regions(source_commitment=source, payload=payload, page_geometry=geometry)
    ocr=run_ocr_on_regions(source_commitment=source, image_regions=regions, payload=payload, text_hint=ocr_text_hint)
    observations=[native, geometry, regions, ocr]
    validations=[validate_pdf_native_text_observation(native), validate_pdf_page_geometry_observation(geometry), validate_document_image_region_observation(regions), validate_ocr_observation(ocr)]
    fusion=fuse_document_observations(source_commitment=source, observations=observations)
    fusion_validation=validate_document_fusion(fusion)
    bundle=build_document_projection_bundle(source_commitment=source, observations=observations, fusion_record=fusion)
    bundle_validation=validate_document_projection_bundle(bundle)
    receipt=build_document_perception_receipt(source_commitment=source, projection_bundle=bundle, fusion_record=fusion)
    receipt_validation=validate_document_perception_receipt(receipt)
    reconstruction=build_document_reconstruction_plan(source_commitment=source, projection_bundle=bundle, perception_receipt=receipt, observation_roots=[o.get("observation_root_hash72") for o in observations])
    reconstruction_validation=validate_document_reconstruction_plan(reconstruction)
    provider_proposal=build_provider_execution_proposal(capability_class="DOCUMENT_EXTRACTION", project_id=project_id, input_payload={"source": source.get("source_root_hash72"), "bundle": bundle.get("bundle_root_hash72")}, requested_operation="document_perception.provider_result_ingress")
    provider_invocation=invoke_provider_with_receipt(provider_proposal, simulated_raw_result={"bundle_root_hash72":bundle.get("bundle_root_hash72"),"fusion_root_hash72":fusion.get("fusion_root_hash72")})
    provider_result_ingress=ingress_provider_result(provider_invocation, project_id=project_id, output_modality="JSON")
    artifact_pipeline=run_universal_artifact_pipeline(project_id=project_id, source_name=source_name, payload={"bundle":bundle.get("bundle_root_hash72")}, source_modality=declared_modality, projection_type="DOCUMENT_GRAPH_PROJECTION", target_modality="GRAPH_OBJECT", target_artifact_type="DOCUMENT_GRAPH_ARTIFACT")
    ok=all(v.get("ok") for v in validations) and fusion_validation.get("ok") and bundle_validation.get("ok") and receipt_validation.get("ok") and reconstruction_validation.get("ok") and provider_result_ingress.get("ok") and artifact_pipeline.get("ok")
    run={"schema":SCHEMA,"version":VERSION,"pipeline_run_id":_unique("document-perception"),"ok":bool(ok),"status":"ADMIT_DEEP_DOCUMENT_PERCEPTION" if ok else "REJECT_DEEP_DOCUMENT_PERCEPTION","project_id":project_id,"source_name":source_name,"declared_modality":declared_modality,"source_commitment":source,"provider_observations":observations,"provider_validations":validations,"fusion_record":fusion,"fusion_validation":fusion_validation,"projection_bundle":bundle,"bundle_validation":bundle_validation,"perception_receipt":receipt,"receipt_validation":receipt_validation,"reconstruction_plan":reconstruction,"reconstruction_validation":reconstruction_validation,"provider_invocation_receipt":provider_invocation,"provider_result_ingress":provider_result_ingress,"universal_artifact_pipeline":artifact_pipeline,"critical_doctrine":{"pdf_parser_output_ne_pdf":True,"ocr_text_ne_page_image":True,"page_image_ne_document":True,"table_extraction_ne_table_source":True,"document_graph_ne_document_identity":True,"provider_agreement_ne_automatic_truth":True,"provider_disagreement_ne_failure":True},"private_document_truth_pipeline_allowed":False,"created_at_unix_ms":_now_ms(),"authority":AUTHORITY}
    run["pipeline_run_root_hash72"]=hash72(SCHEMA, run); return run

def validate_deep_document_perception_run(run:Mapping[str,Any])->Dict[str,Any]:
    reasons=[]
    if run.get("private_document_truth_pipeline_allowed"): reasons.append("REJECT_PROVIDER_PRIVATE_TRUTH_PIPELINE")
    if not run.get("source_commitment") or not run.get("perception_receipt") or not run.get("reconstruction_plan"): reasons.append("REJECT_DOCUMENT_PROJECTION_WITHOUT_RECONSTRUCTION")
    if run.get("projection_bundle",{}).get("source_remains_distinct_from_projections") is False: reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    if run.get("fusion_record",{}).get("provider_disagreement_collapsed_silently"): reasons.append("REJECT_PROVIDER_DISAGREEMENT_COLLAPSED_SILENTLY")
    ok=not reasons and bool(run.get("ok")); out={"schema":"HHS_DEEP_DOCUMENT_PERCEPTION_VALIDATION_V1","version":VERSION,"ok":ok,"status":"ADMIT_DEEP_DOCUMENT_PERCEPTION_RUN" if ok else "REJECT_DEEP_DOCUMENT_PERCEPTION_RUN","reasons":sorted(set(reasons)),"pipeline_run_root_hash72":run.get("pipeline_run_root_hash72"),"authority":AUTHORITY}; out["validation_root_hash72"]=hash72(out["schema"], out); return out

def deep_document_perception_status()->Dict[str,Any]:
    return {"schema":"HHS_DEEP_DOCUMENT_PERCEPTION_STATUS_V1","version":VERSION,"ok":True,"providers":["provider:pdf-native-text","provider:pdf-page-geometry","provider:document-image-region","provider:deterministic-ocr"],"projection_types":["PDF_NATIVE_TEXT_PROJECTION","PAGE_LAYOUT_PROJECTION","PAGE_IMAGE_REGION_PROJECTION","OCR_TEXT_PROJECTION","DOCUMENT_GRAPH_PROJECTION"],"fusion_states":["OBSERVATION_AGREEMENT","OBSERVATION_DISAGREEMENT","UNRESOLVED_AMBIGUITY","MISSING_REGION_OBSERVATION","SELECTED_PROJECTION_WITH_EVIDENCE"],"doctrine":"document provider outputs are typed projections, not canonical document identity"}

def deep_document_perception_pipeline_self_test()->Dict[str,Any]:
    run=run_deep_document_perception(project_id="project:pass052", source_name="spec.pdf", payload="%PDF BT (native HHS text) ET", declared_modality="PDF", page_count_hint=1, ocr_text_hint="native HHS text")
    image=run_deep_document_perception(project_id="project:pass052", source_name="scan.png", payload="scan image HHS", declared_modality="IMAGE", page_count_hint=1, ocr_text_hint="scan image HHS")
    bad=dict(run, private_document_truth_pipeline_allowed=True)
    return {"schema":"HHS_DEEP_DOCUMENT_PERCEPTION_PIPELINE_SELF_TEST_V1","version":VERSION,"ok":bool(validate_deep_document_perception_run(run)["ok"] and validate_deep_document_perception_run(image)["ok"] and not validate_deep_document_perception_run(bad)["ok"]),"pdf_run":run,"image_run":image,"bad_rejection":validate_deep_document_perception_run(bad),"status":deep_document_perception_status()}
if __name__=="__main__":
    import json; print(json.dumps(deep_document_perception_pipeline_self_test(), indent=2, sort_keys=True, default=str))
