import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";
import {
  ExactRational,
  KernelAuthorityAdapter,
  ReadOnlyNFT,
  bigintToCanonicalBytes,
  canonicalBytesToBigint,
} from "./hhs_pass158.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const project = resolve(here, "../..");
const bridge = join(here, "native_receipt_bridge.py");
const library = process.env.HHS_PASS158_LIBRARY || join(project, "dist/libhhs_pass158.so");

function invokeBridge(request) {
  const child = spawnSync(process.env.PYTHON || "python3", [bridge], {
    input: JSON.stringify(request),
    encoding: "utf8",
    env: { ...process.env, HHS_PASS158_LIBRARY: library },
  });
  if (child.status !== 0) throw new Error(`native bridge failed: ${child.stderr}`);
  return JSON.parse(child.stdout);
}

const authority = new KernelAuthorityAdapter({
  identify: (definition) => invokeBridge({ mode: "identity", definition }),
  project: (request) => invokeBridge({ mode: "project", ...request }),
});

const integer = 1799711799710000000000000000000000000000000000000000001n;
assert.equal(canonicalBytesToBigint(bigintToCanonicalBytes(integer)), integer);
assert.equal(canonicalBytesToBigint(bigintToCanonicalBytes(-integer)), -integer);

const rational = new ExactRational(2n, 6n);
assert.equal(rational.canonical(), "1/3");
assert.throws(() => Number(rational), /cannot coerce/);

const definition = {
  name: "PASS158_WASM_OBJECT",
  contractId: "HHS-P158-LLABI-NFTC-API",
  objectClass: "NON_FUNGIBLE_TENSOR_CONSTRAINT",
  constraints: "A==B==C;O!=Pi",
  tensorShape: [9, 9],
  orderedSymbols: ["x", "x", "y"],
};
assert.throws(() => new ReadOnlyNFT(definition), /kernel authority adapter required/);
const nft = new ReadOnlyNFT(definition, authority);
nft.bind("x", rational);
assert.equal(nft.validate().status, "VALIDATED");
const result = nft.project();
assert.equal(result.projection.authority, "PROJECTION_ONLY");
assert.equal(result.receipt.classification, "HHS_P158_PROJECTION_NON_MUTATING");
assert.equal(result.receipt.receiptId.length, 72);
assert.equal(result.receipt.objectRoot.length, 216);
assert.equal(result.receipt.replayVerified, true);
assert.throws(() => nft.bind("x", rational), /DUPLICATE_CONFLICTING_BINDING/);

console.log("HHS_PASS_158_WASM_SANDBOX_BINDING_VERIFIED");
