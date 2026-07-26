import assert from "node:assert/strict";
import {
  ExactRational,
  ReadOnlyNFT,
  bigintToCanonicalBytes,
  canonicalBytesToBigint,
} from "./hhs_pass158.mjs";

const integer = 1799711799710000000000000000000000000000000000000000001n;
assert.equal(canonicalBytesToBigint(bigintToCanonicalBytes(integer)), integer);
assert.equal(canonicalBytesToBigint(bigintToCanonicalBytes(-integer)), -integer);

const rational = new ExactRational(2n, 6n);
assert.equal(rational.canonical(), "1/3");
assert.throws(() => Number(rational), /cannot coerce/);

const nft = new ReadOnlyNFT({
  contractId: "HHS-P158-LLABI-NFTC-API",
  objectClass: "NON_FUNGIBLE_TENSOR_CONSTRAINT",
  constraints: "A==B==C;O!=Pi",
  tensorShape: [9, 9],
  orderedSymbols: ["x", "x", "y"],
});
nft.bind("x", rational);
assert.equal(nft.validate().status, "VALIDATED");
const result = nft.project();
assert.equal(result.projection.authority, "PROJECTION_ONLY");
assert.equal(result.receipt.classification, "HHS_P158_WASM_READ_ONLY_PROJECTION_VERIFIED");
assert.equal(result.receipt.receiptId.length, "hash72:".length + 72);
assert.equal(result.receipt.objectRoot.length, "hash216:".length + 216);
assert.throws(() => nft.bind("x", rational), /DUPLICATE_CONFLICTING_BINDING/);

console.log("HHS_PASS_158_WASM_SANDBOX_BINDING_VERIFIED");
