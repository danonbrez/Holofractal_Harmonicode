import assert from "node:assert/strict";
import { attachModule194Carrier } from "../examples/harmonicode_module194_carrier_adapter.mjs";

function fakeCarrier() {
  let tick = 41, corrupt = -1;
  const api = {
    inspect: () => ({ready:true,physicsTick:tick,particles:10368,groups:81,perGroup:128}),
    address: i => ({
      index:i,group:Math.floor((i%5184)/64),localSlot:i%64,
      reciprocalCluster:i<5184?0:1,partner: i<5184?i+5184:i-5184,
      loShu:4,hnan:0,spawn:[0,0,0],
      ...(i===corrupt ? {partner:0} : {})
    })
  };
  return {api, setTick:n=>{tick=n;}, corrupt:n=>{corrupt=n;}};
}
const source=fakeCarrier(), observer=attachModule194Carrier({HHSModule194:source.api});
assert.equal(observer.readTick(),41n);
const result=observer.auditPairs();
assert.equal(result.status,"PAIR_INDEX_PASS");
assert.equal(result.checkedPairs,5184);
assert.equal(result.brokenPairCount,0);
assert.equal(result.admitted,false);
assert.equal(result.nativeAdmissionVerified,false);
assert.throws(()=>observer.getLiveFourRegisterFrame(),/NOT_VERIFIED/);
assert.throws(()=>observer.readAddress(-1),/PARTICLE_INDEX/);
source.corrupt(5185);
const bad=observer.auditPairs();
assert.equal(bad.status,"PAIR_INDEX_FAIL");
assert.equal(bad.brokenPairCount,1);
source.corrupt(-1);
source.setTick(42);
assert.equal(observer.auditPairs().tick,"42");
const racing=fakeCarrier();
let calls=0;
const original=racing.api.inspect;
racing.api.inspect=()=>{calls++; return {...original(),physicsTick:calls>=2?44:43};};
assert.equal(attachModule194Carrier({HHSModule194:racing.api}).auditPairs().status,
  "RETRY_NONATOMIC_OBSERVATION");
console.log("Module194 read-only pair-index tests passed");
