import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const routesUrl = new URL('../../../hhs_backend/api/pass175_runtime_routes.py', import.meta.url);

test('Pass 175 status remains bounded before VM5184 fabric materialization', async () => {
  const source = await readFile(routesUrl, 'utf8');
  const bounded = source.match(
    /def bounded_status\(\) -> dict\[str, Any\]:[\s\S]*?\n\n@router\.get\("\/authority"\)/,
  );
  assert.ok(bounded, 'bounded Pass 175 status function is present');
  assert.match(bounded[0], /if _RUNTIME is not None:/);
  assert.match(bounded[0], /"heavy_fabric_materialized": _RUNTIME is not None/);
  assert.match(bounded[0], /"bounded_status_read": True/);
  assert.match(bounded[0], /"singleton_vm81_commit_authority": True/);
  assert.match(bounded[0], /"hash72_commit_streams": 1/);
  assert.doesNotMatch(bounded[0], /get_runtime\(\)/);
});

test('Pass 175 retains an explicit materialized status route', async () => {
  const source = await readFile(routesUrl, 'utf8');
  assert.match(source, /@router\.get\("\/status"\)\ndef status\(\)[\s\S]*?return bounded_status\(\)/);
  assert.match(source, /@router\.get\("\/status\/materialized"\)/);
  assert.match(source, /payload = dict\(get_runtime\(\)\.status\(\)\)/);
  assert.match(source, /"bounded_status_read"\] = False/);
  assert.match(source, /@router\.get\("\/authority"\)/);
  assert.match(source, /"authority_witness_only": True/);
});
