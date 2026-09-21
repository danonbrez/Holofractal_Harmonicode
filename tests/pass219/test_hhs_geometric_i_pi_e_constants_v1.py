from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CONSTANTS=ROOT/"contracts/pass219/PASS_219_GEOMETRIC_I_PI_E_CONSTANTS_V1.json"
SOURCE=ROOT/"evidence/pass219/hhs_geometric_i_pi_e_closure_v1.wl"
OUTPUT=ROOT/"evidence/pass219/hhs_geometric_i_pi_e_closure_v1.output.json"
RECEIPT=ROOT/"evidence/pass219/hhs_geometric_i_pi_e_closure_v1.receipt.json"

def test_locked_constants_and_coupled_chain_contract():
    c=json.loads(CONSTANTS.read_text())
    assert c["status"]=="LOCKED_SYSTEM_INTERNAL_GEOMETRIC_CONSTANTS"
    assert c["semantics"]=="typed_geometric_non_scalar_coupled_chain"
    assert c["constants"]["I_H"]["matrix"]==[[0,-1],[1,0]]
    assert c["constants"]["O"]["wolfram_projection"]=="Pi"
    assert c["constants"]["K"]["wolfram_projection"]=="E"
    assert c["constants"]["N_xy"]["value"]==c["constants"]["N_yx"]["value"]==4
    assert c["constants"]["N_xy"]["derivation"]!=c["constants"]["N_yx"]["derivation"]
    assert c["coupled_chain"]["term_count"]==4
    assert c["coupled_chain"]["edge_count"]==3
    assert c["coupled_chain"]["resolved_value"]==[[-1,0],[0,-1]]
    assert c["coupled_chain"]["nested_assert_required"] is True
    assert c["membrane"]["wolfram_builtin_mod_authority"] is False
    assert c["membrane"]["scalar_flattening_canonical_authority"] is False

def test_wolfram_certificate_is_digest_bound_and_full_chain_green():
    r=json.loads(RECEIPT.read_text())
    assert SOURCE.stat().st_size==r["input_bytes"]
    assert OUTPUT.stat().st_size==r["output_bytes"]
    assert sha256(SOURCE.read_bytes()).hexdigest()==r["input_sha256"]
    assert sha256(OUTPUT.read_bytes()).hexdigest()==r["output_sha256"]

    o=json.loads(OUTPUT.read_text())
    assert r["schema"]=="HHS_PASS219_GEOMETRIC_I_PI_E_WOLFRAM_RECEIPT_V2"
    assert o["schema"]=="HHS_PASS219_GEOMETRIC_I_PI_E_WOLFRAM_AUDIT_V2"
    assert o["allPassed"] is True
    assert o["checkCount"]==o["passedCount"]==23
    assert all(o["tests"].values())
    assert o["tests"]["same_candidate_state_binding"] is True
    assert o["tests"]["all_chain_terms_resolved"] is True
    assert o["tests"]["nested_assertion_witness_resolved"] is True
    assert o["tests"]["complete_coupled_chain_passes"] is True
    assert o["details"]["chain_edge_count"]==3
    assert o["details"]["chain_values"]==[
        [[-1,0],[0,-1]],
        [[-1,0],[0,-1]],
        [[-1,0],[0,-1]],
        [[-1,0],[0,-1]],
    ]
