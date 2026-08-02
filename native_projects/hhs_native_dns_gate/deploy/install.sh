#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT=${REPO_ROOT:-/opt/holofractal-harmonicode}
PROJECT="$REPO_ROOT/native_projects/hhs_native_dns_gate"
SERVICE_USER=${SERVICE_USER:-hhs}
if [[ $EUID -ne 0 ]]; then echo "Run as root." >&2; exit 2; fi
if [[ ! -d "$PROJECT" ]]; then echo "Missing DNS gate project at $PROJECT" >&2; exit 3; fi
command -v python3 >/dev/null
command -v systemctl >/dev/null
command -v resolvectl >/dev/null
id -u "$SERVICE_USER" >/dev/null 2>&1 || useradd --system --home /var/lib/hhs --shell /usr/sbin/nologin "$SERVICE_USER"
make -C "$PROJECT" validate
install -m 0644 "$PROJECT/deploy/hhs-dns-gate.service" /etc/systemd/system/hhs-dns-gate.service
install -m 0644 "$PROJECT/deploy/hhs-dns-gate-resolved.service" /etc/systemd/system/hhs-dns-gate-resolved.service
for source in "$PROJECT"/deploy/overrides/*.service.d; do
  unit_dir=/etc/systemd/system/"$(basename "$source")"
  install -d -m 0755 "$unit_dir"
  install -m 0644 "$source/10-hhs-dns-gate.conf" "$unit_dir/10-hhs-dns-gate.conf"
done
systemctl daemon-reload
systemctl enable --now systemd-resolved.service hhs-dns-gate.service hhs-dns-gate-resolved.service
sleep 1
"$PROJECT/deploy/verify.sh"
printf '%s\n' 'HHS native DNS gate installed. The hhs.internal zone now separates same-port services by loopback IP.'
