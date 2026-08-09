import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const uiUrl = new URL('../src/visual-ide-ui.mjs', import.meta.url);
const ideUrl = new URL('../src/visual-ide.mjs', import.meta.url);

test('same-file recovery activation renders recovered state instead of recapturing stale editor DOM', async () => {
  const [ui, ide] = await Promise.all([
    readFile(uiUrl, 'utf8'),
    readFile(ideUrl, 'utf8'),
  ]);

  assert.match(
    ui,
    /editorLoadedPath === prior\.path && prior\.path !== path\) prior\.content = editor\.value/,
  );
  assert.match(ide, /hhs:pass176:recovery-applied/);
  assert.match(ide, /if \(restoredPath\) activateFile\(restoredPath\)/);
});
