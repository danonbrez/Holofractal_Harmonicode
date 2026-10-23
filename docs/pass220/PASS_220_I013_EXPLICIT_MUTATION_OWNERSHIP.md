# Pass 220 I013 — Explicit mutation ownership

Status: **IMPLEMENTED — OWNERSHIP/HANDOFF WITNESS ONLY; CANONICAL MUTATION UNCHANGED**

Schema: `HHS_PASS_220_I013_EXPLICIT_MUTATION_OWNERSHIP_V1`  
Kernel invariant: `HHS-I013 — Explicit mutation ownership`

## 1. Inherited invariant

The kernel invariant registry requires:

```text
Every state mutation declares its owning surface,
persistence policy,
rollback behavior,
and ledger effect.
```

Required witness:

```text
HHS_MUTATION_OWNERSHIP_WITNESS_V1
```

Required validator:

```text
validate_explicit_mutation_ownership
```

The inherited registry rejection code remains:

```text
REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY
```

## 2. Canonical mutation owner

The Pass 219 authority-reconciliation contract and the 1.32 environmental header both identify the production mutation successor as exactly:

```text
hhs_exact_pass219_vm81_environment_admit_signed
```

I013 records that identity but does not call it.

The exact ownership policy used by the Pass 220 handoff witness is:

```text
owner_surface      = hhs_exact_pass219_vm81_environment_admit_signed
persistence_policy = INHERITED_CANONICAL_VM81_RECEIPT_LEDGER
rollback_behavior  = INHERITED_SINGLETON_VM81_ROLLBACK
ledger_effect      = INHERITED_HASH72_HASH216_CANONICAL_TRANSITION
```

These strings are an explicit Pass-220 handoff contract describing the inherited policy. They do not create a new persistence, rollback, ledger, receipt, or mutation implementation.

## 3. I012 -> I013 execution law

I013 consumes the I012 result.

```text
I012 HALT
  -> NO_MUTATION_REQUIRED
  -> no owner claim
  -> no handoff

I012 blocked
  -> REJECT_I012_NOT_ADMITTED
  -> no handoff

I012 coherent Lane-5 candidate
  -> request_canonical_handoff = false
       -> PROPOSAL_ONLY
       -> no owner claim

I012 coherent Lane-5 candidate
  -> request_canonical_handoff = true
       -> require exact owner
       -> require persistence policy
       -> require rollback behavior
       -> require ledger effect
       -> HANDOFF_CONTRACT_VALID
       -> still mutation_performed = false
```

The handoff witness validates routing. It never performs the handoff target's canonical state mutation.

## 4. Fail-closed rejection surface

I013 rejects:

```text
REJECT_I012_NOT_ADMITTED
REJECT_I012_AUTHORITY_ESCALATION
REJECT_MUTATION_OWNER_MISMATCH
REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY
REJECT_MUTATION_ROLLBACK_POLICY_MISSING
REJECT_MUTATION_LEDGER_EFFECT_MISSING
```

The I012 input itself is invalid if it claims canonical VM81, Hash72, or Hash216 authority.

## 5. Composed runtime gate

`Pass220OwnedLane5HandoffGate` composes:

```text
Pass220GenesisZeroSumLane5Gate
        |
        v
I012 halt / harmonic / Lane-5 candidate result
        |
        v
I013 explicit ownership witness
```

The wrapper does not call the native 1.32 ABI. It returns only:

- the I012 result;
- the I013 ownership witness;
- whether the canonical handoff contract is structurally valid.

Every composed result explicitly states:

```text
mutation_performed = false
canonical_vm81_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
canonical_receipt_authority = false
```

## 6. Repository authority-source binding

I013 includes a source witness that verifies the declared owner exists in both:

- `contracts/pass219/PASS_219_VM81_EXTERNAL_ENVIRONMENTAL_AUTHORITY_RECONCILIATION_V1.md`;
- `hhs_runtime/include/hhs_pass219_vm81_environmental_recovery_1_32.h`.

The source witness requires both the production-owner declaration and the 1.32 successor declaration. Missing source evidence fails closed.

## 7. Deterministic witness

Every I013 witness receives a deterministic SHA-256 over canonical sorted JSON.

The SHA-256 is lineage for this projection/witness layer only. It is not presented as Hash72, Hash216, or a canonical VM81 receipt.

## 8. Dependency-scoped validation

Dedicated tests cover:

1. complete HHS-I013 policy tuple;
2. Genesis halt -> no mutation required;
3. blocked I012 -> no ownership handoff;
4. admitted I012 remains proposal-only without explicit handoff;
5. exact inherited owner/policy -> valid handoff contract only;
6. wrong owner rejection;
7. missing/wrong persistence, rollback, and ledger policy rejection;
8. I012 authority-escalation rejection;
9. exact boolean typing;
10. repository source proof of the sole production mutation owner;
11. deterministic witness receipt;
12. composed I012->I013 wrapper remains non-authoritative;
13. blocked I012 cannot be promoted by the wrapper.

The dependency-scoped workflow also reruns I011/I012 exact tests so the handoff cannot become green while its immediate candidate-admission dependency is broken.
