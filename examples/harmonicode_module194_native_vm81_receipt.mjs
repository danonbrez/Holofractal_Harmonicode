/**
 * Signed environmental VM81 admission receipt adapter.
 *
 * This is NOT a VM81 implementation. It authenticates a receipt issued by the
 * existing native admission authority and binds that verdict to exact
 * checkpoint bytes and physics tick. Candidate-only Lane 5 responses, browser
 * projections and unsigned booleans cannot mint admission.
 */
const DOMAIN="HARMONICODE_VM81_NATIVE_ADMISSION_RECEIPT_V1";
const HEX64=/^[0-9a-f]{64}$/;
const HEX128=/^[0-9a-f]{128}$/;
const DEC=/^(0|[1-9][0-9]*)$/;
const KEY_ID=/^[A-Za-z0-9_.:-]{1,128}$/;
const encoder=new TextEncoder();
function requireValue(condition,message){if(!condition)throw Error(message);}
function bytesHex(value){return Array.from(value,v=>v.toString(16).padStart(2,"0")).join("");}
function fromHex(value) {
  requireValue(typeof value==="string"&&value.length%2===0&&/^[0-9a-f]*$/.test(value),
    "HHS_VM81_HEX_INVALID");
  const b=new Uint8Array(value.length/2);
  for(let i=0;i<b.length;i++)b[i]=parseInt(value.slice(i*2,i*2+2),16);
  return b;
}
function sealPayload(receipt) {
  requireValue(receipt?.schema===DOMAIN && receipt.authority==="SIGNED_ENVIRONMENTAL_VM81_ADMISSION",
    "HHS_VM81_AUTHORITY_UNVERIFIED");
  requireValue(typeof receipt.tick==="string" && DEC.test(receipt.tick),
    "HHS_VM81_TICK_INVALID");
  requireValue(HEX64.test(receipt.checkpointSha256??"") &&
    HEX64.test(receipt.hash72ReceiptSha256??"") &&
    HEX64.test(receipt.hash216ProofSha256??""), "HHS_VM81_HASH_MISSING");
  requireValue(typeof receipt.keyId==="string"&&KEY_ID.test(receipt.keyId),
    "HHS_VM81_KEY_INVALID");
  requireValue(receipt.nativeAdmissionVerified===true && receipt.omega===true &&
    receipt.deltaE==="0" && receipt.psi==="0" &&
    Array.isArray(receipt.sVec) && receipt.sVec.length===4 &&
    receipt.sVec.every(v=>v==="0"),"HHS_VM81_CLOSURE_FAILED");
  requireValue(receipt.singleVm81Admission===true &&
    receipt.lane5BiosMediated===true &&
    receipt.hash72Verified===true && receipt.hash216Verified===true,
    "HHS_VM81_PROOF_INCOMPLETE");
  return JSON.stringify({
    schema:DOMAIN,
    authority:receipt.authority,
    tick:receipt.tick,
    checkpointSha256:receipt.checkpointSha256,
    hash72ReceiptSha256:receipt.hash72ReceiptSha256,
    hash216ProofSha256:receipt.hash216ProofSha256,
    nativeAdmissionVerified:true,
    singleVm81Admission:true,
    lane5BiosMediated:true,
    hash72Verified:true,
    hash216Verified:true,
    sVec:["0","0","0","0"],deltaE:"0",psi:"0",omega:true,
    keyId:receipt.keyId
  });
}
export function canonicalVm81Receipt(receipt){return sealPayload(receipt);}
export function createSignedVm81Verifier({readNativeReceipt,trustedKeys}) {
  requireValue(typeof readNativeReceipt==="function","HHS_VM81_NATIVE_READ_REQUIRED");
  requireValue(trustedKeys instanceof Map,"HHS_VM81_TRUST_STORE_REQUIRED");
  return async function verifyVm81(recordBytes,tick) {
    if(!(recordBytes instanceof Uint8Array)||typeof tick!=="bigint"||tick<0n)
      throw Error("HHS_VM81_CHECKPOINT_INPUT");
    // Independently read a native receipt. Do not reconstruct success locally.
    const receipt=await readNativeReceipt(recordBytes.slice(),tick);
    const canonical=sealPayload(receipt);
    requireValue(receipt.tick===tick.toString(),"HHS_VM81_TICK_MISMATCH");
    const subtle=globalThis.crypto?.subtle;
    requireValue(!!subtle,"HHS_VM81_WEBCRYPTO_UNAVAILABLE");
    const digest=bytesHex(new Uint8Array(await subtle.digest("SHA-256",recordBytes)));
    requireValue(receipt.checkpointSha256===digest,"HHS_VM81_CHECKPOINT_MISMATCH");
    requireValue(HEX128.test(receipt.signatureHex??""),"HHS_VM81_SIGNATURE_MISSING");
    const key=trustedKeys.get(receipt.keyId);
    requireValue(key?.algorithm?.name==="Ed25519"&&key.usages?.includes("verify"),
      "HHS_VM81_UNTRUSTED_KEY");
    const valid=await subtle.verify("Ed25519",key,fromHex(receipt.signatureHex),
      encoder.encode(DOMAIN+"|"+canonical));
    requireValue(valid,"HHS_VM81_SIGNATURE_INVALID");
    return Object.freeze({
      nativeAdmissionVerified:true,omega:true,deltaE:0n,psi:0n,
      sVec:Object.freeze([0n,0n,0n,0n])
    });
  };
}
export const VM81_RECEIPT_DOMAIN=DOMAIN;
