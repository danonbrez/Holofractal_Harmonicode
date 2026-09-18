#!/usr/bin/env bash
set -euo pipefail

# Pass 220 I003.1 cold-runner x86_64 raw-byte A:B:C calibration.
#
# Deliberate isolation:
# - no HHS/HARMONICODE import, binary, service, kernel/runtime ABI, or project build
# - no Python
# - no compiled benchmark helper
# - shell + ordinary Linux/coreutils only
#
# The byte workload has no configured size ceiling.  It doubles until the cold
# runner reaches the declared time membrane (or shell integer range).

OUTDIR="${1:-${RUNNER_TEMP:-/tmp}/pass220-i003-cold-raw}"
START_BYTES="${HHS_PASS220_I003_RAW_START_BYTES:-1048576}"
LEG_BUDGET_NS="${HHS_PASS220_I003_RAW_LEG_BUDGET_NS:-120000000}"
GLOBAL_BUDGET_NS="${HHS_PASS220_I003_RAW_GLOBAL_BUDGET_NS:-30000000000}"
REPEATS="${HHS_PASS220_I003_RAW_REPEATS:-3}"
TIMER_TOLERANCE_NS="${HHS_PASS220_I003_RAW_TIMER_TOLERANCE_NS:-5000000}"

mkdir -p "$OUTDIR"
RECORDS="$OUTDIR/records.tsv"
SUMMARY="$OUTDIR/summary.env"
REPORT="$OUTDIR/report.md"
RUNNER="$OUTDIR/runner.txt"

arch="$(uname -m)"
if [[ "$arch" != "x86_64" ]]; then
  echo "expected cold x86_64 runner, observed: $arch" >&2
  exit 2
fi

for cmd in bash date head dd sha256sum timeout uname getconf awk; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "required Linux command missing: $cmd" >&2
    exit 3
  }
done

if ! [[ "$START_BYTES" =~ ^[1-9][0-9]*$ && "$LEG_BUDGET_NS" =~ ^[1-9][0-9]*$ && "$GLOBAL_BUDGET_NS" =~ ^[1-9][0-9]*$ && "$REPEATS" =~ ^[1-9][0-9]*$ ]]; then
  echo "invalid positive integer calibration parameter" >&2
  exit 4
fi

leg_budget_seconds="$(awk -v ns="$LEG_BUDGET_NS" 'BEGIN { printf "%.9f", ns / 1000000000 }')"

{
  echo "runner_os=${RUNNER_OS:-unknown}"
  echo "runner_arch=${RUNNER_ARCH:-unknown}"
  echo "uname_machine=$arch"
  echo "kernel=$(uname -srmo)"
  echo "nproc=$(getconf _NPROCESSORS_ONLN)"
  echo "page_size=$(getconf PAGESIZE)"
  echo "bash=$BASH_VERSION"
  echo "head=$(head --version | head -n 1)"
  echo "dd=$(dd --version | head -n 1)"
  echo "sha256sum=$(sha256sum --version | head -n 1)"
} > "$RUNNER"

printf 'phase\tbytes\torder\tarm\telapsed_ns\trepeats\tcomplete\tcommand_class\tdataset_spec\tdataset_sha256\n' > "$RECORDS"

now_ns() {
  date +%s%N
}

run_arm() {
  local arm="$1"
  local bytes="$2"
  local digest_file="$3"
  local command_text status started ended elapsed complete command_class

  case "$arm" in
    A)
      command_class="HEAD_ZERO_TO_NULL"
      command_text="for ((r=0; r<$REPEATS; r++)); do head -c $bytes /dev/zero > /dev/null; done"
      ;;
    B)
      command_class="HEAD_ZERO_PIPE_DD_NULL"
      command_text="for ((r=0; r<$REPEATS; r++)); do head -c $bytes /dev/zero | dd of=/dev/null bs=1048576 status=none; done"
      ;;
    C)
      command_class="HEAD_ZERO_PIPE_SHA256"
      command_text="for ((r=0; r<$REPEATS; r++)); do head -c $bytes /dev/zero | sha256sum > '$digest_file'; done"
      ;;
    *)
      echo "unknown arm: $arm" >&2
      return 5
      ;;
  esac

  started="$(now_ns)"
  set +e
  timeout --signal=TERM --kill-after=1s "${leg_budget_seconds}s" bash -c "$command_text"
  status=$?
  set -e
  ended="$(now_ns)"
  elapsed=$(( ended - started ))

  complete=0
  if [[ "$status" -eq 0 && "$elapsed" -le $((LEG_BUDGET_NS + TIMER_TOLERANCE_NS)) ]]; then
    complete=1
  fi

  printf '%s\t%s\t%s\t%s\n' "$elapsed" "$complete" "$command_class" "$status"
}

declare -A PHASE_MAX_BYTES
PHASES=(xy yx zw wz)
ORDERS=(ABC BCA CAB)
GLOBAL_STARTED="$(now_ns)"
GLOBAL_STOP_REASON="ALL_PHASES_REACHED_TIME_MEMBRANE"

