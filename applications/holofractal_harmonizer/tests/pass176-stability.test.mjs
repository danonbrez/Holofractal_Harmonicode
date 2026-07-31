import assert from 'node:assert/strict';
import test from 'node:test';

import {
  AtomicRecoveryStore,
  BootStateMachine,
  BoundedJobManager,
  GenerationGate,
  PASS176_BOOT_STAGES,
  ResourceLedger,
} from '../src/pass176-stability-core.mjs';

test('boot state machine is ordered, idempotent, and reaches interactive', () => {
  let now = 1000;
  const boot = new BootStateMachine(PASS176_BOOT_STAGES, () => ++now);
  for (const stage of PASS176_BOOT_STAGES) {
    const first = boot.mark(stage, { stage });
    const duplicate = boot.mark(stage, { changed: true });
    assert.equal(first, duplicate);
  }
  assert.equal(boot.interactive, true);
  assert.equal(boot.snapshot().records.length, PASS176_BOOT_STAGES.length);
  assert.deepEqual(boot.snapshot().remaining, []);
});

test('boot state machine rejects out-of-order advancement', () => {
  const boot = new BootStateMachine();
  assert.throws(() => boot.mark('STATIC_THEME_READY'), /BOOT_STAGE_ORDER_VIOLATION/);
});

test('generation gate rejects stale completions', () => {
  const gate = new GenerationGate();
  const first = gate.next('preview');
  const second = gate.next('preview');
  assert.equal(gate.isCurrent(first), false);
  assert.equal(gate.isCurrent(second), true);
  assert.throws(() => gate.assertCurrent(first), /STALE_ASYNC_RESPONSE/);
});

test('resource ledger releases every resource through repeated cycles', () => {
  const ledger = new ResourceLedger();
  let disposed = 0;
  for (let cycle = 0; cycle < 100; cycle += 1) {
    const handle = ledger.own('preview', () => { disposed += 1; }, { cycle });
    assert.equal(ledger.snapshot().total, 1);
    assert.equal(handle.dispose(), true);
    assert.equal(handle.dispose(), false);
    assert.equal(ledger.snapshot().total, 0);
  }
  assert.equal(disposed, 100);
});

test('bounded jobs deduplicate duplicate invocations and support cancellation', async () => {
  const jobs = new BoundedJobManager();
  let executions = 0;
  let release;
  const blocker = new Promise((resolve) => { release = resolve; });
  const first = jobs.run('compile', async ({ signal }) => {
    executions += 1;
    await blocker;
    if (signal.aborted) throw new DOMException('aborted', 'AbortError');
    return 'ok';
  });
  const duplicate = jobs.run('compile', async () => 'duplicate');
  assert.equal(first, duplicate);
  await Promise.resolve();
  assert.equal(executions, 1);
  assert.equal(jobs.cancel('compile'), true);
  release();
  await assert.rejects(first, /Abort|CANCELLED|USER_CANCELLED/);
  assert.equal(jobs.snapshot().active.length, 0);
});

test('bounded jobs deduplicate command aliases by canonical key', async () => {
  const jobs = new BoundedJobManager();
  let executions = 0;
  let release;
  const blocker = new Promise((resolve) => { release = resolve; });
  const workflow = jobs.run('workflow-lifecycle', async () => {
    executions += 1;
    await blocker;
    return 'complete';
  }, { key: 'lifecycle' });
  const shortcut = jobs.run('shortcut-lifecycle', async () => 'duplicate', { key: 'lifecycle' });
  assert.equal(workflow, shortcut);
  await Promise.resolve();
  assert.equal(executions, 1);
  release();
  assert.equal(await workflow, 'complete');
  assert.equal(jobs.snapshot().active.length, 0);
});

test('bounded jobs settle on timeout even when executor ignores AbortSignal', async () => {
  const jobs = new BoundedJobManager();
  const ignored = jobs.run('ignored-signal', () => new Promise(() => {}), { timeoutMs: 20 });
  await assert.rejects(ignored, /HHS_P176_JOB_TIMEOUT/);
  assert.equal(jobs.snapshot().active.length, 0);
});

test('atomic recovery prefers the newest complete or pending envelope', () => {
  const values = new Map();
  const storage = {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
    removeItem: (key) => values.delete(key),
  };
  const recovery = new AtomicRecoveryStore(storage);
  const first = recovery.save({ activePath: 'src/main.hhs', files: [{ path: 'src/main.hhs', content: '01' }] });
  assert.equal(recovery.load().payload.files[0].content, '01');
  const newer = { ...first, savedAt: first.savedAt + 100, payload: { activePath: 'src/new.hhs', files: [] } };
  storage.setItem(recovery.pendingKey, JSON.stringify(newer));
  assert.equal(recovery.load().payload.activePath, 'src/new.hhs');
  recovery.clear();
  assert.equal(recovery.load(), null);
});

test('atomic recovery prefers pending envelope when timestamps tie', () => {
  const values = new Map();
  const storage = {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
    removeItem: (key) => values.delete(key),
  };
  const recovery = new AtomicRecoveryStore(storage);
  const complete = recovery.save({ activePath: 'src/main.hhs', files: [{ path: 'src/main.hhs' }] });
  const pending = { ...complete, payload: { activePath: 'src/pending.hhs', files: [{ path: 'src/pending.hhs' }] } };
  storage.setItem(recovery.pendingKey, JSON.stringify(pending));
  assert.equal(recovery.load().payload.activePath, 'src/pending.hhs');
});
