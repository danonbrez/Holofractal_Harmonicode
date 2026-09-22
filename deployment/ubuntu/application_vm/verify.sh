#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${HHS_APPLICATION_VM_ENV_FILE:-/etc/hhs/application-vm.env}"
[[ -r "$ENV_FILE" ]] || { echo "env file not readable: $ENV_FILE" >&2; exit 2; }
# shellcheck disable=SC1090
source "$ENV_FILE"

BASE="http://${HHS_APPLICATION_VM_HOST:-127.0.0.1}:${HHS_APPLICATION_VM_PORT:-8720}"
PORT="${HHS_APPLICATION_VM_PORT:-8720}"
CLI="${HHS_APPLICATION_VM_CLI:-hhs-vm}"
export HHS_APPLICATION_VM_ENV_FILE="$ENV_FILE"

RUNTIME_SO="${HHS_APPLICATION_VM_REPOSITORY_ROOT:?missing repository root}/hhs_runtime/builds/libhhs_runtime.so"
[[ "${HHS_DISABLE_C_AUTOBUILD:-}" == "1" ]] || {
  echo "production C autobuild must be disabled after prebuild" >&2
  exit 2
}
[[ -s "$RUNTIME_SO" ]] || {
  echo "native runtime shared library missing: $RUNTIME_SO" >&2
  exit 2
}
nm -D "$RUNTIME_SO" | grep -Eq ' hhs_runtime_initcommand -v "$CLI" >/dev/null 2>&1 || { echo "hhs-vm CLI missing" >&2; exit 2; }
command -v ss >/dev/null 2>&1 || { echo "ss command missing" >&2; exit 2; }

health="$(curl --fail --silent "$BASE/health")"
printf '%s' "$health" | python3 -c '
import json,sys
p=json.load(sys.stdin)
assert p["ok"] is True
assert p["security_configured"] is True
assert p["ubuntu"] is True
assert p["ubuntu_desktop_components_present"] is True
assert p["frontend_attached"] is False
assert p["new_vm81_authority"] is False
'

listener="$(ss -H -ltn "sport = :$PORT")"
[[ -n "$listener" ]] || { echo "application VM listener missing on port $PORT" >&2; exit 3; }
if printf '%s\n' "$listener" | awk '{print $4}' | grep -Ev '^(127\.0\.0\.1|\[::1\]):' >/dev/null; then
  echo "application VM listener is not loopback-only" >&2
  printf '%s\n' "$listener" >&2
  exit 3
fi

