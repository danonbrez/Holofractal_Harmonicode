#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$ROOT/../.." && pwd)"
DNS_GATE="$REPO_ROOT/native_projects/hhs_native_dns_gate"
TARGET="/opt/hhs/pass190-operation-fabric"
STAGE="${TARGET}.new.$$"
BACKUP="${TARGET}.previous"
ENV_DIR="/etc/hhs"
ENV_FILE="${ENV_DIR}/pass190.env"

cd "$ROOT"
make validate
if [[ ! -d "$DNS_GATE" ]]; then
  echo "Missing native DNS gate at $DNS_GATE" >&2
  exit 3
fi
sudo REPO_ROOT="$REPO_ROOT" SERVICE_USER=hhs "$DNS_GATE/deploy/install.sh"

if ! id -u hhs >/dev/null 2>&1; then
  sudo useradd --system --home /var/lib/hhs --shell /usr/sbin/nologin hhs
fi
sudo install -d -o root -g hhs -m 0750 /opt/hhs "$ENV_DIR"
sudo install -d -o hhs -g hhs -m 0700 /var/lib/hhs
sudo install -d -o root -g root -m 0755 /etc/nginx/snippets

if ! sudo test -s "$ENV_FILE"; then
  secret="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
  printf 'HHS_PASS190_CAPABILITY_SECRET=%s\n' "$secret" | sudo tee "$ENV_FILE" >/dev/null
  sudo chown root:hhs "$ENV_FILE"
  sudo chmod 0640 "$ENV_FILE"
fi

sudo rm -rf "$STAGE"
sudo install -d -o root -g hhs -m 0750 "$STAGE"
sudo cp -a "$ROOT/." "$STAGE/"
sudo chown -R root:hhs "$STAGE"

rollback() {
  sudo systemctl stop hhs-pass190-worker.service >/dev/null 2>&1 || true
  sudo systemctl stop hhs-pass190.service >/dev/null 2>&1 || true
  sudo rm -rf "$TARGET"
  if sudo test -d "$BACKUP"; then
    sudo mv -T "$BACKUP" "$TARGET"
    sudo systemctl daemon-reload
    sudo systemctl start hhs-pass190.service >/dev/null 2>&1 || true
    sudo systemctl start hhs-pass190-worker.service >/dev/null 2>&1 || true
  fi
}
trap rollback ERR

sudo rm -rf "$BACKUP"
if sudo test -d "$TARGET"; then sudo mv -T "$TARGET" "$BACKUP"; fi
sudo mv -T "$STAGE" "$TARGET"
sudo install -m 0644 "$TARGET/deploy/hhs-pass190.service" /etc/systemd/system/hhs-pass190.service
sudo install -m 0644 "$TARGET/deploy/hhs-pass190-worker.service" /etc/systemd/system/hhs-pass190-worker.service
sudo install -m 0644 "$TARGET/deploy/nginx-hhs-pass190.conf" /etc/nginx/snippets/hhs-pass190.conf
sudo systemctl daemon-reload
sudo systemctl enable hhs-pass190.service hhs-pass190-worker.service
sudo systemctl restart hhs-pass190.service
sudo systemctl restart hhs-pass190-worker.service
"$TARGET/deploy/verify.sh"

trap - ERR
sudo rm -rf "$BACKUP"
sudo systemctl --no-pager --full status hhs-pass190.service hhs-pass190-worker.service
