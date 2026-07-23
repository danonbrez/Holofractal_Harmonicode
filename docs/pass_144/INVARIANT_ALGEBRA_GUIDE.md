# Invariant Algebra Guide

## Global state surface

Let `S` denote the canonical state and let `C_i(S)` denote mandatory constraint residuals. The admitted state space is

\[
\mathfrak B=\{S\mid C_i(S)==0\text{ for all mandatory }i\}.
\]

## Typed transition

A transition `T` is admissible when it preserves the required state surface or carries an explicit witnessed normalization path:

\[
S\in\mathfrak B\Longrightarrow T(S)\in\mathfrak B.
\]

## Reciprocal closure

For a typed unit `e`, reciprocal closure is

\[
gg^{-1}==e.
\]

Do not replace `e` with the scalar numeral `1` unless the active gate authorizes that normalization.

## Logarithm constraint

The native logarithmic relation is defined by inverse phase transport:

\[
\operatorname{Log}_H(g)==\sigma
\iff
E_H^\sigma==g.
\]

The reciprocal branch requires

\[
E_H^{\operatorname{Cancel}(\sigma)}==g^{-1}.
\]

## Periodic carrier

Hash72 phase positions are indexed by `Z/72Z`, with translation closure

\[
T_aT_b==T_{a+b\bmod72}.
\]

## Entropy neutrality

An internal transformation is globally entropy-neutral when the original canonical state is exactly recoverable from the transformed state and its receipt:

\[
R_T(T(S),\operatorname{Receipt}(T))==S.
\]