cli_status="$("$CLI" status)"
printf '%s' "$cli_status" | python3 -c '
import json,sys
p=json.load(sys.stdin)
assert p["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
assert p["frontend_attached"] is False
assert p["single_vm81_authority_preserved"] is True
assert p["desktop"]["ubuntu"] is True
assert p["desktop"]["ubuntu_desktop_components_present"] is True
'

token="$("$CLI" token issue \
  --principal verifier \
  --scope runtime.mutate \
  --scope workspace:read \
  --scope workspace:write \
  --scope artifact:read \
  --scope artifact:write \
  --ttl 300 | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"

auth="Authorization: HHS-Capability $token"

"$CLI" --capability-token "$token" shell -- hhs status >/tmp/hhs-vm-cli-shell.json
curl --fail --silent -H "$auth" "$BASE/v1/vm/status" >/tmp/hhs-vm-status.json
curl --fail --silent -H "$auth" "$BASE/v1/vm/capabilities" >/tmp/hhs-vm-capabilities.json
curl --fail --silent -H "$auth" -H 'Content-Type: application/json' \
  -d '{"command":"hhs status"}' "$BASE/v1/vm/shell" >/tmp/hhs-vm-shell.json
curl --fail --silent "$BASE/openapi.json" >/tmp/hhs-vm-openapi.json

python3 - <<'PY'
import json
status=json.load(open("/tmp/hhs-vm-status.json"))
caps=json.load(open("/tmp/hhs-vm-capabilities.json"))
shell=json.load(open("/tmp/hhs-vm-shell.json"))
cli_shell=json.load(open("/tmp/hhs-vm-cli-shell.json"))
openapi=json.load(open("/tmp/hhs-vm-openapi.json"))
assert status["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
assert status["frontend_attached"] is False
assert status["single_vm81_authority_preserved"] is True
assert status["desktop"]["ubuntu"] is True
assert status["desktop"]["ubuntu_desktop_components_present"] is True
assert caps["operation_count"] == 52
assert shell["operation_id"] == "system.status"
assert cli_shell["operation_id"] == "system.status"
assert openapi["x-hhs-application-vm"]["frontend_attached"] is False
assert "HhsCapabilityToken" in openapi["components"]["securitySchemes"]
PY

unauth_code="$(curl --silent --output /tmp/hhs-vm-unauth.json --write-out '%{http_code}' "$BASE/v1/vm/status")"
[[ "$unauth_code" == "401" ]] || {
  echo "unauthenticated status returned HTTP $unauth_code instead of 401" >&2
  exit 3
}

if [[ -n "${HHS_APPLICATION_VM_PUBLIC_BASE:-}" ]]; then
  PUBLIC="${HHS_APPLICATION_VM_PUBLIC_BASE%/}"
  curl --fail --silent --show-error "$PUBLIC/health" >/tmp/hhs-vm-public-health.json
  curl --fail --silent --show-error "$PUBLIC/openapi.json" >/tmp/hhs-vm-public-openapi.json
  public_unauth="$(curl --silent --show-error --output /tmp/hhs-vm-public-unauth.json --write-out '%{http_code}' "$PUBLIC/v1/vm/status")"
  [[ "$public_unauth" == "401" ]] || {
    echo "public unauthenticated status returned HTTP $public_unauth instead of 401" >&2
    exit 4
  }
  curl --fail --silent --show-error -H "$auth" "$PUBLIC/v1/vm/status" >/tmp/hhs-vm-public-status.json
  python3 - <<'PY'
import json
health=json.load(open("/tmp/hhs-vm-public-health.json"))
openapi=json.load(open("/tmp/hhs-vm-public-openapi.json"))
status=json.load(open("/tmp/hhs-vm-public-status.json"))
assert health["ok"] is True
assert health["security_configured"] is True
assert health["ubuntu_desktop_components_present"] is True
assert openapi["x-hhs-application-vm"]["backend_first"] is True
assert "HhsCapabilityToken" in openapi["components"]["securitySchemes"]
assert status["single_vm81_authority_preserved"] is True
assert status["frontend_attached"] is False
PY
fi

echo "HHS_APPLICATION_VM_BACKEND_CONTROL_PLANE_VERIFIED"

nm -D "$RUNTIME_SO" | grep -Eq ' hhs_validate_abicommand -v "$CLI" >/dev/null 2>&1 || { echo "hhs-vm CLI missing" >&2; exit 2; }
command -v ss >/dev/null 2>&1 || { echo "ss command missing" >&2; exit 2; }

health="$(curl --fail --silent "$BASE/health")"
printf '%s' "$health" | python3 -c '
import json,sys
p=json.load(sys.stdin)
assert p["ok"] is True
assert p["security_configured"] is True
assert p["ubuntu"] is True
assert p["ubuntu_desktop_components_present"] is True
assert p["frontend_attached"] is False
assert p["new_vm81_authority"] is False
'

listener="$(ss -H -ltn "sport = :$PORT")"
[[ -n "$listener" ]] || { echo "application VM listener missing on port $PORT" >&2; exit 3; }
if printf '%s\n' "$listener" | awk '{print $4}' | grep -Ev '^(127\.0\.0\.1|\[::1\]):' >/dev/null; then
  echo "application VM listener is not loopback-only" >&2
  printf '%s\n' "$listener" >&2
  exit 3
fi

cli_status="$("$CLI" status)"
printf '%s' "$cli_status" | python3 -c '
import json,sys
p=json.load(sys.stdin)
assert p["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
assert p["frontend_attached"] is False
assert p["single_vm81_authority_preserved"] is True
assert p["desktop"]["ubuntu"] is True
assert p["desktop"]["ubuntu_desktop_components_present"] is True
'

token="$("$CLI" token issue \
  --principal verifier \
  --scope runtime.mutate \
  --scope workspace:read \
  --scope workspace:write \
  --scope artifact:read \
  --scope artifact:write \
  --ttl 300 | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"

auth="Authorization: HHS-Capability $token"

"$CLI" --capability-token "$token" shell -- hhs status >/tmp/hhs-vm-cli-shell.json
curl --fail --silent -H "$auth" "$BASE/v1/vm/status" >/tmp/hhs-vm-status.json
curl --fail --silent -H "$auth" "$BASE/v1/vm/capabilities" >/tmp/hhs-vm-capabilities.json
curl --fail --silent -H "$auth" -H 'Content-Type: application/json' \
  -d '{"command":"hhs status"}' "$BASE/v1/vm/shell" >/tmp/hhs-vm-shell.json
curl --fail --silent "$BASE/openapi.json" >/tmp/hhs-vm-openapi.json

python3 - <<'PY'
import json
status=json.load(open("/tmp/hhs-vm-status.json"))
caps=json.load(open("/tmp/hhs-vm-capabilities.json"))
shell=json.load(open("/tmp/hhs-vm-shell.json"))
cli_shell=json.load(open("/tmp/hhs-vm-cli-shell.json"))
openapi=json.load(open("/tmp/hhs-vm-openapi.json"))
assert status["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
assert status["frontend_attached"] is False
assert status["single_vm81_authority_preserved"] is True
assert status["desktop"]["ubuntu"] is True
assert status["desktop"]["ubuntu_desktop_components_present"] is True
assert caps["operation_count"] == 52
assert shell["operation_id"] == "system.status"
assert cli_shell["operation_id"] == "system.status"
assert openapi["x-hhs-application-vm"]["frontend_attached"] is False
assert "HhsCapabilityToken" in openapi["components"]["securitySchemes"]
PY

unauth_code="$(curl --silent --output /tmp/hhs-vm-unauth.json --write-out '%{http_code}' "$BASE/v1/vm/status")"
[[ "$unauth_code" == "401" ]] || {
  echo "unauthenticated status returned HTTP $unauth_code instead of 401" >&2
  exit 3
}

if [[ -n "${HHS_APPLICATION_VM_PUBLIC_BASE:-}" ]]; then
  PUBLIC="${HHS_APPLICATION_VM_PUBLIC_BASE%/}"
  curl --fail --silent --show-error "$PUBLIC/health" >/tmp/hhs-vm-public-health.json
  curl --fail --silent --show-error "$PUBLIC/openapi.json" >/tmp/hhs-vm-public-openapi.json
  public_unauth="$(curl --silent --show-error --output /tmp/hhs-vm-public-unauth.json --write-out '%{http_code}' "$PUBLIC/v1/vm/status")"
  [[ "$public_unauth" == "401" ]] || {
    echo "public unauthenticated status returned HTTP $public_unauth instead of 401" >&2
    exit 4
  }
  curl --fail --silent --show-error -H "$auth" "$PUBLIC/v1/vm/status" >/tmp/hhs-vm-public-status.json
  python3 - <<'PY'
import json
health=json.load(open("/tmp/hhs-vm-public-health.json"))
openapi=json.load(open("/tmp/hhs-vm-public-openapi.json"))
status=json.load(open("/tmp/hhs-vm-public-status.json"))
assert health["ok"] is True
assert health["security_configured"] is True
assert health["ubuntu_desktop_components_present"] is True
assert openapi["x-hhs-application-vm"]["backend_first"] is True
assert "HhsCapabilityToken" in openapi["components"]["securitySchemes"]
assert status["single_vm81_authority_preserved"] is True
assert status["frontend_attached"] is False
PY
fi

echo "HHS_APPLICATION_VM_BACKEND_CONTROL_PLANE_VERIFIED"

nm -D "$RUNTIME_SO" | grep -Eq ' hhs_exact_abi_validatecommand -v "$CLI" >/dev/null 2>&1 || { echo "hhs-vm CLI missing" >&2; exit 2; }
command -v ss >/dev/null 2>&1 || { echo "ss command missing" >&2; exit 2; }

health="$(curl --fail --silent "$BASE/health")"
printf '%s' "$health" | python3 -c '
import json,sys
p=json.load(sys.stdin)
assert p["ok"] is True
assert p["security_configured"] is True
assert p["ubuntu"] is True
assert p["ubuntu_desktop_components_present"] is True
assert p["frontend_attached"] is False
assert p["new_vm81_authority"] is False
'

listener="$(ss -H -ltn "sport = :$PORT")"
[[ -n "$listener" ]] || { echo "application VM listener missing on port $PORT" >&2; exit 3; }
if printf '%s\n' "$listener" | awk '{print $4}' | grep -Ev '^(127\.0\.0\.1|\[::1\]):' >/dev/null; then
  echo "application VM listener is not loopback-only" >&2
  printf '%s\n' "$listener" >&2
  exit 3
fi

cli_status="$("$CLI" status)"
printf '%s' "$cli_status" | python3 -c '
import json,sys
p=json.load(sys.stdin)
assert p["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
assert p["frontend_attached"] is False
assert p["single_vm81_authority_preserved"] is True
assert p["desktop"]["ubuntu"] is True
assert p["desktop"]["ubuntu_desktop_components_present"] is True
'

token="$("$CLI" token issue \
  --principal verifier \
  --scope runtime.mutate \
  --scope workspace:read \
  --scope workspace:write \
  --scope artifact:read \
  --scope artifact:write \
  --ttl 300 | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"

auth="Authorization: HHS-Capability $token"

"$CLI" --capability-token "$token" shell -- hhs status >/tmp/hhs-vm-cli-shell.json
curl --fail --silent -H "$auth" "$BASE/v1/vm/status" >/tmp/hhs-vm-status.json
curl --fail --silent -H "$auth" "$BASE/v1/vm/capabilities" >/tmp/hhs-vm-capabilities.json
curl --fail --silent -H "$auth" -H 'Content-Type: application/json' \
  -d '{"command":"hhs status"}' "$BASE/v1/vm/shell" >/tmp/hhs-vm-shell.json
curl --fail --silent "$BASE/openapi.json" >/tmp/hhs-vm-openapi.json

python3 - <<'PY'
import json
status=json.load(open("/tmp/hhs-vm-status.json"))
caps=json.load(open("/tmp/hhs-vm-capabilities.json"))
shell=json.load(open("/tmp/hhs-vm-shell.json"))
cli_shell=json.load(open("/tmp/hhs-vm-cli-shell.json"))
openapi=json.load(open("/tmp/hhs-vm-openapi.json"))
assert status["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
assert status["frontend_attached"] is False
assert status["single_vm81_authority_preserved"] is True
assert status["desktop"]["ubuntu"] is True
assert status["desktop"]["ubuntu_desktop_components_present"] is True
assert caps["operation_count"] == 52
assert shell["operation_id"] == "system.status"
assert cli_shell["operation_id"] == "system.status"
assert openapi["x-hhs-application-vm"]["frontend_attached"] is False
assert "HhsCapabilityToken" in openapi["components"]["securitySchemes"]
PY

unauth_code="$(curl --silent --output /tmp/hhs-vm-unauth.json --write-out '%{http_code}' "$BASE/v1/vm/status")"
[[ "$unauth_code" == "401" ]] || {
  echo "unauthenticated status returned HTTP $unauth_code instead of 401" >&2
  exit 3
}

if [[ -n "${HHS_APPLICATION_VM_PUBLIC_BASE:-}" ]]; then
  PUBLIC="${HHS_APPLICATION_VM_PUBLIC_BASE%/}"
  curl --fail --silent --show-error "$PUBLIC/health" >/tmp/hhs-vm-public-health.json
  curl --fail --silent --show-error "$PUBLIC/openapi.json" >/tmp/hhs-vm-public-openapi.json
  public_unauth="$(curl --silent --show-error --output /tmp/hhs-vm-public-unauth.json --write-out '%{http_code}' "$PUBLIC/v1/vm/status")"
  [[ "$public_unauth" == "401" ]] || {
    echo "public unauthenticated status returned HTTP $public_unauth instead of 401" >&2
    exit 4
  }
  curl --fail --silent --show-error -H "$auth" "$PUBLIC/v1/vm/status" >/tmp/hhs-vm-public-status.json
  python3 - <<'PY'
import json
health=json.load(open("/tmp/hhs-vm-public-health.json"))
openapi=json.load(open("/tmp/hhs-vm-public-openapi.json"))
status=json.load(open("/tmp/hhs-vm-public-status.json"))
assert health["ok"] is True
assert health["security_configured"] is True
assert health["ubuntu_desktop_components_present"] is True
assert openapi["x-hhs-application-vm"]["backend_first"] is True
assert "HhsCapabilityToken" in openapi["components"]["securitySchemes"]
assert status["single_vm81_authority_preserved"] is True
assert status["frontend_attached"] is False
PY
fi

echo "HHS_APPLICATION_VM_BACKEND_CONTROL_PLANE_VERIFIED"

nm -D "$RUNTIME_SO" | grep -Eq ' hhs_hash216_computecommand -v "$CLI" >/dev/null 2>&1 || { echo "hhs-vm CLI missing" >&2; exit 2; }
command -v ss >/dev/null 2>&1 || { echo "ss command missing" >&2; exit 2; }

health="$(curl --fail --silent "$BASE/health")"
printf '%s' "$health" | python3 -c '
import json,sys
p=json.load(sys.stdin)
assert p["ok"] is True
assert p["security_configured"] is True
assert p["ubuntu"] is True
assert p["ubuntu_desktop_components_present"] is True
assert p["frontend_attached"] is False
assert p["new_vm81_authority"] is False
'

listener="$(ss -H -ltn "sport = :$PORT")"
[[ -n "$listener" ]] || { echo "application VM listener missing on port $PORT" >&2; exit 3; }
if printf '%s\n' "$listener" | awk '{print $4}' | grep -Ev '^(127\.0\.0\.1|\[::1\]):' >/dev/null; then
  echo "application VM listener is not loopback-only" >&2
  printf '%s\n' "$listener" >&2
  exit 3
fi

cli_status="$("$CLI" status)"
printf '%s' "$cli_status" | python3 -c '
import json,sys
p=json.load(sys.stdin)
assert p["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
assert p["frontend_attached"] is False
assert p["single_vm81_authority_preserved"] is True
assert p["desktop"]["ubuntu"] is True
assert p["desktop"]["ubuntu_desktop_components_present"] is True
'

token="$("$CLI" token issue \
  --principal verifier \
  --scope runtime.mutate \
  --scope workspace:read \
  --scope workspace:write \
  --scope artifact:read \
  --scope artifact:write \
  --ttl 300 | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"

auth="Authorization: HHS-Capability $token"

"$CLI" --capability-token "$token" shell -- hhs status >/tmp/hhs-vm-cli-shell.json
curl --fail --silent -H "$auth" "$BASE/v1/vm/status" >/tmp/hhs-vm-status.json
curl --fail --silent -H "$auth" "$BASE/v1/vm/capabilities" >/tmp/hhs-vm-capabilities.json
curl --fail --silent -H "$auth" -H 'Content-Type: application/json' \
  -d '{"command":"hhs status"}' "$BASE/v1/vm/shell" >/tmp/hhs-vm-shell.json
curl --fail --silent "$BASE/openapi.json" >/tmp/hhs-vm-openapi.json

python3 - <<'PY'
import json
status=json.load(open("/tmp/hhs-vm-status.json"))
caps=json.load(open("/tmp/hhs-vm-capabilities.json"))
shell=json.load(open("/tmp/hhs-vm-shell.json"))
cli_shell=json.load(open("/tmp/hhs-vm-cli-shell.json"))
openapi=json.load(open("/tmp/hhs-vm-openapi.json"))
assert status["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
assert status["frontend_attached"] is False
assert status["single_vm81_authority_preserved"] is True
assert status["desktop"]["ubuntu"] is True
assert status["desktop"]["ubuntu_desktop_components_present"] is True
assert caps["operation_count"] == 52
assert shell["operation_id"] == "system.status"
assert cli_shell["operation_id"] == "system.status"
assert openapi["x-hhs-application-vm"]["frontend_attached"] is False
assert "HhsCapabilityToken" in openapi["components"]["securitySchemes"]
PY

unauth_code="$(curl --silent --output /tmp/hhs-vm-unauth.json --write-out '%{http_code}' "$BASE/v1/vm/status")"
[[ "$unauth_code" == "401" ]] || {
  echo "unauthenticated status returned HTTP $unauth_code instead of 401" >&2
  exit 3
}

if [[ -n "${HHS_APPLICATION_VM_PUBLIC_BASE:-}" ]]; then
  PUBLIC="${HHS_APPLICATION_VM_PUBLIC_BASE%/}"
  curl --fail --silent --show-error "$PUBLIC/health" >/tmp/hhs-vm-public-health.json
  curl --fail --silent --show-error "$PUBLIC/openapi.json" >/tmp/hhs-vm-public-openapi.json
  public_unauth="$(curl --silent --show-error --output /tmp/hhs-vm-public-unauth.json --write-out '%{http_code}' "$PUBLIC/v1/vm/status")"
  [[ "$public_unauth" == "401" ]] || {
    echo "public unauthenticated status returned HTTP $public_unauth instead of 401" >&2
    exit 4
  }
  curl --fail --silent --show-error -H "$auth" "$PUBLIC/v1/vm/status" >/tmp/hhs-vm-public-status.json
  python3 - <<'PY'
import json
health=json.load(open("/tmp/hhs-vm-public-health.json"))
openapi=json.load(open("/tmp/hhs-vm-public-openapi.json"))
status=json.load(open("/tmp/hhs-vm-public-status.json"))
assert health["ok"] is True
assert health["security_configured"] is True
assert health["ubuntu_desktop_components_present"] is True
assert openapi["x-hhs-application-vm"]["backend_first"] is True
assert "HhsCapabilityToken" in openapi["components"]["securitySchemes"]
assert status["single_vm81_authority_preserved"] is True
assert status["frontend_attached"] is False
PY
fi

echo "HHS_APPLICATION_VM_BACKEND_CONTROL_PLANE_VERIFIED"

if command -v ldd >/dev/null 2>&1 && ldd "$RUNTIME_SO" | grep -q 'not found'; then
  ldd "$RUNTIME_SO" >&2 || true
  exit 2
fi
PYTHONPATH="$HHS_APPLICATION_VM_REPOSITORY_ROOT${PYTHONPATH:+:$PYTHONPATH}" \
HHS_DISABLE_C_AUTOBUILD=1 \
"${HHS_APPLICATION_VM_PYTHON_BIN:?missing Python runtime}" - <<'PY'
import hhs_python.runtime.hhs_ctypes_bridge
import hhs_python.runtime.hhs_exact_ctypes_bridge
print("HHS_APPLICATION_VM_NATIVE_RUNTIME_LOAD_VERIFIED")
PY

command -v "$CLI" >/dev/null 2>&1 || { echo "hhs-vm CLI missing" >&2; exit 2; }
command -v ss >/dev/null 2>&1 || { echo "ss command missing" >&2; exit 2; }

health="$(curl --fail --silent "$BASE/health")"
printf '%s' "$health" | python3 -c '
import json,sys
p=json.load(sys.stdin)
assert p["ok"] is True
assert p["security_configured"] is True
assert p["ubuntu"] is True
assert p["ubuntu_desktop_components_present"] is True
assert p["frontend_attached"] is False
assert p["new_vm81_authority"] is False
'

listener="$(ss -H -ltn "sport = :$PORT")"
[[ -n "$listener" ]] || { echo "application VM listener missing on port $PORT" >&2; exit 3; }
if printf '%s\n' "$listener" | awk '{print $4}' | grep -Ev '^(127\.0\.0\.1|\[::1\]):' >/dev/null; then
  echo "application VM listener is not loopback-only" >&2
  printf '%s\n' "$listener" >&2
  exit 3
fi

cli_status="$("$CLI" status)"
printf '%s' "$cli_status" | python3 -c '
import json,sys
p=json.load(sys.stdin)
assert p["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
assert p["frontend_attached"] is False
assert p["single_vm81_authority_preserved"] is True
assert p["desktop"]["ubuntu"] is True
assert p["desktop"]["ubuntu_desktop_components_present"] is True
'

token="$("$CLI" token issue \
  --principal verifier \
  --scope runtime.mutate \
  --scope workspace:read \
  --scope workspace:write \
  --scope artifact:read \
  --scope artifact:write \
  --ttl 300 | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"

auth="Authorization: HHS-Capability $token"

"$CLI" --capability-token "$token" shell -- hhs status >/tmp/hhs-vm-cli-shell.json
curl --fail --silent -H "$auth" "$BASE/v1/vm/status" >/tmp/hhs-vm-status.json
curl --fail --silent -H "$auth" "$BASE/v1/vm/capabilities" >/tmp/hhs-vm-capabilities.json
curl --fail --silent -H "$auth" -H 'Content-Type: application/json' \
  -d '{"command":"hhs status"}' "$BASE/v1/vm/shell" >/tmp/hhs-vm-shell.json
curl --fail --silent "$BASE/openapi.json" >/tmp/hhs-vm-openapi.json

python3 - <<'PY'
import json
status=json.load(open("/tmp/hhs-vm-status.json"))
caps=json.load(open("/tmp/hhs-vm-capabilities.json"))
shell=json.load(open("/tmp/hhs-vm-shell.json"))
cli_shell=json.load(open("/tmp/hhs-vm-cli-shell.json"))
openapi=json.load(open("/tmp/hhs-vm-openapi.json"))
assert status["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
assert status["frontend_attached"] is False
assert status["single_vm81_authority_preserved"] is True
assert status["desktop"]["ubuntu"] is True
assert status["desktop"]["ubuntu_desktop_components_present"] is True
assert caps["operation_count"] == 52
assert shell["operation_id"] == "system.status"
assert cli_shell["operation_id"] == "system.status"
assert openapi["x-hhs-application-vm"]["frontend_attached"] is False
assert "HhsCapabilityToken" in openapi["components"]["securitySchemes"]
PY

unauth_code="$(curl --silent --output /tmp/hhs-vm-unauth.json --write-out '%{http_code}' "$BASE/v1/vm/status")"
[[ "$unauth_code" == "401" ]] || {
  echo "unauthenticated status returned HTTP $unauth_code instead of 401" >&2
  exit 3
}

if [[ -n "${HHS_APPLICATION_VM_PUBLIC_BASE:-}" ]]; then
  PUBLIC="${HHS_APPLICATION_VM_PUBLIC_BASE%/}"
  curl --fail --silent --show-error "$PUBLIC/health" >/tmp/hhs-vm-public-health.json
  curl --fail --silent --show-error "$PUBLIC/openapi.json" >/tmp/hhs-vm-public-openapi.json
  public_unauth="$(curl --silent --show-error --output /tmp/hhs-vm-public-unauth.json --write-out '%{http_code}' "$PUBLIC/v1/vm/status")"
  [[ "$public_unauth" == "401" ]] || {
    echo "public unauthenticated status returned HTTP $public_unauth instead of 401" >&2
    exit 4
  }
  curl --fail --silent --show-error -H "$auth" "$PUBLIC/v1/vm/status" >/tmp/hhs-vm-public-status.json
  python3 - <<'PY'
import json
health=json.load(open("/tmp/hhs-vm-public-health.json"))
openapi=json.load(open("/tmp/hhs-vm-public-openapi.json"))
status=json.load(open("/tmp/hhs-vm-public-status.json"))
assert health["ok"] is True
assert health["security_configured"] is True
assert health["ubuntu_desktop_components_present"] is True
assert openapi["x-hhs-application-vm"]["backend_first"] is True
assert "HhsCapabilityToken" in openapi["components"]["securitySchemes"]
assert status["single_vm81_authority_preserved"] is True
assert status["frontend_attached"] is False
PY
fi

echo "HHS_APPLICATION_VM_BACKEND_CONTROL_PLANE_VERIFIED"
