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
RECOVERY_MODE=${HHS_INSTALL_RECOVERY_MODE:-0}
BUNDLE_SHA=${HHS_RUNTIME_OS_BUNDLE_SHA:-}
BUNDLE_ROOT=${HHS_RUNTIME_OS_BUNDLE_ROOT:-/var/lib/hhs/runtime-os}
OWNERSHIP_TIMEOUT=${HHS_UPDATE_OWNERSHIP_TIMEOUT_SECONDS:-900}
PRODUCTION_HEALTH_TIMEOUT=${HHS_PRODUCTION_HEALTH_TIMEOUT_SECONDS:-600}
NATIVE_BUILD='make c-abi && test -s hhs_runtime/builds/libhhs_runtime.so && /opt/hhs/venv/bin/python tools/install_production_language_assets.py --install-if-configured --require-assistant'
LEGACY_RUNTIME_OS_BUILD='bash bin/post_compile && bash deployment/digitalocean/guarded_auto_update/build-runtime-os.sh'

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
[[ "$RECOVERY_MODE" == "0" || "$RECOVERY_MODE" == "1" ]] || {
  echo "HHS_INSTALL_RECOVERY_MODE must be 0 or 1" >&2
  exit 5
}
if [[ "$ENABLE_PROMOTION" == "1" ]]; then
  [[ "$BUNDLE_SHA" =~ ^[0-9a-fA-F]{40}$ ]] || {
    echo "promotion requires exact HHS_RUNTIME_OS_BUNDLE_SHA" >&2
    exit 6
  }
fi

bash -n \
  "$SOURCE/hhs-guarded-update.sh" \
  "$SOURCE/build-runtime-os.sh" \
  "$SOURCE/preserve-host-drift.sh" \
  "$SOURCE/validate-candidate.sh" \
  "$SOURCE/install.sh"
python3 -m py_compile "$SOURCE/runtime-os-bundle.py"

# The periodic timer is a follower, never a concurrent deployment owner.
# Stop it before changing updater assets or environment. If a timer-launched
# oneshot is already running, let that guarded transaction reach its own
# terminal state instead of SIGTERMing it during a possible final promotion.
systemctl stop hhs-guarded-update.timer 2>/dev/null || true
deadline=$((SECONDS + OWNERSHIP_TIMEOUT))
while :; do
  updater_state=$(systemctl show hhs-guarded-update.service -p ActiveState --value 2>/dev/null || printf 'inactive')
  case "$updater_state" in
    inactive|failed|unknown|"") break ;;
  esac
  if (( SECONDS >= deadline )); then
    echo "Timed out waiting for the existing guarded updater owner to finish (state=$updater_state)." >&2
    systemctl status hhs-guarded-update.service --no-pager --full >&2 || true
    journalctl -u hhs-guarded-update.service -n 400 --no-pager >&2 || true
    exit 7
  fi
  sleep 2
done
systemctl reset-failed hhs-guarded-update.service 2>/dev/null || true

# Exact-main takeover normally requires the live service to remain online.
# Recovery is deliberately narrower: it is allowed only after the immediately
# preceding guarded transaction recorded ROLLBACK_HEALTH_FAILED and only when
# no process is already listening on the production port.
if [[ "$ENABLE_PROMOTION" == "1" ]] && ! systemctl is-active --quiet hhs.service; then
  if [[ "$RECOVERY_MODE" != "1" ]]; then
    echo "hhs.service is not active after prior guarded updater ownership ended; refusing a second promotion." >&2
    systemctl status hhs.service --no-pager --full >&2 || true
    journalctl -u hhs.service -n 250 --no-pager >&2 || true
    exit 8
  fi
  if ss -H -ltn 'sport = :8080' | grep -q .; then
    echo "Recovery mode refused because another listener already owns port 8080." >&2
    ss -H -ltnp 'sport = :8080' >&2 || true
    exit 8
  fi
  RECEIPT_LOG_VALUE="$STATE_ROOT/receipts.jsonl" python3 - <<'PY'
import json
import os
from pathlib import Path
path = Path(os.environ["RECEIPT_LOG_VALUE"])
if not path.is_file():
    raise SystemExit("Recovery mode requires an existing guarded-update receipt log")
records = []
for line in path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        records.append(json.loads(line))
    except json.JSONDecodeError:
        continue
