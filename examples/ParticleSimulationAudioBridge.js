/* HHS Pass 220 — stereo PCM projection membrane.
   Audio never mutates canonical VM81, particle physics, or receipts. */
(function () {
  "use strict";
  const PAIR = Object.freeze({
    left: Object.freeze({numerator:Object.freeze(["x","xy","x+y","y"]), denominator:"zw"}),
    right:Object.freeze({numerator:Object.freeze(["z","zw","z-w","w"]), denominator:"xy"}),
    relation:"ordered stereo-bus equality; no scalar cancellation"
  });
  const N=10368;
  const state={
    active:false, geometryEnabled:false, gain:1.25,
    pair:PAIR, peaksL:new Float32Array(N), peaksR:new Float32Array(N),
    crossingEvents:[], sampleRate:0, buffer:null, context:null, source:null,
    processor:null, objectURL:null, audio:null, particleIndex:new WeakMap(),
    waveCanvas:null, started:false, lastFrame:0, lastSample:[0,0], status:null
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
    if(state.crossingEvents.length>1800)
      state.crossingEvents.splice(0,state.crossingEvents.length-1800);
  }
  function installFallback(context,source){
    const processor=context.createScriptProcessor(1024,2,2);
    processor.onaudioprocess=function(ev){
      const input=ev.inputBuffer,output=ev.outputBuffer;
      const left=input.getChannelData(0);
      const right=input.numberOfChannels>1?input.getChannelData(1):left;
      for(let c=0;c<output.numberOfChannels;c++)
        output.getChannelData(c).set(c===0?left:right);
      enqueue(crossingsFromBlock(left,right,
        ev.playbackTime*context.sampleRate,context.sampleRate,state.lastSample));
    };
    source.connect(processor);processor.connect(context.destination);
    return processor;
  }
  const WORKLET=String.raw("class HHSStereoCrossingWorklet extends AudioWorkletProcessor {\n"+
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
    "if(++this.blocks%8===0){if(this.pending.length)\n"+
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
        source.connect(node);node.connect(context.destination);
        return node;
      }catch(err){
        report("AudioWorklet unavailable; PCM fallback active ("+err.message+").");
      }finally{URL.revokeObjectURL(url);}
    }
    return installFallback(context,source);
  }
  async function ensureAudio(){
    if(state.context)return state.context;
    const AudioCtor=window.AudioContext||window.webkitAudioContext;
    if(!AudioCtor)throw new Error("Web Audio is unavailable in this browser");
    const context=new AudioCtor();
    state.context=context;
    state.sampleRate=context.sampleRate;
    const source=context.createMediaElementSource(state.audio);
    state.source=source;
    try{state.processor=await installProcessor(context,source);}
    catch(err){
      /* A missing processor must not silently mute the media element. */
      source.connect(context.destination);
      report("Audio PCM analyzer unavailable: "+err.message);
    }
    return context;
  }
  async function loadFile(file){
    if(!file)return;
    state.active=false;state.geometryEnabled=false;
    state.crossingEvents.length=0;state.lastSample=[0,0];
    state.audio.pause();
    if(state.objectURL)URL.revokeObjectURL(state.objectURL);
    state.objectURL=URL.createObjectURL(file);
    state.audio.src=state.objectURL;state.audio.load();
    report("Reading complete stereo PCM waveform…");
    try{
      const ctx=await ensureAudio();
      const bytes=await file.arrayBuffer();
      const decoded=await ctx.decodeAudioData(bytes);
      state.buffer=decoded;
      state.peaksL=peakEnvelope(decoded.getChannelData(0),N);
      state.peaksR=peakEnvelope(
        decoded.getChannelData(decoded.numberOfChannels>1?1:0),N);
      state.active=true;state.geometryEnabled=true;
      report("Ready — "+decoded.numberOfChannels+" channel(s), "+
        decoded.sampleRate+" Hz, "+decoded.duration.toFixed(2)+
        "s; stereo tensor geometry armed.");
    }catch(err){
      state.geometryEnabled=false;
      report("Audio decode/visualization error: "+err.message);
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
    const now=state.context?state.context.currentTime:0;
    const events=state.crossingEvents;
    let write=0;
    for(let i=0;i<events.length;i++){
      const e=events[i],age=now-e[1];
      if(age<0||age>0.65)continue;
      events[write++]=e;
      const strength=clamp(e[2]*16,0,1)*(1-age/0.65);
      if(strength<0.015)continue;
      const x=left+t*width+(e[0]?12:-12)+(e[3]*strength*28);
      const y=e[0]?baselineR:baselineL;
      const radius=12+strength*80;
      const gradient=ctx.createRadialGradient(x,y,0,x,y,radius);
      const color=e[0]?"200,120,255":"65,215,255";
      gradient.addColorStop(0,"rgba("+color+","+(strength*0.45)+")");
      gradient.addColorStop(0.4,"rgba("+color+","+(strength*0.15)+")");
      gradient.addColorStop(1,"rgba("+color+",0)");
      ctx.fillStyle=gradient;
      ctx.fillRect(x-radius,y-radius,radius*2,radius*2);
    }
    events.length=write;
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
    play.addEventListener("click",async()=>{
      if(!player.src){report("Choose a local audio file first.");return;}
      try{const ctx=await ensureAudio();await ctx.resume();await player.play();}
      catch(err){report("Playback error: "+err.message);}
    });
    stop.addEventListener("click",()=>{player.pause();player.currentTime=0;
      state.crossingEvents.length=0;report("Stopped — waveform retained.");});
    player.addEventListener("play",()=>{
      ensureAudio().then(ctx=>ctx.resume()).catch(err=>report(err.message));
    });
    player.addEventListener("seeked",()=>{state.crossingEvents.length=0;});
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
  }
  window.HHSAudioViz=Object.freeze({
    busPair:PAIR,get active(){return state.active;},
    get geometryEnabled(){return state.geometryEnabled;},
    projectMatrix,bindParticles,peakEnvelope,crossingsFromBlock,
    get diagnostics(){return {
      active:state.active, sampleRate:state.sampleRate,
      crossesQueued:state.crossingEvents.length,
      geometryBins:N, canonicalMutation:false
    };}
  });
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",boot,{once:true});
  else boot();
})();