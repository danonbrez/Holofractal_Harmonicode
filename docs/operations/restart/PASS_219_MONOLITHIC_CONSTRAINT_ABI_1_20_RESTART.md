# Pass 219 — Monolithic Constraint Low-Level ABI 1.20 Restart Record

## Authority and lineage

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass219-exact-xyzw-octonion-abi-repair`
- PR: `#314`
- Branch parent for this tranche: exact ordered-octonion repair head `80a74d8ddceb702233577f6da397f2b2c1921808`
- Original authoritative main base: `f5d8fdc014d888f93c0d85d40d2a2c0c198eefdf`
- Frozen Pass 219 I118 ancestor: `e87bc42b17c03ff98f691838b8d573a5bdf46ff2`
- Merge target: `main`

This tranche is additive. It does not rewrite the frozen 1.15 monolithic residual source or the inherited UQCEL compatibility projection.

## Source authority

The low-level ABI binds three exact representations without declaring normalization identity between them.

1. Native UTF-8 source supplied for this ABI:
   - `contracts/pass219/PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode`
   - SHA-256 `ac143798146d89a3fe932f39ccb4d612e4fb3e45c471abc1a8bbbebb0f9c0a6a`
   - exact UTF-8 byte length `348`
   - preserves `P³`, `P²`, `t³`, `∆`, `√`, `u⁷²`, and `x²` exactly.

2. Stable ASCII HARMONICODE machine fixture inherited by Pass 159-compatible tooling:
   - `contracts/pass219/PASS_219_NATIVE_UNIVERSAL_CONSTRAINT_ENVELOPE_1_8_0.harmonicode`
   - SHA-256 `7eb0cc5707a4a58a5a8e4879e0e2e3bdab22c15fe4503fb3a3b0e16596343d42`
   - exact byte length `354`, including its terminating newline.

3. Frozen 1.15 TeX residual boundary:
   - `contracts/pass219/PASS_219_MONOLITHIC_UQCEL_RESIDUAL_BOUNDARY_1_15_0.tex`
   - SHA-256 `9f2238981bf509d22ffebb46816346f389fd2d949ccd7956cde3630ab2b56944`.

CI dumps both ABI source forms and requires byte-for-byte `cmp` plus exact SHA-256 equality against their repository fixtures.

## Implemented low-level surface

Public functions:

- `hhs_exact_pass219_monolithic_version`
- `hhs_exact_pass219_monolithic_descriptor`
- `hhs_exact_pass219_monolithic_native_source`
- `hhs_exact_pass219_monolithic_source`
- `hhs_exact_pass219_monolithic_native_edge`
- `hhs_exact_pass219_monolithic_edge`
- `hhs_exact_pass219_monolithic_family_span`
- `hhs_exact_pass219_monolithic_verify_proof`

The source scanners preserve the ten ordered relation edges rather than flattening them into independent host Booleans.

```text
native UTF-8 byte offsets: 11, 27, 39, 53, 95, 239, 265, 273, 284, 329
machine ASCII byte offsets: 11, 27, 41, 55, 97, 241, 267, 275, 286, 335
edge kinds:                 =   =   =   =   ==  ==   ==   ==   ==   =
```

Parenthesis, brace and bracket nesting depth is retained for every edge. The differing byte coordinates are explicit consequences of UTF-8 glyph width and ASCII transport spelling; they are not silently conflated.

## Monolithic proof packet

The packet binds one candidate state to all required source families:

- harmonic `P²`, `t³-t`, `m²-m`, `pq`, `∆` relations;
- modified Lo Shu matrix surface;
- ordered phase surface including the exact I119 `xy/yx` identity;
- `s,f,At,Bt` tensor/substitution state;
- `Mod(f/u,72*(pq+xy))`;
- `AB/P²` and `Sqrt[AB]` relation;
- terminal `(AB/(pq+∆)-P²)/(t³-t)*u^72` relation;
- `∆/P=√(pq+u⁷²)^x²` boundary.

The packet records the inherited Pass 159 whole-expression lowering stages:

```text
source-open -> lex -> CST -> AST -> typecheck -> constraint-graph
-> HIR -> VMIR -> interpret -> replay -> VM81 proof
```

Its Hash216 fields bind source, AST, constraint graph, VMIR, candidate state, aggregate proof, and all eight semantic-family witnesses; the Hash72 field carries the receipt identity. The machine-source SHA-256 is the execution-facing source identity because the inherited Pass159 tooling consumes that stable fixture. The descriptor separately binds the native UTF-8 source so presentation/source fidelity cannot be lost.

## Anti-spoofing rule

A caller-populated proof packet is not canonical proof authority. Therefore:

```text
raw_packet_can_prove = 0
```

`hhs_exact_pass219_monolithic_verify_proof` can reject malformed, contradictory, source-mismatched, order-collapsed, or failed packets. A structurally complete packet sets `proof_packet_complete=1`, but still returns `UNRESOLVED` with `requires_vm81_authority=1`.

`HHS_EXACT_PASS219_MONOLITHIC_PROVEN` is reserved for the inherited Pass159 -> VM81 proof adapter after independent graph execution, exact-value validation, receipt verification and deterministic replay. This prevents a caller from manufacturing success by filling ten Boolean edge flags.

Any explicit contradiction returns `REJECTED`. Missing stages, unresolved edges, missing families, or incomplete exact-domain resolution return `UNRESOLVED`.

## Authority boundary

The 1.20 ABI is a source-preserving, proof-carrying low-level boundary. It has:

```text
floating_point_authority = 0
vm81_mutation_authority = 0
hash72_commit_authority = 0
```

It does not create a substitute evaluator or second commit authority. Arithmetic/algebraic proof authority remains the inherited Pass159 whole-expression constraint graph lowered into VM81 as required by Pass169 and the Pass219 contract.

## Files added/updated

- `contracts/pass219/PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode`
- `hhs_runtime/include/hhs_pass219_monolithic_constraint_abi_1_20.h`
- `hhs_runtime/c/hhs_pass219_monolithic_constraint_abi_1_20.inc`
- `hhs_runtime/include/hhs_runtime_exact_abi.h`
- `hhs_runtime/c/hhs_runtime_exact_abi.c`
- `tests/pass219/test_pass219_monolithic_constraint_abi_1_20.c`
- `tests/pass219/test_pass219_monolithic_constraint_abi_1_20.cpp`
- `.github/workflows/pass219-monolithic-constraint-abi-1-20.yml`
- `docs/operations/restart/PASS_219_MONOLITHIC_CONSTRAINT_ABI_1_20_RESTART.md`

## Validation gates

The focused workflow requires exact-head and synthetic-merge success for:

1. native UTF-8, machine ASCII and frozen TeX SHA-256 identities;
2. byte-for-byte native and machine ABI source round trips;
3. strict C11 cumulative exact-ABI compilation with warnings as errors;
4. C native/machine edge topology, family and proof-packet conformance;
5. C++ ABI conformance;
6. rejection of floating-point and mutation/commit/admit exports in the new boundary;
7. anti-spoof behavior: a caller-complete packet cannot self-promote to `PROVEN`;
8. inherited ordered-octonion I119 regression.

The existing UQCEL and VM81 exact-ABI workflows also rerun because the cumulative exact ABI aggregate changed.
