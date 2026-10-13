"""Pass 220: read-only weighted equation -> inherited native Lane 5 lineage.

The weighted expression is an ordered AST witness, not a scalar equality
evaluation. The inherited I074/I148/HNAN candidate supplies lineage,
phase witness and Hash216; no second mint or mutation path is installed.
"""
from fractions import Fraction
from hashlib import sha256
import json

import pytest

from hhs_runtime.hhs_pass220_hnan_lane5_i074_candidate_binding_v1 import execute_candidate
from hhs_runtime.hhs_pass220_i074_full_tensor_hnan_closure_hydration_v1 import build_candidate
from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import hnan_loshu_resolution_receipt
from tests.pass220.test_pass220_weighted_hnan_residual_constraint_v1 import SOURCE, RESIDUAL_SOURCE
from tests.pass220.test_pass220_complex_p_rational_scaling_v1 import BASE, SCALES, add, mul, neg, ONE

def root(obj):
    return sha256(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

@pytest.fixture(scope="module")
def lineage():
    raw = (sha256(b"PASS220_WEIGHTED_HNAN_P").digest().hex() * 100)
    bits = "".join(f"{int(c,16):04b}" for c in raw)[:5184]
    return execute_candidate(bits), bits

def test_weighted_source_binds_to_existing_native_lineage(lineage):
    receipt, raw = lineage
    assert receipt["candidate_only"] is True
    assert receipt["hnan_gate_inherited"] is True
    assert receipt["raw_roundtrip_exact"] is True
    assert receipt["vm81_cells"] == 81
    assert receipt["i074_hash216_components"] == 15552
    assert receipt["i074_hash216"] == (receipt["i074_previous_hash72"]
                                        + receipt["i074_change_hash72"]
                                        + receipt["i074_receipt_hash72"])
    assert receipt["hnan_terminal_source"] == "xy+epsilon"
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_commit_authority"] is False
    assert receipt["canonical_hash216_persistence_authority"] is False
    assert len(root([SOURCE, RESIDUAL_SOURCE, receipt["candidate_receipt_sha256"]])) == 64

@pytest.mark.parametrize("base", BASE)
@pytest.mark.parametrize("scale", SCALES)
def test_complex_p_exact_scale_witness_does_not_claim_native_transition(base, scale):
    p_scaled = mul(base, (scale, Fraction(0)))
    assert mul(add(p_scaled, neg(ONE)), add(p_scaled, ONE)) == add(mul(p_scaled, p_scaled), neg(ONE))
    assert SOURCE[0] == "Eq"
    # A scalar closure certificate alone is NOT an HNAN tick/periodicity witness.
    assert RESIDUAL_SOURCE == "1+y^2-yx-w^2+wz"

def test_inherited_center_and_weighted_expression_are_separate(lineage):
    receipt, _ = lineage
    center = hnan_loshu_resolution_receipt()
    assert center["status"] == "PASS"
    assert center["terminal_source"] == receipt["hnan_terminal_source"]
    assert SOURCE[1][2][0] == "Eq"
