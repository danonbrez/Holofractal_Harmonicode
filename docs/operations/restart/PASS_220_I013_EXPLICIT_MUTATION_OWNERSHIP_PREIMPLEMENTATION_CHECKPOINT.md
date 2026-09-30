# Pass 220 I013 preimplementation checkpoint — explicit mutation ownership

Status: **RESTARTABLE PREIMPLEMENTATION CHECKPOINT**

## Lineage

- base exact main: `e9e6fa60752df4ea8d289037330c99a0c92a8e2a`
- branch: `pass220/i013-explicit-mutation-ownership-v1`
- merge target: `main`
- predecessor: Pass 220 I012 `CLOSED_VERIFIED_MAIN`
- predecessor merge: `e3c4c993a21a2e737b604ee0346dd2d44121d371`

## Objective

Bind the I012 harmonic/Genesis candidate gate to the repository's kernel invariant `HHS-I013 — Explicit mutation ownership` without creating any new mutation implementation.

The invariant requires every mutation path to declare:

```text
owning surface
persistence policy
rollback behavior
ledger effect
```

The Pass 219 production mutation owner remains exactly:

```text
hhs_exact_pass219_vm81_environment_admit_signed
```

I013 will verify the handoff contract only. It will not invoke the C ABI or mutate VM81.

## Planned execution law

```text
I012 result
  -> HALT / blocked:
       no mutation handoff
       no owner claim
  -> Lane-5 candidate admitted:
       candidate remains proposal-only
       optional canonical handoff may be constructed only with exact owner symbol
       persistence/rollback/ledger policy must match inherited canonical policy
       witness records mutation_performed=false
```

Required failure codes:

- `REJECT_MUTATION_OWNER_MISMATCH`
- `REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY`
- `REJECT_MUTATION_ROLLBACK_POLICY_MISSING`
- `REJECT_MUTATION_LEDGER_EFFECT_MISSING`
- `REJECT_I012_NOT_ADMITTED`

## Authority boundary

The I013 witness must always carry:

```text
canonical_vm81_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
mutation_performed = false
```

It may identify the inherited owner, but identity is not authority.

## Planned files

- `hhs_runtime/hhs_pass220_explicit_mutation_ownership_v1.py`
- `tests/pass220/test_hhs_pass220_explicit_mutation_ownership_v1.py`
- `docs/pass220/PASS_220_I013_EXPLICIT_MUTATION_OWNERSHIP.md`
- `.github/workflows/pass220-i013-explicit-mutation-ownership.yml`
- postimplementation restart checkpoint

## Validation policy

Dependency-scoped tests only. Preserve the exact I012 witness semantics and the existing Pass 219 singleton mutation path. Do not wait on unrelated external CI before sealing a restartable implementation checkpoint.
