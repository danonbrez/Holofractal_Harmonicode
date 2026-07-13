from hhs_backend.runtime.multimodal_workspace_ingress_v1 import multimodal_workspace_ingress_self_test

def test_multimodal_workspace_ingress_self_test():
    result = multimodal_workspace_ingress_self_test()
    assert result["ok"]
    assert "PDF" in result["supported_initial_modalities"]
    assert "VIDEO" in result["supported_initial_modalities"]
    assert "AUDIO" in result["supported_initial_modalities"]
    assert result["unsupported_modality_rejection"]["status"] == "WORKSPACE_INGRESS_REJECTED"
