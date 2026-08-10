#!/usr/bin/env bash
set -euo pipefail

# HHS production HTTPS closure.
#
# Production frontend authority is owned exclusively by the versioned Runtime OS
# release selected by hhs.service. This script MUST NOT copy, install, patch, or
# otherwise mutate any frontend source inside /opt/hhs/app. It manages only the
# network/TLS edge and verifies that Nginx proxies the canonical Runtime OS.

HHS_IP="${HHS_IP:-137.184.223.84}"
HHS_CERT_NAME="${HHS_CERT_NAME:-hhs-production-ip}"
HHS_CERTBOT="${HHS_CERTBOT:-/opt/certbot/bin/certbot}"
HHS_BACKEND="${HHS_BACKEND:-http://127.0.0.1:8080}"
HHS_WEBROOT="${HHS_WEBROOT:-/var/www/letsencrypt}"
HHS_TIMER_SCHEDULE="${HHS_TIMER_SCHEDULE:-*-*-* 00,06,12,18:17:00}"
HHS_RUN_RENEW_DRY_RUN="${HHS_RUN_RENEW_DRY_RUN:-0}"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

note() {
  printf '\n==> %s\n' "$*"
}

require_root() {
  [[ "${EUID}" -eq 0 ]] || fail "run as root"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"
}

configure_firewall() {
  if ! command -v ufw >/dev/null 2>&1; then
    printf 'UFW not installed; skipping host-firewall mutation.\n'
    return 0
  fi

  local status
  status="$(ufw status 2>/dev/null | head -n 1 || true)"
  if [[ "${status}" == *inactive* ]]; then
    printf 'UFW is inactive; no firewall rule required.\n'
    return 0
  fi

  ufw allow 80/tcp >/dev/null
  ufw allow 443/tcp >/dev/null
  ufw status | grep -Eq '443/tcp.*ALLOW' || fail "UFW did not admit HTTPS"
}

find_hhs_nginx_site() {
  local candidate
  candidate="$({
    grep -RslE 'proxy_pass[[:space:]]+http://127\.0\.0\.1:8080' \
      /etc/nginx/sites-enabled /etc/nginx/conf.d 2>/dev/null || true
  } | grep -v '/hhs-websocket-map\.conf$' | head -n 1)"
  [[ -n "${candidate}" ]] || fail "unable to locate active Nginx site proxying to 127.0.0.1:8080"
  readlink -f "${candidate}"
}

