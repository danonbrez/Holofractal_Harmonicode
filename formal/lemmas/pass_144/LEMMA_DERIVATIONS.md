# Lemma Derivations and Boundaries

## HHS-L144-002 — Polynomial residual

Assume normalized local unit `1`, `g != 0`, and

\[
\rho=g+g^{-1}-2.
\]

Then

\[
\rho g=g^2+1-2g=(g-1)^2.
\]

This derivation must not be lifted unchanged to a noncentral, nonidempotent typed unit.

## HHS-L144-004 — Instantiated quotient field

For nonzero rational `alpha`, the evaluation map

\[
\operatorname{ev}_\alpha:\mathbb Q[g,h,\rho]\to\mathbb Q
\]

sends

\[
g\mapsto\alpha,\quad h\mapsto\alpha^{-1},\quad \rho\mapsto\alpha+\alpha^{-1}-2.
\]

Its kernel is the state ideal. The induced quotient is isomorphic to `Q`. The generic reciprocal ideal is not asserted to be maximal.

## HHS-L144-007 — XOR recovery

With

\[
P=D_0\oplus D_1\oplus D_2\oplus D_3,
\]

one missing shard satisfies

\[
D_i=P\oplus\bigoplus_{j\ne i}D_j.
\]

The result is readmitted only after canonical identity checks.

## HHS-L144-009 — Entropy-neutral reconstruction

The lemma uses the HHS operational definition of entropy neutrality: exact canonical recoverability, including payload, semantic metadata, ancestry, and authority. It is not a claim about every external thermodynamic entropy measure.
