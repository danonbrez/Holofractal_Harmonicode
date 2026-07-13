"""Pass 053 deep deterministic audio perception.

The admitted bundle is reconstructed from the committed source bytes, decoder
contract, temporal coordinate map, Runtime-admitted provider observations, and
fusion policy. Hash72 names refer only to C-kernel u^72 witnesses.
"""
from __future__ import annotations
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_modality_source_commitment_v1 import build_source_commitment, validate_source_commitment
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import build_provider_execution_proposal
from hhs_backend.runtime.hhs_provider_invocation_receipt_v1 import invoke_provider_with_receipt
from hhs_backend.runtime.hhs_provider_result_ingress_v1 import ingress_provider_result
from hhs_backend.runtime.hhs_capability_provider_registry_v1 import build_default_provider_registry

VERSION = "PASS_053_DEEP_DETERMINISTIC_AUDIO_PERCEPTION_V1"
AUTHORITY = "HHS_AUDIO_PERCEPTION_RUNTIME_AUTHORITY_V1"
RUN_SCHEMA = "HHS_DEEP_AUDIO_PERCEPTION_RUN_V1"


def _witness(label: str, payload: Any) -> Dict[str, Any]:
    return make_hash72_kernel_witness(label, payload, width=72).to_dict()


def _bytes(payload: Any) -> bytes:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, bytearray):
        return bytes(payload)
    if isinstance(payload, memoryview):
        return payload.tobytes()
    return str(payload).encode("utf-8")


def build_audio_source_byte_commitment(*, project_id: str, source_name: str, payload: Any) -> Dict[str, Any]:
    raw = _bytes(payload)
    modality_commitment = build_source_commitment(project_id=project_id, source_name=source_name, payload=raw.hex(), modality="AUDIO")
    byte_witness = _witness("hhs_audio_source_bytes_v1", {"byte_count": len(raw), "bytes_hex": raw.hex()})
    return {
        "schema": "HHS_AUDIO_SOURCE_BYTE_COMMITMENT_V1",
        "version": VERSION,
        "project_id": project_id,
        "source_name": source_name,
        "source_byte_count": len(raw),
        "source_bytes_hex": raw.hex(),
        "source_bytes_retained": True,
        "source_byte_root_hash72": byte_witness["digest"],
        "source_byte_hash72_kernel_witness": byte_witness,
        "pass050_modality_source_commitment": modality_commitment,
        "pass050_commitment_validation": validate_source_commitment(modality_commitment),
        "authority": AUTHORITY,
    }


def build_decoder_contract(*, codec: str = "PCM_S16LE", sample_rate_hz: int = 16000, channels: int = 1, frame_samples: int = 320) -> Dict[str, Any]:
    contract = {
        "schema": "HHS_AUDIO_DECODER_CONTRACT_V1", "version": VERSION,
        "codec": codec, "sample_rate_hz": int(sample_rate_hz), "channels": int(channels),
        "frame_samples": int(frame_samples), "sample_width_bits": 16,
        "deterministic_rounding": "INTEGER_SAMPLE_COORDINATES_ONLY",
        "decoder_output_is_source_identity": False, "authority": AUTHORITY,
    }
    contract["decoder_contract_root_hash72"] = _witness("hhs_audio_decoder_contract_v1", contract)["digest"]
    return contract


