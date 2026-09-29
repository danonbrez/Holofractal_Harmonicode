#!/bin/sh
set -eu

ROOT="${HHS_ROOT:-/opt/hhs/app}"
UNIT_SRC="$ROOT/hhs_gui/interface_gateway/hhs-interface-pty.service"
NGINX_SRC="$ROOT/hhs_gui/interface_gateway/nginx-interface-pty.conf"
ENV_DIR="/etc/hhs"
ENV_FILE="$ENV_DIR/interface-pty.env"
UNIT_DST="/etc/systemd/system/hhs-interface-pty.service"
SNIPPET_DST="/etc/nginx/snippets/hhs-interface-pty.conf"

[ "$(id -u)" -eq 0 ] || { echo "run as root" >&2; exit 2; }
[ -f "$UNIT_SRC" ] || { echo "missing $UNIT_SRC" >&2; exit 3; }
[ -f "$NGINX_SRC" ] || { echo "missing $NGINX_SRC" >&2; exit 4; }
[ -f "$ROOT/bin/hhs-guest" ] || { echo "missing bin/hhs-guest" >&2; exit 5; }

install -d -m 0750 "$ENV_DIR"
if [ ! -f "$ENV_FILE" ]; then
  TOKEN="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
  umask 077
  cat > "$ENV_FILE" <<EOF
HHS_INTERFACE_PTY_ENABLED=1
HHS_INTERFACE_PTY_TOKEN=$TOKEN
HHS_INTERFACE_PTY_MAX_COMMAND_CHARS=4096
HHS_INTERFACE_PTY_MAX_OUTPUT_BYTES=1048576
HHS_INTERFACE_PTY_MAX_TIMEOUT=120
EOF
  chmod 0600 "$ENV_FILE"
  printf '%s\n' "HHS interface PTY token (store securely; browser keeps it in memory only):"
  printf '%s\n' "$TOKEN"
else
  echo "Preserving existing $ENV_FILE"
fi

install -m 0644 "$UNIT_SRC" "$UNIT_DST"
install -m 0644 "$NGINX_SRC" "$SNIPPET_DST"

echo
echo "Nginx integration required in the existing TLS server block:"
echo "  include $SNIPPET_DST;"
echo
echo "Refusing to edit an unknown server block automatically."

systemctl daemon-reload
systemctl enable --now hhs-interface-pty.service
systemctl is-active --quiet hhs-interface-pty.service

curl --fail --silent --show-error http://127.0.0.1:8787/api/interface/ubuntu/pty/status
printf '\n'

if nginx -t; then
  echo "nginx syntax currently valid"
else
  echo "nginx syntax invalid; gateway service remains loopback-only" >&2
  exit 6
fi
