import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const root = resolve(new URL('..', import.meta.url).pathname);
const read = (path) => readFileSync(resolve(root, path), 'utf8');

function assertSyntax(path) {
  const result = spawnSync(process.execPath, ['--check', resolve(root, path)], {
    encoding: 'utf8',
  });
  assert.equal(result.status, 0, `${path} failed node --check:\n${result.stderr || result.stdout}`);
}

test('Pass 176 controller publishes before the dynamic public graph without claiming interactive', () => {
  const coordinator = read('src/production-startup-coordinator.mjs');
  const bootstrap = read('src/pass176-early-bootstrap.mjs');

  assertSyntax('src/production-startup-coordinator.mjs');
  assertSyntax('src/pass176-early-bootstrap.mjs');

  const bootstrapImport = coordinator.indexOf("import './pass176-early-bootstrap.mjs';");
  const publicGraphLaunch = coordinator.indexOf("void import('./public-boot.mjs')");
  assert.ok(bootstrapImport >= 0);
  assert.ok(publicGraphLaunch > bootstrapImport);
  assert.match(coordinator, /pass176_controller_bootstrap_precedes_public_graph:\s*true/);
  assert.match(coordinator, /pass176_early_bootstrap_claims_interactive:\s*false/);

  assert.match(bootstrap, /from '\.\/visual-ide-state\.mjs'/);
  assert.match(bootstrap, /from '\.\/pass176-stability\.mjs'/);
  assert.match(bootstrap, /initPass176Stability\(bootOptions\)/);
  assert.match(bootstrap, /window\.HHSVisualIDEBoot = promise/);
  assert.match(bootstrap, /hhs:visual-ide:interactive/);
  assert.match(bootstrap, /interactive_claimed:\s*false/);
  assert.doesNotMatch(bootstrap, /\.mark\(['"]INTERACTIVE/);
  assert.doesNotMatch(bootstrap, /\.boot\(/);
  assert.doesNotMatch(bootstrap, /^\s*await\s+initPass176Stability/m);
});
