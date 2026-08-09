#!/usr/bin/env bash
set -euo pipefail

# HHS production HTTPS + mobile-interface closure.
# Idempotently configures Nginx TLS, Certbot renewal, deploys the repository
# mobile first-paint repair, runs dependency-scoped tests, and verifies the
# public HTTPS surface.

HHS_IP="${HHS_IP:-137.184.223.84}"
HHS_APP_ROOT="${HHS_APP_ROOT:-/opt/hhs/app}"
HHS_APP_USER="${HHS_APP_USER:-hhs}"
HHS_CERT_NAME="${HHS_CERT_NAME:-hhs-production-ip}"
HHS_CERTBOT="${HHS_CERTBOT:-/opt/certbot/bin/certbot}"
HHS_BACKEND="${HHS_BACKEND:-http://127.0.0.1:8080}"
HHS_HEALTH_PATH="${HHS_HEALTH_PATH:-/api/health}"
HHS_ACME_WEBROOT="${HHS_ACME_WEBROOT:-/var/www/letsencrypt}"
HHS_TIMER_SCHEDULE="${HHS_TIMER_SCHEDULE:-*-*-* 00,06,12,18:17:00}"
HHS_SKIP_FRONTEND_DEPLOY="${HHS_SKIP_FRONTEND_DEPLOY:-0}"
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

run_as_app() {
  if command -v runuser >/dev/null 2>&1; then
    runuser -u "${HHS_APP_USER}" -- "$@"
  elif command -v sudo >/dev/null 2>&1; then
    sudo -u "${HHS_APP_USER}" -H "$@"
  else
    fail "runuser or sudo is required to execute Git as ${HHS_APP_USER}"
  fi
}

