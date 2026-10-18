"""Exact candidate-only Module 15 Lo Shu chiral witness.
Gaussian rational arithmetic; neither Hash216 mint nor signed VM81 admission.
The canonical '/' rank-one gate is preserved as source metadata: this audit's
complex evaluations are explicitly a conventional q-1 projection.
"""
from fractions import Fraction as Q

SOURCE_GATE = "1/(45=={{-I*2/(x*y),-I*9/2/(x*y),-I/(x*y)},{I*3/(x*y),I*5/(x*y),I*7/(x*y)},{(8-I*8)/(x*y),(1-I)/(x*y),(6-I*6)/(x*y)}})=={{-I*(2*y^2),(-I*9/2)*y^2,-I*y^2},{I*(3*y^2),I*(5*y^2),I*(7*y^2)},{(8-I*8)*y^2,(1-I)*y^2,(6-I*6)*y^2}}"
TRANSFER_GATE = "1-(x/2)==c²-a/b"
LO_SHU = ((4,9,2),(3,5,7),(8,1,6))

def mul(a,b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
def add(a,b):
    return (a[0]+b[0],a[1]+b[1])
def neg(a):
    return (-a[0],-a[1])
def audit():
    weights=((Q(0),Q(-1,2)),(Q(0),Q(1)),(Q(1),Q(-1)))
    lhs=tuple(tuple((weights[r][0]*v,weights[r][1]*v) for v in row) for r,row in enumerate(LO_SHU))
    rhs=tuple(tuple(neg(value) for value in row) for row in lhs)
    total=(Q(0),Q(0))
    product=(Q(1),Q(0))
    for weight in weights:
        total=add(total,weight)
        product=mul(product,weight)
    residual=add(total,neg(product))
    if total!=(Q(1),Q(-1,2)):
        raise ValueError("COMPLEX_LOSHU_WEIGHT_SUM_DIVERGENCE")
    if product!=(Q(1,2),Q(-1,2)):
        raise ValueError("COMPLEX_LOSHU_WEIGHT_PRODUCT_DIVERGENCE")
    if residual!=(Q(1,2),Q(0)):
        raise ValueError("COMPLEX_LOSHU_RESIDUAL_DIVERGENCE")
    if sum(map(sum,LO_SHU))!=45:
        raise ValueError("COMPLEX_LOSHU_GLOBAL_SUM_DIVERGENCE")
    if not all(sum(row)==15 for row in LO_SHU):
        raise ValueError("COMPLEX_LOSHU_ROW_DIVERGENCE")
    if not all(sum(LO_SHU[r][c] for r in range(3))==15 for c in range(3)):
        raise ValueError("COMPLEX_LOSHU_COLUMN_DIVERGENCE")
    if sum(LO_SHU[i][i] for i in range(3))!=15 or sum(LO_SHU[i][2-i] for i in range(3))!=15:
        raise ValueError("COMPLEX_LOSHU_DIAGONAL_DIVERGENCE")
    if not all(rhs[r][c]==neg(lhs[r][c]) for r in range(3) for c in range(3)):
        raise ValueError("COMPLEX_LOSHU_RECIPROCAL_DIVERGENCE")
    return {
        "schema":"HHS_PASS220_MODULE15_COMPLEX_LOSHU_EXACT_CANDIDATE_V1",
        "source_gate":SOURCE_GATE, "transfer_gate":TRANSFER_GATE,
        "row_weights":weights, "sum":total, "product":product, "exhaust_residual":residual,
        "lhs":lhs, "rhs":rhs, "xy_q_minus_1":(Q(1),Q(0)),
        "y_squared_q_minus_1":(Q(-1),Q(0)),
        "candidate_only":True, "canonical_hash216_minted":False,
        "signed_vm81_admitted":False, "exhaust_ledger_committed":False,
    }