for phase_index in "${!PHASES[@]}"; do
  phase="${PHASES[$phase_index]}"
  bytes="$START_BYTES"
  rank_index=0
  phase_max=0

  while :; do
    global_now="$(now_ns)"
    if (( global_now - GLOBAL_STARTED >= GLOBAL_BUDGET_NS )); then
      GLOBAL_STOP_REASON="GLOBAL_TIME_MEMBRANE"
      break
    fi

    order="${ORDERS[$((rank_index % 3))]}"
    digest_file="$OUTDIR/${phase}-${bytes}.sha256"
    sample_complete=1
    declare -A ARM_ELAPSED=()
    declare -A ARM_COMPLETE=()
    declare -A ARM_CLASS=()

    for ((pos=0; pos<3; pos++)); do
      arm="${order:$pos:1}"
      IFS=$'\t' read -r elapsed complete command_class status < <(run_arm "$arm" "$bytes" "$digest_file")
      ARM_ELAPSED["$arm"]="$elapsed"
      ARM_COMPLETE["$arm"]="$complete"
      ARM_CLASS["$arm"]="$command_class"
      if [[ "$complete" -ne 1 ]]; then
        sample_complete=0
      fi
    done

    dataset_sha="UNAVAILABLE"
    if [[ -s "$digest_file" ]]; then
      dataset_sha="$(awk '{print $1}' "$digest_file")"
    fi
    dataset_spec="ZERO_BYTES:${bytes}"

    for arm in A B C; do
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$phase" "$bytes" "$order" "$arm" "${ARM_ELAPSED[$arm]}" "$REPEATS" \
        "${ARM_COMPLETE[$arm]}" "${ARM_CLASS[$arm]}" "$dataset_spec" "$dataset_sha" >> "$RECORDS"
    done

    if [[ "$sample_complete" -eq 1 ]]; then
      phase_max="$bytes"
    else
      break
    fi

    rank_index=$((rank_index + 1))
    if (( bytes > 4611686018427387903 )); then
      GLOBAL_STOP_REASON="SHELL_INTEGER_RANGE"
      break
    fi
    bytes=$(( bytes * 2 ))
  done

  PHASE_MAX_BYTES["$phase"]="$phase_max"
  if [[ "$GLOBAL_STOP_REASON" == "GLOBAL_TIME_MEMBRANE" ]]; then
    # Remaining phase cohorts did not get a fair cold-runner time slice.
    break
  fi
done

global_max=0
all_phases=1
for phase in "${PHASES[@]}"; do
  if [[ -z "${PHASE_MAX_BYTES[$phase]+x}" || "${PHASE_MAX_BYTES[$phase]}" -le 0 ]]; then
    all_phases=0
    continue
  fi
  if [[ "$global_max" -eq 0 || "${PHASE_MAX_BYTES[$phase]}" -lt "$global_max" ]]; then
    global_max="${PHASE_MAX_BYTES[$phase]}"
  fi
done

GLOBAL_ELAPSED=$(( $(now_ns) - GLOBAL_STARTED ))

{
  echo "SCHEMA=HHS_PASS_220_I003_1_COLD_X86_64_RAW_BYTES_ABC_V1"
  echo "ARCH=$arch"
  echo "START_BYTES=$START_BYTES"
  echo "LEG_BUDGET_NS=$LEG_BUDGET_NS"
  echo "GLOBAL_BUDGET_NS=$GLOBAL_BUDGET_NS"
  echo "REPEATS=$REPEATS"
  echo "GLOBAL_ELAPSED_NS=$GLOBAL_ELAPSED"
  echo "ALL_FOUR_COHORTS_EXECUTED=$all_phases"
  echo "PHASE_XY_MAX_BYTES=${PHASE_MAX_BYTES[xy]:-0}"
  echo "PHASE_YX_MAX_BYTES=${PHASE_MAX_BYTES[yx]:-0}"
  echo "PHASE_ZW_MAX_BYTES=${PHASE_MAX_BYTES[zw]:-0}"
  echo "PHASE_WZ_MAX_BYTES=${PHASE_MAX_BYTES[wz]:-0}"
  echo "GLOBAL_MAX_CLOSED_BYTES=$global_max"
  echo "STOP_REASON=$GLOBAL_STOP_REASON"
  echo "HHS_SERVICES_USED=0"
  echo "HHS_RUNTIME_ABI_USED=0"
  echo "PROJECT_COMPILED_CODE_USED=0"
  echo "PYTHON_USED=0"
  echo "WORKLOAD_SIZE_STATIC_CEILING=0"
  echo "TIMING_OBSERVATIONAL_ONLY=1"
} > "$SUMMARY"

{
  echo "# Pass 220 I003.1 — cold x86_64 raw-byte A:B:C calibration"
  echo
  echo "- Architecture: `$arch`"
  echo "- Workload: deterministic zero-byte streams from `/dev/zero`"
  echo "- Static workload-size ceiling: **none**"
  echo "- Start bytes: `$START_BYTES`"
  echo "- Per-arm time membrane: `$LEG_BUDGET_NS ns`"
  echo "- Global time membrane: `$GLOBAL_BUDGET_NS ns`"
  echo "- Repeats per arm: `$REPEATS`"
  echo "- HHS services/runtime ABI/project binaries used by calibration: **none**"
  echo "- Python used by calibration: **none**"
  echo
  echo "## Raw A:B:C paths"
  echo
  echo "- A: `head -c N /dev/zero >/dev/null`"
  echo "- B: `head -c N /dev/zero | dd of=/dev/null bs=1M status=none`"
  echo "- C: `head -c N /dev/zero | sha256sum >/dev/null`"
  echo
  echo "The labels xy/yx/zw/wz are repeated calibration cohorts only; the raw-byte benchmark assigns them no HHS phase semantics."
  echo
  echo "## Largest closed raw-byte workload"
  echo
  for phase in "${PHASES[@]}"; do
    echo "- $phase: `${PHASE_MAX_BYTES[$phase]:-0}` bytes"
  done
  echo "- all-cohort minimum: `$global_max` bytes"
  echo "- stop reason: `$GLOBAL_STOP_REASON`"
  echo "- observed global elapsed: `$GLOBAL_ELAPSED ns`"
} > "$REPORT"

cat "$SUMMARY"

if [[ "$all_phases" -ne 1 || "$global_max" -le 0 ]]; then
  echo "cold raw-byte calibration did not close all four cohorts" >&2
  exit 6
fi
