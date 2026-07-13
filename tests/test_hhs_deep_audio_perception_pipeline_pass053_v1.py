from hhs_backend.runtime.hhs_deep_audio_perception_pipeline_v1 import run_deep_audio_perception, validate_deep_audio_perception_run

def test_audio_reconstruction_root_equals_admitted_root():
    run = run_deep_audio_perception(payload=bytes(range(128)), transcript_hint="one two three")
    assert validate_deep_audio_perception_run(run)["ok"]
    assert run["reconstructed_projection_bundle"]["projection_bundle_root_hash72"] == run["admitted_projection_bundle"]["projection_bundle_root_hash72"]

def test_audio_uses_real_fabric_pipeline_ingress_and_kernel_authority():
    run = run_deep_audio_perception(payload=b"\x00\x01\x02\x03")
    assert run["pass050_modality_pipeline_used"]
    assert run["runtime_canonical_ingress_used"]
    assert run["c_kernel_hash72_u72_authority_used"]
    assert all(o["runtime_canonical_ingress"]["ok"] for o in run["provider_observations"])
    assert run["source_commitment"]["source_bytes_hex"] == "00010203"
    assert len(run["source_commitment"]["source_byte_root_hash72"]) == 72
