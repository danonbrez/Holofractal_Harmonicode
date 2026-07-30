const encoder = new TextEncoder();

function asBytes(value) {
  if (value instanceof Uint8Array) return value;
  if (value instanceof ArrayBuffer) return new Uint8Array(value);
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer, value.byteOffset, value.byteLength);
  return encoder.encode(String(value ?? ''));
}

function u16(value) {
  const out = new Uint8Array(2);
  const view = new DataView(out.buffer);
  view.setUint16(0, value & 0xffff, true);
  return out;
}

function u32(value) {
  const out = new Uint8Array(4);
  const view = new DataView(out.buffer);
  view.setUint32(0, value >>> 0, true);
  return out;
}

function concat(chunks) {
  const length = chunks.reduce((total, chunk) => total + chunk.length, 0);
  const out = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) {
    out.set(chunk, offset);
    offset += chunk.length;
  }
  return out;
}

const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let index = 0; index < 256; index += 1) {
    let value = index;
    for (let bit = 0; bit < 8; bit += 1) {
      value = (value & 1) ? (0xedb88320 ^ (value >>> 1)) : (value >>> 1);
    }
    table[index] = value >>> 0;
  }
  return table;
})();

export function crc32(value) {
  const bytes = asBytes(value);
  let crc = 0xffffffff;
  for (const byte of bytes) crc = CRC_TABLE[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

export function createStoredZip(entries) {
  if (!Array.isArray(entries) || entries.length === 0) throw new Error('ZIP_REQUIRES_AT_LEAST_ONE_ENTRY');
  if (entries.length > 65535) throw new Error('ZIP_ENTRY_LIMIT_EXCEEDED');

  const localRecords = [];
  const centralRecords = [];
  const seen = new Set();
  let localOffset = 0;
  const utf8Flag = 0x0800;
  const dosTime = 0;
  const dosDate = 33; // 1980-01-01, deterministic archive timestamp.

  for (const entry of entries) {
    const path = String(entry.path || '').replaceAll('\\', '/').replace(/^\/+/, '');
    if (!path || path.includes('\0') || path.split('/').includes('..')) throw new Error(`ZIP_PATH_REJECTED:${path || '<empty>'}`);
    if (seen.has(path)) throw new Error(`ZIP_DUPLICATE_PATH:${path}`);
    seen.add(path);

    const nameBytes = encoder.encode(path);
    const dataBytes = asBytes(entry.data);
    const checksum = crc32(dataBytes);
    const localHeader = concat([
      u32(0x04034b50),
      u16(20),
      u16(utf8Flag),
      u16(0),
      u16(dosTime),
      u16(dosDate),
      u32(checksum),
      u32(dataBytes.length),
      u32(dataBytes.length),
      u16(nameBytes.length),
      u16(0),
      nameBytes,
      dataBytes,
    ]);
    localRecords.push(localHeader);

    centralRecords.push(concat([
      u32(0x02014b50),
      u16(20),
      u16(20),
      u16(utf8Flag),
      u16(0),
      u16(dosTime),
      u16(dosDate),
      u32(checksum),
      u32(dataBytes.length),
      u32(dataBytes.length),
      u16(nameBytes.length),
      u16(0),
      u16(0),
      u16(0),
      u16(0),
      u32(0),
      u32(localOffset),
      nameBytes,
    ]));
    localOffset += localHeader.length;
  }

  const centralDirectory = concat(centralRecords);
  const endOfCentralDirectory = concat([
    u32(0x06054b50),
    u16(0),
    u16(0),
    u16(entries.length),
    u16(entries.length),
    u32(centralDirectory.length),
    u32(localOffset),
    u16(0),
  ]);
  return concat([...localRecords, centralDirectory, endOfCentralDirectory]);
}
