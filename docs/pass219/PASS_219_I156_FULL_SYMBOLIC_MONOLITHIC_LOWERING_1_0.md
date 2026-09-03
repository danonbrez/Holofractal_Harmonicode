# Pass 219 I156 — Exact Full-Symbolic Monolithic Lowering

I156 implements the next additive Pass 219 boundary after I155.

The historical state was:

```text
production provider              = PRESENT
full-symbolic UQCEL V1           = UNSUPPORTED_DOMAIN
historical residual mask         = 0x001F
aggregate monolithic obligation  = UNRESOLVED
```

I156 does not reinterpret the old V1 input. The V1 structure cannot carry the complete source-level symbolic terms and its compatibility fields named `A` and `B` are not the monolithic source-level left and right sides.

Instead, I156 adds one typed exact lowering ABI for a complete candidate term-value witness.

## 1. New cumulative ABI

Public header:

`hhs_runtime/include/hhs_pass219_full_symbolic_uqcel_lowering_1_22.h`

Implementation:

`hhs_runtime/c/hhs_pass219_full_symbolic_uqcel_lowering_1_22.inc`

Public calls:

```text
hhs_exact_pass219_full_symbolic_version
hhs_exact_pass219_full_symbolic_descriptor
hhs_exact_pass219_full_symbolic_lower
```

The aggregate `hhs_runtime_exact_abi` exports these additively.

## 2. Exact numeric witness type

Every lowered source term uses:

`HHSExactPass219SignedRatioViewV1`

with:

- sign in `{-1,0,+1}`;
- canonical minimal BigUInt numerator magnitude;
- canonical minimal positive BigUInt denominator;
- exact equality by BigInt cross multiplication.

No floating-point conversion participates.

The ratio view is a proof input. It is not a second persisted numeric authority.

## 3. Fifteen unique source terms

The full frozen chain is represented with fifteen shared value nodes:

1. `t^3-t`
2. `P^3-P/(P^2-pq)`
3. `(t^3-t)/Delta`
4. `P^2(MOD)(pq)`
5. `m^2-m`
6. `s`
7. the source-bound `s` substitution RHS
8. `(matrix+x+y)/At`
9. `Mod(f/u,72*(pq+xy))/Bt`
10. `AB/P^2`
11. `Sqrt[AB]`
12. the complete outer LHS
13. the terminal RHS
14. `Delta/P`
15. `Sqrt(pq+u^72)^x^2`

Shared terms are stored once and reused across their equality edges so disconnected per-edge Boolean packets cannot represent different values for one source term.

## 4. Ten frozen equality edges

The exact lowering checks:

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

Every edge belongs to the exact frozen source topology already registered by the 1.20 monolithic ABI.

## 5. Eight semantic families

A complete witness resolves:

```text
HARMONIC
MATRIX
ORDERED_PHASE
TENSOR_SUBSTITUTION
MODULAR
AB_ROOT
TERMINAL
DELTA_ROOT
```

The ordered-phase family additionally requires a valid inherited octonion state and preserves the distinction between `xy` and `yx`.

## 6. Monolithic transaction rule

Lowering succeeds only when:

```text
source SHA-256 exact
AND nonzero Pass159 provenance root bound
AND all fifteen exact ratios are well formed
AND inherited ordered-octonion state validates
AND every one of the ten frozen equality edges is exact
AND all eight semantic families belong to the same witness packet
```

Then:

```text
decision             = LOWERED
edge mask            = 0x03FF
family mask          = 0x00FF
residual mask        = 0
one candidate state  = true
```

Candidate and per-family Hash216 identities are generated deterministically from source identity, provenance root, ordered phase state, and canonical ratio material.

## 7. What I156 resolves

I156 removes the structural inability to represent and verify the complete full-symbolic monolithic equality chain.

For a complete explicit candidate term-value witness, the historical residual bits:

```text
T_M_HARMONIC
TENSOR_S_F_AT_BT
DELTA_P_ROOT
MOD_F_U
MONOLITHIC_EQUALITY_CHAIN
```

all clear to zero together.

A failed equality does not partially admit the candidate. It returns a rejected lowering with failed edge/family diagnostics.

## 8. What I156 does not claim

I156 verifies term values that have already been produced by an exact candidate evaluator. It does not itself derive those values from runtime state.

Therefore:

```text
candidate value producer included = false
VM81 execution verified           = false
Hash72 execution receipt          = false
deterministic replay verified     = false
Pass169 terminal proof            = false
```

This distinction is mandatory.

A caller cannot turn equal input ratios into canonical Pass169 authority merely by filling the witness packet.

## 9. Relationship to the 1.20 monolithic proof ABI

The 1.20 ABI remains the downstream proof-carrying boundary.

Its anti-spoof invariant remains unchanged:

`raw_packet_can_prove = 0`.

I156 is upstream of VM81 proof. It supplies a source-preserving exact lowering state that a later candidate-value producer and VM81 adapter may consume.

It does not weaken the existing rule that only VM81 execution, receipt verification, and replay may complete canonical proof authority.

## 10. Relationship to I155

I155 changed the production blocker from provider absence to an exact full-symbolic residual.

I156 changes the technical nature of that residual:

```text
before I156:
no complete exact term-value lowering surface existed

after I156:
complete exact term-value lowering surface exists,
but production provider still lacks a candidate-bound value producer
```

Thus the next blocker is not “how to represent the monolithic equality chain.”

It is:

`CANDIDATE_BOUND_FULL_SYMBOLIC_VALUE_PRODUCER`.

## 11. Fixed search geometry

I156 does not resize:

[
|Omega|=72^{42}=5184^{21},
]

[
|mathcal M|=3cdot72^{72},
]

or:

[
|mathcal R_omega|=3cdot72^{30}.
]

The production exhaustion requirement remains:

[
7W_{mathrm{baseline}}ge81W_{mathrm{effective}}.
]

No real four-lane exhaustion result is claimed by this lowering layer.

## 12. Next implementation tranche

The next cumulative step must produce the fifteen exact term values from one candidate state under the source-bound Pass159 graph, then feed the already-implemented I156 lowering.

Only after that producer is exact may the system proceed through:

```text
candidate value production
→ I156 monolithic lowering
→ VM81 admission
→ atomic commit
→ Hash72 execution receipt
→ Hash216 proof / transition identity
→ deterministic replay
→ production Pass169 provider packet
→ real I154 exhaustion measurement
```
