# HHS Pass 220 I078 — VM81 Candidate Boundary Expansion

## Scope

I078 begins from verified I077 main:

`c54a9d5d0b57e113f895091065c76b5f4e21e998`.

It expands the downstream candidate boundary without replacing the exact I077
execution surface. A candidate is admitted only when it is byte-identical to
the source-bound I077 VM81 frame for the selected node.

The two inherited source nodes remain:

```text
MatrixPower[M_wz,x^2]
MatrixPower[M_xy,x^4]
```

No host rectangular MatrixPower semantics are introduced.

## Native exact ABI

Public header:

```text
hhs_runtime/include/hhs_pass220_i078_vm81_candidate_boundary_expansion_1_0.h
```

Implementation:

```text
hhs_runtime/c/hhs_pass220_i078_vm81_candidate_boundary_expansion_1_0.inc
```

Exports:

```text
hhs_exact_pass220_i078_version
hhs_exact_pass220_i078_descriptor
hhs_exact_pass220_i078_reference_candidate
hhs_exact_pass220_i078_expand_candidate_boundary
```

The ABI is compiled into the existing `libhhs_runtime.so`.

## Candidate-frame admission

For node 0 or node 1, I078:

1. calls `hhs_exact_pass220_i077_execute`;
2. requires I077 VERIFIED status;
3. reconstructs the exact source-bound I077 candidate frame;
4. requires the incoming downstream frame to be byte-identical;
5. re-runs the inherited exact UQCEL admission/replay path;
6. requires the UQCEL receipt and transition identity to equal I077;
7. applies the exact 1001/1000 scaling witness across all 81 VM81 words;
8. proves every zero word remains the exact zero fixed point;
9. binds the boundary result into a new candidate-only Hash216 lineage;
10. rejects any mismatch without fallback.

A mutated candidate frame is therefore rejected before any fallback path can
be selected.

## Exact 1.001 invariant

The scaling invariant is represented exactly:

[
1.001=rac{1001}{1000}
]

with

[
1001=1000+1=7cdot11cdot13.
]

No floating-point value is authoritative.

For every VM81 word (w), I078 records the exact quotient/remainder witness for

[
rac{1001w}{1000}.
]

The implementation avoids overflow by decomposing

[
w=1000leftlfloorrac{w}{1000}ightfloor+r
]

and representing the scaled integer part with an explicit carry bit plus a
64-bit low word.

For (w=0),

[
rac{1001cdot0}{1000}=0,
]

so the zero state is a fixed point.

## Closure boundary

The admitted boundary requires:

[
Delta e=0,qquad Psi=0,qquad Omega=mathrm{true}.
]

These are stored as exact integer/rational state fields:

```text
Delta e = 0/1
Psi     = 0/1
Omega   = true
```

## Boundary Hash216 lineage

I078 extends, rather than replaces, the I077 execution ancestry:

```text
PREVIOUS = I077 receipt Hash72
CHANGE   = Hash72(candidate digest || 1001/1000 scale witness || node id)
RECEIPT  = Hash72(I077 transition identity || candidate digest ||
                  scale witness || closure/authority flags)
HASH216  = PREVIOUS || CHANGE || RECEIPT
```

A separate 216-character boundary identity is computed from that triplet.

This lineage is candidate-only. It has no canonical commit or persistence
authority.

## Python and native probes

Python binding:

```text
hhs_runtime/hhs_pass220_i078_vm81_candidate_boundary_expansion_v1.py
```

Native probe:

```text
tools/pass220/pass220_i078_vm81_candidate_boundary_probe.c
```

The Python layer calls the same deployed shared exact ABI and performs no
parallel arithmetic implementation.

## Wolfram

Source:

```text
formal/wolfram/pass220_i078_vm81_candidate_boundary_expansion_v1.wl
```

Connected-kernel result:

```text
status = PASS
checks = 30 / 30
root seed = 179971179971 / 1000000
scale = 1001 / 1000
VM81 words = 81
Hash216 width = 216
full attached components = 15552
```

## Lean 4

Module:

```text
HHS.Pass220.I078
```

Source:

```text
formal/lean/HHS/Pass220/VM81CandidateBoundaryExpansion.lean
```

The theorem surface proves:

- exact root-seed numerator/denominator;
- exact 1001/1000 invariant and shell/factor identities;
- zero scaling fixed point;
- inherited I077 node surface;
- exact 81/5184/15552 geometry;
- (Delta e=0,Psi=0,Omega=true);
- byte-exact/UQCEL/replay admission policy;
- no host MatrixPower, square-matrix, float, numeric-exponent, canonical
  mutation, canonical Hash72/Hash216 commit, persistence, or egress authority.

## Authority boundary

I078 is a downstream candidate-admission and evidence expansion layer. It does
not grant:

- host MatrixPower authority;
- square-matrix fallback authority;
- floating-point authority;
- numeric exponent authority;
- canonical VM81 mutation authority;
- canonical Hash72/Hash216 commit authority;
- canonical persistence authority;
- external-egress authority.

CPU exact VM81/UQCEL admission remains authoritative.
