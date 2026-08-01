import { sha256Bytes } from '../sha256.mjs';

const encoder = new TextEncoder();

const DOMAIN = encoder.encode('HHS-P150-HASH216-CONSTRAINT-GENOME-V1\0');
const POSITION_DOMAIN = encoder.encode('HHS-P150-POSITION-V1\0');

function concatBytes(...chunks) {
  const length = chunks.reduce((total, chunk) => total + chunk.length, 0);
  const output = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) {
    output.set(chunk, offset);
    offset += chunk.length;
  }
  return output;
}

function integerBytes(value, width) {
  let remaining = BigInt(value);
  if (remaining < 0n) throw new RangeError('integer must be non-negative');
  const output = new Uint8Array(width);
  for (let index = width - 1; index >= 0; index -= 1) {
    output[index] = Number(remaining & 0xffn);
    remaining >>= 8n;
  }
  if (remaining !== 0n) throw new RangeError(`integer does not fit in ${width} bytes`);
  return output;
}

function bytesToHex(bytes) {
  return [...bytes].map((value) => value.toString(16).padStart(2, '0')).join('');
}

function hexToBytes(value) {
  if (!/^[0-9a-f]{64}$/i.test(value)) throw new TypeError('expected a 64-character hexadecimal digest');
  return Uint8Array.from({ length: 32 }, (_, index) => Number.parseInt(value.slice(index * 2, index * 2 + 2), 16));
}

async function sha256(bytes) {
  return sha256Bytes(bytes);
}

function canonicalValue(value) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return value;
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) throw new TypeError('canonical JSON does not admit non-finite numbers');
    return value;
  }
  if (Array.isArray(value)) return value.map(canonicalValue);
  if (typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonicalValue(value[key])]));
  }
  throw new TypeError(`unsupported canonical JSON value: ${typeof value}`);
}

export function canonicalStringify(value) {
  return JSON.stringify(canonicalValue(value));
}

export function canonicalBytes(value) {
  return encoder.encode(canonicalStringify(value));
}

export async function hash216Positions(payload, { previousRoot = '0'.repeat(64), sequence = 0 } = {}) {
  const bytes = payload instanceof Uint8Array ? payload : canonicalBytes(payload);
  const seed = await sha256(concatBytes(
    DOMAIN,
    encoder.encode(previousRoot),
    integerBytes(sequence, 16),
    bytes,
  ));
  const positions = await Promise.all(Array.from({ length: 216 }, async (_, index) => bytesToHex(await sha256(concatBytes(
    POSITION_DOMAIN,
    integerBytes(index, 2),
    seed,
    bytes,
  )))));
  return Object.freeze(positions);
}

export async function hash216Root(positions) {
  if (!Array.isArray(positions) || positions.length !== 216) {
    throw new TypeError('exactly 216 positions are required');
  }
  const rootBytes = concatBytes(DOMAIN, ...positions.map(hexToBytes));
  return bytesToHex(await sha256(rootBytes));
}

export async function hash216Identity(value, options = {}) {
  const payload = value instanceof Uint8Array ? value : canonicalBytes(value);
  const positions = await hash216Positions(payload, options);
  return Object.freeze({
    algorithm: 'HHS-P150-HASH216-CONSTRAINT-GENOME-V1',
    payloadSha256: bytesToHex(await sha256(payload)),
    positions,
    root: await hash216Root(positions),
    previousRoot: options.previousRoot || '0'.repeat(64),
    sequence: options.sequence || 0,
    vm81EchoRequired: true,
  });
}
