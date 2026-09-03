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


## Feature validation closure

Accepted feature head:

`93f0fac10e06e04555c988c3ebc99fa0f2b08367`

Dedicated I156 workflow:

- run: `33767257127`
- job: `100688184912`
- conclusion: SUCCESS
- artifact: `9898052234`
- artifact SHA-256: `abfd61edeee81471cbfbf70b6fe32b3f5af7948df3ac8a1f1425495d8199a2ce`

Artifact receipts:

```text
conformance.txt
sha256 = 4202f3370f6395295cb7a44697b4675eb850d72f525ca0f31c7fbe0a9718258b

full_symbolic_monolithic_lowering.json
sha256 = 7b9c08633bf7e1e10718d8221353ff06dd3cb5d03b2c8b68bf15d26c9a2aa1ed

benchmark receipt
sha256 = aabd900272762bac9714c004c116953f99ae9ae3bbbd1eebd38f83759faf5d72
```

Validated capability:

```text
terms                         = 15
frozen equality edges         = 10
edge mask on complete witness = 0x03FF
semantic families             = 8
family mask                   = 0x00FF
historical residual mask      = 0x001F
complete-witness residual     = 0
exact ratio equality          = BigInt cross multiplication
source identity               = required
Pass159 provenance root       = required
ordered xy/yx state           = required
single candidate transaction  = required
```

Authority remains bounded:

```text
candidate value producer included = false
VM81 execution verified           = false
Hash72 execution receipt          = false
deterministic replay verified     = false
VM81 mutation authority           = false
Hash72 mint authority             = false
Hash216 persistence authority     = false
floating-point authority          = false
```

Pre-green runs `33766964070`, `33767053587`, `33767117044`, and `33767154528` are preserved as rejected implementation attempts. They all stopped at strict C11 compilation because a pointer-to-array parameter added `const` qualification in a form rejected by ISO C before C2X under `-Werror -pedantic`.

Repair commit:

`93f0fac10e06e04555c988c3ebc99fa0f2b08367`

changed only the internal helper signature; no lowering semantics or authority fields changed.

Feature evidence:

`evidence/pass219/PASS_219_I156_FEATURE_VALIDATION_33767257127.json`

Next integration action:

1. reconcile current `main`;
2. open a ready I156 PR with expected-head guard;
3. inspect dependency-scoped synthetic/PR validation for the exact ABI, monolithic ABI, and UQCEL audit;
4. merge when those impacted gates are clean or already covered by equivalent scoped evidence;
5. verify exact-main I156;
6. collect the I151 history append for the new I156 benchmark surface;
7. seal exact-main evidence/history separately.
