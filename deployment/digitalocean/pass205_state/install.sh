#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

SERVICE_NAME=${HHS_SERVICE_NAME:-hhs.service}
STATE_ROOT=${HHS_PASS205_STATE_ROOT:-/var/lib/hhs/pass205}
DATABASE_PATH=${HHS_PASS205_DB:-$STATE_ROOT/continuation.sqlite3}
DROPIN_DIR=${HHS_PASS205_DROPIN_DIR:-/etc/systemd/system/${SERVICE_NAME}.d}
DROPIN_PATH=$DROPIN_DIR/20-pass205-state.conf

[[ $EUID -eq 0 ]] || {
  echo "Pass 205 state installation requires root." >&2
  exit 2
}

service_user=$(systemctl show "$SERVICE_NAME" --property=User --value 2>/dev/null || true)
service_group=$(systemctl show "$SERVICE_NAME" --property=Group --value 2>/dev/null || true)
service_user=${service_user:-root}
service_group=${service_group:-$service_user}

if ! getent passwd "$service_user" >/dev/null; then
  echo "Configured service user does not exist: $service_user" >&2
  exit 3
fi
if ! getent group "$service_group" >/dev/null; then
  service_group=$(id -gn "$service_user")
fi

install -d -m 0750 -o "$service_user" -g "$service_group" "$STATE_ROOT"
install -d -m 0755 "$DROPIN_DIR"

temporary=$(mktemp)
trap 'rm -f "$temporary"' EXIT
cat >"$temporary" <<EOF
[Service]
Environment=HHS_PASS205_DB=$DATABASE_PATH
ReadWritePaths=$STATE_ROOT
UMask=0027
EOF
install -m 0644 "$temporary" "$DROPIN_PATH"
systemctl daemon-reload

printf 'Pass 205 state configured: service=%s user=%s group=%s database=%s\n' \
  "$SERVICE_NAME" "$service_user" "$service_group" "$DATABASE_PATH"
