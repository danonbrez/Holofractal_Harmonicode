# Pass 220 I003.1 restart checkpoint — cold x86_64 raw-byte calibration isolation

Status: **RESTARTABLE REPAIR CHECKPOINT — CI PENDING**

## Lineage

- repository: danonbrez/Holofractal_Harmonicode
- merge target: main
- working branch: pass220-lo-shu-normalization-checkpoint-1
- predecessor I003 checkpoint: 86832d8cfb26c22b45de8f780d15e9f8d3c35a76
- I003.1 pre-repair checkpoint: 692ef6eb4ecfce8237dc0e89a81e1aca14c5c87d
- draft PR: #491

## Repair completed

The I003 max-hardware calibration has been separated from HHS/HARMONICODE/runtime execution.

The authoritative hardware-calibration workload is now:

benchmarks/pass220/hhs_pass220_i003_cold_x86_64_raw_bytes_abc_v1.sh

It executes immediately after checkout and before package installation, project compilation, Python, make, HHS services, runtime ABI loading, Lane 5, VM81, Hash72, or Hash216 logic.

## Raw workload

The workload is an exact zero-byte stream from /dev/zero with adaptive doubling and no configured byte-size ceiling.

A = head -c N /dev/zero >/dev/null
B = head -c N /dev/zero | dd of=/dev/null bs=1M status=none
C = head -c N /dev/zero | sha256sum >/dev/null

Order rotates ABC/BCA/CAB.

The labels xy/yx/zw/wz remain four repeated cohorts only. They have no HHS phase semantics inside the raw calibration.

## Stop membrane

The byte count doubles until one of:

- an arm exceeds the common leg deadline;
- the global deadline is reached;
- shell integer range would overflow;
- an ordinary Linux command fails.

There is no MAX_BYTES or MAX_CANDIDATES hardware-calibration parameter.

Default time envelope:

- start = 1 MiB
- leg = 120,000,000 ns
- global = 30,000,000,000 ns
- repeats = 3

The start size is a noise floor, not a maximum.

## Raw evidence

The Bash benchmark emits:

- records.tsv
- summary.env
- report.md
- runner.txt

summary.env explicitly records:

HHS_SERVICES_USED=0
HHS_RUNTIME_ABI_USED=0
PROJECT_COMPILED_CODE_USED=0
PYTHON_USED=0
WORKLOAD_SIZE_STATIC_CEILING=0
TIMING_OBSERVATIONAL_ONLY=1

The per-cohort largest closed byte count and their minimum are the cold-runner capacity witness.

## Workflow repair

.github/workflows/pass220-i003-four-phase-abc-max-hardware.yml now:

1. checks out the repository;
2. immediately runs the raw Bash calibration;
3. verifies raw isolation using Bash only;
4. only after calibration installs build/test dependencies;
5. only after calibration builds the project/runtime surfaces;
6. runs I001-I003 dependency-scoped integration tests;
7. records descriptive 5184-byte and 216-byte equivalents after the raw witness is already frozen;
8. uploads raw calibration plus post-calibration integration evidence.

The inherited Pass 219 HHS raw-runner A:B:C preflight was removed from the cold hardware-calibration path because it exercises HHS runtime/ABI services.

## Query harness classification repair

benchmarks/pass220/hhs_pass220_i003_four_phase_abc_max_hardware_v1.py remains useful for post-calibration query comparison, but it now explicitly declares:

hardware_calibration_authority = false
post_calibration_integration_only = true
cold_raw_byte_calibration_required_for_hardware_claim = true

It must not be cited as the max-hardware witness.

## Files changed by I003.1

- benchmarks/pass220/hhs_pass220_i003_cold_x86_64_raw_bytes_abc_v1.sh
- .github/workflows/pass220-i003-four-phase-abc-max-hardware.yml
- benchmarks/pass220/hhs_pass220_i003_four_phase_abc_max_hardware_v1.py
- docs/pass220/PASS_220_I003_FOUR_PHASE_ABC_MAX_HARDWARE_QUERY_CALIBRATION.md
- docs/operations/restart/PASS_220_I003_1_COLD_RAW_BYTES_PRE_REPAIR_CHECKPOINT.md
- docs/operations/restart/PASS_220_I003_1_COLD_RAW_BYTES_REPAIR_CHECKPOINT.md

## Validation remaining

1. Dedicated workflow must execute the cold raw-byte script on an actual GitHub-hosted x86_64 runner.
2. Confirm all four raw cohorts close at least one size and record the measured max bytes.
3. Confirm post-calibration dependency-scoped tests remain green.
4. Repair forward only impacted integration defects.
5. Seal the measured cold-runner raw-byte evidence; do not rewrite prior Pass 219 measurements.

## Next action

Wait for the dedicated workflow evidence. If green, seal the measured I003.1 cold-runner capacity artifact and use that neutral capacity witness to normalize the next real hydrated multimodal query optimization cycle.
