/**
 * HARMONICODE Hash72^2 QPV witness ingress and extended checkpoint seal.
 *
 * R*_t = (R_t, Q_t)
 * h*_t = SHA256(D || h*_(t-1) || Encode(R*_t))
 * A*_t = (s=0) && (DeltaE=0) && (Psi=0) && Omega && VerifyQPV(Q_t)
 *
 * Physical QPV acceptance is performed by an EXTERNAL trusted verifier.
 * This module authenticates its signed statement, binds it to a canonical
 * checkpoint, and enforces ordered witness admission. It does not simulate
 * entangled photons, Bell tests, or independently prove physical location.
 */
const D = "HARMONICODE_VM81_HASH72SQ_V1";
const VERSION = "HHS_QPV_WITNESS_V1";
const HEX_32 = /^[0-9a-f]{64}$/;
const HEX_64 = /^[0-9a-f]{128}$/;
const NAT = /^(0|[1-9][0-9]*)$/;
const ID = /^[A-Za-z0-9_.:-]{1,128}$/;
const enc = new TextEncoder();
const cryptoAPI = () => {
  if (!globalThis.crypto?.subtle) throw Error("HHS_WEBCRYPTO_REQUIRED");
  return globalThis.crypto.subtle;
};
function requireField(ok, code) { if (!ok) throw Error(code); }
function hex(bytes) { return Array.from(bytes, v=>v.toString(16).padStart(2,"0")).join(""); }
function unhex(value) {
  requireField(typeof value==="string" && value.length%2===0 &&
    /^[0-9a-f]*$/.test(value), "HHS_NONCANONICAL_HEX");
  const out=new Uint8Array(value.length/2);
  for(let i=0;i<out.length;i++)out[i]=parseInt(value.slice(2*i,2*i+2),16);
  return out;
}
function u32(n) {
  requireField(Number.isSafeInteger(n) && n>=0 && n<=0xffffffff,"HHS_FRAME_LENGTH");
  return Uint8Array.from([(n>>>24)&255,(n>>>16)&255,(n>>>8)&255,n&255]);
}
function frame(bytes) {
  const out=new Uint8Array(bytes.length+4);
  out.set(u32(bytes.length),0);out.set(bytes,4);return out;
}
function concat(...parts) {
  const out=new Uint8Array(parts.reduce((a,p)=>a+p.length,0));
  let offset=0;for(const p of parts){out.set(p,offset);offset+=p.length;}return out;
}
async function digest(data) { return hex(new Uint8Array(await cryptoAPI().digest("SHA-256",data))); }

export function canonicalQpvStatement(witness) {
  requireField(witness && typeof witness==="object" &&
    witness.version===VERSION && witness.result==="PASS", "HHS_QPV_NOT_ACCEPTED");
  for(const k of ["sessionId","targetId","verifierKeyId"])
    requireField(typeof witness[k]==="string" && ID.test(witness[k]), "HHS_QPV_ID");
  for(const k of ["tick","issuedAtMs","expiresAtMs"])
    requireField(typeof witness[k]==="string" && NAT.test(witness[k]),"HHS_QPV_TIME");
  requireField(BigInt(witness.expiresAtMs)>BigInt(witness.issuedAtMs),
    "HHS_QPV_EXPIRED_WINDOW");
  for(const k of ["nonceHex","evidenceDigestHex","checkpointDigestHex","previousHashHex"])
    requireField(typeof witness[k]==="string" && HEX_32.test(witness[k]),"HHS_QPV_DIGEST");
  // Explicit order: signed canonical payload cannot depend on JS object insertion order.
  return JSON.stringify({
    version:VERSION,result:"PASS",sessionId:witness.sessionId,
    targetId:witness.targetId,tick:witness.tick,
    nonceHex:witness.nonceHex,evidenceDigestHex:witness.evidenceDigestHex,
    checkpointDigestHex:witness.checkpointDigestHex,
    previousHashHex:witness.previousHashHex,
    issuedAtMs:witness.issuedAtMs,expiresAtMs:witness.expiresAtMs,
    verifierKeyId:witness.verifierKeyId
  });
}

export async function verifyQpvWitness(witness, expected, trustedKeys, nowMs) {
  try {
    const statement=canonicalQpvStatement(witness);
    if(!HEX_64.test(witness.signatureHex??""))return false;
    if(!expected || witness.sessionId!==expected.sessionId ||
       witness.targetId!==expected.targetId ||
       witness.tick!==expected.tick ||
       witness.checkpointDigestHex!==expected.checkpointDigestHex ||
       witness.previousHashHex!==expected.previousHashHex)return false;
    requireField(typeof nowMs==="bigint" && nowMs>=0n,"HHS_QPV_NOW_REQUIRED");
    if(nowMs<BigInt(witness.issuedAtMs) || nowMs>BigInt(witness.expiresAtMs))return false;
    const key=trustedKeys?.get(witness.verifierKeyId);
    if(!key || key.algorithm?.name!=="Ed25519" || !key.usages?.includes("verify"))return false;
    return await cryptoAPI().verify("Ed25519",key,unhex(witness.signatureHex),
      enc.encode(D+"|QPV-ATTESTATION|"+statement));
  } catch { return false; }
}

