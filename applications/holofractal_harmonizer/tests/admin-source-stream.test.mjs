import test from 'node:test';
import assert from 'node:assert/strict';
import { Blob } from 'node:buffer';
import { readFileSync } from 'node:fs';
import { stageBrowserFile, continueStagedLane5Candidate, readStagedSource } from '../src/admin-source-stream.mjs';

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
  assert.match(code, /Stage \+ Lane 5 \(Admin\)/);
  assert.match(code, /stageBrowserFile\(file,\s*\{\s*capabilityToken:\s*capabilityToken\.trim\(\)\s*\}\)/);
  for (const preserved of ['ide-import-folder', 'ide-build-project', 'ide-export-project', 'ide-create-path']) {
    assert.ok(code.includes(preserved), preserved);
  }
  assert.match(code, /STAGED ·/);
  assert.match(code, /VM81 admission pending/);
  assert.match(code, /continueStagedLane5Candidate\(receipt\.upload_id/);
});

test('signed Pass190 credential is forwarded to every transport request, never in URL or body', async () => {
  const source = new Blob(['exact source bytes']);
  source.name = 'signed-source.bin';
  const credential = 'fake-fixture-capability-not-a-real-secret';
  const destinations = [];
  let offset = 0;
  const mock = async (url, options) => {
    destinations.push(url);
    assert.equal(options.headers?.Authorization, 'HHS-Capability ' + credential);
    assert.ok(!url.includes(credential));
    assert.ok(!String(options.body).includes(credential));
    if (options.method === 'POST' && url.endsWith('/uploads')) {
      return {ok:true,json:async()=>({upload_id:'stream-id',received_bytes:0})};
    }
    if (options.method === 'PATCH') {
      offset += options.body.size;
      return {ok:true,json:async()=>({received_bytes:offset})};
    }
    return {ok:true,json:async()=>({
      state:'STAGED',received_bytes:source.size,source_sha256:'b'.repeat(64),
      canonical_hash216_admitted:false,
    })};
  };
  const status = await stageBrowserFile(source,{fetchImpl:mock,capabilityToken:credential,chunkBytes:6});
  assert.equal(status.status,'STAGED_NONCANONICAL');
  assert.equal(status.received_bytes,source.size);
  assert.ok(destinations.length > 3);
});

test('native continuation checks signed credential and rejects fabricated authority', async () => {
  const uploadId = '11111111-2222-4333-8444-555555555555';
  let calls = 0;
  const candidateFetch = async (url, opts) => {
    calls++;
    assert.equal(opts.method, 'POST');
    assert.equal(opts.headers.Authorization, 'HHS-Capability verified-fixture');
    assert.equal(url, '/api/runtime/admin-source-stream/uploads/' + uploadId + '/candidate');
    return {ok:true,json:async()=>({
      upload_id:uploadId, canonical_hash216_admitted:false,
      signed_vm81_admission_required:true,
      native_candidate_receipt:{candidate_only:true,workload_byte_count:1234},
    })};
  };
  const receipt = await continueStagedLane5Candidate(uploadId, {
    capabilityToken:'verified-fixture',fetchImpl:candidateFetch,
  });
  assert.equal(receipt.native_candidate_receipt.workload_byte_count,1234);
  assert.equal(calls,1);
  await assert.rejects(continueStagedLane5Candidate(uploadId, {
    fetchImpl:async()=>({ok:true,json:async()=>({
      upload_id:uploadId,canonical_hash216_admitted:true,
      signed_vm81_admission_required:false,
      native_candidate_receipt:{candidate_only:false},
    })}),
  }),/CANDIDATE_AUTHORITY_INVALID/);
});

test('authenticated streaming source egress retains binary bytes without whole-file buffers', async () => {
  const uploadId = '11111111-2222-4333-8444-555555555555';
  const bytes = Uint8Array.from({length: 1709}, (_, i) => i % 256);
  const parts = [bytes.subarray(0, 7), bytes.subarray(7, 1390), bytes.subarray(1390)];
  const observed = [];
  const writable = new WritableStream({
    write(chunk) { observed.push(Uint8Array.from(chunk)); },
  });
  let index = 0;
  const body = new ReadableStream({
    pull(controller) {
      if (index === parts.length) return controller.close();
      controller.enqueue(parts[index++]);
    },
  });
  const fetchImpl = async (url, options) => {
    assert.equal(url, '/api/runtime/admin-source-stream/uploads/' + uploadId + '/source');
    assert.equal(options.headers.Authorization, 'HHS-Capability fixture');
    assert.equal(options.cache, 'no-store');
    return {
      ok: true,
      headers: new Headers({
        'X-HHS-Source-SHA256': 'a'.repeat(64),
        'X-HHS-Canonical-Hash216-Admitted': 'false',
        'Content-Length': String(bytes.length),
      }),
      body,
    };
  };
  const receipt = await readStagedSource(uploadId, writable, {fetchImpl, capabilityToken:'fixture'});
  assert.equal(receipt.received_bytes, bytes.length);
  assert.equal(receipt.canonical_hash216_admitted, false);
  assert.deepEqual(Buffer.concat(observed), Buffer.from(bytes));
});

test('staged egress rejects canonical claims before writing any bytes', async () => {
  let writes = 0;
  const destination = new WritableStream({write() {writes++;}});
  const response = {
    ok: true,
    headers: new Headers({
      'X-HHS-Source-SHA256': 'b'.repeat(64),
      'X-HHS-Canonical-Hash216-Admitted': 'true',
      'Content-Length': '2',
    }),
    body: new ReadableStream({start(controller) {controller.enqueue(Uint8Array.of(1,2));controller.close();}}),
  };
  await assert.rejects(readStagedSource('11111111-2222-4333-8444-555555555555', destination,
    {fetchImpl:async()=>response}), /EGRESS_RECEIPT_INVALID/);
  assert.equal(writes, 0);
});
