#!/usr/bin/env bash
set -Eeuo pipefail
umask 022

TARGET_SHA=${TARGET_SHA:?missing TARGET_SHA}
APP_ROOT=${HHS_APP_ROOT:-/opt/hhs/app}
STATE_DIR=${HHS_RUNTIME_CERTIFICATION_STATE_DIR:-/var/lib/hhs/runtime-certification}
STORYBOOK_DIR=${HHS_STORYBOOK_REEL_STATE_DIR:-/var/lib/hhs/storybook-reels}
DATA_ROOT=${HHS_DATA_ROOT_STATE_DIR:-/var/lib/hhs/data}
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

install -d -o hhs -g hhs -m 0750 "$STATE_DIR" "$STORYBOOK_DIR" "$DATA_ROOT"
install -d -m 0755 "$DROPIN_DIR"
cat >"$DROPIN_PATH" <<EOF
[Service]
Environment=HHS_STORYBOOK_REEL_ARTIFACT_ROOT=$STORYBOOK_DIR
Environment=HHS_DATA_ROOT=$DATA_ROOT
BindPaths=$STATE_DIR:$APP_ROOT/runtime_certification
EOF
chmod 0644 "$DROPIN_PATH"

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
[[ -z "$(git -C "$APP_ROOT" status --porcelain=v1 --untracked-files=normal)" ]] || {
  echo 'state-path repair introduced repository drift' >&2
  git -C "$APP_ROOT" status --short >&2
  exit 22
}

test -s /tmp/hhs-runtime-certification-repair-health.json
printf 'HHS_RUNTIME_CERTIFICATION_STATE_BIND_VERIFIED=1\n'
printf 'HHS_STORYBOOK_REEL_STATE_ROOT_VERIFIED=%s\n' "$STORYBOOK_DIR"
printf 'HHS_DATA_ROOT_VERIFIED=%s\n' "$DATA_ROOT"
printf 'HHS_RUNTIME_CERTIFICATION_TARGET_SHA=%s\n' "$TARGET_SHA"
