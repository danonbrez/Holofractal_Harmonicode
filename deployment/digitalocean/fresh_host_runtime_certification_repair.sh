#!/usr/bin/env bash
set -Eeuo pipefail
umask 022

TARGET_SHA=${TARGET_SHA:?missing TARGET_SHA}
APP_ROOT=${HHS_APP_ROOT:-/opt/hhs/app}
STATE_DIR=${HHS_RUNTIME_CERTIFICATION_STATE_DIR:-/var/lib/hhs/runtime-certification}
STORYBOOK_DIR=${HHS_STORYBOOK_REEL_STATE_DIR:-/var/lib/hhs/storybook-reels}
DATA_ROOT=${HHS_DATA_ROOT_STATE_DIR:-/var/lib/hhs/data}
AGENT_INDEX_DIR=${HHS_AGENT_INDEX_STATE_DIR:-/var/lib/hhs/immutable-agent-index}
AGENT_INDEX_DB=${HHS_AGENT_INDEX_DB_PATH:-$AGENT_INDEX_DIR/hhs-agent-index.sqlite3}
RUNTIME_OS_ROOT=${HHS_RUNTIME_OS_ROOT:-/var/lib/hhs/runtime-os}
RUNTIME_OS_RELEASE="$RUNTIME_OS_ROOT/releases/$TARGET_SHA"
RUNTIME_OS_TOOL="$APP_ROOT/deployment/digitalocean/guarded_auto_update/runtime-os-bundle.py"
DROPIN_DIR=${HHS_SERVICE_DROPIN_DIR:-/etc/systemd/system/hhs.service.d}
DROPIN_PATH="$DROPIN_DIR/10-runtime-certification-state.conf"
HEALTH_URL=${HHS_HEALTH_URL:-http://127.0.0.1:8080/api/system/status}
HEALTH_TIMEOUT=${HHS_HEALTH_TIMEOUT_SECONDS:-120}

[[ $EUID -eq 0 ]] || {
  echo 'runtime certification state repair requires root authority' >&2
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
  echo "production HEAD is not exact target $TARGET_SHA" >&2
  exit 5
}
[[ -z "$(git -C "$APP_ROOT" status --porcelain=v1 --untracked-files=normal)" ]] || {
  echo 'production checkout is not clean before state-path repair' >&2
  git -C "$APP_ROOT" status --short >&2
  exit 6
}
id hhs >/dev/null 2>&1 || {
  echo 'hhs service identity is missing' >&2
  exit 7
}
[[ -f /etc/systemd/system/hhs.service ]] || {
  echo 'hhs.service is not installed' >&2
  exit 8
}

grep -Fq 'User=hhs' /etc/systemd/system/hhs.service
grep -Fq 'ProtectSystem=full' /etc/systemd/system/hhs.service
grep -Fq 'ReadWritePaths=/var/lib/hhs' /etc/systemd/system/hhs.service

install -d -o hhs -g hhs -m 0750 \
  "$STATE_DIR" \
  "$STORYBOOK_DIR" \
  "$DATA_ROOT" \
  "$AGENT_INDEX_DIR"
install -d -m 0755 "$DROPIN_DIR"
cat >"$DROPIN_PATH" <<EOF
[Service]
Environment=HHS_STORYBOOK_REEL_ARTIFACT_ROOT=$STORYBOOK_DIR
Environment=HHS_DATA_ROOT=$DATA_ROOT
Environment=HHS_AGENT_INDEX_DB=$AGENT_INDEX_DB
BindPaths=$STATE_DIR:$APP_ROOT/runtime_certification
EOF
chmod 0644 "$DROPIN_PATH"

# runtime-os-bundle.py stages into tempfile.mkdtemp(), whose root is 0700.
# Its recursive mode normalization covers descendants but not the stage root
# itself. Repair only the already sealed exact release root: keep it root-owned
# and non-writable while allowing the hhs service to traverse/read the bundle.
[[ -d "$RUNTIME_OS_RELEASE" ]] || {
  echo "exact Runtime OS release missing: $RUNTIME_OS_RELEASE" >&2
  exit 9
}
[[ -f "$RUNTIME_OS_RELEASE/index.html" ]] || {
  echo "Runtime OS index missing: $RUNTIME_OS_RELEASE/index.html" >&2
  exit 10
}
[[ -d "$RUNTIME_OS_RELEASE/assets" ]] || {
  echo "Runtime OS assets missing: $RUNTIME_OS_RELEASE/assets" >&2
  exit 11
}
[[ -f "$RUNTIME_OS_RELEASE/.hhs-runtime-os-manifest.json" ]] || {
  echo "Runtime OS release manifest missing" >&2
  exit 12
}
[[ -f "$RUNTIME_OS_TOOL" ]] || {
  echo "Runtime OS verifier missing: $RUNTIME_OS_TOOL" >&2
  exit 13
}
chmod 0755 "$RUNTIME_OS_RELEASE"
runuser -u hhs -- test -x "$RUNTIME_OS_RELEASE"
runuser -u hhs -- test -r "$RUNTIME_OS_RELEASE/index.html"
python3 "$RUNTIME_OS_TOOL" verify --root "$RUNTIME_OS_ROOT" --expected-sha "$TARGET_SHA" >/dev/null

after_mode=$(stat -c '%a' "$RUNTIME_OS_RELEASE")
[[ "$after_mode" == 755 ]] || {
  echo "Runtime OS release root mode repair failed: $after_mode" >&2
  exit 14
}

runuser -u hhs -- test -w "$AGENT_INDEX_DIR"

systemctl daemon-reload
systemctl reset-failed hhs.service || true
systemctl restart hhs.service

deadline=$((SECONDS + HEALTH_TIMEOUT))
until curl -fsS --max-time 10 "$HEALTH_URL" >/tmp/hhs-runtime-certification-repair-health.json; do
  if (( SECONDS >= deadline )); then
    systemctl status hhs.service --no-pager --full >&2 || true
    journalctl -u hhs.service -n 240 --no-pager >&2 || true
    exit 20
  fi
  sleep 2
done

systemctl is-active --quiet hhs.service
pid=$(systemctl show -p MainPID --value hhs.service)
[[ "$pid" =~ ^[1-9][0-9]*$ ]] || {
  echo "invalid hhs.service MainPID: $pid" >&2
  exit 21
}
nsenter -t "$pid" -m -- runuser -u hhs -- test -w "$APP_ROOT/runtime_certification"
runuser -u hhs -- test -w "$STORYBOOK_DIR"
runuser -u hhs -- test -w "$DATA_ROOT"
runuser -u hhs -- test -w "$AGENT_INDEX_DIR"
runuser -u hhs -- test -r "$RUNTIME_OS_RELEASE/index.html"

[[ -s "$AGENT_INDEX_DB" ]] || {
  echo "immutable agent index database was not created: $AGENT_INDEX_DB" >&2
  exit 22
}
[[ "$(stat -c '%U:%G' "$AGENT_INDEX_DB")" == 'hhs:hhs' ]] || {
  echo "immutable agent index database ownership mismatch: $(stat -c '%U:%G' "$AGENT_INDEX_DB")" >&2
  exit 23
}
runuser -u hhs -- sqlite3 "$AGENT_INDEX_DB" 'PRAGMA quick_check;' | grep -Fxq 'ok'

[[ -z "$(git -C "$APP_ROOT" status --porcelain=v1 --untracked-files=normal)" ]] || {
  echo 'state-path repair introduced repository drift' >&2
  git -C "$APP_ROOT" status --short >&2
  exit 24
}

test -s /tmp/hhs-runtime-certification-repair-health.json
printf 'HHS_RUNTIME_CERTIFICATION_STATE_BIND_VERIFIED=1\n'
printf 'HHS_STORYBOOK_REEL_STATE_ROOT_VERIFIED=%s\n' "$STORYBOOK_DIR"
printf 'HHS_DATA_ROOT_VERIFIED=%s\n' "$DATA_ROOT"
printf 'HHS_AGENT_INDEX_DB_VERIFIED=%s\n' "$AGENT_INDEX_DB"
printf 'HHS_RUNTIME_OS_RELEASE_READABILITY_VERIFIED=%s\n' "$RUNTIME_OS_RELEASE"
printf 'HHS_RUNTIME_CERTIFICATION_TARGET_SHA=%s\n' "$TARGET_SHA"
