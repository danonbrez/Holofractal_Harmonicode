import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const assistantUrl = new URL('../src/integrated-assistant.mjs', import.meta.url);

test('simple workflow assistant launcher retains integrated assistant ownership', async () => {
  const source = await readFile(assistantUrl, 'utf8');
  const binding = source.match(
    /function bindSimpleWorkflowLauncher\(\) \{[\s\S]*?\n\}/,
  );
  assert.ok(binding, 'simple workflow launcher binding is present');
  assert.match(binding[0], /closest\('#ide-open-assistant-simple'\)/);
  assert.match(binding[0], /event\.preventDefault\(\)/);
  assert.match(binding[0], /event\.stopImmediatePropagation\(\)/);
  assert.match(binding[0], /openIntegratedAssistant\(\)/);
  assert.match(binding[0], /}, true\);/);
  assert.match(source, /bindSimpleWorkflowLauncher\(\);/);
  assert.match(source, /simple_workflow_launcher_capture_owned:\s*true/);
});