write_nginx_configuration() {
  local site_file="$1"
  local backup
  backup="${site_file}.pre-hhs-https-$(date -u +%Y%m%dT%H%M%SZ)"
  cp -a "${site_file}" "${backup}"
  printf 'Nginx backup: %s\n' "${backup}"

  install -d -m 0755 "${HHS_WEBROOT}/.well-known/acme-challenge"

  cat >/etc/nginx/conf.d/hhs-websocket-map.conf <<'NGINX'
map $http_upgrade $hhs_connection_upgrade {
    default upgrade;
    ''      close;
}
NGINX

  cat >"${site_file}" <<NGINX
server {
    listen 80;
    listen [::]:80;
    server_name ${HHS_IP};

    location ^~ /.well-known/acme-challenge/ {
        root ${HHS_WEBROOT};
        default_type text/plain;
        try_files \$uri =404;
    }

    location / {
        return 308 https://${HHS_IP}\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${HHS_IP};

    ssl_certificate     /etc/letsencrypt/live/${HHS_CERT_NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${HHS_CERT_NAME}/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_session_cache shared:HHS_TLS:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    client_max_body_size 512m;

    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "same-origin" always;

    # One HTTP frontend authority: every application request is proxied to the
    # canonical HHS service. Nginx never serves a repository/static UI tree.
    location / {
        proxy_pass ${HHS_BACKEND};
        proxy_http_version 1.1;

        proxy_set_header Host              \$host;
        proxy_set_header X-Real-IP         \$remote_addr;
        proxy_set_header X-Forwarded-For   \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host  \$host;
        proxy_set_header X-Forwarded-Port  443;

        proxy_set_header Upgrade    \$http_upgrade;
        proxy_set_header Connection \$hhs_connection_upgrade;

        proxy_connect_timeout 30s;
        proxy_send_timeout    300s;
        proxy_read_timeout    300s;
    }
}
NGINX

  nginx -t
  systemctl reload nginx
  systemctl is-active --quiet nginx || fail "Nginx failed to remain active after TLS reload"
}

configure_renewal() {
  cat >/usr/local/sbin/hhs-certbot-deploy-renew <<'SH'
#!/bin/sh
set -eu
nginx -t
systemctl reload nginx
SH
  chmod 0755 /usr/local/sbin/hhs-certbot-deploy-renew

  cat >/etc/systemd/system/hhs-certbot-renew.service <<SYSTEMD
[Unit]
Description=Renew HHS short-lived IP certificate
Wants=network-online.target nginx.service
After=network-online.target nginx.service

[Service]
Type=oneshot
ExecStart=${HHS_CERTBOT} renew --quiet --cert-name ${HHS_CERT_NAME} --deploy-hook /usr/local/sbin/hhs-certbot-deploy-renew
ExecStartPost=/usr/bin/systemctl is-active --quiet nginx
SYSTEMD

  cat >/etc/systemd/system/hhs-certbot-renew.timer <<SYSTEMD
[Unit]
Description=Check HHS short-lived IP certificate renewal every six hours

[Timer]
OnCalendar=${HHS_TIMER_SCHEDULE}
RandomizedDelaySec=15m
Persistent=true
Unit=hhs-certbot-renew.service

[Install]
WantedBy=timers.target
SYSTEMD

  systemctl daemon-reload
  systemctl enable --now hhs-certbot-renew.timer
  systemctl is-enabled --quiet hhs-certbot-renew.timer
  systemctl is-active --quiet hhs-certbot-renew.timer
}

verify_interface_identity() {
  local status_file="$1"
  python3 - "$status_file" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if payload.get("interface") != "HHS_VISUAL_RUNTIME_OS_WORKSPACE":
    raise SystemExit(f"unexpected production interface: {payload}")
if payload.get("legacy_harmonizer_is_public_root") is not False:
    raise SystemExit(f"legacy Harmonizer is still public-root authority: {payload}")
asset_root = str(payload.get("asset_root", ""))
if "/var/lib/hhs/runtime-os/releases/" not in asset_root:
    raise SystemExit(f"production is not serving a versioned Runtime OS release: {payload}")
PY
}

verify_public_surface() {
  local https_root="https://${HHS_IP}"

  curl -fsSI "http://${HHS_IP}/" | grep -Eqi '^HTTP/[0-9.]+ 308|^location: https://' \
    || fail "HTTP did not redirect to HTTPS"

  curl -fsS "${HHS_BACKEND}/api/system/status" >/tmp/hhs-backend-system-status.json
  [[ -s /tmp/hhs-backend-system-status.json ]] || fail "local HHS system status was empty"

  curl -fsS "${HHS_BACKEND}/api/interface/status" >/tmp/hhs-backend-interface-status.json
  verify_interface_identity /tmp/hhs-backend-interface-status.json

  curl -fsS "${https_root}/api/system/status" >/tmp/hhs-production-system-status.json
  [[ -s /tmp/hhs-production-system-status.json ]] || fail "HTTPS system status response was empty"

  curl -fsS "${https_root}/api/interface/status" >/tmp/hhs-production-interface-status.json
  verify_interface_identity /tmp/hhs-production-interface-status.json

  curl -fsS "${https_root}/" >/tmp/hhs-production-runtime-os.html
  grep -Fq 'HHS Visual Runtime OS Workspace' /tmp/hhs-production-runtime-os.html \
    || fail "public root is not the canonical Runtime OS"

  openssl s_client -connect "${HHS_IP}:443" -servername "${HHS_IP}" </dev/null 2>/dev/null \
    | openssl x509 -noout -checkend 86400 \
    || fail "production certificate is invalid or expires within 24 hours"

  systemctl is-active --quiet nginx || fail "Nginx is not active"
  systemctl is-active --quiet hhs-certbot-renew.timer || fail "renewal timer is not active"
}

main() {
  require_root
  require_command nginx
  require_command curl
  require_command openssl
  require_command systemctl
  require_command python3
  [[ -x "${HHS_CERTBOT}" ]] || fail "Certbot not executable at ${HHS_CERTBOT}"

  local cert_root="/etc/letsencrypt/live/${HHS_CERT_NAME}"
  [[ -s "${cert_root}/fullchain.pem" ]] || fail "certificate not found: ${cert_root}/fullchain.pem"
  [[ -s "${cert_root}/privkey.pem" ]] || fail "private key not found: ${cert_root}/privkey.pem"

  note "Checking canonical HHS backend and Runtime OS identity"
  curl -fsS "${HHS_BACKEND}/api/system/status" >/tmp/hhs-backend-system-status.json
  curl -fsS "${HHS_BACKEND}/api/interface/status" >/tmp/hhs-backend-interface-status.json
  verify_interface_identity /tmp/hhs-backend-interface-status.json

  note "Admitting HTTP and HTTPS through the host firewall"
  configure_firewall

  note "Configuring Nginx as proxy-only frontend authority"
  local site_file
  site_file="$(find_hhs_nginx_site)"
  printf 'Active HHS Nginx site: %s\n' "${site_file}"
  write_nginx_configuration "${site_file}"

  note "Configuring online short-lived certificate renewal"
  configure_renewal

  if [[ "${HHS_RUN_RENEW_DRY_RUN}" == "1" ]]; then
    note "Running Certbot renewal dry run"
    "${HHS_CERTBOT}" renew --dry-run --cert-name "${HHS_CERT_NAME}" \
      --deploy-hook /usr/local/sbin/hhs-certbot-deploy-renew
  fi

  note "Verifying one canonical public Runtime OS surface"
  verify_public_surface

  printf '\nHHS_PRODUCTION_HTTPS_RUNTIME_OS_CLOSURE_VERIFIED\n'
  printf 'Public URL: https://%s/\n' "${HHS_IP}"
  printf 'Certificate:\n'
  openssl x509 -in "${cert_root}/fullchain.pem" -noout -subject -issuer -dates -ext subjectAltName
  printf 'Renewal timer:\n'
  systemctl list-timers hhs-certbot-renew.timer --all --no-pager
  printf 'Interface status saved at /tmp/hhs-production-interface-status.json\n'
}

main "$@"
