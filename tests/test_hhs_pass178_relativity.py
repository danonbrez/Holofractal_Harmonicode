import pytest
from hhs_runtime.pass178.exact import ExactRational
from hhs_runtime.pass178.relativity import RelativisticParticle, relativistic_free_step, minkowski_norm2, momentum_mass_shell

def test_exact_proper_time_step_preserves_four_velocity_norm():
    p=RelativisticParticle("p",ExactRational(1),ExactRational(1),(ExactRational(0),)*4,(ExactRational(5,4),ExactRational(3,4),ExactRational(0),ExactRational(0)),ExactRational(1,16))
    n=relativistic_free_step(p)
    assert minkowski_norm2(n.four_velocity)==ExactRational(1)
    assert n.position4[0]==ExactRational(5,64)
    assert n.position4[1]==ExactRational(3,64)

def test_mass_shell_uses_algebraic_positive_energy():
    w=momentum_mass_shell("1",["3/4","0","0"])
    assert w["energy_squared"]==[25,16]
    assert w["energy"]["branch"]=="POSITIVE_REAL"

def test_spacelike_four_velocity_rejected():
    with pytest.raises(Exception):
        RelativisticParticle("x",ExactRational(1),ExactRational(0),(ExactRational(0),)*4,(ExactRational(1),ExactRational(1),ExactRational(0),ExactRational(0)),ExactRational(1))