function checkGate(gate) {
  if(!gate || gate.nativeAdmissionVerified!==true || gate.omega!==true ||
     gate.deltaE!==0n || gate.psi!==0n ||
     !Array.isArray(gate.sVec) || gate.sVec.length!==4 ||
     gate.sVec.some(v=>v!==0n))return false;
  return true;
}

function encodedExtendedRecord(recordBytes,witness) {
  // Encode(R*) is unambiguous binary framing: 4-byte length + raw R,
  // then 4-byte length + canonical signed QPV witness bytes.
  const signed=canonicalQpvStatement(witness);
  requireField(HEX_64.test(witness.signatureHex??""),"HHS_QPV_SIGNATURE_FORMAT");
  const q=enc.encode(signed+"|"+witness.signatureHex);
  return concat(frame(recordBytes),frame(q));
}

const ZERO="0".repeat(64);
export async function appendQpvCheckpoint(chain,params,trust) {
  requireField(Array.isArray(chain),"HHS_CHAIN_REQUIRED");
  requireField(params?.recordBytes instanceof Uint8Array,"HHS_CANONICAL_RECORD_BYTES_REQUIRED");
  requireField(typeof params.tick==="bigint" && params.tick>=0n,"HHS_CHECKPOINT_TICK");
  requireField(typeof trust?.verifyVm81==="function","HHS_TRUSTED_VM81_CALLBACK_REQUIRED");
  const prev=chain.length?chain[chain.length-1].hash:ZERO;
  if(chain.length)requireField(params.tick>BigInt(chain[chain.length-1].tick),
    "HHS_CHECKPOINT_NONMONOTONE");
  const checkpointDigestHex=await digest(params.recordBytes);
  const expected={sessionId:params.sessionId,targetId:params.targetId,
    tick:params.tick.toString(),checkpointDigestHex,previousHashHex:prev};
  const gate=await trust.verifyVm81(params.recordBytes,params.tick);
  requireField(checkGate(gate),"HHS_NATIVE_VM81_HOLD");
  requireField(await verifyQpvWitness(params.witness,expected,
      trust.trustedQpvKeys,trust.nowMs),"HHS_QPV_WITNESS_HOLD");
  const nonceKey=params.witness.sessionId+":"+params.witness.nonceHex;
  requireField(!chain.some(e=>e.nonceKey===nonceKey),"HHS_QPV_NONCE_REPLAY");
  const payload=encodedExtendedRecord(params.recordBytes,params.witness);
  const hash=await digest(concat(frame(enc.encode(D)),unhex(prev),frame(payload)));
  const entry=Object.freeze({
    index:chain.length,tick:params.tick.toString(),prevHash:prev,hash,nonceKey,
    recordHex:hex(params.recordBytes),
    witness:Object.freeze({...params.witness}),admissionBit:1,
    authority:"EXTERNAL_QPV_SIGNED_AND_NATIVE_VM81_CALLBACK"
  });
  chain.push(entry);return entry;
}

export async function verifyQpvTranscript(chain,trust) {
  if(!Array.isArray(chain) || typeof trust?.verifyVm81!=="function")
    return {valid:false,reason:"HHS_AUDIT_TRUST_REQUIRED"};
  let prev=ZERO,lastTick=-1n;const seen=new Set();
  for(let i=0;i<chain.length;i++){
    const e=chain[i];
    try {
      requireField(e.index===i && e.prevHash===prev && HEX_32.test(e.hash),
        "HHS_CHAIN_LINK");
      requireField(typeof e.tick==="string" && NAT.test(e.tick) &&
        BigInt(e.tick)>lastTick,"HHS_CHAIN_TICK");
      const bytes=unhex(e.recordHex);
      const checkpointDigestHex=await digest(bytes);
      const expected={sessionId:e.witness.sessionId,targetId:e.witness.targetId,
        tick:e.tick,checkpointDigestHex,previousHashHex:prev};
      requireField(await verifyQpvWitness(e.witness,expected,
        trust.trustedQpvKeys,trust.nowMs),"HHS_QPV_WITNESS_HOLD");
      const nonceKey=e.witness.sessionId+":"+e.witness.nonceHex;
      requireField(!seen.has(nonceKey),"HHS_QPV_NONCE_REPLAY");seen.add(nonceKey);
      const gate=await trust.verifyVm81(bytes,BigInt(e.tick));
      requireField(checkGate(gate),"HHS_NATIVE_VM81_HOLD");
      const payload=encodedExtendedRecord(bytes,e.witness);
      const h=await digest(concat(frame(enc.encode(D)),unhex(prev),frame(payload)));
      requireField(h===e.hash && e.admissionBit===1,"HHS_CHECKPOINT_HASH");
      prev=e.hash;lastTick=BigInt(e.tick);
    }catch(error){return {valid:false,failedIndex:i,reason:error.message};}
  }
  return {valid:true,verifiedCheckpoints:chain.length,terminalHash:prev};
}
export const QPV_PROTOCOL=Object.freeze({domain:D,version:VERSION,genesisHash:ZERO});
