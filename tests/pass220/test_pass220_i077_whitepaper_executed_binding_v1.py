from pathlib import Path
import pytest
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError
from hhs_runtime.hhs_pass220_i077_whitepaper_executed_binding_v1 import (
    execute_i077_whitepaper_binding, SOURCE, NODES,
)

def test_missing_exact_native_runtime_fails_closed():
    with pytest.raises(ProofCorpusError,match="I077_NATIVE_LIBRARY_REQUIRED"):
        execute_i077_whitepaper_binding("/missing/libhhs_runtime.so")

def test_actual_i077_vm81_receipts_bound_to_frozen_theorem():
    library=Path("hhs_runtime/builds/libhhs_runtime.so")
    assert library.is_file(), "CI must build the actual native exact ABI; skipping forbidden"
    result=execute_i077_whitepaper_binding(str(library))
    assert result["source"]==SOURCE
    assert tuple(x["source_node"] for x in result["native_executions"])==NODES
    assert len(result["native_executions"])==2
    assert len({x["transition_hash216"] for x in result["native_executions"]})==2
    assert result["binding"]["checker"]=="VM81_EXACT"
    assert result["binding"]["candidate_binding_only"]
    assert not result["binding"]["canonical_vm81_admission"]
    assert not result["binding"]["hash216_minted"]
    assert not result["full_corpus_proved"]
