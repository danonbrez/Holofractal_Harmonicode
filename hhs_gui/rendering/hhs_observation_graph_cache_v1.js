/* Pass 220 read-only graphics observation cache; no VM81/Hash216 identity authority. */
(function(root,factory){
  "use strict";
  const api=factory();
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  if(root)root.HHSObservationGraphCacheV1=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const SCHEMA="HHS_PASS_220_PRESENTATION_OBSERVATION_CACHE_V1";
  const HASH216=/^[0-9A-Za-z_-]{216}$/;
  const U64=(1n<<64n)-1n, I64=(1n<<63n)-1n;
  const fail=code=>{throw new Error(code);};
  function integer(value,label,signed=false){
    if(typeof value==="number"&&!Number.isSafeInteger(value))fail("OBS_INVALID_"+label);
    if(!(typeof value==="bigint"||typeof value==="number"||(typeof value==="string"&&/^-?\d+$/.test(value))))fail("OBS_INVALID_"+label);
    const n=BigInt(value),min=signed?-I64-1n:0n,max=signed?I64:U64;
    if(n<min||n>max)fail("OBS_INVALID_"+label);
    return n;
  }
  function hash(value,label){
    if(typeof value!=="string"||!HASH216.test(value))fail("OBS_INVALID_"+label);
    return value;
  }
  function asBytes(input){
    if(input instanceof ArrayBuffer)return new Uint8Array(input);
    if(ArrayBuffer.isView(input))return new Uint8Array(input.buffer,input.byteOffset,input.byteLength);
    fail("OBS_INVALID_PACKET");
  }
  function copy(bytes){const out=new Uint8Array(bytes.byteLength);out.set(bytes);return out;}
  function cmp(a,b){const x=a.timeNum*b.timeDen,y=b.timeNum*a.timeDen;return x<y?-1:x>y?1:0;}
  class ObservationCache{
    constructor(opts={}){
      if(typeof opts.validatePacket!=="function")fail("OBS_NATIVE_VALIDATOR_REQUIRED");
      const c=opts.capacity===undefined?64:opts.capacity;
      if(!Number.isInteger(c)||c<2||c>4096)fail("OBS_INVALID_CAPACITY");
      this._validate=opts.validatePacket;this._capacity=c;this._records=[];this._byFrame=new Map();this._lastVersion=null;
    }
    get length(){return this._records.length;}
    get capacity(){return this._capacity;}
    append(input){
      if(!input||typeof input!=="object")fail("OBS_INVALID_RECORD");
      if(input.nativeAdmission!==true)fail("OBS_NOT_ADMITTED");
      const decayHash216=hash(input.decayHash216,"DECAY_HASH216");
      const frameHash216=hash(input.frameHash216,"FRAME_HASH216");
      const matrixVersion=integer(input.matrixVersion,"MATRIX_VERSION");
      const packet=copy(asBytes(input.packet));
      const info=this._validate(packet);
      if(!info||info.compatibilityUnadmitted!==false||info.vm81AdmissionAuthority===true)fail("OBS_PACKET_NOT_NATIVE_ADMITTED");
      const timeNum=integer(info.exactTimeNum,"TIME_NUM",true);
      const timeDen=integer(info.exactTimeDen,"TIME_DEN");
      if(timeDen===0n)fail("OBS_ZERO_TIME_DEN");
      const frameIndex=integer(info.frameIndex,"FRAME_INDEX");
      if(input.frameIndex!==undefined&&integer(input.frameIndex,"FRAME_INDEX")!==frameIndex)fail("OBS_FRAME_INDEX_MISMATCH");
      if(input.timeNum!==undefined&&integer(input.timeNum,"TIME_NUM",true)!==timeNum)fail("OBS_TIME_MISMATCH");
      if(input.timeDen!==undefined&&integer(input.timeDen,"TIME_DEN")!==timeDen)fail("OBS_TIME_MISMATCH");
      const rec=Object.freeze({schema:SCHEMA,decayHash216,frameHash216,matrixVersion,timeNum,timeDen,frameIndex,packet});
      const last=this._records[this._records.length-1];
      if(this._lastVersion!==null&&matrixVersion<=this._lastVersion)fail("OBS_REPLAY_OR_OUT_OF_ORDER");
      if(last&&(cmp(rec,last)<=0||frameIndex<=last.frameIndex))fail("OBS_NON_MONOTONIC_TIME");
      if(this._byFrame.has(frameHash216))fail("OBS_DUPLICATE_FRAME");
      this._records.push(rec);this._byFrame.set(frameHash216,rec);this._lastVersion=matrixVersion;
      while(this._records.length>this._capacity){const removed=this._records.shift();this._byFrame.delete(removed.frameHash216);}
      return Object.freeze({decayHash216,frameHash216,matrixVersion,frameIndex});
    }
    _copy(x){return Object.freeze({schema:x.schema,decayHash216:x.decayHash216,frameHash216:x.frameHash216,matrixVersion:x.matrixVersion,timeNum:x.timeNum,timeDen:x.timeDen,frameIndex:x.frameIndex,packet:copy(x.packet)});}
    lookup(frameHash216){const v=this._byFrame.get(hash(frameHash216,"FRAME_HASH216"));return v?this._copy(v):null;}
    bracket(timeNum,timeDen){
      const target={timeNum:integer(timeNum,"TIME_NUM",true),timeDen:integer(timeDen,"TIME_DEN")};
      if(target.timeDen===0n)fail("OBS_ZERO_TIME_DEN");
      let previous=null;
      for(const rec of this._records){
        const c=cmp(rec,target);
        if(c===0)return Object.freeze({prior:this._copy(rec),next:this._copy(rec),exact:true});
        if(c>0)return previous?Object.freeze({prior:this._copy(previous),next:this._copy(rec),exact:false}):null;
        previous=rec;
      }
      return null; // Never extrapolate outside cached interval.
    }
    snapshot(){return Object.freeze({schema:SCHEMA,count:this.length,capacity:this.capacity,lastMatrixVersion:this._lastVersion,canonicalMutationAuthority:false,vm81AdmissionAuthority:false,hash216IdentityAuthority:false});}
  }
  return Object.freeze({SCHEMA,ObservationCache});
});
