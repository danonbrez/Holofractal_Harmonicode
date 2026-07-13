from hhs_backend.runtime.hhs_symbolic_document_service_v1 import symbolic_document_service_self_test

def test_symbolic_document_service_self_test():
    result = symbolic_document_service_self_test()
    assert result["ok"]
    assert result["admitted"]["mutation_receipt"]["post_state_hash72"]
    assert not result["ambiguous_rejection"]["ok"]
