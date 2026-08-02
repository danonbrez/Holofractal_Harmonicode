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
install -d -o "$SERVICE_USER" -g "$SERVICE_USER" /var/lib/hhs-pass189 /var/lib/hhs-pass189/iteration3 /var/lib/hhs-pass189/iteration4-quarantine /etc/hhs

make -C "$PROJECT" validate
install -m 0644 "$PROJECT/deployment/digitalocean/hhs-pass189.service" /etc/systemd/system/hhs-pass189.service
install -m 0644 "$PROJECT/deployment/digitalocean/hhs-pass189-iteration2.service" /etc/systemd/system/hhs-pass189-iteration2.service
install -m 0644 "$PROJECT/deployment/digitalocean/hhs-pass189-iteration3.service" /etc/systemd/system/hhs-pass189-iteration3.service
install -m 0644 "$PROJECT/deployment/digitalocean/hhs-pass189-iteration4.service" /etc/systemd/system/hhs-pass189-iteration4.service
if [[ ! -f /etc/hhs/pass189.env ]]; then
  touch /etc/hhs/pass189.env
fi
python3 - /etc/hhs/pass189.env <<'PY'
from pathlib import Path
import sys
path=Path(sys.argv[1]); lines=path.read_text().splitlines(); values={}
for line in lines:
    if '=' in line and not line.lstrip().startswith('#'):
        k,v=line.split('=',1); values[k]=v
values.update({
'HHS189_HOST':'127.0.0.1','HHS189_PORT':'8189','HHS189_QUIET':'0',
'HHS189_I2_HOST':'127.0.0.1','HHS189_I2_PORT':'8190','HHS189_I2_DB':'/var/lib/hhs-pass189/iteration2.sqlite3','HHS189_I2_QUIET':'0',
'HHS189_I3_HOST':'127.0.0.1','HHS189_I3_PORT':'8191','HHS189_I3_DB':'/var/lib/hhs-pass189/iteration3.sqlite3','HHS189_I3_STATE':'/var/lib/hhs-pass189/iteration3','HHS189_I3_QUIET':'0',
'HHS189_I4_HOST':'127.0.0.1','HHS189_I4_PORT':'8192','HHS189_I4_DB':'/var/lib/hhs-pass189/iteration4.sqlite3','HHS189_I4_QUARANTINE':'/var/lib/hhs-pass189/iteration4-quarantine','HHS189_I4_QUIET':'0'})
path.write_text('\n'.join(f'{k}={v}' for k,v in values.items())+'\n')
PY
chown root:"$SERVICE_USER" /etc/hhs/pass189.env
chmod 0640 /etc/hhs/pass189.env

systemctl daemon-reload
systemctl enable --now hhs-pass189.service hhs-pass189-iteration2.service hhs-pass189-iteration3.service hhs-pass189-iteration4.service
sleep 1
curl --fail --silent http://127.0.0.1:8189/api/pass189/health >/dev/null
curl --fail --silent http://127.0.0.1:8190/api/pass189/i2/status >/dev/null
curl --fail --silent http://127.0.0.1:8191/api/pass189/i3/status >/dev/null
curl --fail --silent http://127.0.0.1:8192/api/pass189/i4/status >/dev/null

cat <<EOF
Pass 189 services are healthy on 127.0.0.1 ports 8189, 8190, 8191, and 8192.
Iteration 3 stores fail-closed adapter authority under /var/lib/hhs-pass189/iteration3.
Iteration 4 stores provenance authority and quarantined payloads under /var/lib/hhs-pass189.
Install deployment/digitalocean/nginx-hhs-pass189.conf inside the existing HTTPS server block,
then run: nginx -t && systemctl reload nginx
Vercel is not part of this deployment authority.
EOF
