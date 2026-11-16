import test from 'node:test';
import assert from 'node:assert/strict';
import { Blob } from 'node:buffer';
import { readFileSync } from 'node:fs';
import { stageBrowserFile } from '../src/admin-source-stream.mjs';

test('file streaming uses slices and never entire-file arrayBuffer', async () => {
  const source = new Blob([Uint8Array.from({length: 1459}, (_, i) => i % 256)]);
  source.name = 'foreign.unknown';
  source.arrayBuffer = () => { throw new Error('whole-file materialization forbidden'); };
  let offset = 0, requests = 0;
  const responses = [];
  const mockFetch = async (url, init) => {
    requests++;
    assert.equal(init.credentials, 'same-origin');
    assert.ok(!init.headers || !('x-owner-id' in init.headers));
    let result;
    if (url.endsWith('/uploads')) {
      assert.equal(JSON.parse(init.body).source_name, 'foreign.unknown');
      result = { upload_id: 'test-uuid', received_bytes: 0 };
    } else if (url.includes('?offset=')) {
      const supplied = Number(url.split('offset=')[1]);
      assert.equal(supplied, offset);
      assert.ok(init.body instanceof Blob);
      assert.ok(init.body.size <= 648);
      offset += init.body.size;
      result = { received_bytes: offset };
    } else {
      assert.equal(offset, source.size);
      result = { state: 'STAGED', received_bytes: offset, source_sha256: 'a'.repeat(64), canonical_hash216_admitted: false };
    }
    responses.push(url);
    return { ok: true, json: async () => result };
  };
  const result = await stageBrowserFile(source, { fetchImpl: mockFetch, chunkBytes: 648 });
  assert.equal(result.status, 'STAGED_NONCANONICAL');
  assert.equal(result.received_bytes, 1459);
  assert.equal(requests, 5);
  assert.ok(responses[0].endsWith('/uploads'));
  assert.ok(responses.at(-1).endsWith('/finalize'));
});

test('rejects host-denied authentication without sending any bytes', async () => {
  const source = new Blob(['secret']);
  source.name = 'private.txt';
  let count = 0;
  await assert.rejects(stageBrowserFile(source, {fetchImpl: async () => {
    count++;
    return {ok: false, json: async () => ({detail:'HHS_ADMIN_STREAM_TRUSTED_PRINCIPAL_REQUIRED'})};
  }}), /HHS_ADMIN_STREAM_TRUSTED_PRINCIPAL_REQUIRED/);
  assert.equal(count, 1);
});

test('rejects fabricated canonical receipt and offset drift', async () => {
  const source = new Blob(['xyz']);
  source.name = 'x';
  let n = 0;
  await assert.rejects(stageBrowserFile(source, {fetchImpl: async () => {
    n++;
    return {ok:true,json:async()=>n===1?{upload_id:'x',received_bytes:0}:{received_bytes:20}};
  }}), /OFFSET_CORRUPT/);
});

test('existing IDE retains conventional controls and offers separate administrator staging', () => {
  const code = readFileSync(new URL('../src/project-lifecycle.mjs', import.meta.url), 'utf8');
  assert.match(code, /Stage Source \(Admin\)/);
  assert.match(code, /stageBrowserFile\(file\)/);
  for (const preserved of ['ide-import-folder', 'ide-build-project', 'ide-export-project', 'ide-create-path']) {
    assert.ok(code.includes(preserved), preserved);
  }
  assert.match(code, /STAGED ·/);
  assert.match(code, /native admission pending/);
});
