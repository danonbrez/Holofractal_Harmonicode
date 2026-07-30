import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const read = (path) => readFileSync(resolve(root, path), 'utf8');

test('visual IDE loads the GUI reliability layer', () => {
  const source = read('src/visual-ide.mjs');
  assert.match(source, /import ['"]\.\/gui-reliability\.mjs['"]/);
});

test('temporary surfaces are transparent and always dismissible', () => {
  const source = read('src/gui-reliability.mjs');
  const styles = read('src/gui-reliability.css');
  assert.match(source, /Close command center/);
  assert.match(source, /Close explorer/);
  assert.match(source, /Close inspector/);
  assert.match(source, /event\.key === 'Escape'/);
  assert.match(source, /hhs-mobile-scrim/);
  assert.match(source, /history\.pushState/);
  assert.match(source, /history\.back/);
  assert.match(source, /returnFocus/);
  assert.match(styles, /workflow-command-palette[\s\S]*rgba\(/);
  assert.match(styles, /backdrop-filter:\s*blur/);
  assert.match(styles, /\.registry\.open/);
  assert.match(styles, /\.inspector\.open/);
  assert.match(styles, /\[hidden\][\s\S]*display:\s*none\s*!important/);
});

test('mobile IDE uses one persistent application pane', () => {
  const source = read('src/gui-reliability.mjs');
  const styles = read('src/gui-reliability.css');
  assert.match(source, /hhs\.visualIde\.mobilePane\.v2/);
  assert.match(source, /VALID_PANES/);
  assert.match(source, /selectMobilePane/);
  assert.match(source, /aria-current/);
  assert.match(source, /visualViewport/);
  for (const pane of ['editor', 'lifecycle', 'terminal', 'spatial']) {
    assert.match(styles, new RegExp(`data-mobile-pane=\\"${pane}\\"`));
  }
  assert.match(styles, /safe-area-inset-bottom/);
  assert.match(styles, /touch-action:\s*manipulation/);
});
