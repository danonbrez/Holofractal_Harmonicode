#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${HHS_APPLICATION_VM_ENV_FILE:-/etc/hhs/application-vm.env}"
[[ -r "$ENV_FILE" ]] || { echo "env file not readable: $ENV_FILE" >&2; exit 2; }
# shellcheck disable=SC1090
source "$ENV_FILE"

BASE="http://${HHS_APPLICATION_VM_HOST:-127.0.0.1}:${HHS_APPLICATION_VM_PORT:-8720}"

health="$(curl --fail --silent "$BASE/health")"
python3 - <<PY
import json
p=json.loads('''$health''')
assert p["ok"] is True
assert p["security_configured"] is True
assert p["frontend_attached"] is False
assert p["new_vm81_authority"] is False
PY

token="$(python3 -m hhs_runtime.pass220.application_vm_cli   --env-file "$ENV_FILE" token issue   --principal verifier   --scope runtime.mutate   --scope workspace:read   --scope workspace:write   --scope artifact:read   --scope artifact:write   --ttl 300 | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"

auth="Authorization: HHS-Capability $token"

curl --fail --silent -H "$auth" "$BASE/v1/vm/status" >/tmp/hhs-vm-status.json
curl --fail --silent -H "$auth" "$BASE/v1/vm/capabilities" >/tmp/hhs-vm-capabilities.json
curl --fail --silent -H "$auth" -H 'Content-Type: application/json'   -d '{"command":"hhs status"}' "$BASE/v1/vm/shell" >/tmp/hhs-vm-shell.json
curl --fail --silent "$BASE/openapi.json" >/tmp/hhs-vm-openapi.json

python3 - <<'PY'
import json
status=json.load(open("/tmp/hhs-vm-status.json"))
caps=json.load(open("/tmp/hhs-vm-capabilities.json"))
shell=json.load(open("/tmp/hhs-vm-shell.json"))
openapi=json.load(open("/tmp/hhs-vm-openapi.json"))
assert status["schema"] == "HHS_PASS_220_UBUNTU_APPLICATION_VM_CONTROL_PLANE_V1"
assert status["frontend_attached"] is False
assert status["single_vm81_authority_preserved"] is True
assert caps["operation_count"] == 52
assert shell["operation_id"] == "system.status"
assert openapi["x-hhs-application-vm"]["frontend_attached"] is False
assert "HhsCapabilityToken" in openapi["components"]["securitySchemes"]
PY

if curl --silent --fail "$BASE/v1/vm/status" >/dev/null 2>&1; then
  echo "unauthenticated status unexpectedly succeeded" >&2
  exit 3
fi

echo "HHS_APPLICATION_VM_BACKEND_CONTROL_PLANE_VERIFIED"
