import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { createStoredZip } from '../src/project-zip.mjs';

const sig = (bytes, offset) => new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength).getUint32(offset, true);
const u64 = (bytes, offset) => new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength).getBigUint64(offset, true);

function standardReaderCheck(zip, expectedCount, firstName, lastName, firstBytes, lastBytes) {
  const folder = mkdtempSync(join(tmpdir(), 'hhs-zip64-test-'));
  try {
    const file = join(folder, 'artifact.zip');
    writeFileSync(file, zip);
    const script = [
      'import sys, zipfile',
      'with zipfile.ZipFile(sys.argv[1]) as z:',
      '  names = z.namelist()',
      '  assert len(names) == int(sys.argv[2]), len(names)',
      '  assert names[0] == sys.argv[3], names[0]',
      '  assert names[-1] == sys.argv[4], names[-1]',
      '  assert z.read(names[0]).hex() == sys.argv[5]',
      '  assert z.read(names[-1]).hex() == sys.argv[6]',
      '  assert z.testzip() is None',
    ].join('\n');
    const process = spawnSync('python3', ['-c', script, file, String(expectedCount), firstName, lastName, Buffer.from(firstBytes).toString('hex'), Buffer.from(lastBytes).toString('hex')], { encoding: 'utf8', timeout: 90000 });
    assert.equal(process.status, 0, `standard Python ZIP reader failed: ${process.stderr || process.stdout}`);
  } finally {
    rmSync(folder, { recursive: true, force: true });
  }
}

test('existing small archives retain classic ZIP format and exact binary bytes', () => {
  const payload = Uint8Array.from([0, 255, 0, 1, 72, 216]);
  const zip = createStoredZip([
    { path: 'source/src/main.hhs', data: 'a²=1\n' },
    { path: 'assets/source.bin', data: payload },
  ]);
  assert.equal(sig(zip, zip.length - 22), 0x06054b50);
  assert.equal(sig(zip, 0), 0x04034b50);
  assert.equal(Buffer.from(zip).includes(Buffer.from([0x50, 0x4b, 0x06, 0x06])), false);
  standardReaderCheck(zip, 2, 'source/src/main.hhs', 'assets/source.bin', Buffer.from('a²=1\n'), payload);
});

test('65536 exact ordered file entries produce standards-compatible ZIP64', () => {
  const count = 65536;
  const entries = Array.from({ length: count }, (_, i) => ({
    path: `source/src/file-${String(i).padStart(5, '0')}.txt`,
    data: i === 0 ? 'first' : i === count - 1 ? 'last' : '',
  }));
  const zip = createStoredZip(entries);
  assert.equal(sig(zip, zip.length - 22), 0x06054b50);
  assert.equal(sig(zip, zip.length - 42), 0x07064b50);
  assert.equal(sig(zip, zip.length - 98), 0x06064b50);
  assert.equal(u64(zip, zip.length - 98 + 32), BigInt(count));
  standardReaderCheck(zip, count, entries[0].path, entries[count - 1].path, Buffer.from('first'), Buffer.from('last'));
});

test('duplicate or traversal path remains rejected', () => {
  assert.throws(() => createStoredZip([{path: 'a', data: 'x'}, {path: 'a', data: 'y'}]), /ZIP_DUPLICATE_PATH/);
  assert.throws(() => createStoredZip([{path: '../escape', data: 'x'}]), /ZIP_PATH_REJECTED/);
});
