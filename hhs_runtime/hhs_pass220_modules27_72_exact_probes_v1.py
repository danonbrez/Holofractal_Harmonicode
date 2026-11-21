"""Modules 27–72 exact arithmetic acceptance probes (non-authoritative).

This executable collects independently reproducible *subset* witnesses for the
user-supplied 27–72 specification. It does not transcribe the entire module
source, certify untested chains, or commit VM81/Hash72/Hash216 state. A subset
PASS never upgrades a full module or a composed gate to PASS.
Use the inherited runtime contracts for typed noncommutative operations.
"""
from __future__ import annotations

from fractions import Fraction as Q
from math import comb
from typing import Callable
import json

SCHEMA = "HHS_PASS220_MODULES_27_72_EXACT_PROBES_V1"
MODULES = tuple(range(27, 73))
EXPLICIT_OPEN = {
    43: "fine-structure normalization candidate; experimental residual",
    44: "four measured dimensionless constants retain residuals",
    45: "remaining mass-ratio and other correction residuals",
    54: "cross-register reciprocal gates fail on stated locus",
    55: "E8 root/bracket isomorphism not established",
    56: "cross-register, qubit and contraction interfaces remain open",
    58: "full chained locus and terminal gates remain open",
}
def matrix_product(a, b):
    if not a or not b or len({len(r) for r in a}) != 1 or len({len(r) for r in b}) != 1:
        raise ValueError("invalid rectangular matrices")
    if len(a[0]) != len(b):
        raise ValueError("matrix contraction axis mismatch")
    return [[sum(a[i][k]*b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]

def determinant3(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))

LOSHU = [[4,9,2],[3,5,7],[8,1,6]]
LOSHU2 = [[8,3,4],[1,5,9],[6,7,2]]

def check27():
    c = [[v-5 for v in row] for row in LOSHU]
    assert all(sum(row)==0 for row in c)
    assert all(sum(c[i][j] for i in range(3))==0 for j in range(3))
    assert determinant3(c)==0
    assert determinant3([[LOSHU[i][j]-(5 if i==j else 0)
                          for j in range(3)] for i in range(3)])==490

def check28_29():
    assert Q(4,1)/Q(1,4)==16
    x,y,z,w=Q(1),Q(-1),Q(2),Q(1,2)
    assert x**4/(z*w)==(y*z*w)**(-4)*y**6
    assert y*y == x**4*(z*w)**3

def check30_31():
    assert Q(179971179971,1000000)==179971*Q(1000001,1000000)
    assert 179971==11*16361
    assert 1001==7*11*13
    assert Q(111,10)+Q(10,111)==Q(12421,1110)

def check36_37():
    for p in range(2,30):
        q=p+2; P=p+1
        assert P*P-p*q==1
    for t in range(2,40):
        assert Q(t**3-t,6)==comb(t+1,3)
    for n in range(1,25):
        for k in (2,3,4):
            assert sum(comb(j+1,k) for j in range(1,n+1))==comb(n+2,k+1)

def check38_40():
    e=Q(36)-(Q(34,33)**120)
    assert 0<e<Q(1,20)
    eps=e/36
    assert 1-eps==Q(34,33)**120/36
    assert Q(432,-54)/8==-1

def check46():
    m1=[[Q(1),Q(1001,1000),Q(101,100)],
        [Q(1011,1000),Q(0),Q(11,10)],
        [Q(1101,1000),Q(111,100),Q(1)]]
    m2=[[v for v in row] for row in m1]
    m2[2][2]=Q(-1)
    def euclid(v,mod): return v-(v//mod)*mod
    s=[[euclid(m1[i][j],1)+euclid(m2[i][j],2)
        for j in range(3)] for i in range(3)]
    expected=[[Q(1),Q(501,500),Q(51,50)],
              [Q(511,500),Q(0),Q(6,5)],
              [Q(601,500),Q(61,50),Q(1)]]
    assert s==expected

def check49_50():
    for k in range(1,7):
        assert Q(k,8)*8==k
    cartan=[[2,-1,0],[-1,2,-1],[0,-1,2]]
    assert determinant3(cartan)==4
    assert 248==8*31==16*15+8

def check55_60_62():
    assert 240==3*72+24
    assert Q(4096,248)==Q(512,31)
    for P in (2,3,5,18,1001):
        p,q=P-1,P+1
        assert (p+q,q-p,p*q)==(2*P,2,P*P-1)
        assert P*P-p*q==1
        assert Q((q-p)*P,p+q)==1
        assert P*P==p*q+Q((q-p)*P,p+q)
        assert (P+3)**2-(P+2)*(P+4)==1

def check69_70():
    n=matrix_product(LOSHU,LOSHU2)
    assert n==[[53,71,101],[71,83,71],[101,71,53]]
    assert determinant3(n)==-360**2
    assert Q(31,248)==Q(1,8)
    x,y=Q(1),Q(-1)
    X=[[x*y,x*x,x],[x*x,x+y,y*y],[x,-x*y,x*y]]
    Y=[[2,1,-1],[1,-1,1],[-1,1,2]]
    d=matrix_product(X,Y)
    assert all(v!=0 for row in d for v in row)
    m=[[Q(n[i][j],8*d[i][j]) for j in range(3)] for i in range(3)]
    assert m==[[Q(-53,16),Q(-71,8),Q(101,32)],
               [Q(71,8),Q(83,16),Q(71,8)],
               [Q(101,32),Q(-71,8),Q(-53,16)]]
    assert sum(m[i][i] for i in range(3))==Q(-23,16)

CHECKS: dict[str, tuple[tuple[int,...],Callable[[],None]]] = {
    "centered_loshu": ((27,),check27),
    "genesis_tower_and_reciprocal": ((28,29),check28_29),
    "seed_and_chiral_ratios": ((30,31,33),check30_31),
    "tetrahedral_successor_sums": ((36,37),check36_37),
    "exact_epsilon": ((38,40),check38_40),
    "euclidean_payload_wrap": ((46,),check46),
    "dyadic_and_cartan": ((49,50),check49_50),
    "e8_unit_orbit_successor": ((55,60,62),check55_60_62),
    "ordered_loshu_reciprocal": ((69,70),check69_70),
}

def execute() -> dict:
    checks=[]; passing=set()
    for name,(modules,func) in CHECKS.items():
        try:
            func()
        except Exception as exc:
            checks.append({"name":name,"modules":list(modules),"status":"FAIL",
                           "error":type(exc).__name__+":"+str(exc)})
        else:
            passing.update(modules)
            checks.append({"name":name,"modules":list(modules),"status":"PASS"})
    statuses={str(i):"OPEN" if i in EXPLICIT_OPEN else "NOT_FULLY_VERIFIED"
              for i in MODULES}
    return {"schema":SCHEMA,"checks":checks,"module_status":statuses,
            "covered_by_subset_probes":sorted(passing),
            "explicit_open_gates":{str(k):v for k,v in EXPLICIT_OPEN.items()},
            "whole_course_proved":False,"canonical_vm81_admission":False,
            "hash72_minted":False,"hash216_minted":False}

if __name__=="__main__":
    result=execute()
    print(json.dumps(result,sort_keys=True,indent=2))
    if any(c["status"]!="PASS" for c in result["checks"]):
        raise SystemExit(1)
