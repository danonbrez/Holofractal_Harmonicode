#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
  echo "run as root: sudo $0" >&2
  exit 77
fi

for command in openssl nginx systemctl timeout; do
  command -v "${command}" >/dev/null 2>&1 || {
    echo "required command is missing: ${command}" >&2
    exit 69
  }
done

install -d -m 0750 /etc/hhs
install -m 0750 "${SCRIPT_DIR}/hhs-tls-renew.sh" /usr/local/sbin/hhs-tls-renew
install -m 0644 "${SCRIPT_DIR}/hhs-tls-renew.service" /etc/systemd/system/hhs-tls-renew.service
install -m 0644 "${SCRIPT_DIR}/hhs-tls-renew.timer" /etc/systemd/system/hhs-tls-renew.timer

if [[ ! -e /etc/hhs/tls-renew.env ]]; then
  install -m 0600 "${SCRIPT_DIR}/tls-renew.env.example" /etc/hhs/tls-renew.env
else
  chmod 0600 /etc/hhs/tls-renew.env
fi

systemctl daemon-reload
systemctl enable --now hhs-tls-renew.timer
systemctl start hhs-tls-renew.service
systemctl --no-pager --full status hhs-tls-renew.service || true
systemctl --no-pager --full status hhs-tls-renew.timer
