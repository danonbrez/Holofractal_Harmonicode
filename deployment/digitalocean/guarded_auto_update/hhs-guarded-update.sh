#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

REPO_ROOT=${HHS_REPO_ROOT:-/opt/hhs/app}
REMOTE=${HHS_GIT_REMOTE:-origin}
BRANCH=${HHS_GIT_BRANCH:-main}
SYSTEMD_UNITS=${HHS_SYSTEMD_UNITS:-hhs.service}
STATE_ROOT=${HHS_UPDATE_STATE_ROOT:-/var/lib/hhs-guarded-update}
LOCK_FILE=${HHS_UPDATE_LOCK_FILE:-/run/lock/hhs-guarded-update.lock}
VALIDATOR_REL=${HHS_VALIDATOR_RELATIVE_PATH:-deployment/digitalocean/guarded_auto_update/validate-candidate.sh}
DRIFT_RECONCILER=${HHS_HOST_DRIFT_RECONCILER:-$REPO_ROOT/deployment/digitalocean/guarded_auto_update/preserve-host-drift.sh}
VALIDATE_TIMEOUT=${HHS_VALIDATE_TIMEOUT_SECONDS:-3600}
HEALTH_TIMEOUT=${HHS_HEALTH_TIMEOUT_SECONDS:-180}
HEALTH_INTERVAL=${HHS_HEALTH_INTERVAL_SECONDS:-2}
HEALTH_URLS=${HHS_HEALTH_URLS:-http://127.0.0.1:8080/api/system/status}
EXPECTED_REPOSITORY=${HHS_EXPECTED_REPOSITORY:-danonbrez/Holofractal_Harmonicode}
KEEP_CANDIDATES=${HHS_KEEP_CANDIDATES:-3}
POST_MERGE_COMMAND=${HHS_POST_MERGE_COMMAND:-bash bin/post_compile && bash deployment/digitalocean/guarded_auto_update/build-runtime-os.sh}
ROLLBACK_COMMAND=${HHS_ROLLBACK_COMMAND:-bash bin/post_compile && bash deployment/digitalocean/guarded_auto_update/build-runtime-os.sh}
SYNC_SELF=${HHS_UPDATE_SYNC_SELF:-1}
DRY_RUN=${HHS_UPDATE_DRY_RUN:-0}

CANDIDATE_ROOT="$STATE_ROOT/candidates"
RECEIPT_LOG="$STATE_ROOT/receipts.jsonl"
LAST_SUCCESS="$STATE_ROOT/last-success.json"
CURRENT_CANDIDATE=""
PREVIOUS_SHA=""
CANDIDATE_SHA=""
PROMOTION_STARTED=0

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"
}

fail() {
  log "ERROR: $*"
  exit 1
}

write_receipt() {
  local phase=$1
  local outcome=$2
  local detail=${3:-}
  PHASE="$phase" OUTCOME="$outcome" DETAIL="$detail" \
  PREVIOUS_SHA_VALUE="$PREVIOUS_SHA" CANDIDATE_SHA_VALUE="$CANDIDATE_SHA" \
  REPO_ROOT_VALUE="$REPO_ROOT" BRANCH_VALUE="$BRANCH" \
  RECEIPT_LOG_VALUE="$RECEIPT_LOG" LAST_SUCCESS_VALUE="$LAST_SUCCESS" \
  python3 - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

payload = {
    "schema": "HHS_GUARDED_UPDATE_RECEIPT_V1",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "phase": os.environ["PHASE"],
    "outcome": os.environ["OUTCOME"],
    "detail": os.environ.get("DETAIL", ""),
    "repository_root": os.environ["REPO_ROOT_VALUE"],
    "branch": os.environ["BRANCH_VALUE"],
    "previous_sha": os.environ.get("PREVIOUS_SHA_VALUE", ""),
    "candidate_sha": os.environ.get("CANDIDATE_SHA_VALUE", ""),
}
receipt_log = Path(os.environ["RECEIPT_LOG_VALUE"])
receipt_log.parent.mkdir(parents=True, exist_ok=True)
with receipt_log.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(payload, sort_keys=True) + "\n")
if payload["outcome"] == "PROMOTED":
    last_success = Path(os.environ["LAST_SUCCESS_VALUE"])
    last_success.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
}