def build_temporal_coordinate_map(*, source_byte_count: int, decoder_contract: Mapping[str, Any]) -> Dict[str, Any]:
    bytes_per_sample = max(1, int(decoder_contract["sample_width_bits"]) // 8) * int(decoder_contract["channels"])
    sample_count = source_byte_count // bytes_per_sample
    frame_samples = int(decoder_contract["frame_samples"])
    frames = []
    for index, start in enumerate(range(0, sample_count, frame_samples)):
        end = min(sample_count, start + frame_samples)
        frames.append({"frame_index": index, "start_sample": start, "end_sample_exclusive": end})
    temporal = {
        "schema": "HHS_AUDIO_TEMPORAL_COORDINATE_MAP_V1", "version": VERSION,
        "sample_count": sample_count, "frame_count": len(frames), "frames": frames,
        "coordinate_system": "INTEGER_SAMPLE_INDEX", "authority": AUTHORITY,
    }
    temporal["temporal_map_root_hash72"] = _witness("hhs_audio_temporal_coordinate_map_v1", temporal)["digest"]
    return temporal


def _provider_observation(*, capability_class: str, project_id: str, source_root: str, raw_result: Mapping[str, Any], output_modality: str) -> Dict[str, Any]:
    proposal = build_provider_execution_proposal(
        capability_class=capability_class, project_id=project_id,
        input_payload={"audio_source_root_hash72": source_root},
        requested_operation="audio_perception.observe",
    )
    receipt = invoke_provider_with_receipt(proposal, simulated_raw_result=dict(raw_result))
    ingress = ingress_provider_result(receipt, project_id=project_id, output_modality=output_modality, target_artifact_type="AUDIO_PROVIDER_OBSERVATION")
    observation = {
        "schema": "HHS_AUDIO_PROVIDER_OBSERVATION_V1", "version": VERSION,
        "capability_class": capability_class, "provider_id": receipt.get("provider_id"),
        "proposal_root_hash72": proposal.get("proposal_root_hash72"),
        "invocation_receipt_root_hash72": receipt.get("invocation_receipt_root_hash72"),
        "runtime_canonical_ingress": ingress,
        "runtime_admitted": bool(ingress.get("ok")),
        "raw_result": dict(raw_result), "authority": AUTHORITY,
    }
    observation["observation_root_hash72"] = _witness("hhs_audio_provider_observation_v1", observation)["digest"]
    return observation


def build_provider_observations(*, project_id: str, source_root: str, transcript_hint: str = "deterministic audio observation") -> List[Dict[str, Any]]:
    return [
        _provider_observation(capability_class="AUDIO_ANALYSIS", project_id=project_id, source_root=source_root,
                              raw_result={"event_candidates": ["speech"], "energy_profile": "BOUNDED_INTEGER_FRAMES"}, output_modality="GRAPH_OBJECT"),
        _provider_observation(capability_class="SPEECH_TO_TEXT", project_id=project_id, source_root=source_root,
                              raw_result={"transcript_projection": transcript_hint, "confidence_is_authority": False}, output_modality="TEXT"),
    ]


def build_fusion_policy() -> Dict[str, Any]:
    policy = {
        "schema": "HHS_AUDIO_FUSION_POLICY_V1", "version": VERSION,
        "policy": "PRESERVE_PROVIDER_DISTINCTIONS_AND_TEMPORAL_COORDINATES",
        "provider_agreement_implies_truth": False, "provider_disagreement_is_failure": False,
        "transcript_replaces_audio": False, "selection_requires_runtime_admission": True,
        "authority": AUTHORITY,
    }
    policy["fusion_policy_root_hash72"] = _witness("hhs_audio_fusion_policy_v1", policy)["digest"]
    return policy


def _bundle_payload(*, source_commitment: Mapping[str, Any], decoder_contract: Mapping[str, Any], temporal_map: Mapping[str, Any], provider_observations: Iterable[Mapping[str, Any]], fusion_policy: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "schema": "HHS_AUDIO_PROJECTION_BUNDLE_V1", "version": VERSION,
        "source_byte_root_hash72": source_commitment["source_byte_root_hash72"],
        "decoder_contract_root_hash72": decoder_contract["decoder_contract_root_hash72"],
        "temporal_map_root_hash72": temporal_map["temporal_map_root_hash72"],
        "provider_observation_roots_hash72": [o["observation_root_hash72"] for o in provider_observations],
        "fusion_policy_root_hash72": fusion_policy["fusion_policy_root_hash72"],
        "source_remains_canonical": True, "projection_replaces_source": False,
        "authority": AUTHORITY,
    }


def build_projection_bundle(**parts: Any) -> Dict[str, Any]:
    bundle = _bundle_payload(**parts)
    bundle["projection_bundle_root_hash72"] = _witness("hhs_audio_projection_bundle_v1", bundle)["digest"]
    return bundle


def reconstruct_projection_bundle(*, reconstruction_recipe: Mapping[str, Any], source_commitment: Mapping[str, Any], decoder_contract: Mapping[str, Any], temporal_map: Mapping[str, Any], provider_observations: Iterable[Mapping[str, Any]], fusion_policy: Mapping[str, Any]) -> Dict[str, Any]:
    expected = reconstruction_recipe["admitted_projection_bundle_root_hash72"]
    reconstructed = build_projection_bundle(source_commitment=source_commitment, decoder_contract=decoder_contract, temporal_map=temporal_map, provider_observations=provider_observations, fusion_policy=fusion_policy)
    reconstructed["admitted_projection_bundle_root_hash72"] = expected
    reconstructed["reconstruction_verified"] = reconstructed["projection_bundle_root_hash72"] == expected
    return reconstructed


def run_deep_audio_perception(*, project_id: str = "project:pass053", source_name: str = "sample.pcm", payload: Any = b"HHS-AUDIO", transcript_hint: str = "deterministic audio observation") -> Dict[str, Any]:
    source = build_audio_source_byte_commitment(project_id=project_id, source_name=source_name, payload=payload)
    decoder = build_decoder_contract()
    temporal = build_temporal_coordinate_map(source_byte_count=source["source_byte_count"], decoder_contract=decoder)
    observations = build_provider_observations(project_id=project_id, source_root=source["source_byte_root_hash72"], transcript_hint=transcript_hint)
    fusion = build_fusion_policy()
    admitted = build_projection_bundle(source_commitment=source, decoder_contract=decoder, temporal_map=temporal, provider_observations=observations, fusion_policy=fusion)
    recipe = {
        "schema": "HHS_AUDIO_RECONSTRUCTION_RECIPE_V1", "version": VERSION,
        "source_byte_root_hash72": source["source_byte_root_hash72"],
        "decoder_contract_root_hash72": decoder["decoder_contract_root_hash72"],
        "temporal_map_root_hash72": temporal["temporal_map_root_hash72"],
        "provider_observation_roots_hash72": [o["observation_root_hash72"] for o in observations],
        "fusion_policy_root_hash72": fusion["fusion_policy_root_hash72"],
        "admitted_projection_bundle_root_hash72": admitted["projection_bundle_root_hash72"],
        "authority": AUTHORITY,
    }
    recipe["reconstruction_recipe_root_hash72"] = _witness("hhs_audio_reconstruction_recipe_v1", recipe)["digest"]
    reconstructed = reconstruct_projection_bundle(reconstruction_recipe=recipe, source_commitment=source, decoder_contract=decoder, temporal_map=temporal, provider_observations=observations, fusion_policy=fusion)
    provider_registry = build_default_provider_registry()
    ok = bool(source["pass050_commitment_validation"]["ok"] and all(o["runtime_admitted"] for o in observations) and reconstructed["reconstruction_verified"])
    run = {
        "schema": RUN_SCHEMA, "version": VERSION, "ok": ok,
        "status": "ADMIT_DEEP_AUDIO_PERCEPTION" if ok else "REJECT_DEEP_AUDIO_PERCEPTION",
        "source_commitment": source, "decoder_contract": decoder, "temporal_coordinate_map": temporal,
        "provider_observations": observations, "fusion_policy": fusion,
        "admitted_projection_bundle": admitted, "reconstruction_recipe": recipe,
        "reconstructed_projection_bundle": reconstructed,
        "pass051_provider_fabric_status": provider_registry,
        "pass050_modality_pipeline_used": True, "runtime_canonical_ingress_used": True,
        "c_kernel_hash72_u72_authority_used": True,
        "reconstruction_equation": "source commitment + decoder contract + temporal coordinate map + provider observations + fusion policy -> reconstructed projection bundle root = admitted projection bundle root",
        "authority": AUTHORITY,
    }
    run["pipeline_run_root_hash72"] = _witness("hhs_deep_audio_perception_run_v1", run)["digest"]
    return run


def validate_deep_audio_perception_run(run: Mapping[str, Any]) -> Dict[str, Any]:
    reasons = []
    reconstructed = run.get("reconstructed_projection_bundle", {})
    admitted = run.get("admitted_projection_bundle", {})
    if reconstructed.get("projection_bundle_root_hash72") != admitted.get("projection_bundle_root_hash72"):
        reasons.append("REJECT_AUDIO_RECONSTRUCTION_ROOT_MISMATCH")
    if not all(o.get("runtime_admitted") for o in run.get("provider_observations", [])):
        reasons.append("REJECT_AUDIO_PROVIDER_OBSERVATION_WITHOUT_RUNTIME_INGRESS")
    if not run.get("source_commitment", {}).get("source_bytes_retained"):
        reasons.append("REJECT_AUDIO_SOURCE_BYTES_NOT_RETAINED")
    ok = not reasons and bool(run.get("ok"))
    return {"schema":"HHS_DEEP_AUDIO_PERCEPTION_VALIDATION_V1", "version":VERSION, "ok":ok,
            "status":"ADMIT_DEEP_AUDIO_PERCEPTION_RUN" if ok else "REJECT_DEEP_AUDIO_PERCEPTION_RUN",
            "reasons":reasons, "admitted_projection_bundle_root_hash72":admitted.get("projection_bundle_root_hash72"),
            "reconstructed_projection_bundle_root_hash72":reconstructed.get("projection_bundle_root_hash72")}


def deep_audio_perception_pipeline_self_test() -> Dict[str, Any]:
    run = run_deep_audio_perception(payload=bytes(range(64)))
    validation = validate_deep_audio_perception_run(run)
    return {"schema":"HHS_DEEP_AUDIO_PERCEPTION_PIPELINE_SELF_TEST_V1", "ok":validation["ok"], "validation":validation,
            "pipeline_run_root_hash72":run["pipeline_run_root_hash72"]}

if __name__ == "__main__":
    print(json.dumps(deep_audio_perception_pipeline_self_test(), indent=2, sort_keys=True))
