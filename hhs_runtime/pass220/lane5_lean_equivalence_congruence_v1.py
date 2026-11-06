"""Lane 5 exact rational equivalence/congruence witnesses over existing Lean I053-I054 proofs.

No representative rewriting or quotient collapse. Inputs and original pair identity
stay intact; cross-product equivalence is proven for supplied witnesses only.
"""
from fractions import Fraction

THEOREMS = {
    "eqv_refl": ("HHS.Mathlib.Rat.Equivalence", 1),
    "eqv_symm": ("HHS.Mathlib.Rat.Equivalence", 2),
    "eqv_trans": ("HHS.Mathlib.Rat.Equivalence", 3),
    "eqv_neg_congr": ("HHS.Mathlib.Rat.Equivalence", 2),
    "eqv_add_congr": ("HHS.Mathlib.Rat.Congruence", 4),
    "eqv_mul_congr": ("HHS.Mathlib.Rat.Congruence", 4),
}
SCHEMA="HHS_PASS220_LANE5_LEAN_EXACTRAT_EQUIVALENCE_CONGRUENCE_V1"

class ExactRatEquivalenceError(ValueError):
    pass

def _pair(obj):
    if type(obj) is not dict or set(obj) != {"numerator","denominator"}:
        raise ExactRatEquivalenceError("EXACTRAT_PAIR_REQUIRED")
    n,d=obj["numerator"],obj["denominator"]
    if type(n) is not int or type(d) is not int or d<=0:
        raise ExactRatEquivalenceError("EXACTRAT_POSITIVE_DENOMINATOR_REQUIRED")
    return (n,d)

def _eqv(a,b):
    return a[0]*b[1]==b[0]*a[1]

def instantiate_equivalence(theorem,operands):
    if theorem not in THEOREMS:
        raise ExactRatEquivalenceError("UNREGISTERED_LEAN_THEOREM")
    module,count=THEOREMS[theorem]
    if type(operands) is not list or len(operands)!=count:
        raise ExactRatEquivalenceError("EXACTRAT_ARITY_MISMATCH")
    pairs=[_pair(obj) for obj in operands]
    if theorem=="eqv_refl":
        ok=_eqv(pairs[0],pairs[0])
    elif theorem=="eqv_symm":
        ok=_eqv(pairs[0],pairs[1]) and _eqv(pairs[1],pairs[0])
    elif theorem=="eqv_trans":
        ok=_eqv(pairs[0],pairs[1]) and _eqv(pairs[1],pairs[2]) and _eqv(pairs[0],pairs[2])
    elif theorem=="eqv_neg_congr":
        a,b=pairs
        ok=_eqv(a,b) and _eqv((-a[0],a[1]),(-b[0],b[1]))
    else:
        a,ap,b,bp=pairs
        premises=_eqv(a,ap) and _eqv(b,bp)
        if theorem=="eqv_add_congr":
            left=(a[0]*b[1]+b[0]*a[1],a[1]*b[1])
            right=(ap[0]*bp[1]+bp[0]*ap[1],ap[1]*bp[1])
        else:
            left=(a[0]*b[0],a[1]*b[1])
            right=(ap[0]*bp[0],ap[1]*bp[1])
        ok=premises and _eqv(left,right)
    if not ok:
        raise ExactRatEquivalenceError("LEAN_THEOREM_PREMISE_OR_CONCLUSION_REJECTED")
    return {
        "schema":SCHEMA,"lean_module":module,"theorem":theorem,
        "application_module":"HHS.Pass220.Lane5EquivalenceApplications",
        "application_declaration":theorem+"_application",
        "original_operands":[dict(x) for x in operands],
        "proof_premises_and_conclusion_exact":True,
        "source_pair_identity_preserved":True,
        "canonical_representative_rewrite":False,
        "generic_hnan_commutation_authorized":False,
        "candidate_only":True,"canonical_vm81_admission":False,
        "runtime_lean_kernel_invoked":False,
    }
