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
PRODUCTION_SERVICE_USER=${HHS_PRODUCTION_SERVICE_USER:-hhs}
PRODUCTION_SERVICE_GROUP=${HHS_PRODUCTION_SERVICE_GROUP:-hhs}
VALIDATE_PYTHON=${HHS_VALIDATE_PYTHON:-/opt/hhs/venv/bin/python}
PERMISSION_TOOL=${HHS_PRODUCTION_PERMISSION_TOOL:-$SOURCE/normalize-service-permissions.py}
RECOVERY_VERIFIER=${HHS_PRODUCTION_RECOVERY_VERIFIER:-$SOURCE/verify-recovery-state.py}
WARM_BOOT_TOOL=${HHS_WARM_BOOT_TOOL:-$SOURCE_ROOT/deployment/digitalocean/warm_boot_manifest.py}
WARM_BOOT_SERVICE_DROPIN=${HHS_WARM_BOOT_SERVICE_DROPIN:-$SOURCE_ROOT/deploy/digitalocean/hhs-warm-boot-identity.conf}
INSTALLED_WARM_BOOT_TOOL=$INSTALL_ROOT/warm_boot_manifest.py
WARM_BOOT_ROOT=${HHS_WARM_BOOT_MANIFEST_ROOT:-/var/lib/hhs/warm-boot/releases}
WARM_BOOT_REPOSITORY_SHA_FILE=${HHS_WARM_BOOT_REPOSITORY_SHA_FILE:-/var/lib/hhs/warm-boot/current-repository-sha}
STATIC_FIRST_CONFIGURATOR=${HHS_RUNTIME_OS_STATIC_FIRST_CONFIGURATOR:-$SOURCE_ROOT/deployment/digitalocean/configure_runtime_os_static_first.py}
LANE5_INGRESS_SERVICE=${HHS_LANE5_INGRESS_SERVICE:-$SOURCE_ROOT/deploy/digitalocean/hhs-lane5-ingress.service}
LANE5_INGRESS_SOCKET=${HHS_LANE5_INGRESS_SOCKET:-$SOURCE_ROOT/deploy/digitalocean/hhs-lane5-ingress.socket}
LANE5_INGRESS_CONFIGURATOR=${HHS_LANE5_INGRESS_CONFIGURATOR:-$SOURCE_ROOT/deployment/digitalocean/configure_lane5_ingress_nginx.py}
LANE5_INGRESS_HEALTH_URL=${HHS_LANE5_INGRESS_HEALTH_URL:-http://127.0.0.1:8715/__hhs_lane5_ingress_health}
NATIVE_BUILD='make c-abi && test -s hhs_runtime/builds/libhhs_runtime.so && HHS_NATIVE_CAUSAL_LM_AUTO_PROVISION=1 HHS_NATIVE_CAUSAL_LM_REQUIRED=1 /opt/hhs/venv/bin/python tools/install_production_language_assets.py --install-if-configured --require-assistant'
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
  [[ -x "$VALIDATE_PYTHON" ]] || {
    echo "production validation interpreter is not executable: $VALIDATE_PYTHON" >&2
    exit 6
  }
  "$VALIDATE_PYTHON" -c 'import pytest' || {
    echo "production validation interpreter cannot import pytest: $VALIDATE_PYTHON" >&2
    exit 6
  }
  echo "HHS_PRODUCTION_VALIDATE_PYTHON_VERIFIED=$VALIDATE_PYTHON"
fi

bash -n \
  "$SOURCE/hhs-guarded-update.sh" \
  "$SOURCE/build-runtime-os.sh" \
  "$SOURCE/preserve-host-drift.sh" \
  "$SOURCE/validate-candidate.sh" \
  "$SOURCE/install.sh"
python3 -m py_compile \
  "$SOURCE/runtime-os-bundle.py" \
  "$SOURCE/normalize-service-permissions.py" \
  "$RECOVERY_VERIFIER" \
  "$WARM_BOOT_TOOL" \
  "$LANE5_INGRESS_CONFIGURATOR" \
  "$SOURCE_ROOT/hhs_backend/lane5_ingress_gateway.py"

normalize_production_checkout() {
  python3 "$PERMISSION_TOOL" \
    --repo-root "$REPO_ROOT" \
    --service-user "$PRODUCTION_SERVICE_USER" \
    --service-group "$PRODUCTION_SERVICE_GROUP"
}

prepare_recovery_warm_boot_service() {
  local repository_sha=$1
  [[ "$repository_sha" =~ ^[0-9a-fA-F]{40}$ ]] || {
    echo "Recovery warm-boot identity is not an exact SHA: $repository_sha" >&2
    exit 8
  }
  [[ -f "$WARM_BOOT_TOOL" ]] || {
    echo "Warm-boot verifier missing from deployment source: $WARM_BOOT_TOOL" >&2
    exit 8
  }
  [[ -f "$WARM_BOOT_SERVICE_DROPIN" ]] || {
    echo "Warm-boot service drop-in missing from deployment source: $WARM_BOOT_SERVICE_DROPIN" >&2
    exit 8
  }
  [[ -f "$WARM_BOOT_ROOT/$repository_sha.json" ]] || {
    echo "Authorized rollback warm-boot manifest missing: $WARM_BOOT_ROOT/$repository_sha.json" >&2
    exit 8
  }

  install -d -m 0755 "$INSTALL_ROOT"
  install -d -o "$PRODUCTION_SERVICE_USER" -g "$PRODUCTION_SERVICE_GROUP" -m 0750 \
    "$(dirname "$WARM_BOOT_REPOSITORY_SHA_FILE")" "$WARM_BOOT_ROOT"
  install -m 0755 "$WARM_BOOT_TOOL" "$INSTALLED_WARM_BOOT_TOOL"
  install -d -m 0755 /etc/systemd/system/hhs.service.d
  install -m 0644 "$WARM_BOOT_SERVICE_DROPIN" /etc/systemd/system/hhs.service.d/20-hhs-warm-boot-identity.conf

  local temporary
  temporary=$(mktemp "$(dirname "$WARM_BOOT_REPOSITORY_SHA_FILE")/.current-repository-sha.XXXXXX")
  printf '%s\n' "$repository_sha" >"$temporary"
  chown "$PRODUCTION_SERVICE_USER:$PRODUCTION_SERVICE_GROUP" "$temporary"
  chmod 0640 "$temporary"
  mv -f "$temporary" "$WARM_BOOT_REPOSITORY_SHA_FILE"
  systemctl daemon-reload
  printf 'HHS_RECOVERY_WARM_BOOT_REPOSITORY_IDENTITY_BOUND=%s\n' "$repository_sha"
}

wait_for_production_health() {
  local deadline=$((SECONDS + PRODUCTION_HEALTH_TIMEOUT))
  while (( SECONDS < deadline )); do
    if curl -fsS --max-time 10 http://127.0.0.1:8080/api/system/status >/dev/null; then
      return 0
    fi
    sleep 2
  done
  return 1
}

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

# Permission repair is an independent pre-start invariant. It must run even
# when the native/language build later fails so rollback remains bootable.
normalize_production_checkout

# Exact-main takeover normally requires the live service to remain online.
# Recovery remains fail-closed. The shared verifier admits either a terminal
# rollback-health failure or a validated pre-promotion interruption only when
# the live checkout is still the proven rollback boundary and no other process
# owns the production port.
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
  [[ -f "$RECOVERY_VERIFIER" ]] || {
    echo "Recovery verifier missing: $RECOVERY_VERIFIER" >&2
    exit 8
  }
  current_head=$(git -C "$REPO_ROOT" rev-parse HEAD)
  recovery_report=$(python3 "$RECOVERY_VERIFIER" \
    --receipt-log "$STATE_ROOT/receipts.jsonl" \
    --current-head "$current_head" \
    --repository-root "$REPO_ROOT" \
    --branch main \
    --warm-boot-verifier "$SOURCE_ROOT/deployment/digitalocean/warm_boot_manifest.py" \
    --warm-boot-manifest-root /var/lib/hhs/warm-boot/releases)
  printf '%s\n' "$recovery_report"
  echo "HHS_GUARDED_UPDATE_RECOVERY_RECEIPT_VERIFIED=1"
  echo "HHS_GUARDED_UPDATE_RECOVERY_MODE=1"
  prepare_recovery_warm_boot_service "$current_head"
  systemctl reset-failed hhs.service 2>/dev/null || true
  systemctl start hhs.service
  if ! wait_for_production_health; then
    echo "Rollback boundary service failed health after permission normalization; refusing a new promotion." >&2
    systemctl status hhs.service --no-pager --full >&2 || true
    journalctl -u hhs.service -n 300 --no-pager >&2 || true
    exit 8
  fi
  echo "HHS_ROLLBACK_BOUNDARY_HEALTHY=1"
elif [[ "$ENABLE_PROMOTION" == "1" ]]; then
  if ! wait_for_production_health; then
    echo "Existing production service is active but unhealthy; refusing promotion." >&2
    exit 8
  fi
  echo "HHS_PREPROMOTION_SERVICE_HEALTHY=1"
fi

install -d -m 0755 "$INSTALL_ROOT" /etc/hhs "$BUNDLE_ROOT" "$BUNDLE_ROOT/incoming" "$BUNDLE_ROOT/releases"
install -d -m 0750 "$STATE_ROOT" "$STATE_ROOT/candidates" "$STATE_ROOT/host-drift"
install -m 0755 "$SOURCE/hhs-guarded-update.sh" "$INSTALL_ROOT/hhs-guarded-update.sh"
install -m 0755 "$SOURCE/build-runtime-os.sh" "$INSTALL_ROOT/build-runtime-os.sh"
install -m 0755 "$SOURCE/preserve-host-drift.sh" "$INSTALL_ROOT/preserve-host-drift.sh"
install -m 0755 "$SOURCE/validate-candidate.sh" "$INSTALL_ROOT/validate-candidate.sh"
install -m 0755 "$SOURCE/runtime-os-bundle.py" "$INSTALL_ROOT/runtime-os-bundle.py"
install -m 0755 "$SOURCE/normalize-service-permissions.py" "$INSTALL_ROOT/normalize-service-permissions.py"
install -m 0755 "$RECOVERY_VERIFIER" "$INSTALL_ROOT/verify-recovery-state.py"
install -m 0755 "$WARM_BOOT_TOOL" "$INSTALLED_WARM_BOOT_TOOL"
install -d -m 0755 /etc/systemd/system/hhs.service.d
install -m 0644 "$WARM_BOOT_SERVICE_DROPIN" /etc/systemd/system/hhs.service.d/20-hhs-warm-boot-identity.conf
install -m 0644 "$SOURCE/hhs-guarded-update.service" /etc/systemd/system/hhs-guarded-update.service
install -m 0644 "$SOURCE/hhs-guarded-update.timer" /etc/systemd/system/hhs-guarded-update.timer

if [[ "$ENABLE_PROMOTION" == "1" ]]; then
  [[ -f "$CANONICAL_HHS_SERVICE" ]] || {
    echo "Canonical HHS production service missing: $CANONICAL_HHS_SERVICE" >&2
    exit 9
  }
  [[ -f "$LANE5_INGRESS_SERVICE" ]] || {
    echo "Lane 5 host ingress service missing: $LANE5_INGRESS_SERVICE" >&2
    exit 9
  }
  [[ -f "$LANE5_INGRESS_SOCKET" ]] || {
    echo "Lane 5 host ingress socket missing: $LANE5_INGRESS_SOCKET" >&2
    exit 9
  }
  [[ -f "$LANE5_INGRESS_CONFIGURATOR" ]] || {
    echo "Lane 5 nginx ingress configurator missing: $LANE5_INGRESS_CONFIGURATOR" >&2
    exit 9
  }
  install -m 0644 "$CANONICAL_HHS_SERVICE" /etc/systemd/system/hhs.service
  install -m 0644 "$LANE5_INGRESS_SERVICE" /etc/systemd/system/hhs-lane5-ingress.service
  install -m 0644 "$LANE5_INGRESS_SOCKET" /etc/systemd/system/hhs-lane5-ingress.socket
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
HHS_VALIDATE_PYTHON=$VALIDATE_PYTHON
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
  VALIDATE_PYTHON_VALUE="$VALIDATE_PYTHON" \
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
validate_python = os.environ["VALIDATE_PYTHON_VALUE"]
minimum_validate_timeout = 3600

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

values["HHS_VALIDATE_PYTHON"] = validate_python

if promotion:
    try:
        current_validate_timeout = int(values.get("HHS_VALIDATE_TIMEOUT_SECONDS", "0"))
    except ValueError:
        current_validate_timeout = 0
    values["HHS_VALIDATE_TIMEOUT_SECONDS"] = str(
        max(minimum_validate_timeout, current_validate_timeout)
    )
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
    "HHS_VALIDATE_PYTHON",
    "HHS_VALIDATE_TIMEOUT_SECONDS",
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

# Exact-main promotion seals the Runtime OS bundle before the host transaction.
# Pin that already-authorized commit only for this synchronous oneshot. A later
# repository-index commit may advance origin/main while the deployment runs;
# the updater proves the pin is still on current main history rather than
# silently switching candidates. Remove the manager environment before the
# periodic follower is resumed so timer runs continue to follow latest main.
systemctl unset-environment HHS_EXACT_CANDIDATE_SHA >/dev/null 2>&1 || true
clear_exact_candidate_pin() {
  systemctl unset-environment HHS_EXACT_CANDIDATE_SHA >/dev/null 2>&1 || true
}
if [[ "$ENABLE_PROMOTION" == "1" ]]; then
  systemctl set-environment HHS_EXACT_CANDIDATE_SHA="$BUNDLE_SHA"
  trap clear_exact_candidate_pin EXIT
fi

# Run exactly one synchronous updater while the timer is stopped. Type=oneshot
# makes systemctl start return only after validation/promotion/rollback reaches
# a terminal result. The periodic follower is re-enabled only after success.
if ! systemctl start hhs-guarded-update.service; then
  clear_exact_candidate_pin
  trap - EXIT
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

clear_exact_candidate_pin
trap - EXIT

systemctl enable hhs-guarded-update.timer >/dev/null
systemctl start hhs-guarded-update.timer
systemctl is-active --quiet hhs-guarded-update.timer || {
  echo "Guarded updater promotion succeeded but periodic follower timer did not activate." >&2
  exit 11
}

if [[ "$ENABLE_PROMOTION" == "1" ]]; then
  [[ -f "$STATIC_FIRST_CONFIGURATOR" ]] || {
    echo "Runtime OS first-paint nginx configurator missing: $STATIC_FIRST_CONFIGURATOR" >&2
    exit 12
  }

  # Bring up Lane 5 on loopback before changing any public nginx route. SSH is
  # deliberately outside this dependency chain so recovery access never depends
  # on application or Lane 5 startup.
  lane5_failure_diagnostics() {
    systemctl status hhs-lane5-ingress.socket --no-pager --full >&2 || true
    systemctl status hhs-lane5-ingress.service --no-pager --full >&2 || true
    journalctl -u hhs-lane5-ingress.socket -n 200 --no-pager >&2 || true
    journalctl -u hhs-lane5-ingress.service -n 300 --no-pager >&2 || true
    ss -H -ltnp 'sport = :8715' >&2 || true
  }

  systemctl enable hhs-lane5-ingress.socket >/dev/null

  # A running socket-activated service retains the inherited listening FD.
  # Stop both owners before rebinding the socket so repeated exact-main
  # promotions cannot collide with the already-serving Lane 5 process.
  if ! systemctl stop hhs-lane5-ingress.socket; then
    echo "Lane 5 ingress socket could not stop before deterministic rebind." >&2
    lane5_failure_diagnostics
    exit 12
  fi
  if ! systemctl stop hhs-lane5-ingress.service; then
    echo "Lane 5 ingress service could not stop before deterministic rebind." >&2
    lane5_failure_diagnostics
    exit 12
  fi
  if ! systemctl start hhs-lane5-ingress.socket; then
    echo "Lane 5 ingress socket could not bind after service shutdown." >&2
    lane5_failure_diagnostics
    exit 12
  fi
  if ! systemctl start hhs-lane5-ingress.service; then
    echo "Lane 5 ingress service could not start from the rebound socket." >&2
    lane5_failure_diagnostics
    exit 12
  fi
  lane5_deadline=$((SECONDS + 120))
  until curl -fsS --max-time 10 "$LANE5_INGRESS_HEALTH_URL" >/dev/null; do
    if (( SECONDS >= lane5_deadline )); then
      echo "Lane 5 host ingress failed local health before nginx migration." >&2
      systemctl status hhs-lane5-ingress.service --no-pager --full >&2 || true
      journalctl -u hhs-lane5-ingress.service -n 300 --no-pager >&2 || true
      exit 12
    fi
    sleep 2
  done
  echo "HHS_LANE5_HOST_INGRESS_READY=1"

  # Only after the local gateway proves Lane 5 authority do public routes move
  # off direct :8080/:8720. The configurator rolls nginx back if validation or
  # reload fails, so an incomplete migration is never accepted.
  python3 "$LANE5_INGRESS_CONFIGURATOR"
  python3 "$STATIC_FIRST_CONFIGURATOR" --runtime-os-root "$BUNDLE_ROOT/current"

  nginx_dump=$(nginx -T 2>&1)
  if grep -Fq 'proxy_pass http://127.0.0.1:8080' <<<"$nginx_dump"; then
    echo "Direct public Runtime OS nginx bypass remains after Lane 5 migration." >&2
    exit 12
  fi
  if grep -Fq 'proxy_pass http://127.0.0.1:8720' <<<"$nginx_dump"; then
    echo "Direct public application-VM nginx bypass remains after Lane 5 migration." >&2
    exit 12
  fi
  grep -Fq 'proxy_pass http://127.0.0.1:8715' <<<"$nginx_dump" || {
    echo "Lane 5 nginx gateway route is missing after migration." >&2
    exit 12
  }
  systemctl is-active --quiet hhs-lane5-ingress.socket || exit 12
  systemctl is-active --quiet hhs-lane5-ingress.service || exit 12
  echo "HHS_LANE5_HOST_INGRESS_SOCKET_ACTIVATED=1"
  echo "HHS_LANE5_HOST_INGRESS_NGINX_ZERO_BYPASS=1"
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
