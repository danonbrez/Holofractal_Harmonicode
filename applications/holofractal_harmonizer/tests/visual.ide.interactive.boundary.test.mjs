import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const visualIdeUrl = new URL('../src/visual-ide.mjs', import.meta.url);

test('visual IDE publication is not awaited behind backend authority hydration', async () => {
  const source = await readFile(visualIdeUrl, 'utf8');
  const backendStage = source.match(
    /stage: 'BACKEND_CAPABILITY_CHECKED',[\s\S]*?run: \(\) => scheduleBackendAuthorityHydration\(\),[\s\S]*?optional: true/,
  );
  assert.ok(backendStage, 'backend capability stage schedules rather than awaits hydration');
  assert.match(source, /function scheduleBackendAuthorityHydration\(\)/);
  assert.match(source, /window\.setTimeout\(\(\) => \{/);
  assert.match(source, /authorityRequiredBeforeAcceptance: true/);
  assert.match(source, /requestJson\('\/api\/health'/);
  assert.match(source, /requestJson\('\/api\/runtime\/live\/status'/);
  assert.match(source, /requestJson\('\/api\/v1\/pass175\/status'/);
  assert.doesNotMatch(source, /requestJson\('\/api\/runtime\/authority\/status'/);
  assert.doesNotMatch(source, /requestJson\('\/api\/product\/health'/);
  assert.match(source, /HHS_PASS_176_BOUNDED_RUNTIME_AUTHORITY_PROJECTION_V2/);
  assert.match(source, /HHS_PASS_176_BOUNDED_RUNTIME_AUTHORITY_EVIDENCE_INPUT_V2/);
  assert.match(source, /canonical_runtime_attached: canonicalRuntimeAttached/);
  assert.match(source, /receipt_hash72: receiptHash72/);
  assert.match(source, /runtime_state_hash72: runtimeStateHash72/);
  assert.match(source, /shadowed_role_authority_route_used: false/);
  assert.match(source, /runtime: runtimeStatus/);
  assert.match(source, /assistantHealthExcluded: true/);
  assert.match(source, /stability\.setAuthorityEvidence\(\{ productHealth, pass175 \}\)/);
  assert.match(source, /HHS_P176_BACKEND_AUTHORITY_EVIDENCE_REJECTED/);
});

test('optional projection hydration yields to the interactive continuation', async () => {
  const source = await readFile(visualIdeUrl, 'utf8');
  const optionalStage = source.match(
    /stage: 'OPTIONAL_REGISTRY_HISTORY_DIAGNOSTICS_LOADING',[\s\S]*?run: \(\) => scheduleOptionalProjectionHydration\(\),[\s\S]*?optional: true/,
  );
  assert.ok(optionalStage, 'optional projection stage delegates to the task scheduler');
  const scheduler = source.match(
    /function scheduleOptionalProjectionHydration\(\) \{[\s\S]*?return \{ deferred: true, taskBounded: true, count: initializers\.length \};[\s\S]*?\n\}/,
  );
  assert.ok(scheduler, 'optional projection scheduler is present');
  assert.match(scheduler[0], /window\.setTimeout/);
  assert.doesNotMatch(scheduler[0], /queueMicrotask/);
  assert.match(scheduler[0], /initIntegratedWorkbench/);
  assert.match(scheduler[0], /initIntuitiveIDE/);
  assert.match(scheduler[0], /initPass175Processor/);
  assert.match(scheduler[0], /initPass175TerminalProcessor/);
});
