#!/usr/bin/env bash
set -Eeuo pipefail
umask 022

TARGET_SHA=${TARGET_SHA:?missing TARGET_SHA}
HHS_PUBLIC_IP=${HHS_PUBLIC_IP:?missing HHS_PUBLIC_IP}
APP_ROOT=${HHS_APP_ROOT:-/opt/hhs/app}
VENV_ROOT=${HHS_VENV_ROOT:-/opt/hhs/venv}
BUNDLE_ROOT=${HHS_RUNTIME_OS_BUNDLE_ROOT:-/var/lib/hhs/runtime-os}
REPO_URL=${HHS_REPOSITORY_URL:-https://github.com/danonbrez/Holofractal_Harmonicode.git}
EXPECTED_REPOSITORY=${HHS_EXPECTED_REPOSITORY:-danonbrez/Holofractal_Harmonicode}
CERTBOT_ROOT=${HHS_CERTBOT_ROOT:-/opt/certbot}
CERT_NAME=${HHS_CERT_NAME:-hhs-production-ip}
STATE_ROOT=${HHS_UPDATE_STATE_ROOT:-/var/lib/hhs-guarded-update}

require_root() {
  [[ ${EUID} -eq 0 ]] || {
    echo 'fresh production bootstrap requires root authority' >&2
    exit 2
  }
}

require_exact_sha() {
  [[ "$TARGET_SHA" =~ ^[0-9a-fA-F]{40}$ ]] || {
    echo "TARGET_SHA is not an exact 40-character commit: $TARGET_SHA" >&2
    exit 3
  }
}

normalize_repo_url() {
  local value=$1
  value=${value%.git}
  value=${value#git@github.com:}
  value=${value#https://github.com/}
  value=${value#http://github.com/}
  printf '%s\n' "$value"
}

install_host_dependencies() {
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential pkg-config \
    python3 python3-venv python3-pip \
    sqlite3 nginx ufw openssl libssl-dev libffi-dev
}

prepare_service_identity() {
  if ! id hhs >/dev/null 2>&1; then
    useradd --system --create-home --home-dir /var/lib/hhs --shell /usr/sbin/nologin hhs
  fi
  install -d -m 0755 /opt/hhs /etc/hhs
  install -d -o hhs -g hhs -m 0750 \
    /var/lib/hhs \
    /var/lib/hhs/data \
    /var/lib/hhs/data/runtime \
    /var/lib/hhs/graphics-hydration \
    /var/lib/hhs/pass196 \
    /var/lib/hhs/pass197 \
    /var/lib/hhs/pass198 \
    /var/lib/hhs/pass199 \
    /var/lib/hhs/pass200a \
    /var/lib/hhs/pass200b \
    /var/lib/hhs/pass200c \
    /var/lib/hhs/pass204 \
    /var/lib/hhs/pass205 \
    /var/lib/hhs/pass218 \
    /var/lib/hhs/runtime-bootstrap
  install -d -m 0755 "$BUNDLE_ROOT" "$BUNDLE_ROOT/incoming" "$BUNDLE_ROOT/releases"
  install -d -m 0750 "$STATE_ROOT"
}

hydrate_exact_repository() {
  if [[ ! -d "$APP_ROOT/.git" ]]; then
    [[ ! -e "$APP_ROOT" ]] || {
      echo "refusing to replace non-repository path: $APP_ROOT" >&2
      exit 10
    }
    git clone "$REPO_URL" "$APP_ROOT"
  fi

  actual=$(normalize_repo_url "$(git -C "$APP_ROOT" remote get-url origin)")
  [[ "$actual" == "$EXPECTED_REPOSITORY" ]] || {
    echo "unexpected production origin: $actual" >&2
    exit 11
  }

  git -C "$APP_ROOT" update-index -q --refresh || true
  if [[ -n "$(git -C "$APP_ROOT" status --porcelain=v1 --untracked-files=normal)" ]]; then
    echo 'production checkout contains unexplained local state; refusing bootstrap mutation' >&2
    git -C "$APP_ROOT" status --short >&2
    exit 12
  fi

  git -C "$APP_ROOT" fetch --prune origin main
  remote_sha=$(git -C "$APP_ROOT" rev-parse origin/main)
  [[ "$remote_sha" == "$TARGET_SHA" ]] || {
    echo "origin/main moved: expected $TARGET_SHA got $remote_sha" >&2
    exit 13
  }
  git -C "$APP_ROOT" cat-file -e "$TARGET_SHA^{commit}"
  git -C "$APP_ROOT" checkout -B main "$TARGET_SHA"
  git -C "$APP_ROOT" branch --set-upstream-to=origin/main main
  [[ "$(git -C "$APP_ROOT" rev-parse HEAD)" == "$TARGET_SHA" ]]
  [[ "$(git -C "$APP_ROOT" branch --show-current)" == main ]]
  git config --system --add safe.directory "$APP_ROOT" 2>/dev/null || true
}

install_python_runtime() {
  if [[ ! -x "$VENV_ROOT/bin/python" ]]; then
    python3 -m venv "$VENV_ROOT"
  fi
  "$VENV_ROOT/bin/python" -m pip install --upgrade pip setuptools wheel
  "$VENV_ROOT/bin/python" -m pip install -r "$APP_ROOT/requirements.txt"
}

build_native_authority() {
  make -C "$APP_ROOT" c-abi
  test -s "$APP_ROOT/hhs_runtime/builds/libhhs_runtime.so"
  "$VENV_ROOT/bin/python" -m py_compile \
    "$APP_ROOT/hhs_backend/production_visual_server.py" \
    "$APP_ROOT/hhs_backend/runtime_os_application_server.py" \
    "$APP_ROOT/deployment/digitalocean/guarded_auto_update/runtime-os-bundle.py"
  "$VENV_ROOT/bin/python" \
    "$APP_ROOT/deployment/digitalocean/guarded_auto_update/normalize-service-permissions.py" \
    --repo-root "$APP_ROOT" --service-user hhs --service-group hhs
}

activate_prebuilt_runtime_os() {
  incoming="$BUNDLE_ROOT/incoming/$TARGET_SHA"
  archive="$incoming/runtime-os.tar.gz"
  manifest="$incoming/manifest.json"
  tool="$APP_ROOT/deployment/digitalocean/guarded_auto_update/runtime-os-bundle.py"
  [[ -s "$archive" && -s "$manifest" ]] || {
    echo "exact Runtime OS bundle missing under $incoming" >&2
    exit 20
  }
  release=$(
    "$VENV_ROOT/bin/python" "$tool" stage \
      --root "$BUNDLE_ROOT" \
      --archive "$archive" \
      --manifest "$manifest" \
      --expected-sha "$TARGET_SHA"
  )
  "$VENV_ROOT/bin/python" "$tool" verify --root "$BUNDLE_ROOT" --expected-sha "$TARGET_SHA" >/dev/null
  "$VENV_ROOT/bin/python" "$tool" activate --root "$BUNDLE_ROOT" --expected-sha "$TARGET_SHA" >/dev/null
  test "$(readlink -f "$BUNDLE_ROOT/current")" = "$release"
  grep -Fq 'HHS Visual Runtime OS Workspace' "$BUNDLE_ROOT/current/index.html"
}

install_initial_service() {
  install -m 0644 \
    "$APP_ROOT/deploy/digitalocean/hhs-pass196-integrated-environment.service" \
    /etc/systemd/system/hhs.service
  if [[ ! -f /etc/hhs/pass196.env ]]; then
    install -m 0640 "$APP_ROOT/deploy/digitalocean/hhs-pass196.env.example" /etc/hhs/pass196.env
  fi
  chown root:hhs /etc/hhs/pass196.env
  chmod 0640 /etc/hhs/pass196.env

  "$VENV_ROOT/bin/python" \
    "$APP_ROOT/deployment/digitalocean/guarded_auto_update/normalize-service-permissions.py" \
    --repo-root "$APP_ROOT" --service-user hhs --service-group hhs

  systemctl daemon-reload
  systemctl enable hhs.service >/dev/null
  systemctl restart hhs.service

  deadline=$((SECONDS + 240))
  until curl -fsS --max-time 10 http://127.0.0.1:8080/api/system/status >/tmp/hhs-bootstrap-system-status.json; do
    if (( SECONDS >= deadline )); then
      systemctl status hhs.service --no-pager --full >&2 || true
      journalctl -u hhs.service -n 300 --no-pager >&2 || true
      exit 30
    fi
    sleep 2
  done
  test -s /tmp/hhs-bootstrap-system-status.json
}

install_guarded_follower() {
  REPO_ROOT="$APP_ROOT" \
  SOURCE_ROOT="$APP_ROOT" \
  HHS_RUNTIME_OS_BUNDLE_SHA="$TARGET_SHA" \
  HHS_RUNTIME_OS_BUNDLE_ROOT="$BUNDLE_ROOT" \
  HHS_INSTALL_ENABLE_PROMOTION=0 \
  HHS_PRODUCTION_HEALTH_TIMEOUT_SECONDS=600 \
    bash "$APP_ROOT/deployment/digitalocean/guarded_auto_update/install.sh"
  systemctl is-active --quiet hhs-guarded-update.timer
}

probe_language_authority() {
  set +e
  "$VENV_ROOT/bin/python" "$APP_ROOT/tools/install_production_language_assets.py" --install-if-configured \
    >/tmp/hhs-production-language-status.json 2>/tmp/hhs-production-language-status.err
  rc=$?
  set -e
  [[ $rc -eq 0 ]] || cat /tmp/hhs-production-language-status.err >&2
  return $rc
}

configure_public_tls() {
  ufw allow OpenSSH >/dev/null
  ufw allow 80/tcp >/dev/null
  ufw allow 443/tcp >/dev/null
  ufw --force enable >/dev/null

  if [[ ! -x "$CERTBOT_ROOT/bin/certbot" ]]; then
    python3 -m venv "$CERTBOT_ROOT"
    "$CERTBOT_ROOT/bin/python" -m pip install --upgrade pip
    "$CERTBOT_ROOT/bin/python" -m pip install 'certbot>=5.4,<6.0'
  fi

  cert_root="/etc/letsencrypt/live/$CERT_NAME"
  if [[ ! -s "$cert_root/fullchain.pem" || ! -s "$cert_root/privkey.pem" ]] \
      || ! openssl x509 -in "$cert_root/fullchain.pem" -noout -checkend 86400 >/dev/null 2>&1; then
    systemctl stop nginx 2>/dev/null || true
    if ss -H -ltn 'sport = :80' | grep -q .; then
      echo 'port 80 is unexpectedly occupied before ACME standalone validation' >&2
      ss -H -ltnp 'sport = :80' >&2 || true
      exit 40
    fi
    "$CERTBOT_ROOT/bin/certbot" certonly \
      --non-interactive \
      --agree-tos \
      --register-unsafely-without-email \
      --preferred-profile shortlived \
      --standalone \
      --ip-address "$HHS_PUBLIC_IP" \
      --cert-name "$CERT_NAME"
  fi

  cat >/etc/nginx/conf.d/hhs-websocket-map.conf <<'NGINX_MAP'
map $http_upgrade $hhs_connection_upgrade {
    default upgrade;
    '' close;
}
NGINX_MAP

  cat >/etc/nginx/sites-available/hhs-production <<NGINX_SITE
server {
    listen 80;
    listen [::]:80;
    server_name $HHS_PUBLIC_IP;
    return 308 https://$HHS_PUBLIC_IP\$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name $HHS_PUBLIC_IP;

    ssl_certificate /etc/letsencrypt/live/$CERT_NAME/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$CERT_NAME/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_session_cache shared:HHS_TLS:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    client_max_body_size 512m;

    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "same-origin" always;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \$hhs_connection_upgrade;
        proxy_connect_timeout 30s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
NGINX_SITE

  rm -f /etc/nginx/sites-enabled/default
  ln -sfn /etc/nginx/sites-available/hhs-production /etc/nginx/sites-enabled/hhs-production
  nginx -t
  systemctl enable nginx >/dev/null
  systemctl restart nginx
  systemctl is-active --quiet nginx

  cat >/usr/local/sbin/hhs-certbot-pre-renew <<'HOOK'
#!/bin/sh
set -eu
systemctl stop nginx
HOOK
  cat >/usr/local/sbin/hhs-certbot-post-renew <<'HOOK'
#!/bin/sh
set -eu
nginx -t
systemctl start nginx
HOOK
  chmod 0755 /usr/local/sbin/hhs-certbot-pre-renew /usr/local/sbin/hhs-certbot-post-renew

  cat >/etc/systemd/system/hhs-certbot-renew.service <<SYSTEMD_SERVICE
[Unit]
Description=Renew HHS short-lived IP certificate
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=$CERTBOT_ROOT/bin/certbot renew --quiet --cert-name $CERT_NAME --pre-hook /usr/local/sbin/hhs-certbot-pre-renew --post-hook /usr/local/sbin/hhs-certbot-post-renew
ExecStartPost=/usr/bin/systemctl is-active --quiet nginx
SYSTEMD_SERVICE

  cat >/etc/systemd/system/hhs-certbot-renew.timer <<'SYSTEMD_TIMER'
[Unit]
Description=Check HHS short-lived IP certificate renewal every six hours

[Timer]
OnCalendar=*-*-* 00,06,12,18:17:00
RandomizedDelaySec=15m
Persistent=true
Unit=hhs-certbot-renew.service

[Install]
WantedBy=timers.target
SYSTEMD_TIMER

  systemctl daemon-reload
  systemctl enable --now hhs-certbot-renew.timer >/dev/null
  systemctl is-active --quiet hhs-certbot-renew.timer
  openssl x509 -in "$cert_root/fullchain.pem" -noout -checkend 86400
}

write_initialization_receipt() {
  TARGET_SHA_VALUE="$TARGET_SHA" \
  PUBLIC_IP_VALUE="$HHS_PUBLIC_IP" \
  APP_ROOT_VALUE="$APP_ROOT" \
  BUNDLE_ROOT_VALUE="$BUNDLE_ROOT" \
  STATE_ROOT_VALUE="$STATE_ROOT" \
  "$VENV_ROOT/bin/python" - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

target = os.environ['TARGET_SHA_VALUE']
app = Path(os.environ['APP_ROOT_VALUE'])
bundle_root = Path(os.environ['BUNDLE_ROOT_VALUE'])
state_root = Path(os.environ['STATE_ROOT_VALUE'])
language_path = app / '.hhs' / 'production_language_assets_status.json'
language = {}
if language_path.is_file():
    try:
        language = json.loads(language_path.read_text(encoding='utf-8'))
    except Exception:
        language = {}
receipt = {
    'schema': 'HHS_FRESH_PRODUCTION_INITIALIZATION_RECEIPT_V1',
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'outcome': 'INITIALIZED',
    'repository_sha': target,
    'repository_root': str(app),
    'runtime_os_release': str((bundle_root / 'current').resolve()),
    'public_ip': os.environ['PUBLIC_IP_VALUE'],
    'ssh_host_trust': 'PINNED_ED25519_OUT_OF_BAND_VERIFIED',
    'assistant_ready': bool(language.get('assistant_ready')),
    'language_status_schema': language.get('schema'),
    'rollback_receipt_fabricated': False,
}
state_root.mkdir(parents=True, exist_ok=True)
path = state_root / 'initialization.json'
path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print(json.dumps(receipt, sort_keys=True))
PY
}

verify_local_closure() {
  [[ "$(git -C "$APP_ROOT" rev-parse HEAD)" == "$TARGET_SHA" ]]
  [[ "$(git -C "$APP_ROOT" rev-parse origin/main)" == "$TARGET_SHA" ]]
  [[ "$(git -C "$APP_ROOT" branch --show-current)" == main ]]
  systemctl is-active --quiet hhs.service
  systemctl is-active --quiet hhs-guarded-update.timer
  systemctl is-active --quiet nginx
  systemctl is-active --quiet hhs-certbot-renew.timer
  curl -fsS --max-time 15 http://127.0.0.1:8080/api/system/status >/tmp/hhs-final-loopback-status.json
  curl -fsS --max-time 20 "https://$HHS_PUBLIC_IP/api/system/status" >/tmp/hhs-final-public-status.json
  curl -fsS --max-time 20 "https://$HHS_PUBLIC_IP/" >/tmp/hhs-final-public-root.html
  grep -Fq 'HHS Visual Runtime OS Workspace' /tmp/hhs-final-public-root.html
  test -s "$STATE_ROOT/initialization.json"
}

main() {
  require_root
  require_exact_sha
  install_host_dependencies
  prepare_service_identity
  hydrate_exact_repository
  install_python_runtime
  build_native_authority
  activate_prebuilt_runtime_os
  install_initial_service
  install_guarded_follower
  probe_language_authority
  configure_public_tls
  write_initialization_receipt
  verify_local_closure
  echo "HHS_FRESH_PRODUCTION_INITIALIZATION_VERIFIED=1"
  echo "HHS_PRODUCTION_SHA=$TARGET_SHA"
  echo "HHS_PRODUCTION_PUBLIC_IP=$HHS_PUBLIC_IP"
}

main "$@"
