from copy import deepcopy
from fractions import Fraction
import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass130_default_delta_constraint_envelope_v1 import *


def fixture():
    return canonical_pass130_envelope()


def test_self_test():
    assert pass130_self_test()["status"] == "PASS"


def test_quantum_layer_admitted_without_state_selection():
    e, env = fixture()
    r = e.admit_parameter_layer(env, layer_kind="VM81_QUANTUM_SIMULATOR", parameters={"dimensions":[2,2],"weights":[Fraction(1,4)]*4}, entropy_coordinates=[f"a{i}" for i in range(4)], branch_count=4, dimension_count=2)
    assert r["entropy_preserved"] and r["state_selected"] is False


def test_generic_high_entropy_layer_admitted():
    e, env = fixture()
    r = e.admit_parameter_layer(env, layer_kind="GENERIC_HIGH_ENTROPY_LAYER", parameters={"tokens":128,"noise_budget":64}, entropy_coordinates=["token_order","noise_membership","branch_topology"], branch_count=128, dimension_count=9)
    assert r["status"].startswith("ADMITTED")


def test_defaults_are_constraints_not_assignments():
    _, env = fixture()
    assert env["state_assignment"] is False and "amplitudes" in env["unconstrained_entropy_coordinates"]


def test_float_rejected():
    e, env = fixture()
    with pytest.raises(Pass130Error) as z:
        e.admit_parameter_layer(env, layer_kind="VM81_QUANTUM_SIMULATOR", parameters={"weight":0.5}, entropy_coordinates=["weight"], branch_count=2, dimension_count=1)
    assert z.value.code == "REJECT_FLOAT_PARAMETER_AS_CANONICAL_AUTHORITY"


def test_projection_authority_rejected():
    e, env = fixture()
    with pytest.raises(Pass130Error) as z:
        e.admit_parameter_layer(env, layer_kind="SYMBOLIC_QUANTUM_ALGEBRA", parameters={"external_projection_authority":True}, entropy_coordinates=["phase"], branch_count=2, dimension_count=1)
    assert z.value.code == "REJECT_PROJECTION_PROMOTED_TO_NATIVE_STATE"


def test_forced_branch_rejected():
    e, env = fixture()
    with pytest.raises(Pass130Error) as z:
        e.admit_parameter_layer(env, layer_kind="PROBABILISTIC_PARAMETER_LAYER", parameters={"selected_branch":3}, entropy_coordinates=["branch"], branch_count=9, dimension_count=2)
    assert z.value.code == "REJECT_DEFAULT_CONSTRAINTS_USED_AS_STATE_ASSIGNMENT"


def test_disabled_constraint_rejected():
    e, env = fixture(); bad=deepcopy(env); bad["constraints"]["UNIT_DELTA_CLOSURE"] = False
    body=dict(bad); body.pop("envelope_root_hash72"); bad["envelope_root_hash72"]=_hash("hhs_pass130_envelope_v1",body)
    with pytest.raises(Pass130Error) as z: e.validate_envelope(bad)
    assert z.value.code == "REJECT_REQUIRED_CONSTRAINT_DISABLED"


def test_envelope_tamper_rejected():
    e, env = fixture(); bad=deepcopy(env); bad["mode"]="STATE_ASSIGNMENT"
    with pytest.raises(Pass130Error) as z: e.validate_envelope(bad)
    assert z.value.code == "REJECT_DEFAULT_ENVELOPE_ROOT_MISMATCH"


def test_resource_bound_rejected():
    e, env = fixture()
    with pytest.raises(Pass130Error) as z:
        e.admit_parameter_layer(env, layer_kind="GENERIC_HIGH_ENTROPY_LAYER", parameters={}, entropy_coordinates=[], branch_count=e.bounds.max_branches+1, dimension_count=1)
    assert z.value.code == "REJECT_PARAMETER_RESOURCE_BOUND"


def test_replay_deterministic():
    e, env = fixture(); a=e.admit_parameter_layer(env, layer_kind="MULTIMODAL_TOKEN_LAYER", parameters={"modalities":["text","image","audio"]}, entropy_coordinates=["token","modality","order"], branch_count=27, dimension_count=3)
    assert e.replay(env,a)["status"] == "PASS_130_DETERMINISTIC_REPLAY_VALIDATED"


def test_admission_tamper_rejected():
    e, env = fixture(); a=e.admit_parameter_layer(env, layer_kind="GENERIC_HIGH_ENTROPY_LAYER", parameters={"x":1}, entropy_coordinates=["x"], branch_count=2, dimension_count=1); a["branch_count"]=3
    with pytest.raises(Pass130Error) as z: e.validate_admission(env,a)
    assert z.value.code == "REJECT_PARAMETER_ADMISSION_ROOT_MISMATCH"
