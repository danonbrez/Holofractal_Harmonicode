#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=${REPO_ROOT:-/opt/holofractal-harmonicode}
PROJECT="$REPO_ROOT/native_projects/hhs_pass189_hqlh_runtime"
SERVICE_USER=${SERVICE_USER:-hhs}

if [[ $EUID -ne 0 ]]; then
  echo "Run as root on the DigitalOcean Ubuntu host." >&2
  exit 2
fi
if [[ ! -d "$PROJECT" ]]; then
  echo "Missing project at $PROJECT" >&2
  exit 3
fi

id -u "$SERVICE_USER" >/dev/null 2>&1 || useradd --system --home /var/lib/hhs-pass189 --shell /usr/sbin/nologin "$SERVICE_USER"
install -d -o "$SERVICE_USER" -g "$SERVICE_USER" /var/lib/hhs-pass189 /etc/hhs

make -C "$PROJECT" validate
install -m 0644 "$PROJECT/deployment/digitalocean/hhs-pass189.service" /etc/systemd/system/hhs-pass189.service
if [[ ! -f /etc/hhs/pass189.env ]]; then
  cat >/etc/hhs/pass189.env <<'EOF'
HHS189_HOST=127.0.0.1
HHS189_PORT=8189
HHS189_QUIET=0
EOF
fi

systemctl daemon-reload
systemctl enable --now hhs-pass189.service
sleep 1
curl --fail --silent http://127.0.0.1:8189/api/pass189/health >/dev/null

cat <<EOF
Pass 189 runtime is healthy on 127.0.0.1:8189.
Add deployment/digitalocean/nginx-hhs-pass189.conf to the existing HTTPS server block,
then run: nginx -t && systemctl reload nginx
Vercel is not part of this deployment authority.
EOF
