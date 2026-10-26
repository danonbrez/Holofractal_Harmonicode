"""Pass 220 exact reference Dirac/HNAN boundary evaluation.

Candidate-only: this module cannot mint native state or authorize particle dynamics.
Complex values are represented by pairs of Fraction (real, imaginary).
"""
from __future__ import annotations
from fractions import Fraction as F
from typing import Any

SCHEMA = "HHS_PASS220_DIRAC_EIGHT_HNAN_BOUNDARY_CANDIDATE_V1"
ROLES = (("000","xy"),("001","x+y"),("010","yx"),
         ("011","xy-zw"),("100","wz-yx"),("101","wz"),
         ("110","z+w"),("111","zw"))
ZERO=(F(0),F(0))
ONE=(F(1),F(0))
I=(F(0),F(1))

def c(value: Any) -> tuple[F,F]:
    if not isinstance(value,(tuple,list)) or len(value)!=2:
        raise ValueError("COMPLEX_PAIR_REQUIRED")
    if any(isinstance(v,(float,complex,bool)) for v in value):
        raise ValueError("EXACT_RATIONAL_REQUIRED")
    return F(value[0]),F(value[1])

def add(a,b): return a[0]+b[0],a[1]+b[1]
def sub(a,b): return a[0]-b[0],a[1]-b[1]
def mul(a,b): return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def conj(a): return a[0],-a[1]
def dot(a,b): return sum((mul(conj(x),y) for x,y in zip(a,b)),ZERO) if False else _dot(a,b)
def _dot(a,b):
    out=ZERO
    for x,y in zip(a,b):out=add(out,mul(conj(x),y))
    return out

def reference_projector(psi: tuple[tuple[F,F],...]):
    """P+ = (I4 + i beta alpha_z)/2, without floating point."""
    if len(psi)!=4:raise ValueError("SPINOR4_REQUIRED")
    # sigma_z = diag(1,-1); beta alpha_z has blocks [0,sigma_z;-sigma_z,0]
    kpsi=(mul(I,psi[2]),mul((-I[0],-I[1]),psi[3]),
          mul((-I[0],-I[1]),psi[0]),mul(I,psi[1]))
    return tuple((add(x,y)[0]/2,add(x,y)[1]/2) for x,y in zip(psi,kpsi))

def normal_flux(psi):
    # psi^dagger alpha_z psi, with alpha_z off-diagonal sigma_z
    v=(psi[2],(-psi[3][0],-psi[3][1]),psi[0],(-psi[1][0],-psi[1][1]))
    return _dot(psi,v)

def evaluate(sectors: list[dict], *, center_gate_witness: bool=False,
             conservation_witness: bool=False, native_mapping_witness: bool=False):
    if len(sectors)!=8:raise ValueError("EIGHT_SECTORS_REQUIRED")
    result=[]
    for (address,role),src in zip(ROLES,sectors):
        if src.get("address")!=address or src.get("role")!=role:
            raise ValueError("HNAN_ORDER_ADDRESS_MISMATCH")
        psi=tuple(c(z) for z in src["spinor"])
        if len(psi)!=4:raise ValueError("SPINOR4_REQUIRED")
        projected=reference_projector(psi)
        idempotent=reference_projector(projected)==projected
        in_boundary=projected==psi
        flux=normal_flux(projected)
        result.append({"address":address,"role":role,
                       "reference_projector_idempotent":idempotent,
                       "spinor_in_reference_boundary":in_boundary,
                       "projected_normal_flux_zero":flux==ZERO})
    reference_ok=all(v["reference_projector_idempotent"] and
                     v["spinor_in_reference_boundary"] and
                     v["projected_normal_flux_zero"] for v in result)
    # Boolean flags are explicit external witness assertions, not proof documents.
    # Even True cannot authorize native admission without a verified C++ cell-wall link.
    return {"schema":SCHEMA,"sectors":result,"reference_pass":reference_ok,
            "center_gate_witness_supplied":center_gate_witness,
            "conservation_witness_supplied":conservation_witness,
            "native_mapping_witness_supplied":native_mapping_witness,
            "native_admission":False,
            "particle_physics_mutated":False,
            "reason":"NATIVE_CPP_CELL_WALL_ADMISSION_NOT_CONNECTED"}
