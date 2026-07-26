export const CONTRACT_ID = "HHS-P158-LLABI-NFTC-API";
const HASH72_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";

function requireCanonicalGlyphs(value, length, label) {
  if (typeof value !== "string" || value.length !== length) throw new Error(`${label}_LENGTH_INVALID`);
  for (const symbol of value) if (!HASH72_ALPHABET.includes(symbol)) throw new Error(`${label}_ALPHABET_INVALID`);
  return value;
}

export function bigintToCanonicalBytes(value) {
  if (typeof value !== "bigint") throw new TypeError("BigInt required");
  const sign = value < 0n ? 1 : 0;
  let magnitude = value < 0n ? -value : value;
  const bytes = [];
  do {
    bytes.push(Number(magnitude & 0xffn));
    magnitude >>= 8n;
  } while (magnitude);
  return Uint8Array.from([sign, ...bytes.reverse()]);
}

export function canonicalBytesToBigint(bytes) {
  if (!(bytes instanceof Uint8Array) || bytes.length < 2) throw new TypeError("canonical byte array required");
  if (bytes[0] > 1) throw new RangeError("malformed BigInt sign");
  let magnitude = 0n;
  for (const byte of bytes.subarray(1)) magnitude = (magnitude << 8n) | BigInt(byte);
  return bytes[0] ? -magnitude : magnitude;
}

export class ExactRational {
  constructor(numerator, denominator) {
    if (typeof numerator !== "bigint" || typeof denominator !== "bigint") throw new TypeError("BigInt numerator and denominator required");
    if (denominator <= 0n) throw new RangeError("denominator must be positive");
    const gcd = (a, b) => { let x = a < 0n ? -a : a; let y = b; while (y) [x, y] = [y, x % y]; return x || 1n; };
    const divisor = gcd(numerator, denominator);
    this.numerator = numerator / divisor;
    this.denominator = denominator / divisor;
    Object.freeze(this);
  }
  canonical() { return `${this.numerator}/${this.denominator}`; }
  valueOf() { throw new TypeError("authoritative rational cannot coerce to Number"); }
}

export class KernelAuthorityAdapter {
  constructor({ identify, project }) {
    if (typeof identify !== "function" || typeof project !== "function") throw new TypeError("kernel authority adapter required");
    this._identify = identify;
    this._project = project;
    Object.freeze(this);
  }
  identify(definition) { return this._identify(structuredClone(definition)); }
  project(request) { return this._project(structuredClone(request)); }
}

function verifyKernelResponse(response, definitionId) {
  if (!response || response.kernelAuthority !== "HHS_PASS158_NATIVE_ABI" || response.replayVerified !== true || response.replay?.matched !== true) {
    throw new Error("KERNEL_RECEIPT_REPLAY_REQUIRED");
  }
  if (response.definitionId !== definitionId) throw new Error("HASH216_DEFINITION_ID_MISMATCH");
  const receipt = response.receipt;
  requireCanonicalGlyphs(receipt?.receipt_id, 72, "HASH72_RECEIPT");
  requireCanonicalGlyphs(receipt?.object_root, 216, "HASH216_OBJECT_ROOT");
  if (receipt.classification !== "HHS_P158_PROJECTION_NON_MUTATING") throw new Error("KERNEL_RECEIPT_CLASSIFICATION_INVALID");
  return Object.freeze({
    projection: Object.freeze(response.projection),
    receipt: Object.freeze({
      receiptId: receipt.receipt_id,
      objectRoot: receipt.object_root,
      classification: receipt.classification,
      replayVerified: true,
    }),
  });
}

export class ReadOnlyNFT {
  constructor(definition, authority) {
    if (!(authority instanceof KernelAuthorityAdapter)) throw new TypeError("kernel authority adapter required");
    this.definition = structuredClone(definition);
    this.authority = authority;
    const identity = authority.identify(this.definition);
    if (!identity || identity.kernelAuthority !== "HHS_PASS158_NATIVE_ABI" || identity.definitionReplay?.matched !== true) {
      throw new Error("KERNEL_DEFINITION_RECEIPT_REQUIRED");
    }
    this.definitionId = requireCanonicalGlyphs(identity.definitionId, 216, "HASH216_DEFINITION_ID");
    this.bindings = new Map();
  }
  bind(symbol, value) {
    if (this.bindings.has(symbol)) throw new Error("DUPLICATE_CONFLICTING_BINDING");
    this.bindings.set(symbol, value);
  }
  validate() {
    if (this.definition.constraints.includes("O==Pi")) throw new Error("PHASE_IDENTITY_VIOLATION");
    if (!Array.isArray(this.definition.tensorShape)) throw new Error("TENSOR_SHAPE_MISMATCH");
    return Object.freeze({ status: "VALIDATED", definitionId: this.definitionId, bindingCount: this.bindings.size });
  }
  project(profile = "IEEE754_BINARY64_CONTROL") {
    const bindings = {};
    for (const [symbol, value] of this.bindings.entries()) {
      if (!(value instanceof ExactRational)) throw new Error("TYPE_MISMATCH");
      bindings[symbol] = { kind: "RATIONAL", value: value.canonical() };
    }
    const response = this.authority.project({ definition: this.definition, definitionId: this.definitionId, bindings, profile });
    return verifyKernelResponse(response, this.definitionId);
  }
}
