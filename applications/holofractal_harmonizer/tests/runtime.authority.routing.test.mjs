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
  assert.match(source, /"runtime_readiness_uses_committed_live_projection": True/);
  assert.match(source, /"runtime_authority_route_deduplicated": True/);
});

test('final FastAPI composition installs event-loop-native bounded Pass 175 status owners', async () => {
  const source = await readFile(serverUrl, 'utf8');
  assert.match(source, /from hhs_backend\.api import pass175_runtime_routes as pass175_runtime_api/);
  assert.match(source, /PASS175_AUTHORITY_STATUS_PATH = "\/api\/v1\/pass175\/authority"/);
  assert.match(source, /PASS175_BOUNDED_STATUS_PATH = "\/api\/v1\/pass175\/status"/);
  assert.match(source, /PASS175_MATERIALIZED_STATUS_PATH = "\/api\/v1\/pass175\/status\/materialized"/);
  assert.match(source, /if str\(getattr\(route, "path", ""\)\) not in PASS175_FINAL_STATUS_PATHS/);
  assert.match(source, /async def final_pass175_authority_status\(\)/);
  assert.match(source, /return pass175_runtime_api\.authority_witness\(\)/);
  assert.match(source, /async def final_pass175_bounded_status\(\)/);
  assert.match(source, /return pass175_runtime_api\.bounded_status\(\)/);
  assert.match(source, /PASS175_AUTHORITY_STATUS_PATH,[\s\S]*final_pass175_authority_status/);
  assert.match(source, /PASS175_BOUNDED_STATUS_PATH,[\s\S]*final_pass175_bounded_status/);
  assert.match(source, /PASS175_MATERIALIZED_STATUS_PATH,[\s\S]*pass175_runtime_api\.materialized_status/);
  assert.match(source, /name="hhs-pass175-bounded-status"/);
  assert.match(source, /"pass175_status_routes_deduplicated": True/);
  assert.match(source, /"pass175_bounded_status_async": True/);
  assert.match(source, /"pass175_authority_witness_async": True/);
  assert.match(source, /"pass175_materialized_status_worker_isolated": True/);
  assert.doesNotMatch(source, /async def final_pass175_(?:authority|bounded)_status\(\)[\s\S]{0,200}get_runtime\(\)/);
});

test('final health route is pure process liveness and never traverses runtime objects', async () => {
  const source = await readFile(serverUrl, 'utf8');
  assert.match(source, /FINAL_HEALTH_PATHS = frozenset\(\{"\/health", "\/api\/health"\}\)/);
  assert.match(source, /if str\(getattr\(route, "path", ""\)\) not in FINAL_HEALTH_PATHS/);
  assert.match(source, /"\/health",\s*application_ide_liveness/);
  assert.match(source, /"\/api\/health",\s*application_ide_liveness/);
  assert.match(source, /name="hhs-full-ide-health"/);
  assert.match(source, /name="hhs-full-ide-api-health"/);
  assert.match(source, /"health_routes_deduplicated": True/);
  assert.match(source, /"health_route_owner": "FINAL_APPLICATION_IDE_PROCESS_LIVENESS"/);
  assert.match(source, /"runtime_object_traversal_performed": False/);
  assert.match(source, /"service_registry_traversal_performed": False/);
  assert.match(source, /"runtime_authority_probe_separate": True/);
  const healthBody = source.match(/async def application_ide_liveness\(\)[\s\S]*?\n\n# Health has accumulated/)?.[0] || '';
  assert.doesNotMatch(healthBody, /_runtime_authority_status|authority_status\(|service_registry\.services/);
  assert.doesNotMatch(source, /if not _has_exact_route\("\/api\/health"\)/);
});

test('final runtime service catalog is isolated from the FastAPI event loop', async () => {
  const source = await readFile(serverUrl, 'utf8');
  assert.match(source, /RUNTIME_SERVICES_PATH = "\/api\/runtime\/services"/);
  assert.match(source, /def _runtime_services_projection\(\)/);
  assert.match(source, /runtime_api\.runtime_emulator\.service_registry\.services\(\)/);
  assert.match(source, /async def final_runtime_services\(\)/);
  assert.match(source, /return await asyncio\.to_thread\(_runtime_services_projection\)/);
  assert.match(source, /if str\(getattr\(route, "path", ""\)\) != RUNTIME_SERVICES_PATH/);
  assert.match(source, /name="hhs-final-runtime-services"/);
  assert.match(source, /"runtime_services_route_deduplicated": True/);
  assert.match(source, /"runtime_services_worker_isolated": True/);
});