if not records or records[-1].get("outcome") != "ROLLBACK_HEALTH_FAILED":
    raise SystemExit(f"Recovery mode requires terminal ROLLBACK_HEALTH_FAILED receipt, found {records[-1] if records else None}")
print("HHS_GUARDED_UPDATE_RECOVERY_RECEIPT_VERIFIED=1")
PY
  echo "HHS_GUARDED_UPDATE_RECOVERY_MODE=1"
fi

install -d -m 0755 "$INSTALL_ROOT" /etc/hhs "$BUNDLE_ROOT" "$BUNDLE_ROOT/incoming" "$BUNDLE_ROOT/releases"
install -d -m 0750 "$STATE_ROOT" "$STATE_ROOT/candidates" "$STATE_ROOT/host-drift"
install -m 0755 "$SOURCE/hhs-guarded-update.sh" "$INSTALL_ROOT/hhs-guarded-update.sh"
install -m 0755 "$SOURCE/build-runtime-os.sh" "$INSTALL_ROOT/build-runtime-os.sh"
install -m 0755 "$SOURCE/preserve-host-drift.sh" "$INSTALL_ROOT/preserve-host-drift.sh"
install -m 0755 "$SOURCE/validate-candidate.sh" "$INSTALL_ROOT/validate-candidate.sh"
install -m 0755 "$SOURCE/runtime-os-bundle.py" "$INSTALL_ROOT/runtime-os-bundle.py"
install -m 0644 "$SOURCE/hhs-guarded-update.service" /etc/systemd/system/hhs-guarded-update.service
install -m 0644 "$SOURCE/hhs-guarded-update.timer" /etc/systemd/system/hhs-guarded-update.timer

