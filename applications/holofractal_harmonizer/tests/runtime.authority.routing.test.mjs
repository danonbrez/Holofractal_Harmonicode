import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const coordinatorUrl = new URL('../src/production-startup-coordinator.mjs', import.meta.url);
const serverUrl = new URL('../../../hhs_backend/application_ide_server.py', import.meta.url);

test('public boot routes the shadowed authority read through live runtime status', async () => {
  const source = await readFile(coordinatorUrl, 'utf8');
  assert.match(source, /const SHADOWED_AUTHORITY_PATH = '\/api\/runtime\/authority\/status';/);
  assert.match(source, /const LIVE_RUNTIME_STATUS_PATH = '\/api\/runtime\/live\/status';/);
  assert.match(source, /function isShadowedAuthorityRequest\(input, init\)/);
  assert.match(source, /async function fetchLiveRuntimeAuthority\(input, init = \{\}\)/);
  assert.match(source, /normalizeLiveRuntimeAuthority\(liveStatus\)/);
  assert.match(source, /shadowed_role_authority_route_used: false/);
  assert.match(source, /if \(isShadowedAuthorityRequest\(input, init\)\) return fetchLiveRuntimeAuthority\(input, init\);/);
  assert.match(source, /frontend_is_authority: false/);
  assert.match(source, /live_runtime_authority_projection_fail_closed: true/);
});

test('final FastAPI composition retains one bounded production authority route', async () => {
  const source = await readFile(serverUrl, 'utf8');
  assert.match(source, /RUNTIME_AUTHORITY_STATUS_PATH = "\/api\/runtime\/authority\/status"/);
  assert.match(source, /if str\(getattr\(route, "path", ""\)\) != RUNTIME_AUTHORITY_STATUS_PATH/);
  assert.match(source, /production\.production_runtime_authority_status/);
  assert.match(source, /name="hhs-production-runtime-authority-status"/);
  assert.match(source, /runtime = production\._runtime_authority_status\(\)/);
  assert.match(source, /authority_ready = bool\(runtime\.get\("ok"\)\)/);
  assert.match(source, /"runtime_readiness_uses_committed_live_projection": True/);
  assert.match(source, /"runtime_authority_route_deduplicated": True/);
});

test('final FastAPI composition installs only the bounded Pass 175 status owners', async () => {
  const source = await readFile(serverUrl, 'utf8');
  assert.match(source, /from hhs_backend\.api import pass175_runtime_routes as pass175_runtime_api/);
  assert.match(source, /PASS175_AUTHORITY_STATUS_PATH = "\/api\/v1\/pass175\/authority"/);
  assert.match(source, /PASS175_BOUNDED_STATUS_PATH = "\/api\/v1\/pass175\/status"/);
  assert.match(source, /PASS175_MATERIALIZED_STATUS_PATH = "\/api\/v1\/pass175\/status\/materialized"/);
  assert.match(source, /if str\(getattr\(route, "path", ""\)\) not in PASS175_FINAL_STATUS_PATHS/);
  assert.match(source, /pass175_runtime_api\.authority_status/);
  assert.match(source, /pass175_runtime_api\.status/);
  assert.match(source, /pass175_runtime_api\.materialized_status/);
  assert.match(source, /name="hhs-pass175-bounded-status"/);
  assert.match(source, /"pass175_status_routes_deduplicated": True/);
  assert.doesNotMatch(source, /PASS175_FINAL_STATUS_PATHS[\s\S]*get_runtime\(\)/);
});
