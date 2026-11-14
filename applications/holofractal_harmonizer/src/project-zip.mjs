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

function u64(value) {
  const raw = typeof value === 'bigint' ? value : BigInt(value);
  if (raw < 0n || raw > 0xffffffffffffffffn) throw new RangeError('ZIP64_VALUE_OUT_OF_RANGE');
  const out = new Uint8Array(8);
  new DataView(out.buffer).setBigUint64(0, raw, true);
  return out;
}

function zipExtra(values) {
  return concat([u16(0x0001), u16(values.length * 8), ...values.map(u64)]);
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

  const localRecords = [];
  const centralRecords = [];
  const seen = new Set();
  let localOffset = 0n;
  let centralSize = 0n;
  const utf8Flag = 0x0800;
  const dosTime = 0;
  const dosDate = 33;
  const ZIP32_MAX = 0xffffffffn;
  const ZIP16_MAX = 0xffffn;
  let requiresZip64 = BigInt(entries.length) >= ZIP16_MAX;

  for (const entry of entries) {
    const path = String(entry.path || '').replaceAll('\\', '/').replace(/^\/+/, '');
    if (!path || path.includes('\0') || path.split('/').includes('..')) throw new Error(`ZIP_PATH_REJECTED:${path || '<empty>'}`);
    if (seen.has(path)) throw new Error(`ZIP_DUPLICATE_PATH:${path}`);
    seen.add(path);

    const nameBytes = encoder.encode(path);
    if (nameBytes.length > 0xffff) throw new Error('ZIP_FILENAME_FORMAT_LIMIT');
    const dataBytes = asBytes(entry.data);
    const fileSize = BigInt(dataBytes.length);
    const use64Size = fileSize >= ZIP32_MAX;
    const use64Offset = localOffset >= ZIP32_MAX;
    requiresZip64 ||= use64Size || use64Offset;
    const version = use64Size || use64Offset ? 45 : 20;
    const checksum = crc32(dataBytes);
    const localExtra = use64Size ? zipExtra([fileSize, fileSize]) : new Uint8Array();
    const localHeader = concat([
      u32(0x04034b50),
      u16(version),
      u16(utf8Flag),
      u16(0),
      u16(dosTime),
      u16(dosDate),
      u32(checksum),
      u32(use64Size ? 0xffffffff : dataBytes.length),
      u32(use64Size ? 0xffffffff : dataBytes.length),
      u16(nameBytes.length),
      u16(localExtra.length),
      nameBytes,
      localExtra,
      dataBytes,
    ]);
    localRecords.push(localHeader);

    const zip64Fields = [];
    if (use64Size) zip64Fields.push(fileSize, fileSize);
    if (use64Offset) zip64Fields.push(localOffset);
    const centralExtra = zip64Fields.length ? zipExtra(zip64Fields) : new Uint8Array();
    const centralRecord = concat([
      u32(0x02014b50),
      u16(version),  // version made by
      u16(version),  // version needed to extract
      u16(utf8Flag),
      u16(0),
      u16(dosTime),
      u16(dosDate),
      u32(checksum),
      u32(use64Size ? 0xffffffff : dataBytes.length),
      u32(use64Size ? 0xffffffff : dataBytes.length),
      u16(nameBytes.length),
      u16(centralExtra.length),
      u16(0),
      u16(0),
      u16(0),
      u32(0),
      u32(use64Offset ? 0xffffffff : Number(localOffset)),
      nameBytes,
      centralExtra,
    ]);
    centralRecords.push(centralRecord);
    localOffset += BigInt(localHeader.length);
    centralSize += BigInt(centralRecord.length);
  }

  const count = BigInt(entries.length);
  requiresZip64 ||= centralSize >= ZIP32_MAX || localOffset >= ZIP32_MAX;
  const ending = [];
  if (requiresZip64) {
    const zip64EndOffset = localOffset + centralSize;
    ending.push(concat([
      u32(0x06064b50),
      u64(44n),
      u16(45), u16(45),
      u32(0), u32(0),
      u64(count), u64(count),
      u64(centralSize), u64(localOffset),
    ]));
    ending.push(concat([
      u32(0x07064b50),
      u32(0),
      u64(zip64EndOffset),
      u32(1),
    ]));
  }
  ending.push(concat([
    u32(0x06054b50),
    u16(0), u16(0),
    u16(count >= ZIP16_MAX ? 0xffff : Number(count)),
    u16(count >= ZIP16_MAX ? 0xffff : Number(count)),
    u32(centralSize >= ZIP32_MAX ? 0xffffffff : Number(centralSize)),
    u32(localOffset >= ZIP32_MAX ? 0xffffffff : Number(localOffset)),
    u16(0),
  ]));
  return concat([...localRecords, ...centralRecords, ...ending]);
}
