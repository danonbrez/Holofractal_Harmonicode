import assert from "node:assert/strict";
import {ieeeRational,sampleModule194Projection} from "../examples/harmonicode_module194_live_sampler.mjs";
assert.deepEqual(ieeeRational(0.5),[4503599627370496n,9007199254740992n]);
const state={tick:7,epoch:3};
const positions=new Float32Array(10368*3),phases=new Float64Array(10368);
const positionBits=new BigUint64Array(10368*3);
const scope={
  HHSModule194:{inspect:()=>({ready:true,physicsTick:state.tick})},
  HHSUnifiedProjectionBuffer:{
    describe:()=>({physicsTick:state.tick,renderEpoch:state.epoch}),
    snapshot:()=>[{tick:state.tick,count:10368,positions,phases,ieeePositionBits:positionBits}]
  }
};
const bounds={x:["-1","1"],y:["-1","1"],z:["-1","1"],phase:["0","6.283185307179586"]};
let sample=sampleModule194Projection(scope,bounds);
assert.equal(sample.status,"OBSERVED");
assert.equal(sample.particleCount,10368);
assert.equal(sample.coordinates[0],36);
assert.equal(sample.coordinates[3],0);
assert.equal(sample.brokenComplementPairs,5184);
assert.equal(sample.admitted,false);
assert.equal(sample.nativeAdmissionVerified,false);
const original=scope.HHSUnifiedProjectionBuffer.snapshot;
scope.HHSUnifiedProjectionBuffer.snapshot=()=>{state.epoch++;return original();};
assert.equal(sampleModule194Projection(scope,bounds).status,"RETRY_NONATOMIC_OBSERVATION");
scope.HHSUnifiedProjectionBuffer.snapshot=()=>[{tick:state.tick-1,count:10368,positions,phases,ieeePositionBits:positionBits}];
assert.equal(sampleModule194Projection(scope,bounds).status,"INCOMPLETE_PROJECTION");
console.log("Module194 live projection observation tests passed");
