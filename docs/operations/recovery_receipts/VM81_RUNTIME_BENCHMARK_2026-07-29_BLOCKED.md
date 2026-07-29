# VM81 Runtime Benchmark Recovery Receipt

```text
status: BLOCKED
repository: danonbrez/Holofractal_Harmonicode
base_commit: 92dddbee21bae7e00b79b8f6f974501e039adc11
branch: bench/vm81-runtime-20260729
latest_commit: 13bfea84ce5db07a28bbbcc9f56be9ebf158e91a
worktree_clean: true
merge_target: main
merge_status: unmerged
created_at_utc: 2026-07-29T20:50:00Z
```

## Completed scope

- Identified the authoritative standalone VM81 runtime source as `hhs_runtime/HARMONICODE_VM_RUNTIME.c`.
- Identified the repository build form as:

  ```bash
  gcc -O2 -std=c11 hhs_runtime/HARMONICODE_VM_RUNTIME.c -lm -o hhs_vm81
  ```

- Retrieved the source through the connected GitHub repository and recorded Git blob identity `362cd6e892ae66024333b111aec83f12023fdce3` for the inspected runtime snapshot.
- Inspected the runtime structure, including the 81-cell grid, Hash72 projection, receipt composition, orbit scanning, constraint field, sweep81, close81, identity gate, and additive IR bridge.
- Committed a restartable benchmark harness on `bench/vm81-runtime-20260729`:
  - `bench/vm81_microbench.c`
  - `bench/vm81_process_bench.py`
- Committed three temporary GitHub Actions execution carriers on that branch:
  - `.github/workflows/vm81-runtime-benchmark.yml`
  - `.github/workflows/vm81-runtime-benchmark-pr.yml`
  - `.github/workflows/vm81-runtime-benchmark-trigger.yml`
- Created temporary draft pull requests `#52` and `#53` solely to attempt isolated workflow execution.
- No benchmark numbers were fabricated or estimated.

## Files changed on blocked benchmark branch

```text
.github/workflows/vm81-runtime-benchmark-pr.yml
.github/workflows/vm81-runtime-benchmark-trigger.yml
.github/workflows/vm81-runtime-benchmark.yml
bench/vm81_microbench.c
bench/vm81_process_bench.py
```

## Commands and operations already executed

```text
GitHub repository and commit inspection
GitHub source fetch for hhs_runtime/HARMONICODE_VM_RUNTIME.c
GitHub branch creation: bench/vm81-runtime-20260729
GitHub branch creation: bench/vm81-runtime-trigger-20260729
GitHub workflow-run lookup for benchmark carrier commits
GitHub compare main..bench/vm81-runtime-20260729
GitHub compare bench/vm81-runtime-20260729..bench/vm81-runtime-trigger-20260729
```

The native compile and benchmark commands were prepared but did not execute because no connected execution surface accepted the isolated workflow.

## Validation results

```text
PASS: authoritative main resolved to 92dddbee21bae7e00b79b8f6f974501e039adc11
PASS: benchmark branch state is fully committed
PASS: benchmark harness files are repository-visible
PASS: runtime source path and build command are repository-visible
PASS: temporary workflow jobs have bounded timeout-minutes values
BLOCKED: no GitHub Actions workflow run was registered
NOT_RUN: native build
NOT_RUN: official --verify execution
NOT_RUN: in-process microbenchmarks
NOT_RUN: process latency distribution
NOT_RUN: build-time distribution
NOT_RUN: RSS and perf counters
NOT_RUN: analytical benchmark report
```

## Blocker

GitHub Actions did not execute workflows introduced only on non-default temporary branches. The connected GitHub interface available to the agent could inspect workflow runs and artifacts but could not dispatch an arbitrary workflow. The local execution sandbox could not resolve GitHub, and the connected external compute runners were discoverable but not callable in this session.

This is an execution-surface blocker, not a runtime performance result.

## Last operation

```text
last_command: fetch_commit_workflow_runs(commit_sha=0a287d48b16554124d2c5bdd65db61a59c273f38)
last_exit_status: SUCCESS_WITH_EMPTY_RESULT
captured_output: workflow_runs: []
```

## Exact resumable action

Run the following from any Linux execution environment with Git, GCC, Python 3, `/usr/bin/time`, and optional `perf`:

```bash
set -euo pipefail

REPO='https://github.com/danonbrez/Holofractal_Harmonicode.git'
BASE='92dddbee21bae7e00b79b8f6f974501e039adc11'
HARNESS_BRANCH='bench/vm81-runtime-20260729'

rm -rf Holofractal_Harmonicode_vm81_bench
git clone --filter=blob:none "$REPO" Holofractal_Harmonicode_vm81_bench
cd Holofractal_Harmonicode_vm81_bench

git checkout --detach "$BASE"
git fetch origin "$HARNESS_BRANCH"
git checkout "origin/$HARNESS_BRANCH" -- \
  bench/vm81_microbench.c \
  bench/vm81_process_bench.py

mkdir -p build bench_results logs

timeout 120s gcc -O2 -std=c11 -Wall -Wextra \
  hhs_runtime/HARMONICODE_VM_RUNTIME.c -lm -o build/hhs_vm81 \
  >logs/build.stdout 2>logs/build.stderr

timeout 120s ./build/hhs_vm81 --no-trace --verify \
  >bench_results/verify_stdout.txt 2>bench_results/verify_stderr.txt

grep -q 'FINAL HASH72' bench_results/verify_stdout.txt

timeout 120s gcc -O2 -std=c11 -Wall -Wextra \
  bench/vm81_microbench.c -lm -o build/vm81_microbench \
  >logs/microbuild.stdout 2>logs/microbuild.stderr

timeout 300s ./build/vm81_microbench \
  >bench_results/microbench.csv 2>logs/microbench.stderr

timeout 900s python3 bench/vm81_process_bench.py \
  >bench_results/summary_stdout.txt 2>logs/process_bench.stderr

timeout 120s /usr/bin/time -v -o bench_results/time_rss.txt \
  ./build/hhs_vm81 --no-trace --verify >/dev/null

if command -v perf >/dev/null 2>&1; then
  timeout 180s perf stat -r 5 -x, -o bench_results/perf.csv \
    ./build/hhs_vm81 --no-trace --verify >/dev/null \
    2>logs/perf.stderr || printf '%s\n' 'perf unavailable or permission denied' > bench_results/perf.csv
else
  printf '%s\n' 'perf unavailable' > bench_results/perf.csv
fi

sha256sum \
  hhs_runtime/HARMONICODE_VM_RUNTIME.c \
  build/hhs_vm81 \
  bench_results/* \
  >bench_results/SHA256SUMS
```

## Required completion sequence after execution

```text
1. Preserve runner identity, source commit, source blob SHA, compiler version, CPU, and kernel.
2. Validate verify output and deterministic final Hash72 across repeated runs.
3. Analyze median, mean, standard deviation, p95, p99, throughput, build time, RSS, and perf counters when available.
4. Commit benchmark evidence and report on a fresh branch based on current main.
5. Open a ready-to-merge PR or merge directly after dependency-scoped review.
6. Verify the merged evidence on main.
7. Return a user-facing benchmark completion response.
```

## Temporary carrier cleanup state

```text
PR #52: scheduled for closure; do not merge
PR #53: scheduled for closure; do not merge
bench/vm81-runtime-trigger-20260729: temporary carrier; non-authoritative
bench/vm81-runtime-20260729: authoritative blocked benchmark checkpoint until resumed
```
