import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const read = (path) => readFileSync(resolve(root, path), 'utf8');

test('theme bootstrap is independent from the IDE application module', () => {
  const startup = read('src/production-startup-coordinator.mjs');
  const theme = read('src/theme-bootstrap.mjs');
  assert.match(startup, /import '\.\/theme-bootstrap\.mjs'/);
  assert.match(theme, /hhs-harmonic-studio-theme/);
  assert.match(theme, /harmonic-studio-theme\.css/);
  assert.match(theme, /integrated-workbench\.css/);
});

test('integrated workbench runs local web applications and previews modalities', () => {
  const source = read('src/integrated-workbench.mjs');
  for (const token of [
    'ide-application-frame',
    'allow-scripts allow-forms allow-modals allow-downloads',
    'inlineProjectReferences',
    'image/',
    'audio/',
    'video/',
    'application/pdf',
    'Open Window',
    'Application preview console',
  ]) assert.ok(source.includes(token), `missing ${token}`);
  assert.doesNotMatch(source, /allow-same-origin/);
});

test('repository history is an IDE subsystem rather than a replacement landing page', () => {
  const source = read('src/integrated-workbench.mjs');
  const ide = read('src/visual-ide.mjs');
  for (const endpoint of [
    '/api/runtime/repository/status',
    '/api/runtime/repository/passes',
    '/api/runtime/repository/commits',
    '/api/runtime/repository/file',
  ]) assert.ok(source.includes(endpoint), `missing ${endpoint}`);
  assert.match(source, /PASS CONSTRAINTS \+ HISTORY/);
  assert.match(source, /The editor remains the primary product surface/);

  const lifecycle = ide.indexOf("safeInit('project-lifecycle', initProjectLifecycle)");
  const workbench = ide.indexOf("safeInit('integrated-workbench', initIntegratedWorkbench, { optional: true })");
  const interactive = ide.indexOf("stage: 'INTERACTIVE'");
  assert.ok(lifecycle >= 0, 'project lifecycle is not initialized through Pass 176 safety');
  assert.ok(workbench >= 0, 'repository workbench is not initialized through Pass 176 safety');
  assert.ok(interactive >= 0, 'Pass 176 ordered boot does not expose INTERACTIVE');
  assert.ok(lifecycle < workbench, 'optional repository history must initialize after project lifecycle');
  assert.match(ide, /OPTIONAL_REGISTRY_HISTORY_DIAGNOSTICS_LOADING/);
  assert.match(ide, /queueMicrotask\(/);
});
