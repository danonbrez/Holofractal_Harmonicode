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

The low-level ABI is bound to both inherited source identities:

1. Stable ASCII HARMONICODE machine fixture:
   - `contracts/pass219/PASS_219_NATIVE_UNIVERSAL_CONSTRAINT_ENVELOPE_1_8_0.harmonicode`
   - SHA-256 `7eb0cc5707a4a58a5a8e4879e0e2e3bdab22c15fe4503fb3a3b0e16596343d42`
   - exact byte length `354`

2. Frozen 1.15 TeX residual boundary:
   - `contracts/pass219/PASS_219_MONOLITHIC_UQCEL_RESIDUAL_BOUNDARY_1_15_0.tex`
   - SHA-256 `9f2238981bf509d22ffebb46816346f389fd2d949ccd7956cde3630ab2b56944`

The ABI returns the machine fixture byte-for-byte. CI dumps the ABI source and requires `cmp` equality and the exact SHA-256 above.

## Implemented low-level surface

New public functions:

- `hhs_exact_pass219_monolithic_version`
- `hhs_exact_pass219_monolithic_descriptor`
- `hhs_exact_pass219_monolithic_source`
- `hhs_exact_pass219_monolithic_edge`
- `hhs_exact_pass219_monolithic_family_span`
- `hhs_exact_pass219_monolithic_verify_proof`

The source scanner preserves the ten ordered relation edges exactly as written:

```text
byte offsets: 11, 27, 41, 55, 97, 241, 267, 275, 286, 335
edge kinds:   =   =   =   =   ==  ==   ==   ==   ==   =
```

It also records parenthesis, brace, and bracket nesting depth at every edge. The chain is not lowered to a host-language Boolean expression.

## Monolithic proof rule

The proof packet binds one candidate state to all required source families:

- harmonic `P²`, `t³-t`, `m²-m`, `pq`, `Delta` relations;
- modified Lo Shu matrix surface;
- ordered phase surface including I119 `xy/yx` identity;
- `s,f,At,Bt` tensor/substitution state;
- `Mod(f/u,72*(pq+xy))`;
- `AB/P²` and `Sqrt[AB]` relation;
- terminal `(AB/(pq+Delta)-P²)/(t³-t)*u^72` relation;
- `Delta/P=Sqrt(pq+u^72)^x²` boundary.

The packet also requires the inherited Pass 159 whole-expression lowering stages:

```text
source-open -> lex -> CST -> AST -> typecheck -> constraint-graph
-> HIR -> VMIR -> interpret -> replay -> VM81 proof
```

A proof is `PROVEN` only when:

- source identity matches the frozen machine fixture;
- all required lowering/proof stages completed;
- all eight semantic families are resolved;
- all ten ordered equality/binding edges are satisfied;
- no edge is failed or unresolved;
- every represented value is exact;
- all witnesses belong to one candidate state;
- the full LHS/RHS boundary is equal;
- Hash216/Hash72 proof identities are syntactically canonical;
- the I119 octonion state validates and its ordered `xy` and `yx` products remain distinct and correctly bound.

Any explicit contradiction returns `REJECTED`. Missing stages, unresolved edges, missing families, or incomplete exact-domain resolution return `UNRESOLVED`.

## Authority boundary

The 1.20 ABI is a source-preserving, proof-carrying low-level boundary. It has:

```text
floating_point_authority = 0
vm81_mutation_authority = 0
hash72_commit_authority = 0
```

It does not create a substitute evaluator or a second commit authority. Arithmetic/algebraic proof authority remains the inherited Pass 159 whole-expression constraint graph lowered into VM81 as required by Pass 169 and the Pass 219 contract.

`PROVEN` therefore means that a complete inherited Pass159/VM81 proof packet has been structurally bound to the verbatim source and candidate state. It is not permission for this ABI layer itself to mutate VM81 or mint a canonical receipt.

## Files added/updated

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

1. authoritative source SHA-256 checks;
2. byte-for-byte ABI source round trip;
3. strict C11 cumulative exact-ABI compilation with warnings as errors;
4. C source/edge/family/proof conformance;
5. C++ ABI conformance;
6. absence of floating-point tokens and commit/admit/persist exports in the new boundary;
7. inherited ordered-octonion I119 regression.

The existing UQCEL and VM81 exact-ABI workflows are also expected to rerun because the cumulative exact ABI aggregate changed.
