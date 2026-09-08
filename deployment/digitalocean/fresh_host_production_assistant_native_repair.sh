#!/usr/bin/env bash
set -Eeuo pipefail
umask 022

TARGET_SHA=${TARGET_SHA:?missing TARGET_SHA}
APP_ROOT=${HHS_APP_ROOT:-/opt/hhs/app}
PASS166_ROOT=${HHS_PASS166_PRODUCTION_ROOT:-/var/lib/hhs/pass166}
DROPIN_DIR=${HHS_SERVICE_DROPIN_DIR:-/etc/systemd/system/hhs.service.d}
DROPIN_PATH="$DROPIN_DIR/20-hosted-assistant-native.conf"
SYSTEM_STATUS_URL=${HHS_SYSTEM_STATUS_URL:-http://127.0.0.1:8080/api/system/status}
ASSISTANT_HEALTH_URL=${HHS_ASSISTANT_HEALTH_URL:-http://127.0.0.1:8080/api/assistant/health}
HEALTH_TIMEOUT=${HHS_ASSISTANT_REPAIR_TIMEOUT_SECONDS:-120}

[[ $EUID -eq 0 ]] || {
  echo 'production assistant repair requires root authority' >&2
  exit 2
}
[[ "$TARGET_SHA" =~ ^[0-9a-fA-F]{40}$ ]] || {
  echo "TARGET_SHA is not exact: $TARGET_SHA" >&2
  exit 3
}
[[ -d "$APP_ROOT/.git" ]] || {
  echo "production repository missing: $APP_ROOT" >&2
  exit 4
}
[[ "$(git -C "$APP_ROOT" rev-parse HEAD)" == "$TARGET_SHA" ]] || {
  echo 'production HEAD mismatch' >&2
  exit 5
}
[[ "$(git -C "$APP_ROOT" rev-parse origin/main)" == "$TARGET_SHA" ]] || {
  echo 'production origin/main mismatch' >&2
  exit 6
}
[[ "$(git -C "$APP_ROOT" branch --show-current)" == main ]] || {
  echo 'production checkout is not on main' >&2
  exit 7
}
[[ -z "$(git -C "$APP_ROOT" status --porcelain=v1 --untracked-files=normal)" ]] || {
  echo 'production checkout is dirty before assistant repair' >&2
  git -C "$APP_ROOT" status --short >&2
  exit 8
}
[[ ! -e "$APP_ROOT/.hhs" ]] || {
  echo 'source-tree .hhs state exists before assistant repair' >&2
  exit 9
}
id hhs >/dev/null 2>&1 || {
  echo 'hhs service identity is missing' >&2
  exit 10
}
[[ -f /etc/systemd/system/hhs.service ]] || {
  echo 'hhs.service is not installed' >&2
  exit 11
}

# Prove the requested service configuration is repository-defined hosted
# production behavior rather than a gate relaxation invented by deployment.
grep -Fq 'os.environ.setdefault("HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC", "0")' \
  "$APP_ROOT/hhs_backend/production_server.py"
grep -Fq 'export HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC="${HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC:-0}"' \
  "$APP_ROOT/bin/post_compile"
grep -Fq 'assert installation["word2vec_required"] is False' \
  "$APP_ROOT/tests/test_hhs_production_public_app_v1.py"
grep -Fq 'assert turn["runtime_mutation_admitted"] is False' \
  "$APP_ROOT/tests/test_hhs_production_public_app_v1.py"
echo 'HHS_HOSTED_ASSISTANT_REPOSITORY_POLICY_VERIFIED=1'

install -d -o hhs -g hhs -m 0750 "$PASS166_ROOT"
install -d -m 0755 "$DROPIN_DIR"
cat >"$DROPIN_PATH" <<EOF
[Service]
Environment=HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0
Environment=HHS_PASS166_STORAGE_DIR=$PASS166_ROOT
Environment=HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS=5
EOF
chmod 0644 "$DROPIN_PATH"

systemctl daemon-reload
systemctl reset-failed hhs.service || true
systemctl restart hhs.service

deadline=$((SECONDS + HEALTH_TIMEOUT))
until curl -fsS --connect-timeout 5 --max-time 15 "$SYSTEM_STATUS_URL" >/dev/null; do
  if (( SECONDS >= deadline )); then
    systemctl status hhs.service --no-pager --full >&2 || true
    journalctl -u hhs.service -n 240 --no-pager >&2 || true
    exit 20
  fi
  sleep 2
done

systemctl is-active --quiet hhs.service
service_environment=$(systemctl show hhs.service -p Environment --value)
grep -Fq 'HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0' <<<"$service_environment"
grep -Fq "HHS_PASS166_STORAGE_DIR=$PASS166_ROOT" <<<"$service_environment"
grep -Fq 'HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS=5' <<<"$service_environment"
echo 'HHS_HOSTED_ASSISTANT_SERVICE_ENV_VERIFIED=1'

# Only after the production state path and hosted policy are active may the
# assistant service be initialized. This call is expected to instantiate the
# optional Pass 166 service under /var/lib/hhs, never under the checkout.
deadline=$((SECONDS + HEALTH_TIMEOUT))
until health=$(curl -fsS --connect-timeout 5 --max-time 20 "$ASSISTANT_HEALTH_URL" 2>/dev/null); do
  if (( SECONDS >= deadline )); then
    systemctl status hhs.service --no-pager --full >&2 || true
    journalctl -u hhs.service -n 240 --no-pager >&2 || true
    exit 21
  fi
  sleep 2
done

python3 - "$health" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
assert payload['schema'] == 'HHS_PRODUCTION_ASSISTANT_STATUS_V2', payload
assert payload['ok'] is True, payload
assert payload['online'] is True, payload
assert payload['status'] == 'HHS_PRODUCTION_ASSISTANT_READY', payload
assert payload['selected_provider_id'] == 'provider:hhs.local.text', payload
assert payload['effective_mode'] == 'HHS_NATIVE_LITERT_COMPATIBLE', payload
native = payload['native_hhs']
assert native['ready'] is True, native
installation = native['installation']
assert installation['ready'] is True, installation
assert installation['semantic_membrane_ready'] is True, installation
assert installation['bounded_reasoner_ready'] is True, installation
assert installation['word2vec_required'] is False, installation
assert payload['same_template_response_enabled'] is False, payload
assert payload['repository_search_is_provider'] is False, payload
assert payload['runtime_mutation_admitted'] is False, payload
assert payload.get('status_root_hash72'), payload
print('HHS_HOSTED_ASSISTANT_LOOPBACK_HEALTH=PASS')
print('HHS_HOSTED_ASSISTANT_SELECTED_PROVIDER=' + payload['selected_provider_id'])
print('HHS_HOSTED_ASSISTANT_EFFECTIVE_MODE=' + payload['effective_mode'])
print('HHS_HOSTED_ASSISTANT_STATUS_ROOT_HASH72=' + str(payload['status_root_hash72']))
PY

[[ -d "$PASS166_ROOT" ]] || {
  echo 'Pass 166 production state root disappeared' >&2
  exit 22
}
runuser -u hhs -- test -w "$PASS166_ROOT"
[[ -z "$(git -C "$APP_ROOT" status --porcelain=v1 --untracked-files=normal)" ]] || {
  echo 'assistant initialization dirtied production checkout' >&2
  git -C "$APP_ROOT" status --short >&2
  exit 23
}
[[ ! -e "$APP_ROOT/.hhs" ]] || {
  echo 'assistant initialization recreated source-tree .hhs state' >&2
  exit 24
}

printf 'HHS_HOSTED_ASSISTANT_NATIVE_REPAIR_VERIFIED=1\n'
printf 'HHS_HOSTED_ASSISTANT_PASS166_STATE_ROOT=%s\n' "$PASS166_ROOT"
printf 'HHS_HOSTED_ASSISTANT_PRODUCTION_WORKTREE_CLEAN=1\n'
