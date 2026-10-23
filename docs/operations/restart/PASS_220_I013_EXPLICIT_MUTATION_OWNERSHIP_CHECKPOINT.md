# Pass 220 I013 restart checkpoint — explicit mutation ownership

Status: **RESTARTABLE IMPLEMENTATION CHECKPOINT — DEPENDENCY-SCOPED CI PENDING**

## Lineage

- exact main base: `e9e6fa60752df4ea8d289037330c99a0c92a8e2a`
- branch: `pass220/i013-explicit-mutation-ownership-v1`
- merge target: `main`
- predecessor I012: `CLOSED_VERIFIED_MAIN`
- predecessor merge: `e3c4c993a21a2e737b604ee0346dd2d44121d371`

## Implementation commits

- `ac29cbd8156d7a86191ed1e7fb8dcd2b662f1136` — preimplementation checkpoint
- `3f0ea3e5a14a9b22a1de6e1dc90e96b2743a1546` — exact HHS-I013 ownership witness
- `f2f4857f7179da757b079a77893eaf7f8ab8e59b` — initial ownership tests
- `797dd16c508fece06b138cbeb8a8ebd2966bbde0` — composed I012->I013 handoff gate
- `816a0585ce5cd2c2b46d00ac12066060c633a83a` — composed-gate tests
- `ce22f80e8cdb6d47278dea5574a0d99f3c1aab27` — I013 formalization
- `33b380e7d2e8dfd5fa5b6e365e4ac140b3b33953` — dedicated dependency-scoped CI

## Implemented invariant

```text
HHS-I013 — Explicit mutation ownership

Every state mutation declares:
- owning surface
- persistence policy
- rollback behavior
- ledger effect
```

Pass 220 binds the inherited production owner exactly as:

```text
hhs_exact_pass219_vm81_environment_admit_signed
```

The owner identity is verified against both the Pass 219 reconciliation contract and the 1.32 environmental header.

## I012 -> I013 composed path

```text
I012 HALT
  -> NO_MUTATION_REQUIRED

I012 blocked
  -> REJECT_I012_NOT_ADMITTED

I012 admitted candidate + no explicit handoff
  -> PROPOSAL_ONLY

I012 admitted candidate + explicit handoff
  -> verify exact owner
  -> verify persistence policy
  -> verify rollback behavior
  -> verify ledger effect
  -> HANDOFF_CONTRACT_VALID
```

Even `HANDOFF_CONTRACT_VALID` records:

```text
mutation_performed = false
canonical_vm81_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
canonical_receipt_authority = false
```

The wrapper never invokes the native mutation ABI.

## Fail-closed codes

- `REJECT_I012_NOT_ADMITTED`
- `REJECT_I012_AUTHORITY_ESCALATION`
- `REJECT_MUTATION_OWNER_MISMATCH`
- `REJECT_MUTATION_SURFACE_WITHOUT_PERSISTENCE_POLICY`
- `REJECT_MUTATION_ROLLBACK_POLICY_MISSING`
- `REJECT_MUTATION_LEDGER_EFFECT_MISSING`

## Files added

- `hhs_runtime/hhs_pass220_explicit_mutation_ownership_v1.py`
- `hhs_backend/runtime/hhs_pass220_i013_owned_lane5_handoff_v1.py`
- `tests/pass220/test_hhs_pass220_explicit_mutation_ownership_v1.py`
- `docs/pass220/PASS_220_I013_EXPLICIT_MUTATION_OWNERSHIP.md`
- `.github/workflows/pass220-i013-explicit-mutation-ownership.yml`
- pre/post restart checkpoints

## Dependency-scoped CI

The dedicated workflow runs:

```text
tests/pass220/test_hhs_pass220_mobius_quarter_phase_v1.py
tests/pass220/test_hhs_pass220_genesis_zero_sum_halt_v1.py
tests/pass220/test_hhs_pass220_explicit_mutation_ownership_v1.py
```

This preserves the immediate I011 -> I012 -> I013 dependency chain without rerunning unrelated historical suites.

No green result is claimed at this checkpoint.

## Next action

Open the I013 PR, observe only the dedicated dependency-scoped run, and repair forward if it fails. If green, merge to current main with an expected-head guard and verify the I013 files on main.
