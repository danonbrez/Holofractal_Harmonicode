# Pass 214 Restart Record

## Repository state after Iteration 7 safe checkpoint

- Iteration 7 base commit: `5be251a3df5bd3f949dbae8e34c71cfd5465bcd6`
- Iteration 7 implementation commit: `a5c07bfff57880c60a0ba6e24e1eec17d38e3f88`
- Iteration 7 restart checkpoint: `7cc3c56298078fc40b26f827983cfb04176de928` was superseded by hosted-validation repair/diagnostic commits.
- Iteration 7 hosted CLI repair: `557d58eeacdfba4f19147d19a38ff2744f06f0d0`
- Latest diagnostic parent before safe checkpoint: `4dc4fa4050af78b7da027da9b4f2e8a2bdd17cb5`
- Safe validation evidence commit: `a64027112b393cb2c156dd1e2f12c4ca96f18392`
- Branch: `agent/pass214-operating-compression-gradient`
- Merge target: `main`
- Draft PR: `#170`
- Pass 213 closure dependency: `86ec461818682fc87232740758769602e8f9fe05`
- Iteration 6 candidate-set root: `f11bdbb9940e90500692cd0a0c505727ad94cafc0ea4fca85b134253f72cab9f`
- Pass 215 authorization: `false`

## Cumulative completion

1. Iteration 1 — immutable repository census and optimization registry.
2. Iteration 2 — callable conformance records, normalized groups, conflicts, and compatibility graph.
3. Iteration 3 — Pass 213-bound pure oracle models, adapters, replay, and tamper rejection.
4. Iteration 4 — exact repository-callable identity and isolated deterministic execution membrane; historical payload defect has now been exactly repaired as recorded below.
5. Iteration 5 — five-family three-run exact-parity corpus with positive representation gain.
6. Iteration 6 — exact repository-native candidate binding and strict live-admission membrane.
7. Iteration 7 — operational live-admission bridge, RFC 3161 re-verification, cross-authority binding, governed candidate challenge commitment, and gated five-family ablation plan.

## Iteration 7 authority bridge

A live admission requires one coherent runtime state across three inherited Pass 213 authorities:

- `TrustedTimestampAnchorRecord.validate` must successfully reverify the full RFC 3161 record using the Pass 213 PQC verifier bundle and an explicit trust bundle.
- The Pass 213 governed projection chain must verify and its latest timestamp and moving-tensor projections must bind to the reverified anchor.
- The configured Pass 213 Iteration 10 native-dispatch ledger must verify, contain a receipt, and reference the same moving tensor and trusted anchor.
- The latest dispatch receipt tensor and lineage must agree with current native-dispatch runtime state.
- The Iteration 6 candidate set is committed as a challenge through the existing governed `RECEIPT` projection path and the projection chain is reverified after the commitment.

Fixture, synthetic, mock, dependency-scoped, zero-root, mismatched-anchor, mismatched-tensor, mismatched-lineage, and structurally tampered admissions are rejected.

## Dependency-scoped validation completed

```text
python compile: passed
Iteration 7 tests: 7 passed
deterministic challenge binding: passed
missing operational RFC3161 inputs blocked: passed
fixture/synthetic timestamp authority rejection: passed
tensor/native-dispatch mismatch rejection: passed
governed candidate challenge commit with test double: passed
admission-root tamper rejection: passed
recorded-admission live-recheck gate: passed
```

Deterministic identities:

```text
Iteration 7 manifest root: 32a395d717da140d1406367996afb825b10d894b7eb244b940e6acaca351391f
runtime source SHA-256: 23702a3420453d95fba1f87fb5675992d97dbaf63ed910dfc5aa5e1b117212e0
runtime gzip SHA-256: 4b348a07b59ada0ec471e0e28cdd82d654c7e25928144ea3b1aafe881b8b6750
runtime wrapper SHA-256: d6ef1272d28f28ee6762d64e1da70aba28909ccccb33b3fa41397337f60baecd
```

## Hosted validation state before exact Iteration 4 repair

The Iteration 7 hosted workflow succeeded after the CLI repository-root repair:

```text
workflow: Pass 214 Iteration 7 Live Admission Bridge
run: 31144838012
head: 557d58eeacdfba4f19147d19a38ff2744f06f0d0
conclusion: success
production live admission claimed: false
```

The cumulative Pass 214 workflow had remained blocked before later benchmark/promotion stages because inherited Iteration 4 integrity loading failed:

