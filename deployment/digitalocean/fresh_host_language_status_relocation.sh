#!/usr/bin/env bash
set -Eeuo pipefail
umask 022

TARGET_SHA=${TARGET_SHA:?missing TARGET_SHA}
APP_ROOT=${HHS_APP_ROOT:-/opt/hhs/app}
SOURCE_ROOT="$APP_ROOT/.hhs"
SOURCE_STATUS="$SOURCE_ROOT/production_language_assets_status.json"
STATE_ROOT=${HHS_LANGUAGE_ASSET_STATE_ROOT:-/var/lib/hhs/language-assets}
STATE_STATUS="$STATE_ROOT/production_language_assets_status.json"

[[ $EUID -eq 0 ]] || {
  echo 'language-status relocation requires root authority' >&2
  exit 2
}
[[ "$TARGET_SHA" =~ ^[0-9a-fA-F]{40}$ ]] || {
  echo "TARGET_SHA is not exact: $TARGET_SHA" >&2
  exit 3
}
[[ -d "$APP_ROOT/.git" ]] || {
  echo "production repository missing: $APP_ROOT" >&2
  exit 4
}
[[ "$(git -C "$APP_ROOT" rev-parse HEAD)" == "$TARGET_SHA" ]] || {
  echo 'production HEAD mismatch' >&2
  exit 5
}
[[ "$(git -C "$APP_ROOT" rev-parse origin/main)" == "$TARGET_SHA" ]] || {
  echo 'production origin/main mismatch' >&2
  exit 6
}
[[ "$(git -C "$APP_ROOT" branch --show-current)" == main ]] || {
  echo 'production checkout is not on main' >&2
  exit 7
}

pre_status=$(git -C "$APP_ROOT" status --porcelain=v1 --untracked-files=normal)
[[ "$pre_status" == '?? .hhs/' ]] || {
  echo 'unexpected production pre-state; refusing scoped relocation' >&2
  printf '%s\n' "$pre_status" >&2
  exit 8
}
[[ -d "$SOURCE_ROOT" && ! -L "$SOURCE_ROOT" ]] || {
  echo 'expected .hhs directory is absent or is a symlink' >&2
  exit 9
}
[[ -f "$SOURCE_STATUS" && ! -L "$SOURCE_STATUS" ]] || {
  echo 'expected production language status is absent or is a symlink' >&2
  exit 10
}

mapfile -t source_entries < <(find "$SOURCE_ROOT" -mindepth 1 -maxdepth 1 -printf '%f\n' | LC_ALL=C sort)
[[ ${#source_entries[@]} -eq 1 && "${source_entries[0]}" == 'production_language_assets_status.json' ]] || {
  echo 'unexpected .hhs content; refusing scoped relocation' >&2
  printf 'entry=%s\n' "${source_entries[@]}" >&2
  exit 11
}

python3 - "$SOURCE_STATUS" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding='utf-8'))
if payload.get('schema') != 'HHS_PRODUCTION_LANGUAGE_ASSET_INSTALLATION_STATUS_V1':
    raise SystemExit('unexpected production language status schema')
print('HHS_LANGUAGE_STATUS_SOURCE_SCHEMA_VERIFIED=1')
print('HHS_LANGUAGE_STATUS_SOURCE_ASSISTANT_READY=' + str(bool(payload.get('assistant_ready'))).lower())
PY

source_sha=$(sha256sum "$SOURCE_STATUS" | awk '{print $1}')
source_size=$(stat -c '%s' "$SOURCE_STATUS")
install -d -o root -g hhs -m 0750 "$STATE_ROOT"
install -o root -g hhs -m 0640 "$SOURCE_STATUS" "$STATE_STATUS"
state_sha=$(sha256sum "$STATE_STATUS" | awk '{print $1}')
state_size=$(stat -c '%s' "$STATE_STATUS")
[[ "$source_sha" == "$state_sha" ]] || {
  echo 'language-status relocation hash mismatch; source preserved' >&2
  exit 12
}
[[ "$source_size" == "$state_size" ]] || {
  echo 'language-status relocation size mismatch; source preserved' >&2
  exit 13
}

python3 - "$STATE_STATUS" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
if payload.get('schema') != 'HHS_PRODUCTION_LANGUAGE_ASSET_INSTALLATION_STATUS_V1':
    raise SystemExit('relocated production language status schema mismatch')
print('HHS_LANGUAGE_STATUS_RELOCATED_SCHEMA_VERIFIED=1')
PY

# Recheck the exact source boundary immediately before removing only the proven copy.
mapfile -t source_entries < <(find "$SOURCE_ROOT" -mindepth 1 -maxdepth 1 -printf '%f\n' | LC_ALL=C sort)
[[ ${#source_entries[@]} -eq 1 && "${source_entries[0]}" == 'production_language_assets_status.json' ]]
[[ "$(sha256sum "$SOURCE_STATUS" | awk '{print $1}')" == "$state_sha" ]]
rm -f -- "$SOURCE_STATUS"
rmdir -- "$SOURCE_ROOT"

post_status=$(git -C "$APP_ROOT" status --porcelain=v1 --untracked-files=normal)
[[ -z "$post_status" ]] || {
  echo 'production worktree remains dirty after scoped relocation' >&2
  printf '%s\n' "$post_status" >&2
  exit 14
}

systemctl is-active --quiet hhs.service
systemctl is-active --quiet hhs-guarded-update.timer
systemctl is-active --quiet nginx
systemctl is-active --quiet hhs-certbot-renew.timer
curl -fsS --connect-timeout 5 --max-time 15 http://127.0.0.1:8080/api/system/status >/dev/null

python3 - "$TARGET_SHA" <<'PY'
import json
import sys
from pathlib import Path

target = sys.argv[1]
receipt = json.loads(Path('/var/lib/hhs-guarded-update/initialization.json').read_text(encoding='utf-8'))
assert receipt['schema'] == 'HHS_FRESH_PRODUCTION_INITIALIZATION_RECEIPT_V1'
assert receipt['outcome'] == 'INITIALIZED'
assert receipt['repository_sha'] == target
assert receipt['rollback_receipt_fabricated'] is False
assert receipt['language_status_schema'] == 'HHS_PRODUCTION_LANGUAGE_ASSET_INSTALLATION_STATUS_V1'
print('HHS_LANGUAGE_STATUS_INITIALIZATION_RECEIPT_PRESERVED=1')
PY

printf 'HHS_LANGUAGE_STATUS_RELOCATION_VERIFIED=1\n'
printf 'HHS_LANGUAGE_STATUS_SOURCE_SHA256=%s\n' "$source_sha"
printf 'HHS_LANGUAGE_STATUS_STATE_SHA256=%s\n' "$state_sha"
printf 'HHS_LANGUAGE_STATUS_STATE_PATH=%s\n' "$STATE_STATUS"
printf 'HHS_LANGUAGE_STATUS_PRODUCTION_WORKTREE_CLEAN=1\n'
