import assert from "node:assert/strict";
import {webcrypto} from "node:crypto";
import {canonicalVm81Receipt,createSignedVm81Verifier,VM81_RECEIPT_DOMAIN}
  from "../examples/harmonicode_module194_native_vm81_receipt.mjs";

if(!globalThis.crypto)globalThis.crypto=webcrypto;
const subtle=globalThis.crypto.subtle,enc=new TextEncoder();
const hex=a=>Array.from(a,v=>v.toString(16).padStart(2,"0")).join("");
const hash=async bytes=>hex(new Uint8Array(await subtle.digest("SHA-256",bytes)));
const keys=await subtle.generateKey("Ed25519",false,["sign","verify"]);
const trust=new Map([["fixture-native",keys.publicKey]]);
const record=enc.encode('{"tick":"7","scope":"fixture"}');
const base={
  schema:VM81_RECEIPT_DOMAIN,authority:"SIGNED_ENVIRONMENTAL_VM81_ADMISSION",
  tick:"7",checkpointSha256:await hash(record),
  hash72ReceiptSha256:"a".repeat(64),hash216ProofSha256:"b".repeat(64),
  nativeAdmissionVerified:true,singleVm81Admission:true,
  lane5BiosMediated:true,hash72Verified:true,hash216Verified:true,
  sVec:["0","0","0","0"],deltaE:"0",psi:"0",omega:true,keyId:"fixture-native"
};
async function signed(fields=base){
  const signBytes=enc.encode(VM81_RECEIPT_DOMAIN+"|"+canonicalVm81Receipt(fields));
  const signatureHex=hex(new Uint8Array(await subtle.sign("Ed25519",keys.privateKey,signBytes)));
  return {...fields,signatureHex};
}
let candidate=await signed();
const verify=createSignedVm81Verifier({readNativeReceipt:async()=>candidate,trustedKeys:trust});
assert.deepEqual(await verify(record,7n),{
  nativeAdmissionVerified:true,omega:true,deltaE:0n,psi:0n,sVec:[0n,0n,0n,0n]
});
await assert.rejects(verify(record,8n),/TICK_MISMATCH/);
await assert.rejects(verify(enc.encode("wrong"),7n),/CHECKPOINT_MISMATCH/);
candidate={...candidate,hash216ProofSha256:"c".repeat(64)};
await assert.rejects(verify(record,7n),/SIGNATURE_INVALID/);
candidate={...await signed(),omega:false};
await assert.rejects(verify(record,7n),/CLOSURE_FAILED/);
candidate={...await signed(),lane5BiosMediated:false};
await assert.rejects(verify(record,7n),/PROOF_INCOMPLETE/);
candidate=await signed();
await assert.rejects(createSignedVm81Verifier({
  readNativeReceipt:async()=>candidate,trustedKeys:new Map()
})(record,7n),/UNTRUSTED_KEY/);
await assert.rejects(createSignedVm81Verifier({
  readNativeReceipt:async()=>({status:"ready",candidate_only:true}),
  trustedKeys:trust
})(record,7n),/AUTHORITY_UNVERIFIED/);
console.log("Signed environmental VM81 receipt boundary: fixtures passed");
