import { createHash } from "node:crypto";

export const CONTRACT_ID = "HHS-P158-LLABI-NFTC-API";

function stable(value) {
  if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
  }
  if (typeof value === "bigint") return JSON.stringify(`${value}n`);
  return JSON.stringify(value);
}

function hash216(text) {
  const bytes = [];
  let seed = Buffer.from(text, "utf8");
  for (let lane = 0; lane < 4; lane += 1) {
    seed = createHash("sha256").update(seed).update(Buffer.from([lane])).digest();
    bytes.push(seed);
  }
  return Buffer.concat(bytes).subarray(0, 27).toString("hex");
}

function hash72(text) {
  const digest = createHash("sha256").update(text).digest();
  const alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";
  return Array.from({ length: 72 }, (_, index) => alphabet[digest[index % digest.length] % 72]).join("");
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

export class ReadOnlyNFT {
  constructor(definition) {
    this.definition = structuredClone(definition);
    this.definitionId = `hash216:${hash216(stable(this.definition))}`;
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
    const rational = [...this.bindings.values()].find((value) => value instanceof ExactRational);
    if (!rational) throw new Error("TYPE_MISMATCH");
    const approximate = Number(rational.numerator) / Number(rational.denominator);
    if (!Number.isFinite(approximate)) throw new Error("NONFINITE_PROJECTION");
    const projection = Object.freeze({ profile, approximate, authority: "PROJECTION_ONLY" });
    const delta = Object.freeze({
      ratio: new ExactRational(BigInt(Math.round(approximate * 1_000_000)), 1_000_000n),
      reference: rational,
    });
    const receiptPayload = stable({ definitionId: this.definitionId, profile, approximate, reference: rational.canonical() });
    return Object.freeze({
      projection,
      delta,
      receipt: Object.freeze({
        receiptId: `hash72:${hash72(receiptPayload)}`,
        objectRoot: `hash216:${hash216(receiptPayload)}`,
        classification: "HHS_P158_WASM_READ_ONLY_PROJECTION_VERIFIED",
      }),
    });
  }
}
