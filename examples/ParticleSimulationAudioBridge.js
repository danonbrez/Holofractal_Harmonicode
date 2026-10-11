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
    outputClockSource:"inactive", lightingLatencyMs:0, lastClockStatusTime:-1
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
    state.crossingEvents.length=0;
    state.lastSample=[0,0];
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
    if(!state.geometryEnabled)return;
    const i=state.particleIndex.get(p);
    if(i===undefined)return;
    const l=state.peaksL[i],r=state.peaksR[i];
    const audio=state.audio;
    const playhead=(audio&&Number.isFinite(audio.duration)&&audio.duration>0)
      ?clamp(audio.currentTime/audio.duration,0,1):0;
    const region=i/(N-1);
    const focus=Math.max(0,1-Math.abs(region-playhead)*24);
    const gain=state.gain*(0.45+0.55*focus);
    const e=matrix.elements;
    e[12]+=l*gain; e[13]+=r*gain;
    e[14]+=(l-r)*gain*0.65;
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
    "constructor(){super();this.prev=[0,0];this.pending=[];this.blocks=0;}\n"+
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
      state.peaksL=peakEnvelope(decoded.getChannelData(0),N);
      state.peaksR=peakEnvelope(
        decoded.getChannelData(decoded.numberOfChannels>1?1:0),N);
      state.active=true;state.geometryEnabled=true;
      if(state.audio.paused)
        report("Music ready — "+decoded.numberOfChannels+" channel(s), "+
          decoded.sampleRate+" Hz; press Play.");
      else
        report("Music playing — full-track waveform and geometry ready.");
    }catch(err){
      if(thisFile!==fileVersion)return;
      state.geometryEnabled=false;
      report("Music ready to play; waveform decode unavailable: "+err.message);
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
    if(!canvas||!state.active)return;
    /* The display follows the audible output sample clock, never accumulates
       timer-based FPS drift, and skips stale frames rather than replaying them. */
    const clock=outputClockFrame(state.context,state.audio,
      window.performance && typeof window.performance.now==="function" ?
      window.performance.now():NaN);
    if(!clock)return;
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
    const buses=[{data:state.peaksL,y:baselineL,color:"#43d7fb"},
                 {data:state.peaksR,y:baselineR,color:"#d28cff"}];
    ctx.lineWidth=1;
    for(const bus of buses){
      ctx.strokeStyle=bus.color;ctx.globalAlpha=0.55;
      ctx.beginPath();
      const stride=Math.max(1,Math.ceil(N/Math.max(1,width)));
      for(let i=0;i<N;i+=stride){
        let peak=0;
        for(let j=i;j<Math.min(N,i+stride);j++){
          if(Math.abs(bus.data[j])>Math.abs(peak))peak=bus.data[j];
        }
        const x=left+i/(N-1)*width;
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
    const cells=crossingLightingCells(events,clock.frame);
    for(let bus=0;bus<2;bus++){
      for(let phase=0;phase<72;phase++){
        const strength=cells[bus][phase];
        if(strength<0.02)continue;
        const x=left+t*width+(phase-35.5)*0.9;
        const y=bus?baselineR:baselineL;
        const radius=12+strength*75;
        const gradient=ctx.createRadialGradient(x,y,0,x,y,radius);
        const color=bus?"200,120,255":"65,215,255";
        gradient.addColorStop(0,"rgba("+color+","+(strength*0.45)+")");
        gradient.addColorStop(0.4,"rgba("+color+","+(strength*0.15)+")");
        gradient.addColorStop(1,"rgba("+color+",0)");
        ctx.fillStyle=gradient;
        ctx.fillRect(x-radius,y-radius,radius*2,radius*2);
      }
    }
    const meter=document.getElementById("audioVizClock");
    if(meter && (clock.frame%60===0 || state.lastClockStatusTime<0 ||
        clock.frame-state.lastClockStatusTime>=60)){
      state.lastClockStatusTime=clock.frame;
      meter.textContent="44,100 PCM Hz / 735 samples = 60 audio frames/s | "+
        "device "+clock.nativeRate+" Hz | phase frame "+clock.frame+
        " | dropped visual frames "+state.skippedLightingFrames+
        " | source "+clock.source;
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
      if(state.context && state.context.state!=="running")resumeAudio();
    });
    player.addEventListener("playing",()=>report("Music playing through stereo output."));
    player.addEventListener("pause",()=>{
      if(!player.ended)report("Music paused.");
    });
    player.addEventListener("error",()=>{
      const code=player.error&&player.error.code;
      report("Media playback error "+(code||"unknown")+
        ": try a supported MP3, WAV, or OGG file.");
    });
    player.addEventListener("seeked",resetLightingClock);
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
    projectMatrix,bindParticles,peakEnvelope,crossingsFromBlock,
    audioClock:AUDIO_CLOCK, canonicalSampleIndex,frameForSample,
    sampleForFrame,outputClockFrame,crossingFrame,crossingLightingCells,
    advanceLightingGate,
    get diagnostics(){return {
      active:state.active, sampleRate:state.sampleRate,
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