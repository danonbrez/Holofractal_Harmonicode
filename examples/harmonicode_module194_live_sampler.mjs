/**
 * Read-only V150 Module194 live projection adapter.
 * Observed coordinates: world x,y,z and physical phase; not native VM81 4D state.
 */
const COUNT=10368,PAIR_COUNT=5184,MOD=72n,MAX=26873855;
const residue=n=>((n%MOD)+MOD)%MOD;
function rational(input){
  if(typeof input==="number")return ieeeRational(input);
  if(typeof input==="bigint")return [input,1n];
  if(typeof input==="string" && /^-?[0-9]+(?:\.[0-9]+)?$/.test(input)){
    const negative=input.startsWith("-"),s=negative?input.slice(1):input;
    const [a,b=""]=s.split(".");
    return [(negative?-1n:1n)*BigInt(a+b),10n**BigInt(b.length)];
  }
  throw new TypeError("INVALID_EXACT_BOUND");
}
export function ieeeRational(number){
  if(!Number.isFinite(number))throw new RangeError("NONFINITE_IEEE64");
  const dv=new DataView(new ArrayBuffer(8));
  dv.setFloat64(0,number,false);
  const bits=dv.getBigUint64(0,false),exp=Number((bits>>52n)&2047n);
  const mantissa=(bits&((1n<<52n)-1n))|(exp===0?0n:1n<<52n);
  const shift=(exp===0?-1022:exp-1023)-52;
  const signed=(bits>>63n)?-mantissa:mantissa;
  return shift>=0?[signed<<BigInt(shift),1n]:[signed,1n<<BigInt(-shift)];
}
function floorDivide(num,den){
  if(den<=0n)throw new RangeError("INVALID_QUANTIZATION_SPAN");
  const q=num/den;
  return num<0n && num%den!==0n?q-1n:q;
}
function quantize(value,[mn,md],[xn,xd]){
  if(xn*md<=mn*xd)throw new RangeError("INVALID_QUANTIZATION_BOUNDS");
  const [n,d]=ieeeRational(value);
  // 72 * (value-min)/(max-min), entirely BigInt after IEEE64 ingress.
  return Number(residue(floorDivide(
    72n*(n*md-d*mn)*xd,
    d*(xn*md-mn*xd))));
}
export function sampleModule194Projection(scope,bounds){
  const api=scope?.HHSUnifiedProjectionBuffer,m194=scope?.HHSModule194;
  if(typeof api?.snapshot!=="function" || typeof api?.describe!=="function" ||
     typeof m194?.inspect!=="function")throw Error("V150_PROJECTION_API_UNAVAILABLE");
  const before=api.describe(),mBefore=m194.inspect();
  if(!mBefore.ready || !Number.isSafeInteger(mBefore.physicsTick) ||
     mBefore.physicsTick<0)throw Error("MODULE194_NOT_READY");
  const blocks=api.snapshot(),after=api.describe(),mAfter=m194.inspect();
  if(before.physicsTick!==after.physicsTick || before.renderEpoch!==after.renderEpoch ||
     before.physicsTick!==mBefore.physicsTick || mBefore.physicsTick!==mAfter.physicsTick)
    return Object.freeze({status:"RETRY_NONATOMIC_OBSERVATION",admitted:false});
  if(!Array.isArray(blocks) || blocks.reduce((n,b)=>n+b.count,0)!==COUNT ||
     blocks.some(b=>b.tick!==before.physicsTick || b.positions?.length!==b.count*3 ||
       b.phases?.length!==b.count || b.ieeePositionBits?.length!==b.count*3))
    return Object.freeze({status:"INCOMPLETE_PROJECTION",admitted:false});
  const keys=["x","y","z","phase"];
  const limits=keys.map(k=>{
    if(!Array.isArray(bounds?.[k]) || bounds[k].length!==2)
      throw new TypeError("MISSING_"+k+"_BOUNDS");
    return bounds[k].map(rational);
  });
  const coords=new Uint8Array(COUNT*4),addresses=new Uint32Array(COUNT);
  const dv=new DataView(new ArrayBuffer(8));
  let id=0;
  for(const block of blocks){
    for(let i=0;i<block.count;i++,id++){
      const values=[];
      for(let a=0;a<3;a++){
        // Read source IEEE64 copy, not lossy presentation Float32 positions.
        dv.setBigUint64(0,block.ieeePositionBits[3*i+a],false);
        values.push(dv.getFloat64(0,false));
      }
      values.push(block.phases[i]);
      const c=values.map((v,a)=>quantize(v,...limits[a]));
      coords.set(c,id*4);
      addresses[id]=c[0]+72*c[1]+5184*c[2]+373248*c[3];
    }
  }
  let broken=0;
  for(let i=0;i<PAIR_COUNT;i++)
    if(addresses[i]+addresses[i+PAIR_COUNT]!==MAX)broken++;
  return Object.freeze({
    status:"OBSERVED",admitted:false,physicsTick:BigInt(before.physicsTick),
    projectionEpoch:before.renderEpoch,particleCount:COUNT,
    coordinates:coords,addresses,brokenComplementPairs:broken,
    complementVerified:broken===0,nativeAdmissionVerified:false,
    source:"V150_UNIFIED_RENDER_PROJECTION",
    phaseSource:"PHYSICAL_PHASE_RENDER_COPY",
    exactArithmeticAfterIEEE64Ingress:true
  });
}
