#!/usr/bin/env bash
# I088 operator-side collector. Does NOT deploy, restart, or touch the updater.
# The pinned Chromium suite DOES exercise live user-facing app workflows.
set -Eeuo pipefail
umask 077
PIN="579dbb58f7f9d99419e73cb4d686901e6d123212"
die(){ printf 'HHS_I088_ACCEPTANCE_BLOCKED: %s\n' "$*" >&2; exit 1; }

APPROVED="$(printenv HHS_I088_OPERATOR_APPROVED || true)"
[[ "$APPROVED" == "YES" ]] ||
  die "explicit operator approval for live Chromium workflow tests required"
BASE="$(printenv HHS_PRODUCTION_BASE_URL || true)"
[[ "$BASE" == https://* && "$BASE" != *"@"* ]] ||
  die "https:// production base URL without credentials required"
ROOT="$(printenv HHS_I088_RELEASE_ROOT || true)"
[[ -d "$ROOT" ]] && git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1 ||
  die "pinned source checkout HHS_I088_RELEASE_ROOT required"
[[ "$(git -C "$ROOT" rev-parse HEAD)" == "$PIN" ]] ||
  die "browser suite checkout not pinned to deployed source"
git -C "$ROOT" diff-index --quiet HEAD -- ||
  die "source checkout changed; use clean pinned checkout"
[[ -f "$ROOT/hhs_gui/scripts/production-live-browser-verify.mjs" ]] ||
  die "canonical pinned Chromium verifier unavailable"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI="$(printenv HHS_I088_NATIVE_CLI_RECEIPT || true)"
PROMOTION="$(printenv HHS_I088_PROMOTION_RECEIPT || true)"
[[ -n "$CLI" && -r "$CLI" ]] || die "native CLI host receipt required"
[[ -n "$PROMOTION" && -r "$PROMOTION" ]] || die "host promotion receipt required"
EVIDENCE="$(printenv HHS_I088_EVIDENCE_DIR || true)"
[[ -n "$EVIDENCE" && "$EVIDENCE" == /* ]] ||
  die "absolute evidence output directory required"
for binary in curl git node python3; do
  command -v "$binary" >/dev/null 2>&1 || die "missing executable $binary"
done
# Certificate-validated TLS: do NOT use -k or disable browser validation.
mkdir -p "$EVIDENCE/public" "$EVIDENCE/chromium"
BASE="$(printf '%s' "$BASE" | sed 's@/$@@')"
for endpoint in system/status interface/status runtime/services; do
  case "$endpoint" in
    system/status) output="system.json";;
    interface/status) output="interface.json";;
    runtime/services) output="services.json";;
  esac
  curl --fail --silent --show-error --location --retry 5 \
    --connect-timeout 10 --max-time 40 \
    "$BASE/api/$endpoint" > "$EVIDENCE/public/$output"
done
curl --fail --silent --show-error --location --retry 5 \
  --connect-timeout 10 --max-time 40 "$BASE/" > "$EVIDENCE/public/root.html"
python3 - "$EVIDENCE/public/interface.json" "$EVIDENCE/public/services.json" "$PIN" <<'PY'
import json,sys
from pathlib import Path
interface=json.loads(Path(sys.argv[1]).read_text())
services=json.loads(Path(sys.argv[2]).read_text()).get("services")
assert interface.get("interface")=="HHS_VISUAL_RUNTIME_OS_WORKSPACE"
assert sys.argv[3] in str(interface.get("asset_root",""))
assert isinstance(services,list) and len(services)>0
print("HHS_I088_PUBLIC_RELEASE_SHA_VERIFIED=1")
PY
COUNT="$(python3 - "$EVIDENCE/public/services.json" <<'PY'
import json,sys
from pathlib import Path
print(len(json.loads(Path(sys.argv[1]).read_text())["services"]))
PY
)"
# Install pinned Playwright 1.55.0 and Chromium on the OPERATOR machine
# before use. Neither installation nor repo checkout is done by this script.
cd "$ROOT/hhs_gui"
node --input-type=module -e 'import("playwright")' ||
  die "Playwright not installed in operator pinned checkout"
HHS_PRODUCTION_BASE_URL="$BASE" \
HHS_PRODUCTION_EXPECTED_SHA="$PIN" \
HHS_PRODUCTION_EXPECTED_SERVICE_COUNT="$COUNT" \
HHS_PRODUCTION_PUBLIC_SERVICE_REGISTRY_FILE="$EVIDENCE/public/services.json" \
HHS_PRODUCTION_BROWSER_IGNORE_HTTPS_ERRORS=0 \
HHS_PRODUCTION_BROWSER_EVIDENCE_DIR="$EVIDENCE/chromium" \
  node scripts/production-live-browser-verify.mjs
python3 "$SCRIPT_DIR/verify_production_native_causal_acceptance_579dbb58.py" \
  --native "$CLI" --promotion "$PROMOTION" \
  --public-system "$EVIDENCE/public/system.json" \
  --public-interface "$EVIDENCE/public/interface.json" \
  --public-services "$EVIDENCE/public/services.json" \
  --public-html "$EVIDENCE/public/root.html" \
  --browser "$EVIDENCE/chromium/production-live-browser.json" \
  --screenshot "$EVIDENCE/chromium/production-live-browser.png" \
  --base-url "$BASE" \
  --output "$EVIDENCE/acceptance-evidence-579dbb58.json"
echo "HHS_I088_PRODUCTION_EVIDENCE_VERIFIED_RELEASE_STILL_BLOCKED=1"
