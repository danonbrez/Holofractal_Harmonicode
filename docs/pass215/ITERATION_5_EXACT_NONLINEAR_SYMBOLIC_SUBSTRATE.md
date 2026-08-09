# Pass 215 Iteration 5 — Exact Nonlinear Symbolic Substrate

## Scope

Iteration 5 extends the frozen Iteration 4 exact Q4_0 linear benchmark into the nonlinear transformer domain without weakening `NO_FLOAT_CANONICAL_AUTHORITY` and without mutating the operational runtime.

The implementation introduces a deterministic canonical expression algebra over exact rationals and the closed-form nodes `sqrt`, `rsqrt`, rational power, `exp`, `sin`, and `cos`. Rational and algebraically reducible cases close immediately; irreducible transcendental values remain exact symbolic expressions rather than being converted to floating-point approximations.

## Implemented operators

- RMSNorm: exact rational mean-square plus exact reciprocal-square-root normalization.
- RoPE: exact rational-power frequency construction and closed-form sine/cosine pair rotation.
- Attention scaling: exact multiplication by `1/sqrt(head_dimension)`.
- Softmax: exact first-score shift followed by canonical exponential ratios.
- Sigmoid: `1/(1+exp(-x))`.
- SiLU: `x/(1+exp(-x))`.

The authenticated `stories15M-q4_0.gguf` model remains the source workload. `blk.0.attn_q.weight` is executed with the inherited Iteration 4 exact Q4_0 factored kernel, and that exact rational output seeds the nonlinear witness suite.

## Exactness boundary

Iteration 5 claims exact closed-form symbolic execution, not finite-precision numerical transcendental evaluation. No approximation table, host `float`, NumPy floating type, or decimal transcendental approximation is canonical evidence. This distinction is deliberate: an expression such as `exp(3/7)` is retained exactly as `exp(3/7)` instead of being replaced by an inexact binary approximation.

Accordingly, Iteration 5 still does **not** claim a complete transformer-layer forward, dense-forward replacement, operational Pass 213 compiled-ROM mutation, runtime mutation authority, canonical mutation, migration, or 50B desktop feasibility.

## Frozen inheritance

The implementation binds the Iteration 4 validated head/tree, suite root, terminal evidence root, artifact SHA-256, and Hash72 receipt, together with the Iteration 2/3 evidence roots and Pass 214/215 authority roots. These values are validation inputs and are not regenerated or rewritten.

## Generator/transition accounting

For each nonlinear witness, Iteration 5 records the number of unique canonical expression DAG nodes and an operator histogram. This is a structural generator-complexity measure; it is not presented as equivalent to hardware FLOPs for numerical transcendental evaluation.

## Exact controls

The dependency-scoped suite proves several reducible cases exactly: RMSNorm `(3,3)` with zero epsilon becomes `(1,1)`; RoPE at position zero is identity; attention scaling by head dimension 16 maps `(4,-8)` to `(1,-2)`; equal-score softmax becomes exact uniform rationals; rational softmax is translation invariant under the exact anchor shift; sigmoid zero is `1/2`; and SiLU zero is `0`.

Independent process A/B execution on the authenticated GGUF must produce identical nonlinear suite roots, evidence roots, and Hash72 receipts before Iteration 5 is accepted at an exact repository head.
