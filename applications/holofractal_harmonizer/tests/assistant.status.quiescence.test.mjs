import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const deploymentHealthUrl = new URL('../src/deployment-health.mjs', import.meta.url);
const nativeProviderUrl = new URL(
  '../../../hhs_backend/runtime/hhs_native_litert_lm_provider_v1.py',
  import.meta.url,
);

test('optional Word2Vec does not enter native assistant status critical path', async () => {
  const source = await readFile(nativeProviderUrl, 'utf8');

  assert.match(source, /import asyncio/);
  assert.match(source, /if self\.require_word2vec or self\._word2vec_service is not None:/);
  assert.match(source, /HHS_PASS_166_WORD2VEC_OPTIONAL_UNPROBED/);
  assert.match(source, /async def list_models[\s\S]*await asyncio\.to_thread\(self\._require_ready\)/);
  assert.match(source, /async def chat_completion[\s\S]*await asyncio\.to_thread\(self\._require_ready\)/);
});

test('successful assistant status restores the visible online projection', async () => {
  const source = await readFile(deploymentHealthUrl, 'utf8');
  const update = source.match(/function updateAssistantSurface\(\) \{[\s\S]*?\n\}/);

  assert.ok(update, 'deployment health assistant projection exists');
  assert.match(update[0], /if \(current\.assistantReady\) \{/);
  assert.match(update[0], /ASSISTANT ONLINE/);
  assert.match(update[0], /status online/);
  assert.doesNotMatch(update[0], /if \(current\.assistantReady\) return;/);
});
