# Pass 219 Lane 5 1.51 — Directed Recursive Constraint Semantics

Status: IMPLEMENTED / EXECUTED SYMBOLIC WITNESS / SOURCE-COMPLETE FORMALIZATION IN PROGRESS
Parent: Pass 219 Lane 5 1.50
Canonical mutation authority: unchanged

## 1. Governing law

Every HARMONICODE equality edge is directional constraint enforcement.

For a native edge LHS = RHS, the semantic dependency is:

RHS enforced closure -> admissible LHS manifold -> local values -> local tensor asymmetry.

The RHS is not reconstructed from local LHS asymmetries. Local asymmetry is an admissible consequence of satisfying the closure law.

This rule forbids the inference:

local asymmetry -> cause of RHS closure.

## 2. Recursive and orthogonal application

The same dependency law applies at every nested expression node. A parent expression has its own RHS-to-LHS closure, while each child has a local RHS-to-LHS frame.

For a quotient N/D, N is the local LHS branch and D is the local RHS branch. Their internal tensor content remains present after the parent quotient is projected.

Nested constraints are therefore orthogonal local frames inside the parent constraint, not a flattened scalar evaluation chain.

## 3. Ordered multiplication

The native source AB=P^4 means:

- parent constraint: P^4 constrains AB;
- local ordered product: A is LHS and B is RHS;
- AB retains source order;
- BA is a distinct reverse/phase-inverted native object unless a separate explicit equality gate proves otherwise.

No implementation may sort operands or import ordinary commutative multiplication as native authority.

## 4. Ordered reciprocal rationals

A/B and B/A are reciprocal orientation objects. They are distinct native expressions.

Their scalar shadows may satisfy a registered reciprocal identity, but that does not authorize:

A/B = B/A,
AB = BA,
factor cancellation in the native graph,
or a reordering rewrite.

Every quotient recursively preserves numerator/denominator roles as local LHS/RHS.

## 5. Scalar projection is not substitution

Statements such as a^2=1, b^2=2 and c^2=3 are licensed one-dimensional projections of full tensor objects.

The executable representation is:

pi_1D(a^2)=1
pi_1D(b^2)=2
pi_1D(c^2)=3

The tensor source remains required. The scalar result has no native identity or substitution authority.

Therefore:

pi(E)=s does not imply E may be replaced by s,
and pi(E1)=pi(E2) does not imply E1 and E2 are native-identical.

## 6. Local asymmetry and closure

Local tensor asymmetries may be required by the enforced global constraint. Their presence must not be reinterpreted as a defect or as the generator of the global closure.

A valid formalizer records both:

rhs_enforced_closure=true
local_asymmetry_generates_rhs=false

at every equality node.

## 7. Executable lowering

The additive formalizer is:

hhs_runtime/harmonicode_directed_constraint_semantics_v1.py

It binds to the existing HARMONICODE interpreter receipt and emits:

- directed constraint edges;
- ordered product/quotient/power nodes;
- recursive nested local roles;
- scalar projection witnesses;
- unresolved-source accounting;
- a deterministic SHA-256 formalization receipt.

The core validator contains thirteen semantic checks and fails if any authority boundary is violated.

## 8. Wolfram witness

Evidence:

evidence/pass219/hhs_constraint_orientation_v1.wl
evidence/pass219/hhs_constraint_orientation_v1.output.json
evidence/pass219/hhs_constraint_orientation_v1.receipt.json

The connected Wolfram execution returns 7/7 PASS for:

- RHS-to-LHS closure;
- local asymmetry as consequence;
- recursive nested direction;
- AB distinct from BA;
- A/B distinct from B/A;
- a^2 tensor object distinct from its scalar projection value;
- no scalar substitution authority.

The held symbolic carriers are intentional. The proof tests structural identity/order without allowing Wolfram Times or Divide to flatten the custom algebra.

## 9. Lane 5 integration

The 1.51 CI gate replays the inherited 1.50 exact hydration workload:

72 P states x 5,184 VM81/operation64 positions = 373,248 native classifier cycles.

The directed semantic layer is therefore validated alongside the existing exact ordered phase-support runtime rather than as documentation alone.

## 10. Diagnostic projection boundary

Bridge-only and other isolated scalar diagnostics remain useful for testing whether a fragment alone carries enough information. They do not override the complete typed HARMONICODE manifold.

A diagnostic state that satisfies selected scalar fragments but does not traverse the full source is not a counterexample to the full theorem.

The predecessor phrase OPEN_FULL_MANIFOLD_OBLIGATION is superseded for this integration by:

SOURCE_COMPLETE_FORMALIZATION_IN_PROGRESS.

That status describes implementation coverage, not a falsification or downgrading of the governing theorem.

## 11. Promotion hierarchy

Each verbatim source object is classified only after proof:

AXIOM
CONSTANT
CONSTRAINT
DERIVED_LEMMA
PROJECTION
OPEN_FORMALIZATION_OBLIGATION

No unproved semantic shortcut acquires canonical authority.

## 12. Acceptance

Pass 1.51 requires:

1. thirteen executable semantic checks pass;
2. zero unresolved statements in the core fixture;
3. seven Wolfram structural checks pass;
4. source/output Wolfram hashes match the sealed receipt;
5. scalar projections retain tensor source identity;
6. AB and BA remain distinct;
7. A/B and B/A remain distinct;
8. equality chains are recorded right-to-left;
9. local asymmetry is never marked as causing parent/global RHS closure;
10. all 373,248 inherited hydration cycles pass;
11. required repository baselines pass;
12. canonical VM81/Hash72/Hash216 authority remains unchanged.
