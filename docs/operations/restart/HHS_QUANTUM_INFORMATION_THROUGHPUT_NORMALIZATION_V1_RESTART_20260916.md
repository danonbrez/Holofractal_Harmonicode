# HHS Quantum-Information Throughput Normalization v1 — Restart Record

Date: 2026-09-16

## Base / branch / merge target

- Prior verified white-paper merge: `1c4787258b954b7ef700e7d1ea706da2c1f763b7`
- Direct normalization-paper commit preserved on main: `4a9a9f4883aaaae1ac64238c17f62b86103bfcd8`
- Direct restart/anchor lineage subsequently preserved on main through: `edff67ebe7508c6ce670d544b2e60b7d997dc79a`
- Feature branch: `docs/qinfo-throughput-normalization-20260916`
- Branch base: `edff67ebe7508c6ce670d544b2e60b7d997dc79a`
- Pull request: `#470`
- Merge target: `main`

## Implemented files

```text
docs/whitepapers/HHS_QUANTUM_INFORMATION_THROUGHPUT_NORMALIZATION_V1.md
tools/hhs_qinfo_throughput_normalize_v1.py
tests/docs/test_hhs_qinfo_throughput_normalization_v1.py
.github/workflows/hhs-qinfo-throughput-normalization-v1.yml
docs/whitepapers/HHS_LANE5_WHITEPAPER_INDEX_V1.md
docs/README.md
docs/operations/restart/HHS_QUANTUM_INFORMATION_THROUGHPUT_NORMALIZATION_V1_RESTART_20260916.md
```

Temporary `docs/whitepapers/.hhs_qinfo_branch_anchor` is deleted by the feature branch and must not remain after merge.

## Implemented semantics

- Exact logical/Hilbert-space-equivalent dimension: `72^72`.
- Exact qudit factorization: 72 qudits of dimension 72.
- Qubit-equivalent address information: `log2(72^72)=444.23460010384645` bits-equivalent.
- Minimum binary embedding width: 445 bits.
- Native exact address carrier: 56 bytes / 448 available bits.
- Deterministic candidate-shot rate.
- Basis-coordinate information-rate metric.
- Four-address route-schema capacity-rate metric.
- 72-level qudit-coordinate rate.
- VM5184 block-coordinate rate using `72^72=5184^36`.
- Provisioned-vCPU density.
- Replay-fidelity and coherence-equivalent terminology with explicit non-physical qualifiers.
- Circuit depth, gate rate, and quantum volume retained as usable terms but reserved until compatible instrumentation/protocols exist.
- `REFERENCE_ONLY` clarified as a canonical-authority classification, not a statement that quantum/physics equations are unimportant for comparative analysis.

## Runner normalization

Provider-declared public `ubuntu-24.04` normalization:

```text
architecture: x64
vCPU: 4
RAM: 16 GB
SSD: 14 GB
```

The executable normalizer additionally captures per-run:

```text
observed CPU model
observed logical CPU count
observed memory
observed filesystem capacity/free space
kernel/platform
RUNNER_OS / RUNNER_ARCH / ImageOS / ImageVersion when exposed
compiler version
active benchmark thread count
```

## Commands / validation workflow

Focused CI workflow:

```text
.github/workflows/hhs-qinfo-throughput-normalization-v1.yml
```

It executes:

```text
python -m pytest -q tests/docs/test_hhs_qinfo_throughput_normalization_v1.py
make clean
make c-abi
cc -O3 ... tests/pass219/test_pass219_lane5_unbounded_workload_scaling_1_48.c ...
/tmp/test-pass219-lane5-unbounded-1-48
python tools/hhs_qinfo_throughput_normalize_v1.py native-scaling.json qinfo-throughput-normalization.json
```

Then it validates the hardware record and authority membrane and uploads `hhs-qinfo-throughput-normalization-v1` evidence.

## Validation status

- PR #470: open, non-draft, mergeable.
- Focused normalization workflow run: `35086761604`.
- Focused workflow status at this checkpoint: in progress.
- HHS Lane 5 white-paper conformance workflow also triggered on PR #470.
- No completed success claim is recorded here until the workflow finishes.

## Next action

1. Inspect run `35086761604`.
2. If a dependency-scoped failure appears, repair forward on PR #470 and rerun only the impacted gate.
3. If the focused normalization and white-paper gates pass, merge PR #470.
4. Verify exact `main` and the post-merge normalization check/artifact.
