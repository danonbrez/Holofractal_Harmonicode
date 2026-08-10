#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

REPO_ROOT=${1:-${HHS_REPO_ROOT:-/opt/hhs/app}}
STATE_ROOT=${HHS_UPDATE_STATE_ROOT:-/var/lib/hhs-guarded-update}
DRIFT_ROOT=${HHS_HOST_DRIFT_ROOT:-$STATE_ROOT/host-drift}
RUNTIME_OUTPUT_ROOT=${HHS_RUNTIME_OUTPUT_DIR:-/var/lib/hhs/data/runtime}
MODE=${HHS_HOST_DRIFT_MODE:-source}

case "$MODE" in
  source|final) ;;
  *)
    echo "HHS_HOST_DRIFT_MODE must be source or final" >&2
    exit 2
    ;;
esac

[[ -d "$REPO_ROOT/.git" ]] || {
  echo "repository not found at $REPO_ROOT" >&2
  exit 3
}
command -v git >/dev/null || { echo "git is required" >&2; exit 4; }
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 5; }
command -v tar >/dev/null || { echo "tar is required" >&2; exit 6; }
command -v sha256sum >/dev/null || { echo "sha256sum is required" >&2; exit 7; }

cd "$REPO_ROOT"
git update-index -q --refresh || true
status=$(git status --porcelain=v1 --untracked-files=normal)
if [[ -z "$status" ]]; then
  printf 'HHS_HOST_DRIFT_CLEAN=1\n'
  exit 0
fi

head_sha=$(git rev-parse HEAD)
branch=$(git branch --show-current)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
archive="$DRIFT_ROOT/${stamp}-${MODE}-${head_sha:0:12}"
install -d -m 0700 "$DRIFT_ROOT" "$archive"

printf '%s\n' "$status" >"$archive/status.txt"
git diff --binary --no-ext-diff HEAD -- >"$archive/tracked.patch"
git diff --name-status HEAD -- >"$archive/tracked-name-status.txt"
git ls-files --others --exclude-standard -z >"$archive/untracked-paths.zlist"
git diff --name-only --diff-filter=ACMRTUXB -z HEAD -- >"$archive/tracked-current-paths.zlist"

if [[ -s "$archive/tracked-current-paths.zlist" ]]; then
  tar -C "$REPO_ROOT" --null --files-from="$archive/tracked-current-paths.zlist" -czf "$archive/tracked-current-files.tar.gz"
fi
if [[ -s "$archive/untracked-paths.zlist" ]]; then
  tar -C "$REPO_ROOT" --null --files-from="$archive/untracked-paths.zlist" -czf "$archive/untracked-files.tar.gz"
fi

ledger_migration="not-requested"
legacy_snapshot_rel="data/runtime/hhs_unified_hash72_ledger.json"
legacy_journal_rel="data/runtime/hhs_unified_hash72_ledger.json.journal.jsonl"
legacy_snapshot="$REPO_ROOT/$legacy_snapshot_rel"
legacy_journal="$REPO_ROOT/$legacy_journal_rel"
target_snapshot="$RUNTIME_OUTPUT_ROOT/hhs_unified_hash72_ledger.json"
target_journal="$RUNTIME_OUTPUT_ROOT/hhs_unified_hash72_ledger.json.journal.jsonl"

