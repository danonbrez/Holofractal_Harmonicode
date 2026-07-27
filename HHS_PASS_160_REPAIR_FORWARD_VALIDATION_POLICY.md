# HHS PASS 160 — REPAIR-FORWARD VALIDATION POLICY

## 1. Authority and scope

This policy is additive to `HHS_PASS_160_CONTRACT.md` and `HHS_PASS_160_INHERITANCE_AMENDMENT_V1_2.md`. It governs validation scheduling, evidence reuse, regression response, and final-delivery closure for Pass 160. It does not weaken any semantic, integrity, isolation, replay, or authority requirement.

## 2. Governing rules

```text
UNCHANGED_CODE + UNCHANGED_INPUT + PREVIOUSLY_VALID_RECEIPT
→ REUSE_VERIFIED_EVIDENCE

CHANGED_SCOPE
→ DEPENDENCY_SCOPED_VALIDATION

FINAL_DELIVERY
→ ONE_BOUNDED_INTEGRATION_AND_REPLAY_GATE

LATER_REGRESSION
→ REPAIR_FORWARD_PATCH
```

## 3. Frozen evidence rule

A previously executed receipt is reusable when all of the following remain unchanged:

- source bytes for the validated unit;
- direct dependency bytes and versions;
- canonical test vectors and input datasets;
- compiler/runtime profile relevant to the receipt;
- schema and registry roots consumed by the validated unit;
- authority and inheritance baseline bound by the receipt.

Reused evidence shall be recorded by receipt identity rather than regenerated through an identical execution.

## 4. Dependency-scoped validation

A changed file opens only the validation surface required by that file and its direct dependencies.

| Changed scope | Required validation |
|---|---|
| Native C11 runtime, ABI, crypto, or native tests | strict build, affected native unit/negative tests, sanitizer coverage for changed authority paths, direct C/Python vectors if canonical bytes changed |
| Python reference, API, CLI test tooling, or schemas | affected Python unit/negative tests, direct native/reference vectors, affected CLI/API integration |
| Source transport chunks or materialization | per-chunk SHA-256, reconstructed archive SHA-256, gzip/tar structure, materialization smoke test |
| Evidence or release tooling | receipt schema validation, manifest integrity, deterministic packaging check using frozen executed reports |
| Workflow-only change | workflow syntax/graph review and the smallest executable smoke test needed to prove the changed orchestration |
| Contract or documentation only | no runtime rerun unless executable requirements or canonical inputs changed |

## 5. One bounded final gate

Pass 160 final delivery receives one bounded gate containing:

1. clean strict build;
2. essential native runtime matrix;
3. essential Python/reference and native differential matrix;
4. controlled negative matrix;
5. deterministic replay and canonical-root generation;
6. one x86_64 and one aarch64 canonical replay comparison where runner availability permits;
7. inherited completion-receipt verification for Passes 157, 158, and 159 without rerunning unchanged exhaustive suites;
8. release-bundle and evidence-package integrity validation;
9. terminal completion predicate evaluation.

The evidence-closure stage shall consume the final-gate reports. It shall not execute the same full validation suite a second time.

## 6. Non-blocking follow-up classification

The following do not block Pass 160 when the bounded terminal predicate is otherwise satisfied:

- non-critical compiler or platform warnings that do not alter authoritative bytes or behavior;
- redundant architecture/compiler permutations beyond the required canonical replay pair;
- repeated execution over byte-identical datasets;
- performance repetitions after the required bounded workload has produced a valid receipt;
- advisory improvements that do not affect admission, identity, integrity, replay, isolation, or commit authority.

Such items are recorded as follow-up work and addressed through scoped patches.

## 7. Repair-forward regression handling

A later failure does not erase valid unrelated evidence. It creates a corrective scope consisting of:

- the failing unit;
- files changed since its last valid receipt;
- direct dependencies that can affect the failure;
- affected integration boundaries;
- the specific evidence artifacts invalidated by the defect.

The correction shall receive dependency-scoped validation and a new superseding receipt. Unaffected receipts remain frozen and valid.

## 8. Current Pass 160 frozen evidence

Unless their bytes or direct dependencies change, the following completed results are frozen:

- native runtime matrix: `1,000,595` positive checks, `160` controlled negative checks, `0` failures;
- exact lookup workload: `1,000,000` successful lookups;
- native/Python differential vectors: `7/7` matched;
- Python reference tests: `6/6` passed;
- CLI command matrix: `24/24` passed;
- governed API matrix: `10/10` passed;
- property fuzz: `2,048` valid checks and `512` controlled rejections;
- fault injection: `22/22` interruption points with `0` partial authoritative states;
- concurrency: exactly `1` admitted commit and `1` stale rejection from `2` conflicting proposals;
- sanitizer authority-path matrix: `4,691` positive checks, `160` negative checks, `0` failures;
- native source capsule SHA-256: `f14c0f49cd6cd0c627d546279c38066968140debcc3911c95af0b42f95a22270`;
- five verified immutable source-transport chunks unaffected by the isolated reference-chunk truncation.

The current changed scope is limited to reference-source transport repair, reference-package identity metadata, and workflow orchestration that previously repeated full validation.

## 9. Terminal boundary

This policy does not itself emit the terminal classification. The terminal classification remains reserved for the bounded final gate and complete evidence-package integrity predicate:

```text
HHS_PASS_160_FIBONACCI_PRIME_PSEUDORANDOM_OVERLAP_RECEIPT_TIP_VALIDATED_TRANSITION_RUNTIME_VERIFIED
```