atomic_install_from_main() {
  local path="$1"
  local tmp
  tmp="$(mktemp)"
  if ! run_as_app git -C "${HHS_APP_ROOT}" show "origin/main:${path}" >"${tmp}"; then
    rm -f "${tmp}"
    fail "unable to read origin/main:${path}"
  fi
  [[ -s "${tmp}" ]] || {
    rm -f "${tmp}"
    fail "refusing to install empty file: ${path}"
  }
  install -o "${HHS_APP_USER}" -g "${HHS_APP_USER}" -m 0644 "${tmp}" "${HHS_APP_ROOT}/${path}"
  rm -f "${tmp}"
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

prepare_acme_webroot() {
  install -d -m 0755 "${HHS_ACME_WEBROOT}/.well-known/acme-challenge"
}

write_nginx_configuration() {
  local site_file="$1"
  local backup
  backup="${site_file}.pre-hhs-https-$(date -u +%Y%m%dT%H%M%SZ)"
  cp -a "${site_file}" "${backup}"
  printf 'Nginx backup: %s\n' "${backup}"

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
        root ${HHS_ACME_WEBROOT};
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

verify_acme_webroot() {
  local token="hhs-acme-selftest-$$"
  local challenge_file="${HHS_ACME_WEBROOT}/.well-known/acme-challenge/${token}"
  printf 'HHS_ACME_WEBROOT_OK\n' >"${challenge_file}"
  trap 'rm -f "${challenge_file}"' RETURN

  curl --max-time 5 -fsS \
    -H "Host: ${HHS_IP}" \
    "http://127.0.0.1/.well-known/acme-challenge/${token}" \
    | grep -qx 'HHS_ACME_WEBROOT_OK' \
    || fail "Nginx is not serving the ACME webroot challenge path"

  rm -f "${challenge_file}"
  trap - RETURN
}

configure_renewal() {
  # Webroot renewal requires Nginx to stay online for the HTTP-01 challenge.
  # Remove the obsolete stop/start hooks that caused production renewal to fail
  # with connection refused while Certbot was attempting validation.
  rm -f /usr/local/sbin/hhs-certbot-pre-renew /usr/local/sbin/hhs-certbot-post-renew

  cat >/etc/systemd/system/hhs-certbot-renew.service <<SYSTEMD
[Unit]
Description=Renew HHS short-lived IP certificate
Wants=network-online.target nginx.service
After=network-online.target nginx.service

[Service]
Type=oneshot
ExecStart=${HHS_CERTBOT} renew --quiet --cert-name ${HHS_CERT_NAME} --deploy-hook "/usr/bin/systemctl reload nginx"
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

deploy_frontend_repair() {
  [[ "${HHS_SKIP_FRONTEND_DEPLOY}" == "1" ]] && return 0

  [[ -d "${HHS_APP_ROOT}/.git" ]] || fail "repository not found at ${HHS_APP_ROOT}"
  id "${HHS_APP_USER}" >/dev/null 2>&1 || fail "application user not found: ${HHS_APP_USER}"

  run_as_app git -C "${HHS_APP_ROOT}" fetch origin main

  atomic_install_from_main applications/holofractal_harmonizer/src/sha256.mjs
  atomic_install_from_main applications/holofractal_harmonizer/src/core.mjs
  atomic_install_from_main applications/holofractal_harmonizer/src/pass177/hash216-browser.mjs
  atomic_install_from_main applications/holofractal_harmonizer/src/mobile-first-paint-fix.mjs
  atomic_install_from_main applications/holofractal_harmonizer/src/production-startup-coordinator.mjs
  atomic_install_from_main applications/holofractal_harmonizer/tests/http-insecure-sha256-fallback.test.mjs
  atomic_install_from_main applications/holofractal_harmonizer/tests/mobile-first-paint-fix.test.mjs

  node --check "${HHS_APP_ROOT}/applications/holofractal_harmonizer/src/sha256.mjs"
  node --check "${HHS_APP_ROOT}/applications/holofractal_harmonizer/src/core.mjs"
  node --check "${HHS_APP_ROOT}/applications/holofractal_harmonizer/src/pass177/hash216-browser.mjs"
  node --check "${HHS_APP_ROOT}/applications/holofractal_harmonizer/src/mobile-first-paint-fix.mjs"
  node --check "${HHS_APP_ROOT}/applications/holofractal_harmonizer/src/production-startup-coordinator.mjs"

  node --test \
    "${HHS_APP_ROOT}/applications/holofractal_harmonizer/tests/http-insecure-sha256-fallback.test.mjs" \
    "${HHS_APP_ROOT}/applications/holofractal_harmonizer/tests/mobile-first-paint-fix.test.mjs"
}

verify_public_surface() {
  local https_root="https://${HHS_IP}"
  local asset

  curl --max-time 10 -fsSI "http://${HHS_IP}/" | grep -Eqi '^HTTP/[0-9.]+ 308|^location: https://' \
    || fail "HTTP did not redirect to HTTPS"

  curl --max-time 10 -fsSI "${https_root}/" >/tmp/hhs-production-root-headers.txt \
    || fail "HTTPS root did not respond successfully"

  curl --max-time 10 -fsS "${https_root}${HHS_HEALTH_PATH}" >/tmp/hhs-production-health.json
  [[ -s /tmp/hhs-production-health.json ]] || fail "HTTPS health response was empty"

  for asset in \
    styles.css \
    ux-default.css \
    production-integration.css \
    visual-ide.css \
    harmonic-studio-theme.css \
    integrated-workbench.css \
    integrated-assistant.css \
    intuitive-ide.css \
    application-studio.css
  do
    curl --max-time 10 -fsSI "${https_root}/src/${asset}" >/dev/null \
      || fail "critical stylesheet unavailable over HTTPS: ${asset}"
  done

  curl --max-time 10 -fsSI "${https_root}/src/production-startup-coordinator.mjs" >/dev/null \
    || fail "critical startup JavaScript unavailable over HTTPS"

  curl --max-time 10 -fsS "${https_root}/src/sha256.mjs?production-closure=1" \
    | grep -q 'fallbackSha256' \
    || fail "SHA-256 fallback is not served over HTTPS"

  curl --max-time 10 -fsS "${https_root}/src/mobile-first-paint-fix.mjs?production-closure=1" \
    | grep -q 'HHS_MOBILE_FIRST_PAINT_AND_OVERLAY_OWNERSHIP_V1' \
    || fail "mobile first-paint repair is not served over HTTPS"

  openssl s_client -connect "${HHS_IP}:443" -servername "${HHS_IP}" </dev/null 2>/dev/null \
    | openssl x509 -noout -checkend 86400 \
    || fail "production certificate is invalid or expires within 24 hours"

  systemctl is-active --quiet nginx || fail "Nginx is not active"
  systemctl is-active --quiet hhs-certbot-renew.timer || fail "renewal timer is not active"
}

main() {
  require_root
  require_command git
  require_command nginx
  require_command curl
  require_command openssl
  require_command systemctl
  require_command node
  [[ -x "${HHS_CERTBOT}" ]] || fail "Certbot not executable at ${HHS_CERTBOT}"

  local cert_root="/etc/letsencrypt/live/${HHS_CERT_NAME}"
  [[ -s "${cert_root}/fullchain.pem" ]] || fail "certificate not found: ${cert_root}/fullchain.pem"
  [[ -s "${cert_root}/privkey.pem" ]] || fail "private key not found: ${cert_root}/privkey.pem"

  note "Checking backend health"
  curl -fsS "${HHS_BACKEND}${HHS_HEALTH_PATH}" >/tmp/hhs-backend-health.json

  note "Admitting HTTP and HTTPS through the host firewall"
  configure_firewall

  note "Preparing ACME webroot"
  prepare_acme_webroot

  note "Configuring Nginx HTTPS, ACME challenge, and WebSocket proxy"
  local site_file
  site_file="$(find_hhs_nginx_site)"
  printf 'Active HHS Nginx site: %s\n' "${site_file}"
  write_nginx_configuration "${site_file}"
  verify_acme_webroot

  note "Configuring short-lived certificate renewal"
  configure_renewal

  note "Removing staging certificate when present"
  if [[ -d /etc/letsencrypt/live/hhs-production-ip-staging ]]; then
    "${HHS_CERTBOT}" delete --cert-name hhs-production-ip-staging --non-interactive || true
  fi

  note "Deploying and validating browser repairs"
  deploy_frontend_repair

  if [[ "${HHS_RUN_RENEW_DRY_RUN}" == "1" ]]; then
    note "Running Certbot renewal dry run with Nginx online"
    "${HHS_CERTBOT}" renew --dry-run --cert-name "${HHS_CERT_NAME}" \
      --deploy-hook "/usr/bin/systemctl reload nginx"
  fi

  note "Verifying public production surface"
  verify_public_surface

  printf '\nHHS_PRODUCTION_HTTPS_MOBILE_CLOSURE_VERIFIED\n'
  printf 'Public URL: https://%s/?production-closure=1\n' "${HHS_IP}"
  printf 'Certificate:\n'
  openssl x509 -in "${cert_root}/fullchain.pem" -noout -subject -issuer -dates -ext subjectAltName
  printf 'Renewal timer:\n'
  systemctl list-timers hhs-certbot-renew.timer --all --no-pager
  printf 'Health response saved at /tmp/hhs-production-health.json\n'
}

main "$@"