normalize_repository() {
  local url=$1
  url=${url%.git}
  url=${url#git@github.com:}
  url=${url#https://github.com/}
  url=${url#http://github.com/}
  printf '%s\n' "$url"
}

read_units() {
  read -r -a HHS_UNITS <<<"$SYSTEMD_UNITS"
  ((${#HHS_UNITS[@]} > 0)) || fail "HHS_SYSTEMD_UNITS is empty"
}

stop_units() {
  local index
  for ((index=${#HHS_UNITS[@]}-1; index>=0; index--)); do
    log "Stopping ${HHS_UNITS[$index]}"
    systemctl stop "${HHS_UNITS[$index]}"
  done
}

start_units() {
  local unit
  for unit in "${HHS_UNITS[@]}"; do
    log "Starting $unit"
    systemctl start "$unit"
  done
}

wait_for_health() {
  local deadline=$((SECONDS + HEALTH_TIMEOUT))
  local url
  while (( SECONDS < deadline )); do
    local healthy=1
    for url in $HEALTH_URLS; do
      if ! curl --fail --silent --show-error --max-time 10 "$url" >/dev/null; then
        healthy=0
        break
      fi
    done
    if (( healthy == 1 )); then
      return 0
    fi
    sleep "$HEALTH_INTERVAL"
  done
  return 1
}

cleanup_candidate() {
  if [[ -n "$CURRENT_CANDIDATE" && -d "$CURRENT_CANDIDATE" ]]; then
    git -C "$REPO_ROOT" worktree remove --force "$CURRENT_CANDIDATE" >/dev/null 2>&1 || true
  fi
}

reconcile_host_drift() {
  local mode=$1
  local status
  status=$(git -C "$REPO_ROOT" status --porcelain=v1 --untracked-files=normal)
  [[ -n "$status" ]] || return 0
  [[ -f "$DRIFT_RECONCILER" ]] || fail "Host drift reconciler missing: $DRIFT_RECONCILER"
  log "Preserving and reconciling host drift in $mode mode"
  HHS_REPO_ROOT="$REPO_ROOT" \
  HHS_UPDATE_STATE_ROOT="$STATE_ROOT" \
  HHS_RUNTIME_OUTPUT_DIR="${HHS_RUNTIME_OUTPUT_DIR:-/var/lib/hhs/data/runtime}" \
  HHS_HOST_DRIFT_MODE="$mode" \
    bash "$DRIFT_RECONCILER" "$REPO_ROOT"
}

sync_installed_assets() {
  [[ "$SYNC_SELF" == "1" ]] || return 0
  local source="$REPO_ROOT/deployment/digitalocean/guarded_auto_update"
  local hhs_service="$REPO_ROOT/deploy/digitalocean/hhs-pass196-integrated-environment.service"
  [[ -d "$source" ]] || return 0
  log "Synchronizing guarded updater and canonical production service assets"
  install -d -m 0755 /usr/local/lib/hhs-guarded-update
  install -m 0755 "$source/hhs-guarded-update.sh" /usr/local/lib/hhs-guarded-update/hhs-guarded-update.sh
  install -m 0755 "$source/validate-candidate.sh" /usr/local/lib/hhs-guarded-update/validate-candidate.sh
  install -m 0755 "$source/build-runtime-os.sh" /usr/local/lib/hhs-guarded-update/build-runtime-os.sh
  install -m 0755 "$source/preserve-host-drift.sh" /usr/local/lib/hhs-guarded-update/preserve-host-drift.sh
  install -m 0644 "$source/hhs-guarded-update.service" /etc/systemd/system/hhs-guarded-update.service
  install -m 0644 "$source/hhs-guarded-update.timer" /etc/systemd/system/hhs-guarded-update.timer
  if [[ -f "$hhs_service" ]]; then
    install -m 0644 "$hhs_service" /etc/systemd/system/hhs.service
  fi
}

rollback_live_checkout() {
  local reason=$1
  log "Promotion failed: $reason"
  stop_units || true
  git -C "$REPO_ROOT" reset --hard "$PREVIOUS_SHA"
  if [[ -n "$ROLLBACK_COMMAND" ]]; then
    log "Rebuilding restored commit"
    (cd "$REPO_ROOT" && timeout --signal=TERM --kill-after=30s "$VALIDATE_TIMEOUT" bash -lc "$ROLLBACK_COMMAND") || true
  fi
  sync_installed_assets || true
  systemctl daemon-reload
  start_units
  if wait_for_health; then
    write_receipt "rollback" "ROLLED_BACK" "$reason"
    log "Rollback restored $PREVIOUS_SHA"
    return 0
  fi
  write_receipt "rollback" "ROLLBACK_HEALTH_FAILED" "$reason"
  fail "Rollback completed at $PREVIOUS_SHA but health verification failed"
}

on_exit() {
  local status=$?
  cleanup_candidate
  if (( status != 0 && PROMOTION_STARTED == 0 )) && [[ -n "$CANDIDATE_SHA" ]]; then
    write_receipt "candidate" "REJECTED" "candidate validation or pre-promotion guard failed"
  fi
}
trap on_exit EXIT

[[ $EUID -eq 0 ]] || fail "Run through the root-owned systemd service or as root"
command -v git >/dev/null || fail "git is required"
command -v flock >/dev/null || fail "flock is required"
command -v curl >/dev/null || fail "curl is required"
command -v python3 >/dev/null || fail "python3 is required"
command -v systemctl >/dev/null || fail "systemctl is required"
[[ -d "$REPO_ROOT/.git" ]] || fail "Repository not found at $REPO_ROOT"

install -d -m 0750 "$STATE_ROOT" "$CANDIDATE_ROOT"
install -d -m 0755 "$(dirname "$LOCK_FILE")"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  log "Another guarded update is already running"
  exit 0
fi

read_units

remote_url=$(git -C "$REPO_ROOT" remote get-url "$REMOTE")
actual_repository=$(normalize_repository "$remote_url")
[[ "$actual_repository" == "$EXPECTED_REPOSITORY" ]] || \
  fail "Remote repository mismatch: expected $EXPECTED_REPOSITORY, found $actual_repository"

# Preserve host-local source edits before restoring committed source authority.
# Runtime-generated untracked files remain in place until the service is stopped
# immediately before promotion, preventing a live process from writing to a
# deleted inode during candidate validation.
reconcile_host_drift source
if ! git -C "$REPO_ROOT" diff-index --quiet HEAD -- || ! git -C "$REPO_ROOT" diff --cached --quiet; then
  fail "Tracked live checkout drift remains after reconciliation"
fi

current_branch=$(git -C "$REPO_ROOT" branch --show-current)
[[ "$current_branch" == "$BRANCH" ]] || \
  fail "Live checkout must be on $BRANCH, found ${current_branch:-detached}"

log "Fetching $REMOTE/$BRANCH"
git -C "$REPO_ROOT" fetch --prune "$REMOTE" "$BRANCH"

PREVIOUS_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD)
CANDIDATE_SHA=$(git -C "$REPO_ROOT" rev-parse "$REMOTE/$BRANCH")

if [[ "$PREVIOUS_SHA" == "$CANDIDATE_SHA" ]]; then
  write_receipt "fetch" "NO_CHANGE" "already at remote branch tip"
  log "No new commit"
  exit 0
fi

git -C "$REPO_ROOT" merge-base --is-ancestor "$PREVIOUS_SHA" "$CANDIDATE_SHA" || \
  fail "Remote history is not a fast-forward descendant of the deployed commit"

CURRENT_CANDIDATE="$CANDIDATE_ROOT/$CANDIDATE_SHA"
git -C "$REPO_ROOT" worktree prune
rm -rf "$CURRENT_CANDIDATE"
log "Creating isolated candidate worktree $CANDIDATE_SHA"
git -C "$REPO_ROOT" worktree add --detach "$CURRENT_CANDIDATE" "$CANDIDATE_SHA"

validator="$CURRENT_CANDIDATE/$VALIDATOR_REL"
[[ -f "$validator" ]] || fail "Candidate validator missing: $VALIDATOR_REL"

log "Validating candidate $CANDIDATE_SHA"
(
  cd "$CURRENT_CANDIDATE"
  timeout --signal=TERM --kill-after=30s "$VALIDATE_TIMEOUT" bash "$validator" "$CURRENT_CANDIDATE"
)
write_receipt "validation" "VALIDATED" "candidate passed isolated validation"

if [[ "$DRY_RUN" == "1" ]]; then
  write_receipt "promotion" "DRY_RUN" "candidate validated without live promotion"
  log "Dry run complete; candidate was not promoted"
  exit 0
fi

log "Stopping live units for final host-state reconciliation"
stop_units
if ! reconcile_host_drift final; then
  log "Final host drift reconciliation failed; restoring unchanged live service"
  start_units || true
  fail "final host drift reconciliation failed"
fi
remaining=$(git -C "$REPO_ROOT" status --porcelain=v1 --untracked-files=normal)
if [[ -n "$remaining" ]]; then
  start_units || true
  fail "Live checkout remains dirty immediately before promotion"
fi

PROMOTION_STARTED=1
log "Promoting $CANDIDATE_SHA over $PREVIOUS_SHA"
if ! git -C "$REPO_ROOT" merge --ff-only "$CANDIDATE_SHA"; then
  rollback_live_checkout "fast-forward merge failed"
  exit 1
fi

if [[ -n "$POST_MERGE_COMMAND" ]]; then
  log "Running configured post-merge command"
  if ! (cd "$REPO_ROOT" && timeout --signal=TERM --kill-after=30s "$VALIDATE_TIMEOUT" bash -lc "$POST_MERGE_COMMAND"); then
    rollback_live_checkout "post-merge command failed"
    exit 1
  fi
fi

sync_installed_assets
systemctl daemon-reload
if ! start_units; then
  rollback_live_checkout "service start failed"
  exit 1
fi
if ! wait_for_health; then
  rollback_live_checkout "post-promotion health check failed"
  exit 1
fi

write_receipt "promotion" "PROMOTED" "candidate activated and health-verified"
log "Promotion complete: $CANDIDATE_SHA"

mapfile -t old_candidates < <(find "$CANDIDATE_ROOT" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' | sort -nr | awk '{print $2}' | tail -n "+$((KEEP_CANDIDATES + 1))")
for candidate in "${old_candidates[@]:-}"; do
  [[ -n "$candidate" ]] || continue
  git -C "$REPO_ROOT" worktree remove --force "$candidate" >/dev/null 2>&1 || rm -rf "$candidate"
done
