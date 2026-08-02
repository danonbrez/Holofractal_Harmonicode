#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=${REPO_ROOT:-/opt/holofractal-harmonicode}
PROJECT="$REPO_ROOT/native_projects/hhs_pass189_hqlh_runtime"
SERVICE_USER=${SERVICE_USER:-hhs}

if [[ $EUID -ne 0 ]]; then echo "Run as root on the DigitalOcean Ubuntu host." >&2; exit 2; fi
if [[ ! -d "$PROJECT" ]]; then echo "Missing project at $PROJECT" >&2; exit 3; fi

id -u "$SERVICE_USER" >/dev/null 2>&1 || useradd --system --home /var/lib/hhs-pass189 --shell /usr/sbin/nologin "$SERVICE_USER"
install -d -o "$SERVICE_USER" -g "$SERVICE_USER" /var/lib/hhs-pass189 /var/lib/hhs-pass189/iteration3 /etc/hhs
make -C "$PROJECT" validate
install -m 0644 "$PROJECT/deployment/digitalocean/hhs-pass189.service" /etc/systemd/system/hhs-pass189.service
install -m 0644 "$PROJECT/deployment/digitalocean/hhs-pass189-iteration2.service" /etc/systemd/system/hhs-pass189-iteration2.service
install -m 0644 "$PROJECT/deployment/digitalocean/hhs-pass189-iteration3.service" /etc/systemd/system/hhs-pass189-iteration3.service
[[ -f /etc/hhs/pass189.env ]] || touch /etc/hhs/pass189.env
python3 - /etc/hhs/pass189.env <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); values={}
for line in p.read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k,v=line.split('=',1); values[k]=v
values.update({'HHS189_HOST':'127.0.0.1','HHS189_PORT':'8189','HHS189_QUIET':'0','HHS189_I2_HOST':'127.0.0.1','HHS189_I2_PORT':'8190','HHS189_I2_DB':'/var/lib/hhs-pass189/iteration2.sqlite3','HHS189_I2_QUIET':'0','HHS189_I3_HOST':'127.0.0.1','HHS189_I3_PORT':'8191','HHS189_I3_DB':'/var/lib/hhs-pass189/iteration3.sqlite3','HHS189_I3_STATE':'/var/lib/hhs-pass189/iteration3','HHS189_I3_QUIET':'0'})
p.write_text('\n'.join(f'{k}={v}' for k,v in values.items())+'\n')
PY
chown root:"$SERVICE_USER" /etc/hhs/pass189.env
chmod 0640 /etc/hhs/pass189.env
systemctl daemon-reload
systemctl enable --now hhs-pass189.service hhs-pass189-iteration2.service hhs-pass189-iteration3.service
sleep 1
curl --fail --silent http://127.0.0.1:8189/api/pass189/health >/dev/null
curl --fail --silent http://127.0.0.1:8190/api/pass189/i2/status >/dev/null
curl --fail --silent http://127.0.0.1:8191/api/pass189/i3/status >/dev/null
printf '%s\n' 'Pass 189 services are healthy on ports 8189, 8190, and 8191.' 'Install nginx-hhs-pass189.conf in the existing HTTPS server block and reload nginx.' 'Vercel is not part of this deployment authority.'
