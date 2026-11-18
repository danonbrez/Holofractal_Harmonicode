import assert from "node:assert/strict";
import {webcrypto} from "node:crypto";
import {QPV_PROTOCOL,canonicalQpvStatement,verifyQpvWitness,
  appendQpvCheckpoint,verifyQpvTranscript} from "../examples/harmonicode_module194_qpv_checkpoint.mjs";

if(!globalThis.crypto)globalThis.crypto=webcrypto;
const api=globalThis.crypto.subtle,enc=new TextEncoder();
const keypair=await api.generateKey("Ed25519",false,["sign","verify"]);
const keys=new Map([["fixture-verifier-1",keypair.publicKey]]);
const digest=async bytes=>Array.from(new Uint8Array(await api.digest("SHA-256",bytes)),
  n=>n.toString(16).padStart(2,"0")).join("");
const hex=bytes=>Array.from(bytes,n=>n.toString(16).padStart(2,"0")).join("");
const gate=Object.freeze({nativeAdmissionVerified:true,omega:true,
  deltaE:0n,psi:0n,sVec:[0n,0n,0n,0n]});
const trust={trustedQpvKeys:keys,nowMs:1000n,
  // This is a FIXTURE ONLY; production must invoke native authoritative gate.
  verifyVm81:async()=>gate};
async function sign(recordBytes,tick,prev,nonce) {
  const statement={
    version:QPV_PROTOCOL.version,result:"PASS",sessionId:"fixture-session",
    targetId:"test-target",tick:String(tick),nonceHex:nonce,
    evidenceDigestHex:"1".repeat(64),checkpointDigestHex:await digest(recordBytes),
    previousHashHex:prev,issuedAtMs:"500",expiresAtMs:"1500",
    verifierKeyId:"fixture-verifier-1"
  };
  const bytes=enc.encode(QPV_PROTOCOL.domain+"|QPV-ATTESTATION|"+
    canonicalQpvStatement(statement));
  const signatureHex=hex(new Uint8Array(await api.sign("Ed25519",keypair.privateKey,bytes)));
  return {...statement,signatureHex};
}
const chain=[],recordBytes=enc.encode('{"tick":"1","status":"fixture"}');
const witness=await sign(recordBytes,1n,QPV_PROTOCOL.genesisHash,"2".repeat(64));
assert.equal(await verifyQpvWitness(witness,{
  sessionId:"fixture-session",targetId:"test-target",tick:"1",
  checkpointDigestHex:await digest(recordBytes),previousHashHex:QPV_PROTOCOL.genesisHash
},keys,1000n),true);
const params={recordBytes,tick:1n,sessionId:"fixture-session",targetId:"test-target",witness};
const added=await appendQpvCheckpoint(chain,params,trust);
assert.equal(added.admissionBit,1);
assert.equal((await verifyQpvTranscript(chain,trust)).valid,true);
assert.equal((await verifyQpvTranscript(chain,{...trust,nowMs:1501n})).valid,false);
assert.equal((await verifyQpvTranscript(chain,{...trust,
  verifyVm81:async()=>({...gate,psi:1n})})).valid,false);
const swapped={...witness,targetId:"attacker-target"};
await assert.rejects(appendQpvCheckpoint([],{...params,witness:swapped},trust),/QPV_WITNESS_HOLD/);
await assert.rejects(appendQpvCheckpoint([],{...params,sessionId:"other"},trust),/QPV_WITNESS_HOLD/);
await assert.rejects(appendQpvCheckpoint([],{...params},
  {...trust,verifyVm81:async()=>({...gate,nativeAdmissionVerified:false})}),/NATIVE_VM81_HOLD/);
const secondRecord=enc.encode('{"tick":"2","status":"fixture"}');
const repeated=await sign(secondRecord,2n,added.hash,witness.nonceHex);
await assert.rejects(appendQpvCheckpoint(chain,{
  ...params,recordBytes:secondRecord,tick:2n,witness:repeated},trust),/NONCE_REPLAY/);
const fresh=await sign(secondRecord,2n,added.hash,"3".repeat(64));
await appendQpvCheckpoint(chain,{...params,recordBytes:secondRecord,
  tick:2n,witness:fresh},trust);
assert.equal((await verifyQpvTranscript(chain,trust)).verifiedCheckpoints,2);
const mutated=chain.map(x=>({...x}));
mutated[0]={...mutated[0],recordHex:"00"};
assert.equal((await verifyQpvTranscript(mutated,trust)).valid,false);
console.log("QPV signed-receipt fixture and extended transcript tests passed");
