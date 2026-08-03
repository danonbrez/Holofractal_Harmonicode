#!/usr/bin/env bash
set -Eeuo pipefail

ENV_FILE="${HHS_TLS_ENV_FILE:-/etc/hhs/tls-renew.env}"
if [[ -r "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi

HHS_TLS_HOST="${HHS_TLS_HOST:-137.184.223.84}"
HHS_TLS_PORT="${HHS_TLS_PORT:-443}"
HHS_TLS_RENEW_BEFORE_DAYS="${HHS_TLS_RENEW_BEFORE_DAYS:-14}"
HHS_TLS_MINIMUM_VALID_DAYS="${HHS_TLS_MINIMUM_VALID_DAYS:-2}"
HHS_TLS_RENEW_COMMAND="${HHS_TLS_RENEW_COMMAND:-/usr/bin/certbot renew --quiet}"
HHS_TLS_RELOAD_COMMAND="${HHS_TLS_RELOAD_COMMAND:-/usr/bin/systemctl reload nginx}"
OPENSSL_BIN="${OPENSSL_BIN:-/usr/bin/openssl}"

case "${HHS_TLS_RENEW_BEFORE_DAYS}" in
  ''|*[!0-9]*) echo 'HHS_TLS_RENEW_BEFORE_DAYS must be a non-negative integer' >&2; exit 64 ;;
esac
case "${HHS_TLS_MINIMUM_VALID_DAYS}" in
  ''|*[!0-9]*) echo 'HHS_TLS_MINIMUM_VALID_DAYS must be a non-negative integer' >&2; exit 64 ;;
esac

renew_window_seconds=$((HHS_TLS_RENEW_BEFORE_DAYS * 86400))
minimum_valid_seconds=$((HHS_TLS_MINIMUM_VALID_DAYS * 86400))

certificate_pem() {
  timeout 20 "${OPENSSL_BIN}" s_client \
    -servername "${HHS_TLS_HOST}" \
    -connect "${HHS_TLS_HOST}:${HHS_TLS_PORT}" \
    -showcerts </dev/null 2>/dev/null |
    "${OPENSSL_BIN}" x509 -outform PEM
}

certificate_metadata() {
  certificate_pem | "${OPENSSL_BIN}" x509 -noout -subject -issuer -serial -enddate
}

certificate_valid_for() {
  local seconds="$1"
  certificate_pem | "${OPENSSL_BIN}" x509 -noout -checkend "${seconds}" >/dev/null
}

emit() {
  local status="$1"
  local detail="$2"
  printf '{"schema":"HHS_DIGITALOCEAN_TLS_RENEWAL_V1","status":"%s","host":"%s","port":%s,"detail":"%s"}\n' \
    "${status}" "${HHS_TLS_HOST}" "${HHS_TLS_PORT}" "${detail//\"/\\\"}"
}

before="$(certificate_metadata)" || {
  emit "TLS_PROBE_FAILED" "unable to retrieve the active certificate"
  exit 69
}

if certificate_valid_for "${renew_window_seconds}"; then
  emit "TLS_CERTIFICATE_WITHIN_POLICY" "${before//$'\n'/; }"
  exit 0
fi

emit "TLS_RENEWAL_REQUIRED" "${before//$'\n'/; }"

if ! command -v certbot >/dev/null 2>&1 && [[ "${HHS_TLS_RENEW_COMMAND}" == *certbot* ]]; then
  emit "TLS_RENEWAL_BLOCKED" "certbot is not installed"
  exit 69
fi

/bin/bash -lc "${HHS_TLS_RENEW_COMMAND}"
/usr/sbin/nginx -t
/bin/bash -lc "${HHS_TLS_RELOAD_COMMAND}"

# Nginx reload is asynchronous. Give workers a bounded interval to present the
# renewed certificate before enforcing the postcondition.
for _ in $(seq 1 20); do
  if certificate_valid_for "${minimum_valid_seconds}"; then
    after="$(certificate_metadata)"
    emit "TLS_RENEWAL_VERIFIED" "${after//$'\n'/; }"
    exit 0
  fi
  sleep 1
done

emit "TLS_RENEWAL_FAILED_POSTCONDITION" "certificate is still inside the minimum-validity window after renewal"
exit 70
