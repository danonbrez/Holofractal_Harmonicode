import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const sourceUrl = new URL('../src/integrated-workbench.mjs', import.meta.url);
const visualIdeUrl = new URL('../src/visual-ide.mjs', import.meta.url);

async function source() {
  return readFile(sourceUrl, 'utf8');
}

async function visualIdeSource() {
  return readFile(visualIdeUrl, 'utf8');
}

test('integrated workbench runs local web applications and previews modalities', async () => {
  const text = await source();
  for (const token of [
    'ide-preview-panel',
    'ide-application-frame',
    'inlineProjectReferences',
    'project-local CSS and JavaScript',
    'image/',
    'audio/',
    'video/',
    'application/pdf',
  ]) assert.match(text, new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
});

test('repository history is an IDE subsystem rather than a replacement landing page', async () => {
  const text = await source();
  for (const endpoint of [
    '/api/runtime/repository/status',
    '/api/runtime/repository/passes',
    '/api/runtime/repository/commits',
    '/api/runtime/repository/file',
  ]) assert.match(text, new RegExp(endpoint.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.match(text, /Repository Lineage/);
  assert.match(text, /Pass constraints/);
  assert.match(text, /Commit history/);
});

test('repository lineage hydration is explicitly user initiated', async () => {
  const text = await source();
  const initStart = text.indexOf('export function initIntegratedWorkbench()');
  const initBody = text.slice(initStart);

  assert.ok(initStart >= 0);
  assert.match(text, /function openRepositoryPanel\(mode\)[\s\S]*void loadRepositoryData\(\);/);
  assert.match(text, /lineageHydration: 'USER_INITIATED'/);
  assert.match(text, /ON DEMAND/);
  assert.match(text, /OPEN TO LOAD/);
  assert.doesNotMatch(initBody, /void loadRepositoryData\(\);/);
});

test('primary IDE boots intuitive workflow, integrated assistant, and workbench', async () => {
  const text = await visualIdeSource();
  assert.match(text, /initIntuitiveIDE/);
  assert.match(text, /initIntegratedAssistant/);
  assert.match(text, /initIntegratedWorkbench/);
  assert.match(text, /OPTIONAL_REGISTRY_HISTORY_DIAGNOSTICS_LOADING/);
});