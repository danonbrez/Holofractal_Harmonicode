# HHS Pass 136 — GfE Ideal, Gröbner, and Field-Quotient Proof Contract

## Scope

This contract formalizes the exact rational GfE reciprocal lane with variables
`g`, `h = g⁻¹`, and `rho = g + h - 2`.

Two ideals must remain distinct:

1. **Generic reciprocal ideal**
   \[
   I=\langle gh-1,\;\rho-g-h+2\rangle\subset\mathbb Q[g,h,\rho].
   \]
   Its quotient is isomorphic to \(\mathbb Q[g,g^{-1}]\), so it is an integral
   domain but **not a field**.

2. **Instantiated admitted-state ideal**, for \(\alpha\in\mathbb Q^\times\),
   \[
   J_\alpha=\langle g-\alpha,\;h-\alpha^{-1},\;
   \rho-(\alpha+\alpha^{-1}-2)\rangle.
   \]
   This ideal is maximal. Every polynomial reduces to a rational constant, and
   \[
   \mathbb Q[g,h,\rho]/J_\alpha\cong\mathbb Q.
   \]

## Gröbner contract

For lexicographic order \(g>h>\rho\), the three monic linear generators of
\(J_\alpha\) form a reduced Gröbner basis. Their leading monomials are pairwise
coprime. The package records all three S-polynomial reductions and verifies
that the generic GfE equations reduce to zero.

For \(\alpha=5/4\):

\[
J_{5/4}=\langle g-5/4,\;h-4/5,\;\rho-1/20\rangle.
\]

## Proof artifacts

- `formal/coq/HHS_GFE_Field_Quotient.v` — proof-complete Coq source with no
  `Admitted` or axioms. It defines the polynomial AST, explicit generated ideal,
  membership certificates, Buchberger certificates, canonical quotient normal
  forms, and `quotient_isomorphic_to_field`.
- `formal/lean/HHS_GFE_Field_Quotient.lean` — Lean 4/mathlib-style mirror. It
  intentionally contains one `sorry` at the general kernel-equality step and is
  classified as a verification sketch, not a completed Lean proof.
- `tools/verify_gfe_grobner.py` — exact SymPy/QQ Gröbner checker.
- `formal/certificates/gfe_state_5_4_grobner.json` — deterministic certificate.

## Authority statement

The Coq source was generated in an environment without `coqc`; therefore this
checkpoint proves source completeness and independent exact Gröbner execution,
but does not claim a local Coq compiler receipt. A future environment with Coq
must compile the file before promoting `COQ_SOURCE_COMPLETE` to
`COQ_KERNEL_VERIFIED`.
