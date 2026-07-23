from copy import deepcopy
from fractions import Fraction
import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass131_electrochemical_atomic_physics_sandbox_v1 import *


def fixture():
    e, env = canonical_pass131_sandbox()
    s = e.create_atomic_state(env, species_id="Li", atomic_number=3, mass_number=7, charge=0, electron_configuration={"1s":2,"2s":1}, symbolic_fields={"energy":"E_0"})
    return e, env, s


def test_self_test():
    assert pass131_self_test()["status"] == "PASS"


def test_exact_atomic_state():
    _, _, s = fixture()
    assert s["electron_count"] == 3 and s["canonical_authority"] == "EXACT_SYMBOLIC_RATIONAL_ONLY"


def test_ionization_and_replay():
    e, env, s = fixture()
    r = e.execute_transition(env, s, operation="IONIZE", parameters={"electron_count":1,"orbital":"2s"})
    assert r["charge_delta"] == 1 and r["electron_delta"] == -1
    assert e.replay(env, s, r)["status"].endswith("VALIDATED")


def test_reduction():
    e, env, _ = fixture()
    ion = e.create_atomic_state(env, species_id="Li+", atomic_number=3, mass_number=7, charge=1, electron_configuration={"1s":2})
    r = e.execute_transition(env, ion, operation="REDUCE", parameters={"electron_count":1,"orbital":"2s"})
    assert r["after_state"]["charge"] == 0


def test_symbolic_hamiltonian_exact():
    e, env, s = fixture()
    r = e.execute_transition(env, s, operation="APPLY_SYMBOLIC_HAMILTONIAN", parameters={"operator":"H","state":"psi","result":"H psi"})
    assert r["exact"] is True


def test_tensor_promotion_describes_finite_path():
    e, env, _ = fixture()
    p = e.promote_tensor(env, variable_name="V", scalar_value=Fraction(1,3), dimensions=["x","y","z","phase"], constraints=[{"eq":"div J + dq/dt = 0"}], finite_solution_witness={"provably_finite":True,"steps":9})
    assert p["tensor_rank"] == 4 and p["information_discarded"] is False
    e.validate_promotion(env,p)


def test_balanced_reaction():
    e, env, _ = fixture()
    r=e.balance_reaction(env, reactants=[{"coefficient":1,"elements":{"Zn":1},"charge":0},{"coefficient":2,"elements":{"H":1},"charge":1}], products=[{"coefficient":1,"elements":{"Zn":1},"charge":2},{"coefficient":1,"elements":{"H":2},"charge":0}])
    assert r["status"] == "EXACT_REACTION_BALANCED"


def test_float_rejected():
    e, env, s = fixture()
    with pytest.raises(Pass131Error) as z:
        e.execute_transition(env,s,operation="APPLY_SYMBOLIC_HAMILTONIAN",parameters={"energy":0.5})
    assert z.value.code == "REJECT_FLOAT_CANONICAL_PHYSICS_AUTHORITY"


def test_invalid_electron_configuration_rejected():
    e, env = canonical_pass131_sandbox()
    with pytest.raises(Pass131Error) as z:
        e.create_atomic_state(env,species_id="Li",atomic_number=3,mass_number=7,charge=0,electron_configuration={"1s":2})
    assert z.value.code == "REJECT_INVALID_ORBITAL_OCCUPANCY"


def test_unbalanced_elements_rejected():
    e, env, _ = fixture()
    with pytest.raises(Pass131Error) as z:
        e.balance_reaction(env,reactants=[{"elements":{"H":2},"charge":0}],products=[{"elements":{"H":1},"charge":0}])
    assert z.value.code == "REJECT_ELEMENT_CONSERVATION_FAILURE"


def test_unbalanced_charge_rejected():
    e, env, _ = fixture()
    with pytest.raises(Pass131Error) as z:
        e.balance_reaction(env,reactants=[{"elements":{"H":1},"charge":1}],products=[{"elements":{"H":1},"charge":0}])
    assert z.value.code == "REJECT_CHARGE_CONSERVATION_FAILURE"


def test_finite_solution_requires_constraints():
    e, env, _ = fixture()
    with pytest.raises(Pass131Error) as z:
        e.promote_tensor(env,variable_name="x",scalar_value="x",dimensions=["phase"],constraints=[],finite_solution_witness={"provably_finite":True})
    assert z.value.code == "REJECT_PROVEN_FINITE_PATH_NOT_DESCRIBED"


def test_state_tamper_rejected():
    e, env, s = fixture(); s["charge"]=2
    with pytest.raises(Pass131Error) as z: e.validate_state(env,s)
    assert z.value.code == "REJECT_STATE_ROOT_MISMATCH"


def test_transition_tamper_rejected():
    e, env, s=fixture(); r=e.execute_transition(env,s,operation="IONIZE",parameters={"electron_count":1,"orbital":"2s"}); r["charge_delta"]=9
    with pytest.raises(Pass131Error) as z: e.validate_transition(env,r)
    assert z.value.code == "REJECT_TRANSITION_ROOT_MISMATCH"


def test_approximate_hamiltonian_rejected():
    e, env, s=fixture()
    with pytest.raises(Pass131Error) as z: e.execute_transition(env,s,operation="APPLY_SYMBOLIC_HAMILTONIAN",parameters={"approximate":True,"operator":"H"})
    assert z.value.code == "REJECT_APPROXIMATION_PROMOTED_TO_AUTHORITY"


def test_global_mutation_rejected():
    e, env, s=fixture(); bad=deepcopy(s); bad.pop("state_root_hash72"); bad["global_state_mutation"]=True; bad["state_root_hash72"]=_hash("hhs_pass131_atomic_state_v1",bad)
    with pytest.raises(Pass131Error) as z: e.validate_state(env,bad)
    assert z.value.code == "REJECT_UNAUTHORIZED_GLOBAL_MUTATION"


def test_tensor_resource_bound():
    e, env, _=fixture()
    with pytest.raises(Pass131Error) as z: e.promote_tensor(env,variable_name="x",scalar_value=1,dimensions=[str(i) for i in range(e.bounds.max_tensor_rank+1)],constraints=[{"eq":"x=x"}])
    assert z.value.code == "REJECT_RESOURCE_BOUND"
