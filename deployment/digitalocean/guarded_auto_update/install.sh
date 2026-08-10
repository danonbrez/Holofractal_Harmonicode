#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

REPO_ROOT=${REPO_ROOT:-/opt/hhs/app}
SOURCE_ROOT=${SOURCE_ROOT:-$REPO_ROOT}
SOURCE="$SOURCE_ROOT/deployment/digitalocean/guarded_auto_update"
CANONICAL_HHS_SERVICE="$SOURCE_ROOT/deploy/digitalocean/hhs-pass196-integrated-environment.service"
INSTALL_ROOT=${INSTALL_ROOT:-/usr/local/lib/hhs-guarded-update}
ENV_FILE=${ENV_FILE:-/etc/hhs/guarded-update.env}
STATE_ROOT=${STATE_ROOT:-/var/lib/hhs-guarded-update}
ENABLE_PROMOTION=${HHS_INSTALL_ENABLE_PROMOTION:-0}
RUNTIME_OS_BUILD='bash bin/post_compile && bash deployment/digitalocean/guarded_auto_update/build-runtime-os.sh'

[[ $EUID -eq 0 ]] || {
  echo "Run as root on the DigitalOcean host." >&2
  exit 2
}
[[ -d "$REPO_ROOT/.git" ]] || {
  echo "Repository not found at $REPO_ROOT" >&2
  exit 3
}
[[ -d "$SOURCE" ]] || {
  echo "Guarded update source not found at $SOURCE" >&2
  exit 4
}
[[ "$ENABLE_PROMOTION" == "0" || "$ENABLE_PROMOTION" == "1" ]] || {
  echo "HHS_INSTALL_ENABLE_PROMOTION must be 0 or 1" >&2
  exit 5
}

bash -n \
  "$SOURCE/hhs-guarded-update.sh" \
  "$SOURCE/build-runtime-os.sh" \
  "$SOURCE/preserve-host-drift.sh" \
  "$SOURCE/validate-candidate.sh" \
  "$SOURCE/install.sh"

install -d -m 0755 "$INSTALL_ROOT" /etc/hhs
install -d -m 0750 "$STATE_ROOT" "$STATE_ROOT/candidates" "$STATE_ROOT/host-drift"
install -m 0755 "$SOURCE/hhs-guarded-update.sh" "$INSTALL_ROOT/hhs-guarded-update.sh"
install -m 0755 "$SOURCE/build-runtime-os.sh" "$INSTALL_ROOT/build-runtime-os.sh"
install -m 0755 "$SOURCE/preserve-host-drift.sh" "$INSTALL_ROOT/preserve-host-drift.sh"
install -m 0755 "$SOURCE/validate-candidate.sh" "$INSTALL_ROOT/validate-candidate.sh"
install -m 0644 "$SOURCE/hhs-guarded-update.service" /etc/systemd/system/hhs-guarded-update.service
install -m 0644 "$SOURCE/hhs-guarded-update.timer" /etc/systemd/system/hhs-guarded-update.timer

if [[ "$ENABLE_PROMOTION" == "1" ]]; then
  [[ -f "$CANONICAL_HHS_SERVICE" ]] || {
    echo "Canonical HHS production service missing: $CANONICAL_HHS_SERVICE" >&2
    exit 6
  }
  install -m 0644 "$CANONICAL_HHS_SERVICE" /etc/systemd/system/hhs.service
fi

if [[ ! -f "$ENV_FILE" ]]; then
  cat >"$ENV_FILE" <<EOF_ENV
HHS_REPO_ROOT=$REPO_ROOT
HHS_GIT_REMOTE=origin
HHS_GIT_BRANCH=main
HHS_EXPECTED_REPOSITORY=danonbrez/Holofractal_Harmonicode
HHS_SYSTEMD_UNITS=hhs.service
HHS_HEALTH_URLS=http://127.0.0.1:8080/api/system/status
HHS_VALIDATE_TIMEOUT_SECONDS=3600
HHS_HEALTH_TIMEOUT_SECONDS=180
HHS_VALIDATE_NATIVE=1
HHS_VALIDATE_NODE_TESTS=1
HHS_VALIDATE_BOOT=1
HHS_VALIDATE_BROWSER=0
HHS_CANDIDATE_PORT=18080
HHS_KEEP_CANDIDATES=3
HHS_POST_MERGE_COMMAND=$RUNTIME_OS_BUILD
HHS_ROLLBACK_COMMAND=$RUNTIME_OS_BUILD
HHS_UPDATE_SYNC_SELF=1
HHS_UPDATE_DRY_RUN=1
EOF_ENV
else
  # Migrate only historical repository defaults. Explicit operator-customized
  # build/rollback commands remain untouched.
  RUNTIME_OS_BUILD_VALUE="$RUNTIME_OS_BUILD" python3 - "$ENV_FILE" <<'PY'
from pathlib import Path
import os
import sys

path = Path(sys.argv[1])
replacement = os.environ["RUNTIME_OS_BUILD_VALUE"]
lines = path.read_text(encoding="utf-8").splitlines()
legacy = {
    "HHS_POST_MERGE_COMMAND=bash bin/post_compile": f"HHS_POST_MERGE_COMMAND={replacement}",
    "HHS_ROLLBACK_COMMAND=bash bin/post_compile": f"HHS_ROLLBACK_COMMAND={replacement}",
}
changed = False
result = []
for line in lines:
    new_line = legacy.get(line, line)
    changed = changed or new_line != line
    result.append(new_line)
if changed:
    path.write_text("\n".join(result) + "\n", encoding="utf-8")
PY
fi

if [[ "$ENABLE_PROMOTION" == "1" ]]; then
  if grep -q '^HHS_UPDATE_DRY_RUN=' "$ENV_FILE"; then
    sed -i 's/^HHS_UPDATE_DRY_RUN=.*/HHS_UPDATE_DRY_RUN=0/' "$ENV_FILE"
  else
    printf '%s\n' 'HHS_UPDATE_DRY_RUN=0' >>"$ENV_FILE"
  fi
fi

chown root:root "$ENV_FILE"
chmod 0640 "$ENV_FILE"

if ! git config --system --get-all safe.directory | grep -Fxq "$REPO_ROOT"; then
  git config --system --add safe.directory "$REPO_ROOT"
fi

systemctl daemon-reload
systemctl enable --now hhs-guarded-update.timer
if ! systemctl start hhs-guarded-update.service; then
  echo "HHS guarded updater failed during installation; emitting exact service diagnostics." >&2
  systemctl status hhs-guarded-update.service --no-pager --full >&2 || true
  journalctl -u hhs-guarded-update.service -n 400 --no-pager >&2 || true
  exit 7
fi

cat <<EOF_SUMMARY
Guarded continuous deployment installed.

Source root:  $SOURCE_ROOT
Repository:   $REPO_ROOT
Environment:  $ENV_FILE
Timer:        hhs-guarded-update.timer
Service:      hhs-guarded-update.service
State:        $STATE_ROOT
Drift archive:$STATE_ROOT/host-drift
Promotion:    $([[ "$ENABLE_PROMOTION" == "1" ]] && printf enabled || printf dry-run)

Inspect:
  systemctl status hhs-guarded-update.timer --no-pager
  journalctl -u hhs-guarded-update.service -n 200 --no-pager
  tail -n 20 $STATE_ROOT/receipts.jsonl

If Promotion is dry-run, validate one candidate receipt before setting HHS_UPDATE_DRY_RUN=0.
EOF_SUMMARY