```text
workflow: Pass 214 Compound Optimization Benchmark Authority
observed run: 31145448541
head: 4dc4fa4050af78b7da027da9b4f2e8a2bdd17cb5
conclusion: failure
blocking stage: Iteration 4 integrity payload validation
later benchmark/promotion stages authoritative: false
```

## Iteration 4 integrity defect — historical diagnostic

The repository contained a single historical Iteration 4 runtime payload lineage from its implementation commit. Hosted validation proved that its gzip container was invalid and that the raw-deflate-recoverable source did not match the frozen historical source hash.

Historical diagnostic facts:

```text
historical claimed source SHA-256:
a946cde1338bc33eb6873c13125b306a45882dec46fd29ac4820ce38ea5612a9

recoverable corrupted source SHA-256:
3bceeed0b19ee20b242db89660706ffcf7e2c4996b5481c9dc547a0b936ce9f4

recoverable source size: 48547 bytes
gzip trailer ISIZE: 48547 bytes
recoverable source compile: failed
```

The diagnostic source showed statement separators represented by literal `b` bytes at many source boundaries. The equal source size and gzip ISIZE constrained the defect toward byte substitution rather than arbitrary insertion/deletion.

## Iteration 4 exact repair — 2026-08-07

The historical runtime payload was recovered cryptographically without rebinding any frozen identity. Exhaustive search of the one-byte substitution neighborhood of the compressed payload found a unique candidate matching the frozen payload SHA-256. That candidate decompressed to a source matching the frozen source SHA-256 exactly and compiled successfully.

Exact repair identities:

```text
corrupted payload SHA-256:
3169204e65935b44fc7269e66568a5aa0325a4db603947af50209a5d2f59142a

frozen/recovered payload SHA-256:
392d655df87628832fbd14d19301bc7dc8c002cf69b571fc6f12ab867961930d

frozen/recovered source SHA-256:
a946cde1338bc33eb6873c13125b306a45882dec46fd29ac4820ce38ea5612a9

source size: 48547 bytes
compressed byte repair: offset 973, 0xBE -> 0xDE
python compile: passed
original Iteration 4 dependency-scoped tests: 11 passed
```

Repair commits and evidence:

```text
exact evidence commit: 4f5eda8b4545d7ce72c415ca99aaa34f4fef6122
validation workflow update: e2b33ccc952769cda27bda92a5985b02b27411e9
exact payload restore commit: 45c81ac4c7cc9402c02e7901c51b0df4b3cefe43
recovery workflow run: 31181177757
recovery conclusion: success
```

The exact repair gate preserved all non-promotion constraints:

```text
integrity metadata rebound: false
authority promoted: false
terminal Pass 214 root minted: false
Pass 215 authorized: false
```

The repaired payload was committed only after reproducing both frozen hashes and passing the original 11-test Iteration 4 dependency-scoped suite. Failed or incomplete candidates were never promoted to the production payload path.

## Iteration 7 changed files

- `hhs_backend/runtime/hhs_pass214_iteration7_live_admission_ablation_v1.py`
- `hhs_backend/runtime/pass214_i7_payload/runtime.py.gz`
- `tools/pass214_iteration7_live_admission.py`
- `tools/pass214_iteration7_manifest.py`
- `tests/test_hhs_pass214_iteration7_live_admission_ablation_v1.py`
- `.github/workflows/pass214-iteration7-live-admission.yml`
- `.github/workflows/pass214-compound-optimization-benchmark.yml`
- `scripts/run_pass214_contract_validation.sh`
- `docs/pass214/ITERATION_7_LIVE_ADMISSION_ABLATION_BRIDGE.md`
- `evidence/pass214/PASS_214_ITERATION_7_IMPLEMENTATION_RECORD.json`
- `evidence/pass214/PASS_214_ITERATION_7_SAFE_CHECKPOINT.json`
- `docs/pass214/RESTART_RECORD.md`

## Current next exact action

1. Preserve the exact Iteration 4 restored payload and its cryptographic recovery evidence.
2. Run the cumulative Pass 214 Iterations 1–7 validation on the exact restored payload.
3. Repair forward only from any newly exposed dependency-scoped failure; do not rerun or rewrite already frozen identities unnecessarily.
4. Only after cumulative validation passes should production Pass 213 live admission and the five-family baseline/optimized/ablation execution continue.
5. Preserve `HOLD` on migration, authority promotion, terminal Pass 214 closure, and Pass 215 until every production gate passes.

Pass 214 remains draft and unmerged. Pass 215 remains unauthorized.
