# Proof Lemma Corpus Guide

The corpus in `formal/lemmas/pass_144/` provides stable lemma identifiers, natural-language statements, formal signatures, assumptions, dependencies, proof status, and intended verification targets.

## Status values

- `EXECUTED_EXACT`: demonstrated by an exact runtime or certificate.
- `SOURCE_COMPLETE`: complete proof source exists but kernel execution is not recorded in this environment.
- `SKETCH`: formalization outline contains unresolved proof obligations.
- `CONTRACT_LEMMA`: normative requirement not yet represented as a completed kernel proof.

## Use

API documentation may cite a lemma identifier, but must preserve its status. A `CONTRACT_LEMMA` or `SKETCH` must not be described as kernel-verified.

## Corpus identity

`LEMMA_CORPUS.json` is the canonical machine-readable index. Individual Markdown files provide readable derivations and boundary conditions.
