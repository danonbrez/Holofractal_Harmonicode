/* HHS Pass 220 — stereo PCM projection membrane.
   Audio never mutates canonical VM81, particle physics, or receipts. */
(function () {
  "use strict";
  const PAIR = Object.freeze({
    left: Object.freeze({numerator:Object.freeze(["x","xy","x+y","y"]), denominator:"zw"}),
    right:Object.freeze({numerator:Object.freeze(["z","zw","z-w","w"]), denominator:"xy"}),
    relation:"ordered stereo-bus equality; no scalar cancellation"
  });
  /* Typed presentation address identities. One stereo side projects over
     81*64 == 72*72 == 5184 positions; two ordered sides carry 10368.
     The equality is a lane cardinality, not an authority to scalarize Hash72. */
  const N=10368;
  const AUDIO_CLOCK=Object.freeze({
    canonicalRate:44100,visualHz:60,samplesPerFrame:735,
    laneCells:81*64,hash72Cells:72*72,pairedParticles:N,
    phaseBins:72,fadeFrames:6
  });
  if(AUDIO_CLOCK.canonicalRate!==AUDIO_CLOCK.visualHz*AUDIO_CLOCK.samplesPerFrame ||
     AUDIO_CLOCK.laneCells!==AUDIO_CLOCK.hash72Cells ||
     AUDIO_CLOCK.pairedParticles!==2*AUDIO_CLOCK.laneCells)
    throw new Error("HHS audio projection cardinality violated");

  /* Full-saturation Q144 color spectrum. Each Q144 index is retained as
     an integer phase address; RGB is derived only for the display. */
  const Q144_RGB=new Float32Array(144*3);
  for(let q=0;q<144;q++){
    const sector=Math.floor(q/24), fraction=(q%24)/24;
    let r=0,g=0,b=0;
    if(sector===0){r=1;g=fraction;}
    else if(sector===1){r=1-fraction;g=1;}
    else if(sector===2){g=1;b=fraction;}
    else if(sector===3){g=1-fraction;b=1;}
    else if(sector===4){r=fraction;b=1;}
    else {r=1;b=1-fraction;}
    Q144_RGB[q*3]=r;Q144_RGB[q*3+1]=g;Q144_RGB[q*3+2]=b;
  }
  function q144Index(address,sample,rms,harmonicPhase,bus){
    /* No commutation or scalarization of HHS tensor operands. These are
       raster-only hue addresses with the declared reciprocal +72 turn. */
    const original=((Math.trunc(address)%144)+144)%144;
    const audioStep=Math.round(finite(sample)*36)+Math.round(finite(rms)*36);
    return ((original+Math.round(finite(harmonicPhase))+audioStep+(bus?72:0))%144+144)%144;
  }
  function q144Css(q,alpha){
    const i=((Math.trunc(q)%144)+144)%144*3;
    return "rgba("+Math.round(Q144_RGB[i]*255)+","+
      Math.round(Q144_RGB[i+1]*255)+","+
      Math.round(Q144_RGB[i+2]*255)+","+
      clamp(alpha,0,1).toFixed(3)+")";
  }
  const HARMONIC=Object.freeze({referenceHz:432,stepsPerFrame:12,partials:4});
  /* RML2/RML4 integer u^72 rotor addresses, with u^18 quarter turns.
     "Larone" names this user's visual phase-gear projection profile, not
     an independent native VM81 operator or authenticated proof. */
  const GYRO_SHADER=Object.freeze({
    schema:"HHS_PASS220_LARONE_VERTICAL_RECIPROCAL_GYRO_SHADER_V1",
    phaseModulus:72,quarterTurn:18,halfTurn:36,
    channels:Object.freeze(["x","y","z","w","xy","yx","zw","wz"]),
    xPlane:"PRIMARY_XZ_CW",zPlane:"PRIMARY_XZ_CCW",
    yPlane:"ORTHOGONAL_YW_CCW",wPlane:"ORTHOGONAL_YW_CW",
    projectionOnly:true,canonicalMutationAuthority:false
  });
  const GEOMETRY_GAIN=Object.freeze({defaultValue:0.020,max:0.050,step:0.001});
  /* Light-emission gain remains independent of the geometry-normalization
     control, so a subtle physical silhouette does not erase the soft glow. */
  const HALO_EMISSION_GAIN=0.16;
  const BACK_LIGHT=Object.freeze({layerCells:5184,layers:2,alphaCap:0.045,
    bandCap:0.022,authority:"PRESENTATION_ONLY"});
  function lightAttenuation(rms,frequencyHz,normalizedDistance){
    const amp=Math.sqrt(clamp(finite(rms),0,1));
    const hz=1/(1+Math.max(0,finite(frequencyHz))/720);
    const d=Math.max(0,finite(normalizedDistance));
    return clamp(BACK_LIGHT.alphaCap*amp*hz/(1+10*d*d),0,BACK_LIGHT.alphaCap);
  }
  /* Two 5184 particle-address layers, NOT an elapsed tick delay. */
  function particleLayer5184(index,phase72){
    if(!Number.isInteger(index)||index<0||index>=10368)return null;
    const layer=index<5184?0:1,address=index%5184;
    const phase=2*Math.PI*(finite(phase72)+(layer?18:0))/72;
    const modulation=.55+.45*(.5+.5*Math.cos(2*Math.PI*address/5184+phase));
    return {layer,address,phase72:(finite(phase72)+(layer?18:0))%72,modulation};
  }
  /* 5184 anti-particle light-to-neuronal-like Brownian visual bridge.
     Probability is gated by PCM energy and pitch; four nearest neighbors
     on the 72x72 wrapped lattice correlate stochastic visual offsets.
     Signed x/y/z/w operator identities and native physics are untouched. */
  const BROWNIAN=Object.freeze({schema:"HHS_PASS220_BROWNIAN_5184_ANTIPARTICLE_V1",
    layerOffset:5184,cells:5184,tickDelay:5184,maxOffset:0.05,
    physicsAdmission:false,actualFlyConnectome:false});
  const brownianProbabilities=new Float32Array(5184);
  const brownianOffsets=new Float32Array(5184*3);
  const brownianCandidates=new Float32Array(5184*3);
  const brownianRingRms=new Float32Array(5184);
  const brownianRingPhase=new Uint8Array(5184);
  const brownianRingFlip=new Uint8Array(5184);
  let brownianAudioFrame=-1,brownianTick=0,brownianDelayedTick=-1;
  let brownianDelayedLight=0,brownianDelayedPhase=0,brownianDelayedFlip=0;
  function brownianUniform(addr,frame,phase,channel){
    let u=(Math.imul(addr+1,0x9e3779b1)^Math.imul(frame+1,0x85ebca6b)^
      Math.imul(phase+1,0xc2b2ae35)^Math.imul(channel+1,0x27d4eb2f))>>>0;
    u^=u>>>16;u=Math.imul(u,0x7feb352d);
    u^=u>>>15;u=Math.imul(u,0x846ca68b);u^=u>>>16;
    return (u>>>0)/4294967296;
  }
  function brownianProbabilityAt(index,rms,hz,phase,flip){
    if(!Number.isInteger(index)||index<0||index>=5184)return 0;
    const light=Math.sqrt(clamp(finite(rms),0,1))/
      (1+Math.max(0,finite(hz))/720);
    const layer=particleLayer5184(5184+index,phase);
    return clamp(light*layer.modulation*((flip&1)?.85:1)*.55,0,.55);
  }
  function resetBrownianVisual(){
    brownianProbabilities.fill(0);brownianOffsets.fill(0);
    brownianCandidates.fill(0);brownianAudioFrame=-1;
  }
  function advanceBrownianVisual(frame,rms,hz,phase,flip){
    if(!Number.isSafeInteger(frame)||frame<0)return false;
    if(frame===brownianAudioFrame)return false;
    if(frame<brownianAudioFrame)resetBrownianVisual();
    brownianAudioFrame=frame;
    const active=finite(rms)>=.002;
    const sector=((Math.trunc(finite(phase))%72)+72)%72;
    for(let k=0;k<5184;k++){
      const probability=active?brownianProbabilityAt(k,rms,hz,sector,flip):0;
      brownianProbabilities[k]=probability;
      for(let axis=0;axis<3;axis++){
        const accepted=brownianUniform(k,frame,sector,axis)<probability;
        brownianCandidates[k*3+axis]=accepted?
          (2*brownianUniform(k,frame,sector,axis+4)-1)*probability:0;
      }
    }
    /* No atom allocations or host RNG in the hot 5184-cell path. */
    for(let k=0;k<5184;k++){
      const row=(k/72)|0,col=k%72;
      const n0=row*72+(col+71)%72,n1=row*72+(col+1)%72;
      const n2=((row+71)%72)*72+col,n3=((row+1)%72)*72+col;
      for(let axis=0;axis<3;axis++){
        const j=k*3+axis;
        const neighbors=(brownianCandidates[n0*3+axis]+
          brownianCandidates[n1*3+axis]+brownianCandidates[n2*3+axis]+
          brownianCandidates[n3*3+axis])*.25;
        /* Alternating ordered xy:zw VISUAL channel (no commutation). */
        const sign=(axis===0&&(flip&1))?-1:1;
        const noise=sign*(.6*brownianCandidates[j]+.4*neighbors)*.05;
        brownianOffsets[j]=clamp((active?.86:.72)*brownianOffsets[j]+
          (active?.14:0)*noise,-BROWNIAN.maxOffset,BROWNIAN.maxOffset);
      }
    }
    return true;
  }
  /* EXACT simulation substeps, independent of RAF quartic render gate:
     tick n reads n-5184 before slot overwrite, then persists its own
     observation/ordered parity. No force admission or mutation occurs. */
  function observeBrownianSubstep(){
    const n=brownianTick++,slot=n%5184;
    if(n>=5184){
      brownianDelayedTick=n-5184;
      brownianDelayedLight=brownianRingRms[slot];
      brownianDelayedPhase=brownianRingPhase[slot];
      brownianDelayedFlip=brownianRingFlip[slot];
    }else brownianDelayedTick=-1;
    brownianRingRms[slot]=state.frameSignalReady?state.frameRmsR:0;
    brownianRingPhase[slot]=state.gyroPhase72%72;
    brownianRingFlip[slot]=n&1;
    return {tick:n,delayedTick:brownianDelayedTick,flip:n&1};
  }
  function projectBrownianAntiParticle(p,matrix){
    if(!state.frameSignalReady||!state.geometryEnabled)return false;
    const index=state.particleIndex.get(p);
    if(index===undefined||index<5184||index>=10368)return false;
    const slot=(index-5184)*3,e=matrix.elements;
    e[12]+=brownianOffsets[slot];
    e[13]+=brownianOffsets[slot+1];
    e[14]+=brownianOffsets[slot+2];
    return true;
  }
  function brownianOffsetAt(index){
    if(!Number.isInteger(index)||index<0||index>=5184)return null;
    return [brownianOffsets[index*3],brownianOffsets[index*3+1],
            brownianOffsets[index*3+2]];
  }
  function brownianProbabilitySlot(index){
    return Number.isInteger(index)&&index>=0&&index<5184?
      brownianProbabilities[index]:null;
  }
  const geometryScratch=new Float32Array(3);
  const HANN_735=new Float32Array(AUDIO_CLOCK.samplesPerFrame);
  for(let i=0;i<HANN_735.length;i++)
    HANN_735[i]=0.5-0.5*Math.cos(2*Math.PI*i/(HANN_735.length-1));
  const state={
    active:false, geometryEnabled:false, gain:GEOMETRY_GAIN.defaultValue,
    pair:PAIR, peaksL:new Float32Array(N), peaksR:new Float32Array(N),
    crossingEvents:[], sampleRate:0, buffer:null, context:null, source:null,
    processor:null, objectURL:null, audio:null, particleIndex:new WeakMap(), particles:null,
    waveCanvas:null,backLightCanvas:null,backLightTexture:null, started:false, lastFrame:-1, lastSample:[0,0], status:null,
    processorReady:null, renderedLightingFrames:0, skippedLightingFrames:0,
    outputClockSource:"inactive", lightingLatencyMs:0, lastClockStatusTime:-1,
    analyserL:null,analyserR:null,analyserDataL:new Float32Array(2048),
    analyserDataR:new Float32Array(2048),frameL:new Float32Array(735),
    frameR:new Float32Array(735),frameCrossings:[],frameRmsL:0,frameRmsR:0,
    framePeakL:0,framePeakR:0,frameSignalReady:false,lastSignalFrame:-1,
    harmonicPhase:[0,0],harmonicFrequencyHz:[0,0],harmonicMoment:[1,1],
    gyroTransport72:0,gyroPhase72:0,
    lastRisingSample:[NaN,NaN],
    particleFrame:-1,particleVisualFrames:0,liveFrameCount:0,
    renderSource:"none",decodedChannels:null
  };
  function clamp(x,a,b){return Math.min(b,Math.max(a,x));}
  function finite(x){return Number.isFinite(x)?x:0;}
  /* Display-only cellular envelope; canonical wall and particle state intact.
     0=displacement, 1=cellular boundary scale, 2=particle scale.
     The visual boundary radius always grows at least as fast as particle size. */
  function amplitudeGeometry(sample,rms,gain,out){
    const g=clamp(finite(gain),0,GEOMETRY_GAIN.max);
    const energy=clamp(Math.sqrt(Math.max(0,finite(rms)))*2.2,0,1);
    const transient=clamp(Math.abs(finite(sample))*2.5,0,1);
    out[0]=g*(energy*2.8+transient*3.2);
    out[1]=1+g*(energy*2.0+transient*2.4);
    out[2]=1+g*(energy*1.4+transient*1.8);
    return out;
  }
  /* When a busy frame or low pitch yields fewer than two reliable rises,
     recover a frequency from the strongest windowed PCM harmonic. The
     scan runs only on crossing-insufficient audio frames, not per particle.
     A silent/zero-energy window has no phase advancement. */
  function spectralFallbackHz(samples){
    let best=0,bestPower=0;
    for(let bin=1;bin<=96;bin++){
      const coeff=2*Math.cos(2*Math.PI*bin/samples.length);
      let a=0,b=0;
      for(let i=0;i<samples.length;i++){
        const next=finite(samples[i])*HANN_735[i]+coeff*a-b;
        b=a;a=next;
      }
      const power=Math.max(0,a*a+b*b-coeff*a*b);
      if(power>bestPower){bestPower=power;best=bin;}
    }
    return bestPower>0.01?best*AUDIO_CLOCK.canonicalRate/samples.length:0;
  }
  /* Per-bus PCM fundamental from interpolated rising zero-crossing periods;
     four ordered harmonic Goertzel powers weight the Q144 rotation rate.
     Neither display frequency nor color phase has VM81 authority. */
  function harmonicProfile(samples,firstSample,previousRising){
    const n=samples.length;
    let last=Number.isFinite(previousRising)?previousRising:NaN;
    let previous=n?finite(samples[0]):0,periods=0,total=0;
    for(let k=1;k<n;k++){
      const current=finite(samples[k]);
      if(previous<=0&&current>0){
        const delta=current-previous;
        const at=firstSample+k-1+(delta?clamp(-previous/delta,0,1):0);
        if(Number.isFinite(last)&&at>last&&
           at-last<AUDIO_CLOCK.canonicalRate/20){
          total+=at-last;periods++;
        }
        last=at;
      }
      previous=current;
    }
    const frequencyHz=periods?clamp(AUDIO_CLOCK.canonicalRate*periods/total,
      0,AUDIO_CLOCK.canonicalRate/2):spectralFallbackHz(samples);
    if(!Number.isFinite(frequencyHz)||frequencyHz<20)
      return {frequencyHz:0,harmonicMoment:1,lastRising:last};
    let sum=0,weighted=0;
    for(let harmonic=1;harmonic<=HARMONIC.partials;harmonic++){
      if(harmonic*frequencyHz>=AUDIO_CLOCK.canonicalRate/2)break;
      const coefficient=2*Math.cos(2*Math.PI*harmonic*frequencyHz/
        AUDIO_CLOCK.canonicalRate);
      let a=0,b=0;
      for(let k=0;k<n;k++){
        const window=n>1?0.5-0.5*Math.cos(2*Math.PI*k/(n-1)):1;
        const next=finite(samples[k])*window+coefficient*a-b;
        b=a;a=next;
      }
      const power=Math.max(0,a*a+b*b-coefficient*a*b);
      sum+=power;weighted+=harmonic*power;
    }
    return {frequencyHz,harmonicMoment:sum>1e-12?
      clamp(weighted/sum,1,HARMONIC.partials):1,lastRising:last};
  }
  /* Signed rotor coordinates always carry their typed, ordered identity.
     The product channels are +18 or -18 directed images, never a
     host-language commutative rewrite of xy/yx or zw/wz. */
  function gyroscopicPhaseGear72(phase){
    const step=((Math.trunc(finite(phase))%72)+72)%72;
    const x=step,z=(72-step)%72;
    const y=(18-step+72)%72,w=(18+step)%72;
    return {
      phase72:step, x,y,z,w,
      xy:(x+18)%72,yx:(y-18+72)%72,
      zw:(z-18+72)%72,wz:(w+18)%72
    };
  }
  /* Frequency-harmonic transport through one u72 carrier.
     Only exact PCM output-clock frame advancement invokes this stage.
     Two stereo harmonic rates contribute reciprocally to one rotor. */
  function transportGyroscopicPhase72(current,leftHz,leftMoment,rightHz,rightMoment,elapsedFrames=1){
    const l=harmonicStep(leftHz,leftMoment);
    const r=harmonicStep(rightHz,rightMoment);
    const active=(l>0?1:0)+(r>0?1:0);
    if(!active)return ((finite(current)%72)+72)%72;
    const frames=Number.isSafeInteger(elapsedFrames)&&elapsedFrames>0?elapsedFrames:1;
    return (((finite(current)+frames*(l+r)/(active*HARMONIC.stepsPerFrame))%72)+72)%72;
  }
  /* Reciprocal vertical-raster lanes from one ordered gyroscope state.
     The inverse-address folding below belongs ONLY to the color projection.
     It never asserts equality of native x/z, xy/zw, y/w, or yx/wz tensors. */
  function verticalReciprocalGradientPair(phase,leftSample,rightSample,leftRms,rightRms,leftHz=432,rightHz=432){
    const g=gyroscopicPhaseGear72(phase);
    const sharedSample=(finite(leftSample)+finite(rightSample))/2;
    const sharedRms=(Math.max(0,finite(leftRms))+Math.max(0,finite(rightRms)))/2;
    const leftAddress=[g.x,g.xy,g.y,g.yx];
    const rightMirrored=[(-g.z+72)%72,(-g.zw+72)%72,
                         (36-g.w+72)%72,(36-g.wz+72)%72];
    /* All four mirror addresses equal the left projection addresses.
       The right Q144 lane is +72 in the full-color circle. */
    const leftHues=leftAddress.map(k=>q144Index(2*k,sharedSample,sharedRms,0,0));
    const rightHues=rightMirrored.map(k=>q144Index(2*k,sharedSample,sharedRms,0,1));
    const alphaL=lightAttenuation(leftRms,leftHz,0);
    const alphaR=lightAttenuation(rightRms,rightHz,0);
    return {phase72:g.phase72,rotors:g,leftHues,rightHues,alphaL,alphaR,
      oppositeHuePairs:leftHues.every((q,i)=>((q+72)%144)===rightHues[i]),
      quarterTurn:GYRO_SHADER.quarterTurn};
  }
  /* Two true orthogonal gradient axes, not top-to-bottom columns.
     The first axis is theta and the other theta+pi/2, so their dot product
     vanishes for every continuous presentation phase. Color addresses remain
     discrete u72 sectors; the *render angle* uses fractional phase for smooth
     motion between audio-frame ticks. The viewport is fully covered by both
     crossed linear fields, with no circular/radial halo. */
  function gyroscopicGradientAxes72(phase,width,height){
    const p=((finite(phase)%72)+72)%72;
    const angle=2*Math.PI*p/72;
    const c=Math.cos(angle),s=Math.sin(angle);
    const span=Math.hypot(width,height)*1.05;
    const cx=width/2,cy=height/2,half=span/2;
    const left=[cx-half*c,cy-half*s,cx+half*c,cy+half*s];
    const right=[cx+half*s,cy-half*c,cx-half*s,cy+half*c];
    return {phase72:p,left,right,dot:c*(-s)+s*c};
  }
  /* Four-tick interlace: derive presentation state from the PCM frame,
     never from rAF or a new canonical VM81 clock. Geometry and light are
     render-only; source particle positions and receipts are not touched. */
  const INTERLACE=Object.freeze({
    schema:"HHS_PASS220_FOUR_PHASE_LIQUID_LIGHT_V1",
    period:4,quarterTurn72:18,projectionOnly:true,
    canonicalMutationAuthority:false
  });
  function fourPhasePresentationPacket(frame){
    if(!Number.isSafeInteger(frame)||frame<0)return null;
    const phase=frame%INTERLACE.period;
    const inverted=(phase&1)===1;
    return Object.freeze({
      frame,phase,rotationPhase72:phase*INTERLACE.quarterTurn72,
      rotationQuarterTurns:phase,
      colorPolarity:inverted?-1:1,
      topology:inverted?"convex":"concave",
      depthSign:inverted?1:-1,
      horizontalInversion:phase===1||phase===3,
      verticalInversion:phase===2||phase===3,
      backlightReveal:inverted?0.6:1,
      source:"PCM_44100_FRAME_735",
      projectionOnly:true
    });
  }
  function paintGyroscopicVerticalPair(ctx,width,height,leftSample,rightSample,
                                        leftRms,rightRms,phase,leftHz=432,rightHz=432){
    const pair=verticalReciprocalGradientPair(
      phase,leftSample,rightSample,leftRms,rightRms,leftHz,rightHz);
    if(pair.alphaL<0.004 && pair.alphaR<0.004)return pair;
    const packet=fourPhasePresentationPacket(state.lastFrame);
    const axes=gyroscopicGradientAxes72(
      phase+(packet?packet.rotationPhase72:0),width,height);
    ctx.globalCompositeOperation="lighter";
    for(let bus=0;bus<2;bus++){
      const axis=bus?axes.right:axes.left;
      const shader=ctx.createLinearGradient(axis[0],axis[1],axis[2],axis[3]);
      const hues=bus?pair.rightHues:pair.leftHues;
      const strength=(bus?pair.alphaR:pair.alphaL)*
        (packet?packet.backlightReveal:1);
      const shift=packet&&packet.colorPolarity<0?72:0;
      shader.addColorStop(0,q144Css((hues[0]+shift)%144,0));
      for(let k=0;k<4;k++){
        const d=Math.abs((k+1)/5-.5);
        const curvature=packet&&packet.depthSign>0?
          (0.35+2.6*d):(1/(1+10*d*d));
        shader.addColorStop((k+1)/5,
          q144Css((hues[k]+shift)%144,clamp(strength*curvature,0,BACK_LIGHT.alphaCap)));
      }
      shader.addColorStop(1,q144Css((hues[3]+shift)%144,0));
      ctx.fillStyle=shader;
      ctx.fillRect(0,0,width,height);
    }
    ctx.globalCompositeOperation="source-over";
    return pair;
  }
  /* Broad lights and 72 sample-phase flashes rotate with the exact same
     two gyroscopic normals as the global reciprocal color gradients.
     A local quad bounds overdraw; there is no radial/donut overlay. */
  function paintGyroscopicLightBand(ctx,width,height,phase,bus,
                                    normalizedOffset,halfWidth,hue,opacity){
    const axes=gyroscopicGradientAxes72(phase,width,height);
    const axis=bus?axes.right:axes.left;
    const dx=axis[2]-axis[0],dy=axis[3]-axis[1];
    const length=Math.hypot(dx,dy)||1,nx=dx/length,ny=dy/length;
    const tx=-ny,ty=nx,diagonal=Math.hypot(width,height);
    const centerDist=finite(normalizedOffset)*diagonal;
    const cx=width/2+nx*centerDist,cy=height/2+ny*centerDist;
    const radius=Math.max(1,finite(halfWidth));
    ctx.beginPath();
    ctx.moveTo(cx-tx*diagonal-nx*radius,cy-ty*diagonal-ny*radius);
    ctx.lineTo(cx+tx*diagonal-nx*radius,cy+ty*diagonal-ny*radius);
    ctx.lineTo(cx+tx*diagonal+nx*radius,cy+ty*diagonal+ny*radius);
    ctx.lineTo(cx-tx*diagonal+nx*radius,cy-ty*diagonal+ny*radius);
    ctx.closePath();
    const gradient=ctx.createLinearGradient(
      cx-nx*radius,cy-ny*radius,cx+nx*radius,cy+ny*radius);
    gradient.addColorStop(0,q144Css(hue,0));
    const falloff=1/(1+8*Math.pow(finite(normalizedOffset),2));
    gradient.addColorStop(.5,q144Css(hue,
      clamp(finite(opacity)*falloff,0,BACK_LIGHT.bandCap)));
    gradient.addColorStop(1,q144Css(hue,0));
    ctx.fillStyle=gradient;
    ctx.fill();
    return {normal:[nx,ny],center:[cx,cy]};
  }
  function harmonicStep(frequencyHz,harmonicMoment){
    if(!Number.isFinite(frequencyHz)||frequencyHz<=0)return 0;
    return clamp(frequencyHz/HARMONIC.referenceHz*HARMONIC.stepsPerFrame*
      (1+0.35*(clamp(finite(harmonicMoment),1,4)-1)),0,72);
  }
  /* Scan every decoded PCM sample, conserving signed extrema within each
     full-track geometry bin; no downsampling precedes this pass. */
  function peakEnvelope(samples,bins){
    const peaks=new Float32Array(bins);
    if(!samples || !samples.length)return peaks;
    for(let i=0;i<samples.length;i++){
      const k=Math.min(bins-1,Math.floor(i*bins/samples.length));
      const value=finite(samples[i]);
      if(Math.abs(value)>Math.abs(peaks[k]))peaks[k]=value;
    }
    return peaks;
  }
  /* Sample-precise crossing, including fractional sub-sample interpolation.
     The preceding sample is inherited across audio-render blocks. */
  function crossingsFromBlock(left,right,firstFrame,sampleRate,prior){
    const out=[],n=left?left.length:0;
    const channels=[left,right||left];
    for(let bus=0;bus<2;bus++){
      const data=channels[bus];if(!data)continue;
      let prev=finite(prior[bus]);
      for(let i=0;i<n;i++){
        const curr=finite(data[i]);
        if(prev!==0 && ((prev<0 && curr>=0)||(prev>0 && curr<=0))){
          const denom=curr-prev;
          const frac=denom ? clamp(-prev/denom,0,1) : 0;
          out.push([bus,(firstFrame+i-1+frac)/sampleRate,
                    Math.min(1,Math.abs(denom)),curr>=prev?1:-1]);
        }
        prev=curr;
      }
      prior[bus]=prev;
    }
    return out;
  }
  /* An audio sample index is the authoritative presentation clock.
     No rAF timestamp determines phase, and no host pixel frame may mint
     native VM81/Hash72 state. At a 48 kHz hardware rate, the same 60 Hz
     boundary occurs every 800 device samples instead of 735 canonical ones. */
  function canonicalSampleIndex(nativeSample, nativeRate){
    const rate=Number(nativeRate);
    if(!Number.isFinite(nativeSample)||!Number.isFinite(rate)||rate<=0)
      return 0;
    return Math.max(0,Math.floor(nativeSample*AUDIO_CLOCK.canonicalRate/rate+1e-9));
  }
  function frameForSample(nativeSample,nativeRate){
    return Math.floor(canonicalSampleIndex(nativeSample,nativeRate) /
                      AUDIO_CLOCK.samplesPerFrame);
  }
  function sampleForFrame(frame){return frame*AUDIO_CLOCK.samplesPerFrame;}
  function outputClockFrame(context,player,perfNowMs){
    if(!player || player.paused || player.ended)return null;
    let seconds=0,source="media-playhead";
    if(context && context.state==="running"){
      const stamp=(typeof context.getOutputTimestamp==="function") ?
        context.getOutputTimestamp():null;
      if(stamp && Number.isFinite(stamp.contextTime) &&
         Number.isFinite(stamp.performanceTime) && stamp.performanceTime>0 &&
         Number.isFinite(perfNowMs)){
        /* Timestamp anchors audio-output sample time to monotonic UI time.
           Do not additionally subtract outputLatency in this branch. */
        seconds=stamp.contextTime+
          Math.max(0,(perfNowMs-stamp.performanceTime)/1000);
        seconds=Math.min(seconds,context.currentTime);
        source="output-timestamp";
      }else{
        /* Approximation only when the output timestamp API is unavailable. */
        const latency=Number.isFinite(context.outputLatency)?context.outputLatency:
          (Number.isFinite(context.baseLatency)?context.baseLatency:0);
        seconds=Math.max(0,context.currentTime-latency);
        source="context-latency-estimate";
      }
    }else if(Number.isFinite(player.currentTime)){
      seconds=player.currentTime;
    }
    const nativeRate=(context&&Number.isFinite(context.sampleRate)) ?
      context.sampleRate:AUDIO_CLOCK.canonicalRate;
    const nativeSample=Math.max(0,Math.floor(seconds*nativeRate+1e-9));
    const sample=canonicalSampleIndex(nativeSample,nativeRate);
    const frame=Math.floor(sample/AUDIO_CLOCK.samplesPerFrame);
    return {frame,sample,seconds,source,nativeRate,frameStart:sampleForFrame(frame)};
  }
  function crossingFrame(eventSeconds){
    return Math.floor(Math.max(0,eventSeconds)*AUDIO_CLOCK.visualHz+1e-9);
  }
  function crossingLightingCells(events,frame){
    const cells=[new Float32Array(AUDIO_CLOCK.phaseBins),
                 new Float32Array(AUDIO_CLOCK.phaseBins)];
    if(!Number.isFinite(frame)||frame<0)return cells;
    for(const e of events){
      if(!Array.isArray(e)||e.length<4||e[0]!==0&&e[0]!==1)continue;
      const eventFrame=crossingFrame(e[1]);
      const age=frame-eventFrame;
      if(age<0||age>=AUDIO_CLOCK.fadeFrames)continue;
      const strength=clamp(finite(e[2])*16,0,1)*
                     (1-age/AUDIO_CLOCK.fadeFrames);
      const sample=Math.max(0,Math.floor(e[1]*AUDIO_CLOCK.canonicalRate+1e-9));
      const phase=sample % AUDIO_CLOCK.phaseBins;
      cells[e[0]][phase]=Math.min(1,cells[e[0]][phase]+strength*0.22);
    }
    return cells;
  }
  function resetLightingClock(){
    state.lastFrame=-1;
    state.lastClockStatusTime=-1;
    state.lastSignalFrame=-1;
    state.particleFrame=-1;
    state.frameSignalReady=false;
    resetBrownianVisual();
    if(state.backLightCanvas){
      const back=state.backLightCanvas.getContext("2d");
      if(back){
        back.setTransform(1,0,0,1,0,0);
        back.fillStyle="#000000";
        back.fillRect(0,0,state.backLightCanvas.width,state.backLightCanvas.height);
        if(state.backLightTexture)state.backLightTexture.needsUpdate=true;
      }
    }
    state.frameCrossings=[];
    state.crossingEvents.length=0;
    state.lastSample=[0,0];
    state.harmonicPhase=[0,0];
    state.gyroTransport72=0;state.gyroPhase72=0;
    state.harmonicFrequencyHz=[0,0];
    state.harmonicMoment=[1,1];
    state.lastRisingSample=[NaN,NaN];
    if(state.processor && state.processor.port &&
       typeof state.processor.port.postMessage==="function")
      state.processor.port.postMessage({type:"reset"});
  }
  function advanceLightingGate(frame){
    if(!Number.isSafeInteger(frame)||frame<0)return false;
    if(frame===state.lastFrame)return false;
    if(frame<state.lastFrame)resetLightingClock();
    if(state.lastFrame>=0 && frame>state.lastFrame+1)
      state.skippedLightingFrames+=frame-state.lastFrame-1;
    state.lastFrame=frame;
    state.renderedLightingFrames++;
    return true;
  }
  /* Browser adapter: decoded track provides sample-aligned media windows;
     the stereo AnalyserNode provides live PCM if full-file decoding fails.
     Both are read-only visualization ingress, never simulation authority. */
  function attachLiveStereo(context,source){
    if(typeof context.createChannelSplitter!=="function" ||
       typeof context.createAnalyser!=="function")return false;
    try{
      const splitter=context.createChannelSplitter(2);
      const L=context.createAnalyser(),R=context.createAnalyser();
      L.fftSize=2048; R.fftSize=2048;
      L.smoothingTimeConstant=0;R.smoothingTimeConstant=0;
      source.connect(splitter);
      splitter.connect(L,0);
      splitter.connect(R,1);
      /* Keep a pulled, zero-volume analysis branch without sending a
         second audible copy to the speakers on browser audio graphs. */
      const silent=context.createGain();
      silent.gain.value=0;
      L.connect(silent);R.connect(silent);
      silent.connect(context.destination);
      state.analyserL=L;state.analyserR=R;
      return true;
    }catch(error){
      report("Stereo live PCM analyzer unavailable: "+error.message);
      return false;
    }
  }
  function decodedWindow(player){
    if(!state.buffer || !state.decodedChannels || !player ||
       !Number.isFinite(player.currentTime))return false;
    const decoded=state.buffer,ch=state.decodedChannels;
    const rate=decoded.sampleRate;
    if(!rate || !ch[0] || !ch[0].length)return false;
    const duration=ch[0].length/rate;
    const mediaTime=Math.max(0,Math.min(duration,player.currentTime));
    const first=Math.floor(Math.floor(mediaTime*AUDIO_CLOCK.visualHz)*
                           rate/AUDIO_CLOCK.visualHz);
    const step=rate/AUDIO_CLOCK.canonicalRate;
    for(let i=0;i<AUDIO_CLOCK.samplesPerFrame;i++){
      const idx=Math.min(ch[0].length-1,first+Math.floor(i*step));
      state.frameL[i]=finite(ch[0][idx]);
      state.frameR[i]=finite(ch[1][Math.min(ch[1].length-1,idx)]);
    }
    state.renderSource="decoded";
    return true;
  }
  function liveWindow(){
    const L=state.analyserL,R=state.analyserR;
    if(!L || typeof L.getFloatTimeDomainData!=="function")return false;
    L.getFloatTimeDomainData(state.analyserDataL);
    if(R && typeof R.getFloatTimeDomainData==="function")
      R.getFloatTimeDomainData(state.analyserDataR);
    else state.analyserDataR.set(state.analyserDataL);
    const deviceRate=(state.context&&Number.isFinite(state.context.sampleRate))
      ?state.context.sampleRate:AUDIO_CLOCK.canonicalRate;
    const count=Math.ceil(AUDIO_CLOCK.samplesPerFrame*deviceRate/
                          AUDIO_CLOCK.canonicalRate);
    const offset=Math.max(0,state.analyserDataL.length-count);
    for(let i=0;i<AUDIO_CLOCK.samplesPerFrame;i++){
      const k=Math.min(state.analyserDataL.length-1,
        offset+Math.floor(i*deviceRate/AUDIO_CLOCK.canonicalRate));
      state.frameL[i]=finite(state.analyserDataL[k]);
      state.frameR[i]=finite(state.analyserDataR[k]);
    }
    state.renderSource="live-analyser";
    state.liveFrameCount++;
    return true;
  }
  function frameSampleMetrics(left,right){
    let sumL=0,sumR=0,peakL=0,peakR=0;
    for(let i=0;i<AUDIO_CLOCK.samplesPerFrame;i++){
      const l=finite(left[i]),r=finite(right[i]);
      sumL+=l*l;sumR+=r*r;
      peakL=Math.max(peakL,Math.abs(l));peakR=Math.max(peakR,Math.abs(r));
    }
    return {
      rmsL:Math.sqrt(sumL/AUDIO_CLOCK.samplesPerFrame),
      rmsR:Math.sqrt(sumR/AUDIO_CLOCK.samplesPerFrame),
      peakL,peakR
    };
  }
  function frameCrossingEvents(left,right,frame){
    const out=[],base=sampleForFrame(frame),rate=AUDIO_CLOCK.canonicalRate;
    for(let bus=0;bus<2;bus++){
      const pcm=bus===0?left:right;
      let previous=finite(pcm[0]);
      for(let i=1;i<AUDIO_CLOCK.samplesPerFrame;i++){
        const current=finite(pcm[i]);
        if(previous!==0 &&
           ((previous<0 && current>=0)||(previous>0 && current<=0))){
          const delta=current-previous;
          const frac=delta?clamp(-previous/delta,0,1):0;
          out.push([bus,(base+i-1+frac)/rate,
                  Math.min(1,Math.abs(delta)),current>=previous?1:-1]);
        }
        previous=current;
      }
    }
    return out;
  }
  function prepareVisualFrame(clock){
    if(!clock || !state.audio || state.audio.paused || state.audio.ended)
      return false;
    if(clock.frame===state.lastSignalFrame)return state.frameSignalReady;
    if(clock.frame<state.lastSignalFrame)resetLightingClock();
    const priorFrame=state.lastSignalFrame;
    const elapsedFrames=priorFrame<0?1:clock.frame-priorFrame;
    /* Prefer sample-aligned decoded PCM; use live stereo when a long
       file has not decoded or its format is unsupported by decodeAudioData.
       Analyser nodes can return silence on some platforms even while the
       native player remains audible, so do not hide decoded data behind them. */
    state.frameSignalReady=decodedWindow(state.audio) ||
      liveWindow();
    state.lastSignalFrame=clock.frame;
    if(!state.frameSignalReady)return false;
    const m=frameSampleMetrics(state.frameL,state.frameR);
    state.frameRmsL=m.rmsL;state.frameRmsR=m.rmsR;
    state.framePeakL=m.peakL;state.framePeakR=m.peakR;
    state.frameCrossings=frameCrossingEvents(state.frameL,state.frameR,clock.frame);
    for(let bus=0;bus<2;bus++){
      const rms=bus?m.rmsR:m.rmsL;
      if(rms<0.002){
        state.harmonicFrequencyHz[bus]=0;
        state.harmonicMoment[bus]=1;
        state.lastRisingSample[bus]=NaN;
        continue; /* Quiet signals never rotate the color wheel. */
      }
      const profile=harmonicProfile(bus?state.frameR:state.frameL,
        sampleForFrame(clock.frame),
        elapsedFrames===1?state.lastRisingSample[bus]:NaN);
      state.lastRisingSample[bus]=profile.lastRising;
      state.harmonicFrequencyHz[bus]=profile.frequencyHz;
      state.harmonicMoment[bus]=profile.harmonicMoment;
      state.harmonicPhase[bus]=(state.harmonicPhase[bus]+
        elapsedFrames*harmonicStep(profile.frequencyHz,profile.harmonicMoment))%144;
    }
    state.gyroTransport72=transportGyroscopicPhase72(
      state.gyroTransport72,
      state.harmonicFrequencyHz[0],state.harmonicMoment[0],
      state.harmonicFrequencyHz[1],state.harmonicMoment[1],elapsedFrames);
    state.gyroPhase72=Math.floor(state.gyroTransport72);
    advanceBrownianVisual(clock.frame,state.frameRmsR,
      state.harmonicFrequencyHz[1],state.gyroPhase72,brownianTick&1);
    state.active=true;state.geometryEnabled=true;
    return true;
  }
  function currentAudioClock(){
    return outputClockFrame(state.context,state.audio,
      window.performance && typeof window.performance.now==="function" ?
      window.performance.now():NaN);
  }
  function needsProjectionFrame(){
    const clock=currentAudioClock();
    if(!prepareVisualFrame(clock))return false;
    if(clock.frame===state.particleFrame)return false;
    state.particleFrame=clock.frame;
    state.particleVisualFrames++;
    return true;
  }
  /* Never touch logical particle data. Only edit an InstancedMesh projection
     matrix and a scratch Color used with setColorAt. */
  /* PCM-derived peak opacity on each particle, no per-carrier allocations. */
  function projectParticleGlow(p){
    if(!state.geometryEnabled||!state.frameSignalReady)return 0;
    const i=state.particleIndex.get(p);
    if(i===undefined)return 0;
    const bus=i<AUDIO_CLOCK.laneCells?0:1;
    const k=i%AUDIO_CLOCK.laneCells;
    const sample=bus?state.frameR[k%AUDIO_CLOCK.samplesPerFrame]:
                     state.frameL[k%AUDIO_CLOCK.samplesPerFrame];
    const rms=bus?state.frameRmsR:state.frameRmsL;
    const layer=particleLayer5184(i,state.gyroTransport72);
    const frequency=Math.max(0,state.harmonicFrequencyHz[bus]);
    return clamp(HALO_EMISSION_GAIN*layer.modulation*
      (.48*Math.sqrt(Math.max(0,rms))+.42*Math.abs(sample))/
      (1+frequency/720),0,.12);
  }
  /* CPU reference for the instanced fragment smoothstep^2 falloff.
     Zero is particle center; radius one or greater is transparent. */
  function particleHaloOpacity(normalizedRadius,peakAlpha){
    const r=clamp(finite(normalizedRadius),0,1);
    const smooth=r*r*(3-2*r);
    return (1-smooth)*(1-smooth)*clamp(finite(peakAlpha),0,1);
  }
  /* Read-only physical projection. Validated inherited particle metadata only.
     Charge and mass are independent values; neither is inferred from index,
     scale, phase, or the nine display bins. Kinetic energy is dimensionless
     here ONLY if the source explicitly supplies a normalized value. */
  function particlePhysicalProjection(p){
    if(!p||!state.particleIndex.has(p))return null;
    const index=state.particleIndex.get(p);
    const data=p.userData||{};
    const physical=data.hhsPhysicalState||data.physicalState||null;
    const valid=physical&&typeof physical==="object";
    const number=(key)=>valid&&Number.isFinite(physical[key])?
      physical[key]:null;
    const charge=number("charge");
    const mass=number("mass");
    const energy=number("normalizedKineticEnergy");
    const position=p.position&&
      Number.isFinite(p.position.x)&&Number.isFinite(p.position.y)&&
      Number.isFinite(p.position.z)?
      Object.freeze([p.position.x,p.position.y,p.position.z]):null;
    return Object.freeze({
      index, reciprocalIndex:(index+5184)%10368,
      constraintAddress:Math.floor((index%5184)/648),
      fractalAddress:Math.floor(((index%5184)%648)/72),
      phaseAddress:(index%5184)%72,
      charge, mass, kineticEnergy:energy===null?null:Math.max(0,energy),
      position, hasMeasuredCharge:charge!==null,
      hasMeasuredMass:mass!==null, hasParticlePosition:position!==null,
      chargeFromAddress:false, physicsMutation:false,
      source:valid?"inherited-particle-metadata":"unavailable"
    });
  }
  /* One inherited population; eight constraint lanes, nine scale/ionic
     addresses, 72 phase positions and two reciprocal orientations.
     Offsets remain zero until supplied through a future parameter contract. */
  function coupledParticleFrame(index,frame=state.lastFrame){
    if(!Number.isInteger(index)||index<0||index>=10368)return null;
    const particle=state.particles&&state.particles[index];
    const physical=particle?particlePhysicalProjection(particle):null;
    const side=Math.floor(index/5184),local=index%5184;
    const group=Math.floor(local/72);
    const constraint=Math.floor(group/9),scale=group%9;
    const phase=local%72;
    const quarter=Number.isSafeInteger(frame)&&frame>=0?frame%4:0;
    return Object.freeze({
      index,side,reciprocalIndex:(1-side)*5184+local,
      constraint,fractalScale:scale,ionicLayer:scale-4,
      hnanCenter:scale===4,spinor:side===0?"xyzw":"yxwz",
      phase72:(phase+18*quarter)%72,quarter,
      position:physical?physical.position:null,
      charge:physical?physical.charge:null,
      mass:physical?physical.mass:null,
      normalizedKineticEnergy:physical?physical.kineticEnergy:null,
      source:physical?physical.source:"unavailable",
      projectionOnly:true,physicsMutation:false
    });
  }
  function projectColor(p,color){
    const base=p.material.color;
    if(!state.frameSignalReady || !state.geometryEnabled){
      color.setRGB(base.r,base.g,base.b);
      return color;
    }
    const idx=state.particleIndex.get(p);
    if(idx===undefined)return color;
    const bus=idx<AUDIO_CLOCK.laneCells?0:1;
    const local=idx%AUDIO_CLOCK.laneCells;
    const sample=bus?state.frameR[local%AUDIO_CLOCK.samplesPerFrame]:
                     state.frameL[local%AUDIO_CLOCK.samplesPerFrame];
    const rms=bus?state.frameRmsR:state.frameRmsL;
    const phase=(p.userData&&Number.isInteger(p.userData.q144))?
      p.userData.q144:(idx%144);
    /* Match the exact global u72 orientation for every halo/core color.
       Typed per-particle Q144 offset and right-bus +72 remain distinct. */
    const q=q144Index(2*state.gyroPhase72+phase,sample,rms,0,bus);
    const c=q*3;
    // Physical state can modify the presentation only when supplied by the
    // inherited particle simulation. Never synthesize charge from scale/index.
    const physical=particlePhysicalProjection(p);
    const physicalFactor=physical&&physical.kineticEnergy!==null?
      1/(1+physical.kineticEnergy):1;
    const brightness=clamp((0.12+Math.sqrt(rms)*1.15+
      Math.abs(sample)*0.65)*physicalFactor,0.12,1);
    color.setRGB(Q144_RGB[c]*brightness,
                 Q144_RGB[c+1]*brightness,
                 Q144_RGB[c+2]*brightness);
    return color;
  }
  function report(message){
    if(state.status)state.status.textContent=message;
  }
  function bindParticles(particles){
    if(!particles)return;
    state.particleIndex=new WeakMap();
    state.particles=particles;
    for(let i=0;i<particles.length;i++)state.particleIndex.set(particles[i],i);
  }
  /* Graphics-only matrix offset. The logical Mesh position remains untouched,
     so manifold hashes, physics, and deterministic receipts are unchanged. */
  function projectMatrix(p, matrix){
    if(!state.geometryEnabled || !state.frameSignalReady)return;
    const i=state.particleIndex.get(p);
    if(i===undefined)return;
    const bus=i<AUDIO_CLOCK.laneCells?0:1;
    const local=i%AUDIO_CLOCK.laneCells;
    const sample=bus?state.frameR[local%AUDIO_CLOCK.samplesPerFrame]:
                     state.frameL[local%AUDIO_CLOCK.samplesPerFrame];
    const rms=bus?state.frameRmsR:state.frameRmsL;
    amplitudeGeometry(sample,rms,state.gain,geometryScratch);
    const strength=geometryScratch[0];
    const cellularBoundaryScale=geometryScratch[1];
    const particleSize=geometryScratch[2];
    const e=matrix.elements;
    const x=e[12],y=e[13],z=e[14];
    const radius=Math.hypot(x,y,z)||1;
    const orientation=bus? -1:1;
    /* Expanding visible cellular boundary and particle, projection ONLY. */
    e[12]=x*cellularBoundaryScale+
          strength*(x/radius*.7+sample*orientation*1.5);
    e[13]=y*cellularBoundaryScale+
          strength*(y/radius*.7+sample*.9);
    e[14]=z*cellularBoundaryScale+
          strength*(z/radius*.5+sample*orientation*.65);
    e[0]*=particleSize;e[5]*=particleSize;e[10]*=particleSize;
  }
  function enqueue(events){
    const now=state.context?state.context.currentTime:0;
    for(const ev of events){
      if(!Array.isArray(ev)||ev.length<4)continue;
      if(ev[1]<now-0.8||ev[1]>now+0.1)continue;
      state.crossingEvents.push(ev);
    }
    if(state.crossingEvents.length>4096)
      state.crossingEvents.splice(0,state.crossingEvents.length-4096);
  }
  function installFallback(context,source){
    /* 256 hardware samples < 735 canonical samples/frame. Callback jitter
       remains browser-dependent, and only AudioWorklet is low-latency. */
    const processor=context.createScriptProcessor(256,2,2);
    processor.onaudioprocess=function(ev){
      const input=ev.inputBuffer,output=ev.outputBuffer;
      const left=input.getChannelData(0);
      const right=input.numberOfChannels>1?input.getChannelData(1):left;
      for(let c=0;c<output.numberOfChannels;c++)
        output.getChannelData(c).set(c===0?left:right);
      enqueue(crossingsFromBlock(left,right,
        ev.playbackTime*context.sampleRate,context.sampleRate,state.lastSample));
    };
    /* The audio source ALREADY connects directly to speakers. Observation
       remains a zero-gain side branch, so analyzer failure cannot mute music. */
    const silence=context.createGain();
    silence.gain.value=0;
    source.connect(processor);processor.connect(silence);
    silence.connect(context.destination);
    return processor;
  }
  const WORKLET=("class HHSStereoCrossingWorklet extends AudioWorkletProcessor {\n"+
    "constructor(){super();this.prev=[0,0];this.pending=[];this.blocks=0;\n"+
    "this.port.onmessage=e=>{if(e.data&&e.data.type==='reset'){\n"+
    "this.prev=[0,0];this.pending=[];this.blocks=0;}};}\n"+
    "process(inputs,outputs){const input=inputs[0]||[],output=outputs[0]||[];\n"+
    "const L=input[0],R=input[1]||L;if(!L)return true;\n"+
    "for(let c=0;c<output.length;c++)output[c].set(input[c]||L);\n"+
    "for(let bus=0;bus<2;bus++){const data=bus===0?L:R;let prev=this.prev[bus];\n"+
    "for(let i=0;i<data.length;i++){const cur=data[i];\n"+
    "if(prev!==0&&((prev<0&&cur>=0)||(prev>0&&cur<=0))){\n"+
    "const delta=cur-prev,frac=delta?-prev/delta:0;\n"+
    "this.pending.push([bus,(currentFrame+i-1+Math.max(0,Math.min(1,frac)))/sampleRate,\n"+
    "Math.min(1,Math.abs(delta)),cur>=prev?1:-1]);}prev=cur;}\n"+
    "this.prev[bus]=prev;}\n"+
    "if(++this.blocks%2===0){if(this.pending.length)\n"+
    "this.port.postMessage({crossings:this.pending});this.pending=[];}\n"+
    "return true;}}\n"+
    "registerProcessor('hhs-stereo-crossings',HHSStereoCrossingWorklet);\n");
  async function installProcessor(context,source){
    if(context.audioWorklet && typeof AudioWorkletNode!=="undefined"){
      const url=URL.createObjectURL(new Blob([WORKLET],{type:"application/javascript"}));
      try{
        await context.audioWorklet.addModule(url);
        const node=new AudioWorkletNode(context,"hhs-stereo-crossings",{
          numberOfInputs:1,numberOfOutputs:1,outputChannelCount:[2]
        });
        node.port.onmessage=e=>{if(e.data && e.data.crossings)enqueue(e.data.crossings);};
        const silence=context.createGain();
        silence.gain.value=0;
        source.connect(node);node.connect(silence);
        silence.connect(context.destination);
        node.onprocessorerror=()=>report("Music continues; the PCM light analyzer stopped.");
        return node;
      }catch(err){
        report("AudioWorklet unavailable; PCM fallback active ("+err.message+").");
      }finally{URL.revokeObjectURL(url);}
    }
    return installFallback(context,source);
  }
  /* User gesture initialization. NEVER await a worklet or a decode before play.
     MediaElementAudioSource captures native output, so connect the dry bus to
     context.destination immediately, before starting optional PCM analysis. */
  function ensureAudio(){
    if(state.context)return state.context;
    const AudioCtor=window.AudioContext||window.webkitAudioContext;
    if(!AudioCtor){
      report("Native audio playback available; Web Audio visualization unsupported.");
      return null;
    }
    let ctx=null;
    try{
      ctx=new AudioCtor();
      const source=ctx.createMediaElementSource(state.audio);
      source.connect(ctx.destination); // SPEAKER PATH: synchronous, guaranteed first
      state.context=ctx;
      state.source=source;
      state.sampleRate=ctx.sampleRate;
      attachLiveStereo(ctx,source);
      state.processorReady=installProcessor(ctx,source).then(processor=>{
        state.processor=processor;
      }).catch(err=>{
        /* The independent dry path stays live even if analysis fails. */
        report("Music continues; audio lighting unavailable: "+err.message);
      });
      return ctx;
    }catch(err){
      if(ctx && typeof ctx.close==="function")
        Promise.resolve(ctx.close()).catch(()=>{});
      report("Native playback mode: "+err.message);
      return null;
    }
  }
  function resumeAudio(){
    const ctx=ensureAudio();
    if(ctx && ctx.state!=="running"){
      const pending=ctx.resume();
      if(pending && typeof pending.catch==="function")
        pending.catch(err=>report("Tap Play to unlock audio: "+err.message));
    }
    return ctx;
  }
  async function decodeFile(bytes){
    /* Offline decoding must not capture or suspend audible media playback.
       The playback node is created separately under the user's Play gesture. */
    const OfflineCtor=window.OfflineAudioContext||window.webkitOfflineAudioContext;
    if(OfflineCtor){
      const decoder=new OfflineCtor(2,1,44100);
      return decoder.decodeAudioData(bytes);
    }
    const AudioCtor=window.AudioContext||window.webkitAudioContext;
    if(!AudioCtor)throw new Error("PCM decoder unavailable");
    const decoder=new AudioCtor();
    try{return await decoder.decodeAudioData(bytes);}
    finally{
      if(typeof decoder.close==="function")
        Promise.resolve(decoder.close()).catch(()=>{});
    }
  }
  let fileVersion=0;
  async function loadFile(file){
    if(!file)return;
    const thisFile=++fileVersion;
    state.active=false;state.geometryEnabled=false;state.buffer=null;
    state.decodedChannels=null;
    resetLightingClock();
    state.audio.pause();
    if(state.objectURL)URL.revokeObjectURL(state.objectURL);
    state.objectURL=URL.createObjectURL(file);
    state.audio.src=state.objectURL;
    state.audio.load();
    /* Browsers can start native playback IMMEDIATELY; never wait for decode. */
    report("Music loaded: "+file.name+". Press Play; waveform analyzing separately.");
    try{
      const bytes=await file.arrayBuffer();
      const decoded=await decodeFile(bytes);
      if(thisFile!==fileVersion)return;
      state.buffer=decoded;
      const sourceL=decoded.getChannelData(0);
      const sourceR=decoded.getChannelData(decoded.numberOfChannels>1?1:0);
      state.decodedChannels=[sourceL,sourceR];
      state.peaksL=peakEnvelope(sourceL,N);
      state.peaksR=peakEnvelope(sourceR,N);
      state.active=true;state.geometryEnabled=true;
      if(state.audio.paused)
        report("Music ready — "+decoded.numberOfChannels+" channel(s), "+
          decoded.sampleRate+" Hz; press Play.");
      else
        report("Music playing — full-track waveform and geometry ready.");
    }catch(err){
      if(thisFile!==fileVersion)return;
      /* Live analyser is a real PCM path even for large/unsupported
         offline-decode files. Never turn off a working live visualization. */
      state.geometryEnabled=!!state.analyserL;
      state.active=state.geometryEnabled;
      report("Music ready; "+(state.analyserL?
        "live stereo waveform active.":"visual PCM unavailable.")+
        " Offline decode: "+err.message);
    }
  }
  function resizeCanvas(){
    const canvas=state.waveCanvas;
    if(!canvas)return;
    const ratio=clamp(window.devicePixelRatio||1,1,2);
    canvas.width=Math.floor(window.innerWidth*ratio);
    canvas.height=Math.floor(window.innerHeight*ratio);
    canvas.style.width=window.innerWidth+"px";
    canvas.style.height=window.innerHeight+"px";
    if(state.backLightCanvas){
      state.backLightCanvas.width=canvas.width;
      state.backLightCanvas.height=canvas.height;
      if(state.backLightTexture)state.backLightTexture.needsUpdate=true;
    }
    return ratio;
  }
  function draw(){
    window.requestAnimationFrame(draw);
    const canvas=state.waveCanvas;
    if(!canvas || !state.audio || state.audio.paused)return;
    /* The display follows the audible output sample clock, never accumulates
       timer-based FPS drift, and skips stale frames rather than replaying them. */
    const clock=currentAudioClock();
    if(!clock)return;
    if(!prepareVisualFrame(clock))return;
    if(!advanceLightingGate(clock.frame))return;
    state.outputClockSource=clock.source;
    const ctx=canvas.getContext("2d");
    if(!ctx)return;
    const scale=window.devicePixelRatio?clamp(window.devicePixelRatio,1,2):1;
    const W=canvas.width/scale,H=canvas.height/scale;
    ctx.setTransform(scale,0,0,scale,0,0);
    ctx.clearRect(0,0,W,H);
    /* Stereo fields paint behind the particle scene, not over the HUD. */
    const lightCtx=state.backLightCanvas?
      state.backLightCanvas.getContext("2d"):ctx;
    if(state.backLightCanvas){
      lightCtx.setTransform(scale,0,0,scale,0,0);
      lightCtx.globalCompositeOperation="source-over";
      lightCtx.fillStyle="#000000";
      lightCtx.fillRect(0,0,W,H);
    }
    paintGyroscopicVerticalPair(lightCtx,W,H,
      state.frameL[367],state.frameR[367],
      state.frameRmsL,state.frameRmsR,state.gyroTransport72,
      state.harmonicFrequencyHz[0],state.harmonicFrequencyHz[1]);
    const player=state.audio;
    const t=(player&&isFinite(player.duration)&&player.duration>0)
      ?clamp(player.currentTime/player.duration,0,1):0;
    const left=18,right=W-18,width=Math.max(1,right-left);
    const lower=Math.max(65,H-110),baselineL=lower-35,baselineR=lower+30;
    const waveformLength=state.buffer ? N : AUDIO_CLOCK.samplesPerFrame;
    const buses=[{
      data:state.buffer?state.peaksL:state.frameL,y:baselineL,
      color:q144Css(q144Index(0,state.frameL[0],state.frameRmsL,state.harmonicPhase[0],0),.85)
    },{
      data:state.buffer?state.peaksR:state.frameR,y:baselineR,
      color:q144Css(q144Index(0,state.frameR[0],state.frameRmsR,state.harmonicPhase[1],1),.85)
    }];
    ctx.lineWidth=1;
    for(const bus of buses){
      ctx.strokeStyle=bus.color;ctx.globalAlpha=0.55;
      ctx.beginPath();
      const stride=Math.max(1,Math.ceil(waveformLength/Math.max(1,width)));
      for(let i=0;i<waveformLength;i+=stride){
        let peak=0;
        for(let j=i;j<Math.min(waveformLength,i+stride);j++){
          if(Math.abs(bus.data[j])>Math.abs(peak))peak=bus.data[j];
        }
        const x=left+i/(waveformLength-1)*width;
        ctx.moveTo(x,bus.y);
        ctx.lineTo(x,bus.y-peak*27);
      }
      ctx.stroke();
    }
    ctx.globalAlpha=0.8;ctx.strokeStyle="#eff3ff";
    ctx.beginPath();ctx.moveTo(left+t*width,lower-68);
    ctx.lineTo(left+t*width,lower+62);ctx.stroke();
    ctx.globalAlpha=1;
    /* Lighting consumes 735-sample canonical audio frames at 60 Hz.
       Frame-relative gradients preserve each sample's crossing phase and
       accumulate no more than six audio ticks of fading history. */
    const events=state.crossingEvents;
    let write=0;
    for(let i=0;i<events.length;i++){
      const frame=crossingFrame(events[i][1]);
      /* Keep future crossings until their exact audio frame is audible.
         Drop only obsolete samples, never look-ahead audio messages. */
      if(frame>clock.frame-AUDIO_CLOCK.fadeFrames)
        events[write++]=events[i];
    }
    events.length=write;
    const cells=crossingLightingCells(
      events.length?events:state.frameCrossings,clock.frame);
    /* Every light band uses the SAME phase and orthogonal normals as
       the full-viewport stereo overlays, never fixed vertical x-columns. */
    lightCtx.globalCompositeOperation="lighter";
    const screenEnergy=[state.frameRmsL,state.frameRmsR];
    for(let bus=0;bus<2;bus++){
      const energy=lightAttenuation(screenEnergy[bus],state.harmonicFrequencyHz[bus],0);
      if(energy<.0005)continue;
      const sample=bus?state.frameR[367]:state.frameL[367];
      const hue=q144Index(0,sample,screenEnergy[bus],state.harmonicPhase[bus],bus);
      const angle=2*Math.PI*state.gyroTransport72/72;
      const offset=.13*Math.sin(angle+bus*Math.PI/2);
      paintGyroscopicLightBand(lightCtx,W,H,state.gyroTransport72,bus,
        offset,Math.min(W,H)*(.12+energy*.18),hue,energy*.35);
    }
    for(let bus=0;bus<2;bus++){
      for(let phase=0;phase<AUDIO_CLOCK.phaseBins;phase++){
        const strength=cells[bus][phase];
        if(strength<.02)continue;
        const offset=((phase+.5)/AUDIO_CLOCK.phaseBins-.5)*.84;
        const sample=bus?state.frameR[phase]:state.frameL[phase];
        const hue=q144Index(phase,sample,screenEnergy[bus],state.harmonicPhase[bus],bus);
        paintGyroscopicLightBand(lightCtx,W,H,state.gyroTransport72,bus,
          offset,2+strength*12,hue,
          lightAttenuation(screenEnergy[bus],state.harmonicFrequencyHz[bus],
            Math.abs(offset))*strength*.8);
      }
    }
    lightCtx.globalCompositeOperation="source-over";
    if(state.backLightTexture)state.backLightTexture.needsUpdate=true;
    ctx.globalAlpha=1;
    const meter=document.getElementById("audioVizClock");
    if(meter && (clock.frame%60===0 || state.lastClockStatusTime<0 ||
        clock.frame-state.lastClockStatusTime>=60)){
      state.lastClockStatusTime=clock.frame;
      meter.textContent="44,100 PCM Hz / 735 samples = 60 audio frames/s | "+
        "device "+clock.nativeRate+" Hz | phase frame "+clock.frame+
        " | dropped visual frames "+state.skippedLightingFrames+
        " | source "+clock.source+
        " | PCM "+state.renderSource+
        " | rms L/R "+state.frameRmsL.toFixed(3)+"/"+
        state.frameRmsR.toFixed(3)+
        " | pitch L/R "+Math.round(state.harmonicFrequencyHz[0])+"/"+
        Math.round(state.harmonicFrequencyHz[1])+"Hz"+
        " | u72 rotor "+state.gyroTransport72.toFixed(2)+
        " | crossed gradient 90deg"+
        " | particles "+state.particleVisualFrames;
    }
  }
  function boot(){
    const player=document.getElementById("audioVizPlayer");
    const picker=document.getElementById("audioVizFile");
    const play=document.getElementById("audioVizPlay");
    const stop=document.getElementById("audioVizStop");
    const gain=document.getElementById("audioVizGain");
    state.status=document.getElementById("audioVizStatus");
    if(!player||!picker||!play||!stop||!gain)return;
    state.audio=player;
    bindParticles(typeof particles!=="undefined"?particles:null);
    const canvas=document.createElement("canvas");
    canvas.id="audioVizOverlay";
    canvas.setAttribute("aria-hidden","true");
    Object.assign(canvas.style,{
      position:"fixed",top:"0",left:"0",zIndex:"2",
      pointerEvents:"none",display:"block"
    });
    document.body.appendChild(canvas);
    state.waveCanvas=canvas;
    if(typeof window.HHSInstallAudioBacklight==="function"){
      const back=document.createElement("canvas");
      state.backLightTexture=window.HHSInstallAudioBacklight(back);
      state.backLightCanvas=back;
    }
    resizeCanvas();
    window.addEventListener("resize",resizeCanvas);
    window.requestAnimationFrame(draw);
    picker.addEventListener("change",()=>{loadFile(picker.files&&picker.files[0]);});
    play.addEventListener("click",()=>{
      if(!player.getAttribute("src")){report("Choose a local audio file first.");return;}
      /* Both operations are invoked synchronously within this user gesture. */
      resumeAudio();
      if(player.ended)player.currentTime=0;
      const started=player.play();
      if(started && typeof started.catch==="function")
        started.catch(err=>report("Playback blocked: "+err.message+
          ". Use the native audio play control."));
    });
    stop.addEventListener("click",()=>{
      player.pause();
      try{player.currentTime=0;}catch(_ignored){}
      resetLightingClock();
      report("Stopped — music and waveform retained.");
    });
    /* Native <audio controls> needs the same gesture-bound unlock; a play
       event is delivered later and may no longer carry user activation. */
    player.addEventListener("pointerdown",()=>{
      if(player.getAttribute("src"))resumeAudio();
    },{passive:true});
    player.addEventListener("touchstart",()=>{
      if(player.getAttribute("src"))resumeAudio();
    },{passive:true});
    player.addEventListener("keydown",()=>{
      if(player.getAttribute("src"))resumeAudio();
    });
    player.addEventListener("play",()=>{
      resetLightingClock();
      if(state.context && state.context.state!=="running")resumeAudio();
    });
    player.addEventListener("playing",()=>{
      state.active=!!(state.analyserL || state.buffer);
      state.geometryEnabled=state.active;
      report(state.active?"Music playing — audio-driven particles and glow enabled.":
        "Music playing — no audio PCM visualization source available.");
    });
    player.addEventListener("pause",()=>{
      resetLightingClock();
      if(!player.ended)report("Music paused.");
    });
    player.addEventListener("error",()=>{
      const code=player.error&&player.error.code;
      report("Media playback error "+(code||"unknown")+
        ": try a supported MP3, WAV, or OGG file.");
    });
    player.addEventListener("seeked",resetLightingClock);
    player.addEventListener("ended",resetLightingClock);
    gain.addEventListener("input",()=>{
      state.gain=clamp(Number(gain.value)||0,0,GEOMETRY_GAIN.max);
      const out=document.getElementById("audioVizGainValue");
      if(out)out.textContent=state.gain.toFixed(3);
    });
    window.addEventListener("pagehide",()=>{
      player.pause();
      if(state.objectURL)URL.revokeObjectURL(state.objectURL);
    });
    report("Select an audio file to enable stereo PCM geometry.");
    const meter=document.getElementById("audioVizClock");
    if(meter)meter.textContent=
      "44,100 PCM Hz / 735 samples = 60 audio frames/s | awaiting playback";
  }
  window.HHSAudioViz=Object.freeze({
    busPair:PAIR,get active(){return state.active;},
    get geometryEnabled(){return state.geometryEnabled;},
    projectMatrix,projectColor,projectParticleGlow,particleHaloOpacity,
    projectBrownianAntiParticle,observeBrownianSubstep,
    advanceBrownianVisual,resetBrownianVisual,
    brownianProbabilityAt,brownianProbabilitySlot,brownianOffsetAt,
    particleLayer5184,lightAttenuation,
    q144Index,q144Css,bindParticles,particlePhysicalProjection,coupledParticleFrame,peakEnvelope,crossingsFromBlock,
    amplitudeGeometry,harmonicProfile,harmonicStep,
    gyroscopicPhaseGear72,transportGyroscopicPhase72,
    gyroscopicGradientAxes72,spectralFallbackHz,
    verticalReciprocalGradientPair,paintGyroscopicVerticalPair,
    paintGyroscopicLightBand,fourPhasePresentationPacket,interlaceContract:INTERLACE,
    prepareVisualFrame,needsProjectionFrame,frameSampleMetrics,
    frameCrossingEvents,attachLiveStereo,
    audioClock:AUDIO_CLOCK, canonicalSampleIndex,frameForSample,
    sampleForFrame,outputClockFrame,crossingFrame,crossingLightingCells,
    advanceLightingGate,
    get diagnostics(){return {
      active:state.active, sampleRate:state.sampleRate,
      geometryEnabled:state.geometryEnabled,
      frameSignalReady:state.frameSignalReady,
      visualSource:state.renderSource,
      palette:"Q144-full-spectrum-audio-phase",donut:false,
       fourPhaseInterlacing:true,
       fourPhasePacket:fourPhasePresentationPacket(state.lastFrame),
       geometryNormalizationGain:state.gain,
       geometryNormalizationGainMax:GEOMETRY_GAIN.max,
       haloEmissionGain:HALO_EMISSION_GAIN,
       brownianSchema:BROWNIAN.schema,
       brownianAntiParticleCells:BROWNIAN.cells,
       brownianTickDelay:BROWNIAN.tickDelay,
       brownianTick:brownianTick,
       brownianDelayedTick:brownianDelayedTick,
       brownianDelayedLight:brownianDelayedLight,
       brownianDelayedPhase:brownianDelayedPhase,
       brownianDelayedFlip:brownianDelayedFlip,
       brownianAudioFrame:brownianAudioFrame,
       brownianMaxOffset:BROWNIAN.maxOffset,
       brownianPhysicsAdmission:false,
       backLightLayerCells:BACK_LIGHT.layerCells,
       backLightLayerCount:BACK_LIGHT.layers,
       backLightOpacityCap:BACK_LIGHT.alphaCap,
       backLightBandCap:BACK_LIGHT.bandCap,
       backLightActive:!!state.backLightTexture,
       lightingBehindOpaqueParticles:true,
       cellularBoundaryAmplitudeResponsive:true,
       particleSizeAmplitudeResponsive:true,
       harmonicColorWheel:true,
       verticalReciprocalGyroscopicGradient:true,
       gyroscopeSchema:GYRO_SHADER.schema,
       gyroscopePhase72:state.gyroPhase72,
       gyroscopeVisualPhase72:state.gyroTransport72,
       visualGradientAxesOrthogonal:true,
       particleHalosPhaseLocked:true,
       allLightBandsRotatingWithGyro:true,
       gyroscopeQuarterTurn:GYRO_SHADER.quarterTurn,
       gyroscopeFullPeriod:GYRO_SHADER.phaseModulus,
       harmonicFrequencyLHz:state.harmonicFrequencyHz[0],
       harmonicFrequencyRHz:state.harmonicFrequencyHz[1],
       harmonicMomentL:state.harmonicMoment[0],
       harmonicMomentR:state.harmonicMoment[1],
       harmonicPhaseL:state.harmonicPhase[0],
       harmonicPhaseR:state.harmonicPhase[1],
      frameRmsL:state.frameRmsL,frameRmsR:state.frameRmsR,
      particleVisualFrames:state.particleVisualFrames,
      liveFrameCount:state.liveFrameCount,
      canonicalRate:AUDIO_CLOCK.canonicalRate,
      visualHz:AUDIO_CLOCK.visualHz,
      samplesPerFrame:AUDIO_CLOCK.samplesPerFrame,
      audioFrame:state.lastFrame,
      visualFramesRendered:state.renderedLightingFrames,
      visualFramesSkipped:state.skippedLightingFrames,
      clockSource:state.outputClockSource,
      crossesQueued:state.crossingEvents.length,
      geometryBins:N, canonicalMutation:false
    };}
  });
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",boot,{once:true});
  else boot();
})();