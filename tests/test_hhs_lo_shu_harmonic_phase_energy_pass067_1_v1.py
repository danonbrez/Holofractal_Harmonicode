from fractions import Fraction
from hhs_backend.runtime.hhs_lo_shu_harmonic_phase_energy_v1 import *

def test_self_test(): assert harmonic_phase_energy_self_test()["ok"]
def test_base_geometry():
 r=run_harmonic_phase_energy(); assert r["base_energy"]==[40,5,30,15,25,35,20,45,10]; assert r["base_conservation"]["ok"]
def test_four_tensors_preserve_75_225_and_center():
 r=run_harmonic_phase_energy(); assert all(t["projection"]["conservation"]["ok"] and t["projection"]["center_fixed"] for t in r["weighted_tensors"].values())
def test_deformation_space_exact():
 d=delta(Fraction(2),Fraction(-1)); assert validate_magic([Fraction(x)+y for x,y in zip(BASE,d)])["ok"]
def test_phase_states_and_interstitial_constraints():
 r=run_harmonic_phase_energy(); assert r["phase_states"]==["x","y","z","w","xy","yx","zw","wz"]; assert r["interstitial_constraint_states"]==["PLASTIC_EQUILIBRIUM","ZERO_SUM_CLOSURE"]
def test_ordered_products_remain_distinct(): assert run_harmonic_phase_energy()["ordered_products_distinct"]
def test_plastic_equilibrium_and_zero_sum_gate():
 r=run_harmonic_phase_energy(); assert all(g["plastic_equilibrium"]["equilibrium_satisfied"] and g["zero_sum_closure"]["closure_satisfied"] for g in r["ordered_phase_gates"].values())
def test_energy_never_confers_authority(): assert not run_harmonic_phase_energy()["energy_confers_authority"]
