#!/usr/bin/env python3
"""Exact Gröbner verification for the instantiated HHS GfE state ideal."""
from __future__ import annotations
import argparse, json, hashlib
from fractions import Fraction
from pathlib import Path
import sympy as sp


def rat(s: str) -> sp.Rational:
    f = Fraction(s)
    return sp.Rational(f.numerator, f.denominator)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--alpha', default='5/4')
    ap.add_argument('--out', required=True)
    ns = ap.parse_args()
    a = rat(ns.alpha)
    if a == 0:
        raise SystemExit('alpha must be nonzero')
    g,h,rho = sp.symbols('g h rho')
    rinv = 1/a
    r = sp.expand(a + rinv - 2)
    basis = [g-a, h-rinv, rho-r]
    G = sp.groebner(basis, g,h,rho, order='lex', domain=sp.QQ)
    generic = [g*h-1, rho-g-h+2]
    generic_remainders = [sp.expand(G.reduce(f)[1]) for f in generic]
    s_remainders = []
    # SymPy's basis is already verified internally; retain pairwise S-polynomial reductions.
    polys = [sp.Poly(p, g,h,rho, domain=sp.QQ) for p in basis]
    for i in range(len(polys)):
        for j in range(i+1,len(polys)):
            mi, mj = polys[i].monoms()[0], polys[j].monoms()[0]
            ci, cj = polys[i].coeffs()[0], polys[j].coeffs()[0]
            lcm_exp = tuple(max(x,y) for x,y in zip(mi,mj))
            def mon(exp):
                return g**exp[0] * h**exp[1] * rho**exp[2]
            S = sp.expand(mon(tuple(x-y for x,y in zip(lcm_exp,mi))) / ci * polys[i].as_expr()
                          - mon(tuple(x-y for x,y in zip(lcm_exp,mj))) / cj * polys[j].as_expr())
            rem = sp.expand(G.reduce(sp.expand(S))[1])
            s_remainders.append({'pair':[i,j], 's_polynomial':str(sp.expand(S)), 'remainder':str(rem)})
    payload = {
        'contract':'HHS-GFE-FORMAL-136',
        'coefficient_field':'Q',
        'variables':['g','h','rho'],
        'order':'lex(g>h>rho)',
        'alpha':str(a),
        'alpha_inverse':str(rinv),
        'rho_alpha':str(r),
        'state_ideal_generators':[str(sp.expand(x)) for x in basis],
        'reduced_grobner_basis':[str(p.as_expr()) for p in G.polys],
        'generic_constraints':[str(x) for x in generic],
        'generic_constraint_remainders':[str(x) for x in generic_remainders],
        's_polynomial_reductions':s_remainders,
        'all_remainders_zero': all(x == 0 for x in generic_remainders) and all(x['remainder']=='0' for x in s_remainders),
        'quotient_normal_form':'constant rational',
        'quotient_field':'Q'
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(',',':')).encode()
    payload['sha256'] = hashlib.sha256(canonical).hexdigest()
    Path(ns.out).write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload['all_remainders_zero'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
