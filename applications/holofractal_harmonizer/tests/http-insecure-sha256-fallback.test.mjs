import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import test from 'node:test';

import { sha256Hex } from '../src/sha256.mjs';

function referenceSha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

const vectors = [
  '',
  'abc',
  'The quick brown fox jumps over the lazy dog',
  'π φ √2 — UTF-8',
  'a'.repeat(55),
  'a'.repeat(56),
  'a'.repeat(64),
  'a'.repeat(1000),
];

test('pure JavaScript SHA-256 fallback matches reference vectors', async () => {
  for (const vector of vectors) {
    assert.equal(
      await sha256Hex(vector, { subtle: null }),
      referenceSha256(vector),
      `SHA-256 mismatch for ${vector.length}-byte vector`,
    );
  }
});

test('Pass 161 receipts and Hash216 browser identity work without crypto.subtle', async () => {
  const originalCrypto = Object.getOwnPropertyDescriptor(globalThis, 'crypto');
  Object.defineProperty(globalThis, 'crypto', {
    configurable: true,
    value: {},
  });

  try {
    const nonce = `${Date.now()}-${Math.random()}`;
    const core = await import(`../src/core.mjs?http-fallback=${nonce}`);
    const hash216 = await import(`../src/pass177/hash216-browser.mjs?http-fallback=${nonce}`);

    const ledger = new core.ReceiptLedger();
    const receipt = await ledger.append('P161_OBJECT_REGISTER', {
      object_id: 'test:http-insecure-context',
      state: 'VALIDATED_PROJECTION',
    });

    assert.equal(ledger.size, 1);
    assert.match(receipt.payload_sha256, /^[0-9a-f]{64}$/);
    assert.match(receipt.receipt_sha256, /^[0-9a-f]{64}$/);
    assert.equal(await ledger.verify(), true);

    const payload = {
      schema: 'HHS_HTTP_INSECURE_CONTEXT_HASH216_TEST_V1',
      text: 'fallback identity',
      sequence: 7,
    };
    const identity = await hash216.hash216Identity(payload, {
      previousRoot: '0'.repeat(64),
      sequence: 7,
    });
    const replay = await hash216.hash216Identity(payload, {
      previousRoot: '0'.repeat(64),
      sequence: 7,
    });

    assert.equal(identity.positions.length, 216);
    assert.match(identity.root, /^[0-9a-f]{64}$/);
    assert.equal(identity.root, replay.root);
    assert.deepEqual(identity.positions, replay.positions);
    assert.equal(identity.payloadSha256, referenceSha256(hash216.canonicalBytes(payload)));
  } finally {
    if (originalCrypto) Object.defineProperty(globalThis, 'crypto', originalCrypto);
    else delete globalThis.crypto;
  }
});
