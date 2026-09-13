# Pass 219 Generation Integrity and Adversarial Perturbation Contract V1

## Status

Operational Pass 219 integrity contract. This layer verifies repository and generated-state integrity around the existing VM81 / Hash72 / Hash216 / environmental-PQC authority chain. It does not create a second transition, receipt, persistence, or mutation authority.

## Response target

Any generated, edited, restored, merged, or externally supplied source state that can affect the canonical runtime SHALL be treated as untrusted until it passes the complete integrity pipeline:

```text
untrusted repository state
        -> structural verification
        -> cryptographic artifact verification
        -> fail-closed build
        -> ABI verification
        -> semantic authority verification
        -> admissible repository state
```

The contract is intentionally source-agnostic. A perturbation may originate in generation, editing, merge conflict resolution, tooling, filesystem corruption, build synthesis, or another mechanism; the same gate applies.

## Closure law

Let:

- `V_structure` be the exact structural-invariant verifier;
- `V_artifact` be the protected-artifact identity verifier;
- `V_build` be the fail-closed build verifier;
- `V_ABI` be the dynamic ABI/export verifier;
- `V_authority` be the canonical-authority boundary verifier.

Then:

```text
V = V_structure AND V_artifact AND V_build AND V_ABI AND V_authority
```

and:

```text
NOT(V_structure)
OR NOT(V_artifact)
OR NOT(V_build)
OR NOT(V_ABI)
OR NOT(V_authority)
    => HALT / reject candidate repository state
```

No failed stage may fall through to a weaker path.

## Structural invariants

The active compile-time proof header is:

```text
hhs_runtime/include/hhs_pass219_generation_integrity_v1.h
```

It binds the existing exact ABI constants to compiler-visible assertions:

```text
VM81 cells       = 81
VM81 word bits   = 64
VM81 frame bits  = 5184
VM81 frame bytes = 648
Hash72 coords    = 5184
sizeof(HHSExactVM81Frame) = 648
```

It additionally freezes the integrity policy flags:

```text
NO_UNCHECKED_CANONICAL_MUTATION = TRUE
NO_HOST_ESCALATION              = TRUE
HALT_ON_DIVERGENCE              = TRUE
CANONICAL_VM81_DYNAMIC_ALLOC    = FALSE
```

The proof header is included by the internal Pass 219 signed-PQC boundary, so drift is compilation-visible on the active native path.

## Allocation boundary

`NO_DYNAMIC_ALLOCATION` is not asserted globally because the repository's PQC provider path uses bounded OpenSSL-owned scratch allocations for public-key and signature material.

The stronger repository-true rule is:

```text
canonical VM81 state allocation = static / caller-owned
provider PQC scratch allocation = non-canonical, bounded, cleaned, and freed
```

The integrity verifier therefore enforces the current OpenSSL allocation/free surface and rejects raw allocator introduction into the guarded canonical cell-wall path.

## Cryptographic artifact seal

The manifest is:

```text
contracts/pass219/PASS_219_GENERATION_INTEGRITY_MANIFEST_V1.json
```

Each protected artifact is sealed by:

```text
repository path
canonical byte length
Git blob identity
SHA-256 digest
```

The verifier recomputes all three identities from repository bytes and halts on mismatch. A legitimate mutation therefore requires an explicit manifest reseal in the same reviewable change set.

The aggregate protected-artifact record is itself canonicalized and SHA-256 hashed into the emitted evidence receipt.

Hash72 / Hash216 runtime authority is not replaced by repository SHA-256. Source-artifact integrity and runtime transition identity remain typed, separate surfaces.

## Authority boundary

The following internal mutation surfaces SHALL remain local/non-dynamic:

```text
hhs_exact_vm81_admit_uqcel
hhs_exact_pass219_admit_composed
hhs_exact_pass219_rna_admit_composed
hhs_exact_pass219_vm81_pqc_admit
hhs_exact_pass219_vm81_pqc_admit_signed
hhs_exact_pass219_vm81_environment_checkpoint_seal
```

The production environmental successor remains public:

```text
hhs_exact_pass219_vm81_environment_admit_signed
```

The integrity gate verifies both sides after building the shared runtime.

## Fail-closed build surface

The dedicated deterministic build scaffold is:

```text
tools/pass219/pass219_generation_integrity_make_v1.mk
```

It requires Bash strict mode semantics through:

```make
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
.SUFFIXES:
```

The dedicated gate deliberately disables suffix fallback behavior rather than changing every inherited repository build target at once.

## Perturbation evidence record

A reproducible perturbation investigation SHALL retain, when available:

```text
base commit
branch / merge target
prompt or source-operation identity
pre-change protected-artifact root
candidate patch or changed paths
post-change protected-artifact root
compiler / linker result
ABI export result
semantic gate result
repeat-run identity
```

The contract distinguishes observations from attribution. Repeated mutations can be classified from the evidence record without weakening the fail-closed response while causality remains unresolved.

## Negative tests

The validation cycle SHALL prove at minimum:

1. the sealed current tree passes;
2. a protected-byte mutation fails artifact verification;
3. a VM81 structural-constant mutation fails structural verification or compilation;
4. an internal authority export leak fails ABI verification;
5. removal of signed-before-VM81 or scratch-cleanup evidence fails semantic verification.

## Authority invariant

This contract is a verifier only:

```text
canonical_mutation_authority_created = FALSE
canonical_receipt_authority_created  = FALSE
Hash72_authority_created              = FALSE
Hash216_authority_created             = FALSE
```

The existing VM81 / RNA / signed environmental successor chain remains authoritative.