if [[ "$ENABLE_PROMOTION" == "1" ]]; then
  [[ -f "$CANONICAL_HHS_SERVICE" ]] || {
    echo "Canonical HHS production service missing: $CANONICAL_HHS_SERVICE" >&2
    exit 9
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
HHS_HEALTH_TIMEOUT_SECONDS=$PRODUCTION_HEALTH_TIMEOUT
HHS_VALIDATE_NATIVE=1
HHS_VALIDATE_NODE_TESTS=1
HHS_VALIDATE_BOOT=1
HHS_VALIDATE_BROWSER=0
HHS_CANDIDATE_PORT=18080
HHS_KEEP_CANDIDATES=3
HHS_RUNTIME_OS_BUNDLE_MODE=prebuilt
HHS_RUNTIME_OS_BUNDLE_ROOT=$BUNDLE_ROOT
HHS_RUNTIME_OS_BUNDLE_TOOL=$INSTALL_ROOT/runtime-os-bundle.py
HHS_RUNTIME_OS_BUNDLE_SHA=$BUNDLE_SHA
HHS_POST_MERGE_COMMAND=$NATIVE_BUILD
HHS_ROLLBACK_COMMAND=$NATIVE_BUILD
HHS_UPDATE_SYNC_SELF=1
HHS_UPDATE_DRY_RUN=1
EOF_ENV
else
  ENV_FILE_VALUE="$ENV_FILE" \
  BUNDLE_SHA_VALUE="$BUNDLE_SHA" \
  BUNDLE_ROOT_VALUE="$BUNDLE_ROOT" \
  BUNDLE_TOOL_VALUE="$INSTALL_ROOT/runtime-os-bundle.py" \
  NATIVE_BUILD_VALUE="$NATIVE_BUILD" \
  LEGACY_RUNTIME_OS_BUILD_VALUE="$LEGACY_RUNTIME_OS_BUILD" \
  ENABLE_PROMOTION_VALUE="$ENABLE_PROMOTION" \
  PRODUCTION_HEALTH_TIMEOUT_VALUE="$PRODUCTION_HEALTH_TIMEOUT" \
  python3 - <<'PY'
from pathlib import Path
import os

path = Path(os.environ["ENV_FILE_VALUE"])
lines = path.read_text(encoding="utf-8").splitlines()
native = os.environ["NATIVE_BUILD_VALUE"]
legacy_combined = os.environ["LEGACY_RUNTIME_OS_BUILD_VALUE"]
bundle_sha = os.environ["BUNDLE_SHA_VALUE"]
bundle_root = os.environ["BUNDLE_ROOT_VALUE"]
bundle_tool = os.environ["BUNDLE_TOOL_VALUE"]
promotion = os.environ["ENABLE_PROMOTION_VALUE"] == "1"
health_timeout = str(max(600, int(os.environ["PRODUCTION_HEALTH_TIMEOUT_VALUE"])))

values = {}
order = []
for line in lines:
    if not line or line.lstrip().startswith("#") or "=" not in line:
        order.append((None, line))
        continue
    key, value = line.split("=", 1)
    if key in {"HHS_POST_MERGE_COMMAND", "HHS_ROLLBACK_COMMAND"} and value in {"bash bin/post_compile", legacy_combined}:
        value = native
    values[key] = value
    order.append((key, None))

if promotion:
    values["HHS_RUNTIME_OS_BUNDLE_MODE"] = "prebuilt"
    values["HHS_RUNTIME_OS_BUNDLE_ROOT"] = bundle_root
    values["HHS_RUNTIME_OS_BUNDLE_TOOL"] = bundle_tool
    values["HHS_RUNTIME_OS_BUNDLE_SHA"] = bundle_sha
    values["HHS_HEALTH_TIMEOUT_SECONDS"] = health_timeout
    values["HHS_POST_MERGE_COMMAND"] = native
    values["HHS_ROLLBACK_COMMAND"] = native

emitted = set()
result = []
for key, literal in order:
    if key is None:
        result.append(literal)
        continue
    if key in emitted:
        continue
    result.append(f"{key}={values[key]}")
    emitted.add(key)
for key in (
    "HHS_HEALTH_TIMEOUT_SECONDS",
    "HHS_RUNTIME_OS_BUNDLE_MODE",
    "HHS_RUNTIME_OS_BUNDLE_ROOT",
    "HHS_RUNTIME_OS_BUNDLE_TOOL",
    "HHS_RUNTIME_OS_BUNDLE_SHA",
    "HHS_POST_MERGE_COMMAND",
    "HHS_ROLLBACK_COMMAND",
):
    if key in values and key not in emitted:
        result.append(f"{key}={values[key]}")
        emitted.add(key)
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
systemctl reset-failed hhs-guarded-update.service 2>/dev/null || true

# Run exactly one synchronous updater while the timer is stopped. Type=oneshot
# makes systemctl start return only after validation/promotion/rollback reaches
# a terminal result. The periodic follower is re-enabled only after success.
if ! systemctl start hhs-guarded-update.service; then
  echo "HHS guarded updater failed during exclusive installation/promotion; timer remains stopped." >&2
  systemctl status hhs-guarded-update.service --no-pager --full >&2 || true
  journalctl -u hhs-guarded-update.service -n 400 --no-pager >&2 || true
  echo "=== HHS PRODUCTION SERVICE DIAGNOSTICS ===" >&2
  systemctl status hhs.service --no-pager --full >&2 || true
  systemctl show hhs.service -p ActiveState -p SubState -p MainPID -p ExecStart -p WorkingDirectory -p Environment --no-pager >&2 || true
  ss -ltnp | grep ':8080' >&2 || true
  journalctl -u hhs.service -n 400 --no-pager >&2 || true
  exit 10
fi

systemctl enable hhs-guarded-update.timer >/dev/null
systemctl start hhs-guarded-update.timer
systemctl is-active --quiet hhs-guarded-update.timer || {
  echo "Guarded updater promotion succeeded but periodic follower timer did not activate." >&2
  exit 11
}

cat <<EOF_SUMMARY
Guarded continuous deployment installed.

Source root:  $SOURCE_ROOT
Repository:   $REPO_ROOT
Environment:  $ENV_FILE
Timer:        hhs-guarded-update.timer
Service:      hhs-guarded-update.service
State:        $STATE_ROOT
Drift archive:$STATE_ROOT/host-drift
Bundle root:  $BUNDLE_ROOT
Bundle SHA:   ${BUNDLE_SHA:-not-pinned}
Promotion:    $([[ "$ENABLE_PROMOTION" == "1" ]] && printf enabled || printf dry-run)
Recovery:     $([[ "$RECOVERY_MODE" == "1" ]] && printf enabled || printf normal)
Ownership:    exclusive synchronous service; timer resumed after success

Inspect:
  systemctl status hhs-guarded-update.timer --no-pager
  journalctl -u hhs-guarded-update.service -n 200 --no-pager
  tail -n 20 $STATE_ROOT/receipts.jsonl
EOF_SUMMARY
