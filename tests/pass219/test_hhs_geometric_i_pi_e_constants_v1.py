import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
C=json.loads((ROOT/"contracts/pass219/PASS_219_GEOMETRIC_I_PI_E_CONSTANTS_V1.json").read_text())
O=json.loads((ROOT/"evidence/pass219/hhs_geometric_i_pi_e_closure_v1.output.json").read_text())

def test_locked_constants():
    assert C["status"]=="LOCKED_SYSTEM_INTERNAL_GEOMETRIC_CONSTANTS"
    assert C["semantics"]=="typed_geometric_non_scalar"
    c=C["constants"]
    assert c["I_H"]["matrix"]==[[0,-1],[1,0]]
    assert c["O"]["wolfram_projection"]=="Pi"
    assert c["K"]["wolfram_projection"]=="E"
    assert c["N_xy"]["value"]==c["N_yx"]["value"]==4
    assert c["N_xy"]["derivation"]!=c["N_yx"]["derivation"]
    assert c["MU_base"]["exact"]=="2*Sqrt[6]"
    assert c["MU_phase"]["exact"]=="6"
    assert C["membrane"]["operator"]=="HMod"
    assert C["membrane"]["wolfram_builtin_mod_authority"] is False
    assert C["membrane"]["scalar_flattening_canonical_authority"] is False

def test_wolfram_certificate():
    assert O["allPassed"] is True
    assert O["checkCount"]==O["passedCount"]==11
    assert all(O["tests"].values())
    assert O["details"]["phase_orders"]==[4,4]
    assert O["details"]["I_square"]==[[-1,0],[0,-1]]