if [[ "$MODE" == "final" && -f "$legacy_journal" ]]; then
  install -d -m 0750 "$RUNTIME_OUTPUT_ROOT"
  committed_snapshot="$archive/committed-hhs-unified-hash72-ledger.json"
  if git cat-file -e "HEAD:$legacy_snapshot_rel" 2>/dev/null; then
    git show "HEAD:$legacy_snapshot_rel" >"$committed_snapshot"
  fi

  if [[ ! -e "$target_snapshot" && ! -e "$target_journal" && -s "$committed_snapshot" ]]; then
    install -m 0640 "$committed_snapshot" "$target_snapshot"
    install -m 0640 "$legacy_journal" "$target_journal"
    ledger_migration="committed-snapshot-and-repository-journal-migrated"
  elif [[ -e "$target_snapshot" && ! -e "$target_journal" && -s "$committed_snapshot" ]] \
      && cmp -s "$committed_snapshot" "$target_snapshot"; then
    install -m 0640 "$legacy_journal" "$target_journal"
    ledger_migration="repository-journal-migrated-onto-matching-external-snapshot"
  else
    ledger_migration="repository-journal-archived-only-external-ledger-already-initialized-or-diverged"
  fi

  if id -u hhs >/dev/null 2>&1; then
    [[ -e "$target_snapshot" ]] && chown hhs:hhs "$target_snapshot"
    [[ -e "$target_journal" ]] && chown hhs:hhs "$target_journal"
    chown hhs:hhs "$RUNTIME_OUTPUT_ROOT" || true
  fi
fi

# Host-local source edits are not deployment authority. Preserve their exact
# patch/current bytes above, then restore the checkout to its committed HEAD.
git reset --hard HEAD >/dev/null

if [[ "$MODE" == "final" && -s "$archive/untracked-paths.zlist" ]]; then
  while IFS= read -r -d '' relative; do
    [[ -n "$relative" ]] || continue
    case "$relative" in
      /*|../*|*/../*)
        echo "unsafe untracked path from git: $relative" >&2
        exit 8
        ;;
    esac
    rm -rf -- "$REPO_ROOT/$relative"
  done <"$archive/untracked-paths.zlist"
fi

if [[ "$MODE" == "source" ]]; then
  git update-index -q --refresh || true
  if ! git diff-index --quiet HEAD -- || ! git diff --cached --quiet; then
    echo "tracked host drift remains after source reconciliation" >&2
    exit 9
  fi
else
  remaining=$(git status --porcelain=v1 --untracked-files=normal)
  if [[ -n "$remaining" ]]; then
    echo "live checkout remains dirty after final reconciliation" >&2
    printf '%s\n' "$remaining" >&2
    exit 10
  fi
fi

ARCHIVE_VALUE="$archive" \
MODE_VALUE="$MODE" \
HEAD_VALUE="$head_sha" \
BRANCH_VALUE="$branch" \
LEDGER_MIGRATION_VALUE="$ledger_migration" \
python3 - <<'PY'
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

archive = Path(os.environ["ARCHIVE_VALUE"])
status_lines = (archive / "status.txt").read_text(encoding="utf-8").splitlines()
files = {}
for path in sorted(archive.iterdir()):
    if path.is_file() and path.name not in {"manifest.json", "SHA256SUMS"}:
        files[path.name] = {
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
payload = {
    "schema": "HHS_DIGITALOCEAN_HOST_DRIFT_ARCHIVE_V1",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "mode": os.environ["MODE_VALUE"],
    "repository_head": os.environ["HEAD_VALUE"],
    "branch": os.environ.get("BRANCH_VALUE", ""),
    "status": status_lines,
    "ledger_migration": os.environ["LEDGER_MIGRATION_VALUE"],
    "files": files,
    "authoritative_source": "GITHUB_COMMITTED_HEAD",
    "host_edits_preserved_before_reset": True,
}
(archive / "manifest.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

(
  cd "$archive"
  find . -maxdepth 1 -type f ! -name SHA256SUMS -print0 \
    | sort -z \
    | xargs -0 sha256sum >SHA256SUMS
)
archive_digest=$(sha256sum "$archive/manifest.json" | awk '{print $1}')
printf 'HHS_HOST_DRIFT_ARCHIVE=%s\n' "$archive"
printf 'HHS_HOST_DRIFT_MANIFEST_SHA256=%s\n' "$archive_digest"
printf 'HHS_HOST_DRIFT_MODE=%s\n' "$MODE"
printf 'HHS_HOST_DRIFT_LEDGER_MIGRATION=%s\n' "$ledger_migration"
