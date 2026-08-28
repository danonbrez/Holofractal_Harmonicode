import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawn } from 'node:child_process';
import { chromium } from 'playwright';

const root = mkdtempSync(join(tmpdir(), 'hhs-pass187-browser-'));
const db = join(root, 'composition.sqlite3');
const port = 18187;
const server = spawn(
  'python3',
  [
    'native_projects/hhs_pass187_composition_fabric/tools/hhs_pass187_browser_fixture.py',
    '--db', db,
    '--port', String(port),
  ],
  { stdio: ['ignore', 'pipe', 'pipe'], env: { ...process.env, PYTHONPATH: process.cwd() } },
);

let stderr = '';
server.stderr.on('data', chunk => { stderr += chunk.toString(); });

async function waitForHealth() {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/api/pass187/health`);
      if (response.ok) return;
    } catch (_) {}
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error('Pass 187 browser fixture failed to start: ' + stderr);
}

function receipt(n) {
  return n.toString(16).padStart(72, '0');
}

let browserInstance;
try {
  await waitForHealth();
  browserInstance = await chromium.launch({ headless: true });
  const context = await browserInstance.newContext({
    viewport: { width: 1280, height: 900 },
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));

  await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: 'networkidle' });
  await page.getByRole('status').waitFor();
  assert.equal(await page.getByRole('article').count(), 2);

  const source = page.getByRole('button', { name: /output browser\\.source out value\\/exact/i });
  const target = page.getByRole('button', { name: /input browser\\.target in value\\/exact/i });
  const receiptField = page.getByLabel('Inherited VM81 Hash72 receipt');

  // Real browser mouse drag/drop acceptance.
  await receiptField.fill(receipt(10));
  await source.dragTo(target);
  await page.getByRole('status').filter({ hasText: 'admitted' }).waitFor({ timeout: 10000 });
  assert.match(await page.locator('#event-log').innerText(), /receipt_commit/);

  // Real browser keyboard acceptance.
  await receiptField.fill(receipt(11));
  await source.focus();
  await page.keyboard.press('Enter');
  await target.focus();
  await page.keyboard.press('Enter');
  await page.getByRole('status').filter({ hasText: 'admitted' }).waitFor({ timeout: 10000 });

  // Browser PointerEvent stylus acceptance.
  await receiptField.fill(receipt(13));
  await source.dispatchEvent('pointerdown', {
    pointerId: 31,
    pointerType: 'pen',
    isPrimary: true,
    buttons: 1,
  });
  await target.dispatchEvent('pointerup', {
    pointerId: 31,
    pointerType: 'pen',
    isPrimary: true,
    buttons: 0,
  });
  await page.getByRole('status').filter({ hasText: 'admitted' }).waitFor({ timeout: 10000 });

  // Accessibility/navigation acceptance.
  assert.ok(await source.getAttribute('aria-label'));
  assert.ok(await target.getAttribute('aria-label'));
  await page.keyboard.press('Tab');
  assert.ok(await page.evaluate(() => document.activeElement !== document.body));

  const logText = await page.locator('#event-log').innerText();
  for (const phase of [
    'candidate_graph_intent',
    'authority_admission',
    'runtime_execution',
    'projection_update',
    'receipt_commit',
  ]) {
    assert.match(logText, new RegExp(phase));
  }
  await source.focus();
  await page.keyboard.press('Enter');
  await page.getByRole('button', { name: 'Cancel intent' }).click();
  await page.getByRole('status').filter({ hasText: 'cancelled' }).waitFor();
  assert.match(await page.locator('#event-log').innerText(), /failure_or_cancellation/);

  await page.getByRole('button', { name: 'Replay' }).click();
  await page.getByRole('status').filter({ hasText: 'replay verified' }).waitFor();
  assert.match(await page.locator('#event-log').innerText(), /replay_event/);
  await context.close();

  // Separate real touch-capable browser context.
  const touchContext = await browserInstance.newContext({
    hasTouch: true,
    viewport: { width: 1280, height: 900 },
  });
  const touchPage = await touchContext.newPage();
  touchPage.on('pageerror', error => errors.push(String(error)));
  await touchPage.goto(`http://127.0.0.1:${port}/`, { waitUntil: 'networkidle' });
  const touchSource = touchPage.getByRole('button', { name: /output browser\\.source out value\\/exact/i });
  const touchTarget = touchPage.getByRole('button', { name: /input browser\\.target in value\\/exact/i });
  await touchPage.getByLabel('Inherited VM81 Hash72 receipt').fill(receipt(12));
  const sourceBox = await touchSource.boundingBox();
  const targetBox = await touchTarget.boundingBox();
  assert.ok(sourceBox && targetBox);
  await touchPage.touchscreen.tap(sourceBox.x + sourceBox.width / 2, sourceBox.y + sourceBox.height / 2);
  await touchPage.touchscreen.tap(targetBox.x + targetBox.width / 2, targetBox.y + targetBox.height / 2);
  await touchPage.getByRole('status').filter({ hasText: 'admitted' }).waitFor({ timeout: 10000 });
  assert.match(await touchPage.locator('#event-log').innerText(), /receipt_commit/);
  await touchContext.close();

  assert.deepEqual(errors, []);
  await context.close();
} finally {
  if (browserInstance) await browserInstance.close();
  server.kill('SIGTERM');
  await new Promise(resolve => {
    server.once('exit', resolve);
    setTimeout(resolve, 1000);
  });
  rmSync(root, { recursive: true, force: true });
}
