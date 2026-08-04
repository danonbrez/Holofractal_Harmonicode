import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const stateUrl = new URL('../src/visual-ide-state.mjs', import.meta.url);
const healthUrl = new URL('../src/deployment-health.mjs', import.meta.url);

test('unchanged IDE status text preserves DOM identity', async () => {
  const source = await readFile(stateUrl, 'utf8');
  assert.match(source, /const next = String\(value\);/);
  assert.match(source, /if \(node\.textContent === next\) return false;/);
  assert.match(source, /node\.textContent = next;/);
});

test('deployment health observes child mutations through the idempotent text membrane', async () => {
  const source = await readFile(healthUrl, 'utf8');
  assert.match(source, /mutationObserver = new MutationObserver\(\(\) => \{ applyHealthState\(\); repairAssistantInput\(\); dedupePreviewConsole\(\); \}\);/);
  assert.match(source, /mutationObserver\.observe\(document\.body, \{ childList: true, subtree: true \}\);/);
  assert.match(source, /setText\('#hhs-backend-health-title'/);
  assert.match(source, /setText\('#hhs-backend-health-message'/);
  assert.doesNotMatch(source, /characterData:\s*true/);
});
