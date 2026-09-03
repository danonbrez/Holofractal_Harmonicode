# Pass 219 I156 — Full-Symbolic Monolithic Lowering Restart

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base: `main @ 2e0dd3ad7245e97191f78abb5ceb119785f90f85`
- Branch: `agent/pass219-i156-full-symbolic-monolithic-lowering`
- Merge target: `main`
- Implementation head before validation: `3e43ddeff1852f7ba9792e29e592e92741998132`

## Purpose

I156 implements the additive exact lowering layer required after I155.

It does not reinterpret the legacy V1 full-symbolic UQCEL input. Instead it adds a typed exact witness ABI capable of representing all ten frozen equality edges and all eight semantic families in one source-bound transaction.

## Implemented files

- `hhs_runtime/include/hhs_pass219_full_symbolic_uqcel_lowering_1_22.h`
- `hhs_runtime/c/hhs_pass219_full_symbolic_uqcel_lowering_1_22.inc`
- `hhs_runtime/include/hhs_runtime_exact_abi.h`
- `hhs_runtime/c/hhs_runtime_exact_abi.c`
- `tests/pass219/test_pass219_i156_full_symbolic_monolithic_lowering.c`
- `benchmarks/pass219/pass219_i156_full_symbolic_monolithic_lowering_benchmark.py`
- `contracts/pass219/PASS_219_I156_FULL_SYMBOLIC_MONOLITHIC_LOWERING_1_0.json`
- `docs/pass219/PASS_219_I156_FULL_SYMBOLIC_MONOLITHIC_LOWERING_1_0.md`
- `.github/workflows/pass219-i156-full-symbolic-monolithic-lowering.yml`
- this restart record.

## New callable surface

```text
hhs_exact_pass219_full_symbolic_version
hhs_exact_pass219_full_symbolic_descriptor
hhs_exact_pass219_full_symbolic_lower
```

## Exact witness model

The lowering packet contains:

- exact machine-source SHA-256;
- one nonzero Pass159 provenance root;
- one inherited ordered octonion state;
- fifteen shared source term values;
- exact term values represented as signed BigUInt ratios.

Ratio equality is checked through exact BigInt cross multiplication.

No float conversion exists in the lowering surface.

## Ten source edges

```text
t3_minus_t                    = p3_minus_p_over_delta
p3_minus_p_over_delta         = t3_minus_t_over_delta
t3_minus_t_over_delta         = p2_mod_pq
p2_mod_pq                     = m2_minus_m
s                             = s_substitution_rhs
matrix_plus_xy_over_At        = mod_f_over_u_over_Bt
mod_f_over_u_over_Bt          = AB_over_P2
AB_over_P2                    = sqrt_AB
outer_LHS                     = terminal_RHS
Delta_over_P                  = Delta_root_RHS
```

## Completion semantics

For one complete witness:

```text
edge satisfied mask     = 0x03FF
family resolved mask    = 0x00FF
residual mask           = 0
source identity exact   = true
provenance root bound   = true
all values exact        = true
ordered xy/yx bound     = true
one candidate state     = true
monolithic chain lowered= true
```

The implementation derives deterministic candidate-state and family Hash216 identities from the exact witness material.

## Authority boundary

I156 does not include a term-value producer.

Therefore:

```text
candidate value producer authority  = false
VM81 execution verified             = false
Hash72 execution receipt verified   = false
deterministic replay verified       = false
canonical VM81 mutation authority   = false
canonical Hash72 mint authority     = false
canonical Hash216 persistence       = false
floating-point authority            = false
```

A caller-complete witness cannot self-promote to Pass169 terminal proof.

## Inherited behavior preserved

The 1.20 monolithic proof ABI remains downstream and keeps:

`raw_packet_can_prove = 0`.

The historical V1 UQCEL full-symbolic input remains insufficient because it cannot carry all monolithic terms.

The integer/symmetric V1 compatibility projection remains unchanged.

## Validation plan

The dedicated I156 workflow must:

1. enforce no floating-point or mutation authority in I156 surfaces;
2. strict-compile the cumulative exact ABI;
3. run positive exact cross-multiplication conformance;
4. reject edge mismatch, source drift, zero provenance root, and malformed ratio encoding;
5. preserve the inherited 1.20 monolithic anti-spoof boundary;
6. preserve the 1.15 residual-boundary regression;
7. build a shared ABI and prove all three I156 symbols are exported;
8. emit a benchmark receipt;
9. publish an immutable workflow artifact.

The benchmark source is repository-visible so I151 can append it after integration.

## Next implementation transition after I156

`CANDIDATE_BOUND_FULL_SYMBOLIC_VALUE_PRODUCER`

That producer must derive the fifteen exact term values from one source-bound candidate state under the Pass159 graph.

Only after that producer is validated may the system proceed through:

```text
I156 lowering
→ VM81 admission
→ atomic commit
→ Hash72 execution receipt
→ Hash216 proof / transition identity
→ deterministic replay
→ production Pass169 provider authority
→ real I154 four-lane exhaustion measurement
```

## Restart action

If interrupted:

1. resume from the branch head recorded above or newer repository-visible commits;
2. inspect only the I156 workflow and direct UQCEL/monolithic regressions;
3. repair forward any scoped failure;
4. commit green feature evidence;
5. open a ready PR against current main;
6. merge with exact-head guard;
7. verify exact-main I156 and I151 history;
8. seal evidence/history on a separate evidence-only branch;
9. do not wait on unrelated workflows.

Current implementation blocker: none before CI.
Current downstream authority blocker: candidate-bound full-symbolic value production.
