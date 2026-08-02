#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT=${REPO_ROOT:-/opt/holofractal-harmonicode}
PROJECT="$REPO_ROOT/native_projects/hhs_native_dns_gate"
PYTHONPATH="$PROJECT/python" python3 "$PROJECT/python/hhs_dns_gate.py" --registry "$PROJECT/config/service_registry.json" query pass189-calibration.hhs.internal --type A | grep -q '127.189.0.2'
PYTHONPATH="$PROJECT/python" python3 "$PROJECT/python/hhs_dns_gate.py" --registry "$PROJECT/config/service_registry.json" query pass190-runtime.hhs.internal --type A | grep -q '127.190.0.1'
PYTHONPATH="$PROJECT/python" python3 "$PROJECT/python/hhs_dns_gate.py" --registry "$PROJECT/config/service_registry.json" query _http._tcp.pass189-calibration.hhs.internal --type SRV | grep -q '8190'
PYTHONPATH="$PROJECT/python" python3 "$PROJECT/python/hhs_dns_gate.py" --registry "$PROJECT/config/service_registry.json" query _http._tcp.pass190-runtime.hhs.internal --type SRV --tcp | grep -q '8190'
if command -v resolvectl >/dev/null && systemctl is-active --quiet systemd-resolved.service; then
  resolvectl query pass189-calibration.hhs.internal | grep -q '127.189.0.2'
  resolvectl query pass190-runtime.hhs.internal | grep -q '127.190.0.1'
fi
if command -v ss >/dev/null; then
  listeners=$(ss -ltnH 2>/dev/null || true)
  if grep -q '127.189.0.2:8190' <<<"$listeners" && grep -q '127.190.0.1:8190' <<<"$listeners"; then
    printf '%s\n' 'HHS_NATIVE_DNS_GATE_SOCKET_SEPARATION_PASS'
  fi
fi
printf '%s\n' 'HHS_NATIVE_DNS_GATE_VERIFY_PASS pass189=127.189.0.2:8190 pass190=127.190.0.1:8190' 
