import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const uiUrl = new URL('../src/visual-ide-ui.mjs', import.meta.url);
const visualUrl = new URL('../src/visual-ide.mjs', import.meta.url);

test('same-path recovery reload cannot overwrite restored content with the stale editor buffer', async () => {
  const ui = await readFile(uiUrl, 'utf8');
  const visual = await readFile(visualUrl, 'utf8');
  assert.match(ui, /if \(path !== state\.activePath && prior && editor && !prior\.bytesB64 && editorLoadedPath === prior\.path\) prior\.content = editor\.value;/);
  assert.match(ui, /editor\.value = editor\.readOnly[\s\S]*\(file\.content \|\| ''\)/);
  assert.match(visual, /hhs:pass176:recovery-applied/);
  assert.match(visual, /activateFile\(restoredPath\)/);
  assert.doesNotMatch(ui, /if \(prior && editor && !prior\.bytesB64 && editorLoadedPath === prior\.path\) prior\.content = editor\.value;/);
});
