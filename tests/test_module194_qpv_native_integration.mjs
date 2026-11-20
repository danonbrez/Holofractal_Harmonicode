import assert from "node:assert/strict";
import {webcrypto} from "node:crypto";
import {VM81_RECEIPT_DOMAIN,canonicalVm81Receipt,createSignedVm81Verifier}
  from "../examples/harmonicode_module194_native_vm81_receipt.mjs";
import {QPV_PROTOCOL,canonicalQpvStatement,appendQpvCheckpoint,verifyQpvTranscript}
  from "../examples/harmonicode_module194_qpv_checkpoint.mjs";

if(!globalThis.crypto)globalThis.crypto=webcrypto;
const subtle=globalThis.crypto.subtle,enc=new TextEncoder();
const hex=a=>Array.from(a,v=>v.toString(16).padStart(2,"0")).join("");
const sha=async b=>hex(new Uint8Array(await subtle.digest("SHA-256",b)));
const native=await subtle.generateKey("Ed25519",false,["sign","verify"]);
const qpv=await subtle.generateKey("Ed25519",false,["sign","verify"]);
const record=enc.encode('{"source":"Module194","tick":"8"}'),tick=8n;
const receipt={
  schema:VM81_RECEIPT_DOMAIN,authority:"SIGNED_ENVIRONMENTAL_VM81_ADMISSION",
  tick:"8",checkpointSha256:await sha(record),
  hash72ReceiptSha256:"a".repeat(64),hash216ProofSha256:"b".repeat(64),
  nativeAdmissionVerified:true,singleVm81Admission:true,lane5BiosMediated:true,
  hash72Verified:true,hash216Verified:true,
  sVec:["0","0","0","0"],deltaE:"0",psi:"0",omega:true,keyId:"native-test"
};
const signedNative={...receipt,signatureHex:hex(new Uint8Array(
  await subtle.sign("Ed25519",native.privateKey,
    enc.encode(VM81_RECEIPT_DOMAIN+"|"+canonicalVm81Receipt(receipt)))))};
const nativeVerifier=createSignedVm81Verifier({
  readNativeReceipt:async()=>signedNative,trustedKeys:new Map([["native-test",native.publicKey]])
});
const witness={
  version:QPV_PROTOCOL.version,result:"PASS",sessionId:"integration-test",
  targetId:"test-area",tick:"8",nonceHex:"c".repeat(64),
  evidenceDigestHex:"d".repeat(64),checkpointDigestHex:await sha(record),
  previousHashHex:QPV_PROTOCOL.genesisHash,issuedAtMs:"1",expiresAtMs:"2000",
  verifierKeyId:"qpv-test"
};
const signedQpv={...witness,signatureHex:hex(new Uint8Array(
  await subtle.sign("Ed25519",qpv.privateKey,
    enc.encode(QPV_PROTOCOL.domain+"|QPV-ATTESTATION|"+canonicalQpvStatement(witness)))))};
const trust={verifyVm81:nativeVerifier,nowMs:1000n,
  trustedQpvKeys:new Map([["qpv-test",qpv.publicKey]])};
const chain=[];
await appendQpvCheckpoint(chain,{
  recordBytes:record,tick,sessionId:"integration-test",targetId:"test-area",
  witness:signedQpv
},trust);
assert.equal(chain.length,1);
assert.equal((await verifyQpvTranscript(chain,trust)).valid,true);
const invalidNative={...signedNative,hash72ReceiptSha256:"0".repeat(64)};
const failTrust={...trust,verifyVm81:createSignedVm81Verifier({
  readNativeReceipt:async()=>invalidNative,
  trustedKeys:new Map([["native-test",native.publicKey]])
})};
assert.equal((await verifyQpvTranscript(chain,failTrust)).valid,false);
await assert.rejects(appendQpvCheckpoint([],{
  recordBytes:record,tick,sessionId:"integration-test",targetId:"wrong-area",
  witness:signedQpv},trust),/QPV_WITNESS_HOLD/);
console.log("Module194 signed native VM81 plus QPV integration fixture passed");
