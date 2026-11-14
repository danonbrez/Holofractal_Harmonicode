import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { validateProjectBuildInputs } from '../src/project-lifecycle.mjs';

const source = readFileSync(new URL('../src/project-lifecycle.mjs', import.meta.url), 'utf8');

test('project validation accepts more than 64 files', () => {
  const files = Array.from({ length: 80 }, (_, i) => ({ path: 'src/file-' + i + '.ts' }));
  assert.doesNotThrow(() => validateProjectBuildInputs(files, ['C_SOURCE']));
});

test('project validation accepts source manifests larger than historical 24 MiB', () => {
  const files = [{ path: 'assets/model.bin', sourceByteLength: 25 * 1024 * 1024 + 1 }];
  assert.doesNotThrow(() => validateProjectBuildInputs(files, ['HHS_IR']));
});

test('required inputs are still validated', () => {
  assert.throws(() => validateProjectBuildInputs([], ['HHS_IR']), /PROJECT_HAS_NO_FILES/);
  assert.throws(() => validateProjectBuildInputs([{ path: 'main.hhs' }], []), /PROJECT_HAS_NO_COMPILER_TARGETS/);
});

test('the real project builder uses the common validation and has no synthetic cap', () => {
  assert.match(source, /validateProjectBuildInputs\(files, targets\)/);
  assert.doesNotMatch(source, /MAX_PROJECT_FILES|MAX_PROJECT_BYTES|PROJECT_FILE_LIMIT_EXCEEDED|PROJECT_BYTE_LIMIT_EXCEEDED/);
  assert.match(source, /createStoredZip\(archiveEntries\)/);
  assert.match(source, /\/api\/runtime\/development\/lifecycle/);
});
