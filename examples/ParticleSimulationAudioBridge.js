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
  const state={
    active:false, geometryEnabled:false, gain:1.25,
    pair:PAIR, peaksL:new Float32Array(N), peaksR:new Float32Array(N),
    crossingEvents:[], sampleRate:0, buffer:null, context:null, source:null,
    processor:null, objectURL:null, audio:null, particleIndex:new WeakMap(),
    waveCanvas:null, started:false, lastFrame:-1, lastSample:[0,0], status:null,
    processorReady:null, renderedLightingFrames:0, skippedLightingFrames:0,
    outputClockSource:"inactive", lightingLatencyMs:0, lastClockStatusTime:-1,
    analyserL:null,analyserR:null,analyserDataL:new Float32Array(2048),
    analyserDataR:new Float32Array(2048),frameL:new Float32Array(735),
    frameR:new Float32Array(735),frameCrossings:[],frameRmsL:0,frameRmsR:0,
    framePeakL:0,framePeakR:0,frameSignalReady:false,lastSignalFrame:-1,
    particleFrame:-1,particleVisualFrames:0,liveFrameCount:0,
    renderSource:"none",decodedChannels:null
  };
  function clamp(x,a,b){return Math.min(b,Math.max(a,x));}
  function finite(x){return Number.isFinite(x)?x:0;}
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
    state.frameCrossings=[];
    state.crossingEvents.length=0;
    state.lastSample=[0,0];
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
    const heat=clamp(Math.sqrt(rms)*2.1+Math.abs(sample)*0.65,0,1);
    const bright=0.42+0.58*heat;
    if(bus===0)color.setRGB(
      clamp(base.r*bright+heat*0.22,0,1),
      clamp(base.g*bright+heat*0.72,0,1),
      clamp(base.b*bright+heat*0.95,0,1));
    else color.setRGB(
      clamp(base.r*bright+heat*0.93,0,1),
      clamp(base.g*bright+heat*0.23,0,1),
      clamp(base.b*bright+heat*0.75,0,1));
    return color;
  }
  function report(message){
    if(state.status)state.status.textContent=message;
  }
  function bindParticles(particles){
    if(!particles)return;
    state.particleIndex=new WeakMap();
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
    const energy=clamp(Math.sqrt(rms)*2.2,0,1);
    const transient=clamp(Math.abs(sample)*2.5,0,1);
    const gain=state.gain;
    const strength=gain*(energy*2.8+transient*3.2);
    const e=matrix.elements;
    const radius=Math.hypot(e[12],e[13],e[14])||1;
    const orientation=bus? -1:1;
    e[12]+=strength*(e[12]/radius*.7+sample*orientation*1.5);
    e[13]+=strength*(e[13]/radius*.7+sample*.9);
    e[14]+=strength*(e[14]/radius*.5+sample*orientation*.65);
    /* With SphereGeometry(0.1), scaling the instance basis makes transients
       actually visible without modifying p.scale or canonical positions. */
    const size=1+gain*(energy*1.4+transient*1.8);
    e[0]*=size;e[5]*=size;e[10]*=size;
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
    const player=state.audio;
    const t=(player&&isFinite(player.duration)&&player.duration>0)
      ?clamp(player.currentTime/player.duration,0,1):0;
    const left=18,right=W-18,width=Math.max(1,right-left);
    const lower=Math.max(65,H-110),baselineL=lower-35,baselineR=lower+30;
    const waveformLength=state.buffer ? N : AUDIO_CLOCK.samplesPerFrame;
    const buses=[{data:state.buffer?state.peaksL:state.frameL,y:baselineL,color:"#43d7fb"},
                 {data:state.buffer?state.peaksR:state.frameR,y:baselineR,color:"#d28cff"}];
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
    /* Full-scene illumination is distinct from bottom waveform tracing.
       Stereo RMS drives two additive glow fields; zero crossings add small
       phase-offset flashes. This is raster-only; MeshBasicMaterial itself
       cannot react to Three.js PointLight. */
    ctx.globalCompositeOperation="lighter";
    const screenEnergy=[state.frameRmsL,state.frameRmsR];
    for(let bus=0;bus<2;bus++){
      const energy=clamp(Math.sqrt(screenEnergy[bus])*1.8,0,1);
      if(energy<0.012)continue;
      const x=W*(bus===0?.37:.63), y=H*.47;
      const radius=Math.max(125,Math.min(W,H)*(.25+energy*.45));
      const gradient=ctx.createRadialGradient(x,y,0,x,y,radius);
      const color=bus?"184,77,255":"38,198,255";
      gradient.addColorStop(0,"rgba("+color+","+(energy*.46)+")");
      gradient.addColorStop(.45,"rgba("+color+","+(energy*.20)+")");
      gradient.addColorStop(1,"rgba("+color+",0)");
      ctx.fillStyle=gradient;
      ctx.fillRect(x-radius,y-radius,radius*2,radius*2);
    }
    for(let bus=0;bus<2;bus++){
      for(let phase=0;phase<72;phase++){
        const strength=cells[bus][phase];
        if(strength<0.02)continue;
        const phaseAngle=phase/72*Math.PI*2;
        const x=W*.5+Math.cos(phaseAngle+bus*Math.PI)*W*.23;
        const y=H*.48+Math.sin(phaseAngle+bus*Math.PI)*H*.22;
        const radius=16+strength*Math.min(W,H)*.16;
        const gradient=ctx.createRadialGradient(x,y,0,x,y,radius);
        const color=bus?"200,120,255":"65,215,255";
        gradient.addColorStop(0,"rgba("+color+","+(strength*0.7)+")");
        gradient.addColorStop(0.4,"rgba("+color+","+(strength*0.27)+")");
        gradient.addColorStop(1,"rgba("+color+",0)");
        ctx.fillStyle=gradient;
        ctx.fillRect(x-radius,y-radius,radius*2,radius*2);
      }
    }
    ctx.globalCompositeOperation="source-over";
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
      state.gain=clamp(Number(gain.value)||0,0,5);
      const out=document.getElementById("audioVizGainValue");
      if(out)out.textContent=state.gain.toFixed(2);
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
    projectMatrix,projectColor,bindParticles,peakEnvelope,crossingsFromBlock,
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