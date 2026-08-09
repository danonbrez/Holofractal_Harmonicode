import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const sourceUrl = new URL('../src/integrated-assistant.mjs', import.meta.url);

async function source() {
  return readFile(sourceUrl, 'utf8');
}

test('Explorer Assistant launcher preserves DOM identity and delegates user intent', async () => {
  const text = await source();
  assert.doesNotMatch(text, /cloneNode\s*\(/);
  assert.doesNotMatch(text, /replaceWith\s*\(/);
  assert.match(text, /document\.addEventListener\('click',[\s\S]*?#assistant-home[\s\S]*?stopImmediatePropagation\(\)[\s\S]*?openIntegratedAssistant\(\)[\s\S]*?}, true\)/);
  assert.match(text, /explorer_launcher_delegated:\s*true/);
});
