"""Regression guards for the canonical particle-game stereo HTML patch."""
import shutil
import subprocess
import re
from pathlib import Path
import pytest

HTML=Path("examples/ParticleSimulation.html")
BRIDGE=Path("examples/ParticleSimulationAudioBridge.js")

def test_game_controls_are_present_and_all_primary_bindings_work():
    html=HTML.read_text(encoding="utf-8")
    for control in ("toggleShell","runCommand","runCalibration","stepCycle",
                    "freqSlider","massSlider","collSlider","ctorSlider",
                    "bondSlider","topoBtn","chaseBtn","jsonCommandInput",
                    "sendQpuCommand","audioVizFile","audioVizPlayer",
                    "audioVizPlay","audioVizStop","audioVizGain"):
        assert html.count('id="'+control+'"')==1,control
    for action in ("runCommand","runCalibration","stepCycle"):
        assert 'document.getElementById("'+action+'").addEventListener("click"' in html
    for slider in ("freqSlider","massSlider","collSlider","ctorSlider","bondSlider"):
        assert slider+'.addEventListener("input"' in html
    assert 'chaseBtn.addEventListener("click"' in html
    assert 'topoBtn.addEventListener("click"' in html
    assert 'toggleButton.addEventListener("click"' in html
    assert 'id="qpuConsolePanel"' in html
    assert '<details id="qpuConsolePanel"' in html
    inline = re.search(r'<script id="hhsAudioInline">\s*([\s\S]*?)\s*</script>', html)
    assert inline, "Standalone HTML must include audio implementation without external file"
    assert inline.group(1).strip() == BRIDGE.read_text(encoding="utf-8").strip()
    assert '<canvas id="audioVizOverlay"' not in html # no duplicate static canvas
    assert 'canvas.id="audioVizOverlay";' in html # the inline bridge creates one
    assert 'document.getElementById("commandOutput").innerHTML' not in html

def test_audio_waveform_is_projection_only_and_preserves_physics_receipts():
    html=HTML.read_text(encoding="utf-8")
    bridge=BRIDGE.read_text(encoding="utf-8")
    assert 'for(let s=0;s<steps;s++){ updateSpiralParticles();' in html
    assert 'renderGate=((renderTick%4)===0);' in html
    assert 'compressedHash: computeManifoldHash()' in html
    assert 'audioVisual.projectMatrix(p,particleBatchMatrix);' in html
    assert 'particleBatchMatrix.makeTranslation(q.x,q.y,q.z);' in html
    assert 'const N=10368;' in bridge
    assert 'p.position.' not in bridge
    assert 'canonicalMutation:false' in bridge
    assert 'numerator:Object.freeze(["x","xy","x+y","y"]), denominator:"zw"' in bridge
    assert 'numerator:Object.freeze(["z","zw","z-w","w"]), denominator:"xy"' in bridge
    assert 'Math.floor(i*bins/samples.length)' in bridge
    assert 'firstFrame+i-1+frac' in bridge
    assert 'registerProcessor(' in bridge
    assert 'cells=[new Float32Array(AUDIO_CLOCK.phaseBins),' in bridge

def test_bridge_js_and_pcm_crossing_runtime():
    node=shutil.which("node")
    if not node:
        pytest.skip("Node.js is not installed")
    program=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const code=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const window={},document={readyState:"loading",addEventListener(){}};
vm.runInNewContext(code,{window,document,Float32Array,WeakMap,Array,Math,Number,Object,
  isFinite,URL,Blob,AudioWorkletNode:undefined});
const viz=window.HHSAudioViz;
assert.equal(viz.busPair.left.denominator,"zw");
assert.equal(viz.busPair.right.denominator,"xy");
const p=viz.peakEnvelope(new Float32Array([.1,-.7,.3,.1,.9,-.2]),3);
assert.ok(Math.abs(p[0]+.7)<1e-6 && Math.abs(p[1]-.3)<1e-6 && Math.abs(p[2]-.9)<1e-6);
const prior=[0,0];
const a=viz.crossingsFromBlock(new Float32Array([-1,-.5]),
  new Float32Array([1,.5]),0,100,prior);
assert.equal(a.length,0);
const b=viz.crossingsFromBlock(new Float32Array([.5,-.5]),
  new Float32Array([-.5,.5]),2,100,prior);
assert.equal(b.length,4);
assert.ok(Math.abs(b[0][1]-.015)<1e-9);
assert.ok(Math.abs(b[1][1]-.025)<1e-9);
assert.equal(viz.diagnostics.canonicalMutation,false);
const m=code.match(/const WORKLET=\(([\s\S]*?)\);\s*async function installProcessor/);
assert.ok(m);
const processorSource=Function("return ("+m[1]+")")();
new Function(processorSource); // parse generated AudioWorklet in isolation
"""
    run=subprocess.run([node,"-e",program],text=True,capture_output=True)
    assert run.returncode==0,run.stderr


def test_audio_play_is_gesture_bound_and_has_direct_speaker_connection():
    """Catch the original regression: play() waited for asynchronous worklet
    installation while MediaElementAudioSource had no speaker connection."""
    node=shutil.which("node")
    if not node:
        pytest.skip("Node.js is not installed")
    program=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const code=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const events=[], nodes={};
class Element {
  constructor(id){this.id=id;this.style={};this.listeners={};this.src="";this.paused=true;}
  addEventListener(name,fn){this.listeners[name]=fn;}
  setAttribute(k,v){this[k]=v;}
  getAttribute(k){return this[k]||null;}
  pause(){this.paused=true;}
  load(){}
  play(){
    // This must run before AudioWorklet.addModule resolves.
    assert(events.includes("dry speaker connected"));
    events.push("play invoked");
    this.paused=false;
    return Promise.resolve();
  }
}
for(const name of ["audioVizPlayer","audioVizFile","audioVizPlay",
   "audioVizStop","audioVizGain","audioVizStatus","audioVizGainValue"])
   nodes[name]=new Element(name);
nodes.audioVizPlayer.src="blob:example";
const player=nodes.audioVizPlayer;
class FakeContext {
  constructor(){
    this.destination={speaker:true};this.sampleRate=48000;
    this.state="suspended";events.push("context created");
    this.audioWorklet={addModule:()=>new Promise(()=>{})}; // never finishes
  }
  createMediaElementSource(el){
    assert.strictEqual(el,player);
    return {connect:(target)=>{
       if(target===this.destination)events.push("dry speaker connected");
       else events.push("analyzer connected");
    }};
  }
  resume(){this.state="running";events.push("context resumed");return Promise.resolve();}
}
const window={
  AudioContext:FakeContext,devicePixelRatio:1,innerWidth:800,innerHeight:600,
  addEventListener(){},requestAnimationFrame(){},
};
const document={
  readyState:"complete",getElementById(id){return nodes[id]},
  createElement(tag){return new Element(tag)},
  body:{appendChild(){}}
};
const FakeURL={createObjectURL(){return "blob:mock-worklet"},revokeObjectURL(){}};
vm.runInNewContext(code,{
   window,document,Float32Array,WeakMap,Array,Math,Number,Object,
   isFinite,URL:FakeURL,Blob,AudioWorkletNode:function(){},
});
nodes.audioVizPlay.listeners.click();
assert(events.indexOf("dry speaker connected")>=0,events);
assert(events.indexOf("play invoked")>events.indexOf("dry speaker connected"),events);
assert(events.indexOf("play invoked")>=0,events);
assert(events.indexOf("context resumed")>=0,events);
"""
    run=subprocess.run([node,"-e",program],text=True,capture_output=True)
    assert run.returncode==0,run.stderr


def test_audio_clock_44100_60hz_stereo_addressing_and_skipped_frames():
    """44100/60=735 exact sample ticks, 5184 per phase lane, 10368 paired.
    Test 48k hardware rate mapping, timestamp alignment and bounded light bins.
    """
    node=shutil.which("node")
    if not node:
        pytest.skip("Node.js is not installed")
    program=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const source=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const win={},doc={readyState:"loading",addEventListener(){}};
vm.runInNewContext(source,{window:win,document:doc,Float32Array,WeakMap,
  Array,Math,Number,Object,URL,Blob,isFinite});
const v=win.HHSAudioViz,k=v.audioClock;
assert.equal(k.canonicalRate,44100);
assert.equal(k.visualHz,60);
assert.equal(k.samplesPerFrame,735);
assert.equal(k.laneCells,81*64);
assert.equal(k.hash72Cells,72*72);
assert.equal(k.pairedParticles,2*81*64);
for(let frame=0;frame<1200;frame++){
  assert.equal(v.sampleForFrame(frame),frame*735);
  assert.equal(v.frameForSample(frame*735,44100),frame);
  assert.equal(v.frameForSample(frame*735+734,44100),frame);
  assert.equal(v.frameForSample(frame*800,48000),frame);
  assert.equal(v.frameForSample(frame*800+799,48000),frame);
}
const audio={paused:false,ended:false,currentTime:5};
const ctx={state:"running",sampleRate:48000,currentTime:1.5,
  getOutputTimestamp(){return {contextTime:1,performanceTime:1000}}};
const clock=v.outputClockFrame(ctx,audio,1016.66666667);
assert.equal(clock.frame,61);
assert.equal(clock.source,"output-timestamp");
assert.equal(clock.nativeRate,48000);
assert.equal(v.outputClockFrame(ctx,{paused:true},1016),null);
assert.ok(v.advanceLightingGate(0));
assert.ok(!v.advanceLightingGate(0));
assert.ok(v.advanceLightingGate(2));
assert.equal(v.diagnostics.audioFrame,2);
assert.equal(v.diagnostics.visualFramesSkipped,1);
assert.equal(v.diagnostics.visualFramesRendered,2);
assert.ok(v.advanceLightingGate(60));
assert.equal(v.diagnostics.visualFramesSkipped,58);
const c=v.crossingLightingCells([
  [0,735/44100,.5,1],
  [1,736/44100,.5,-1],
  [0,3*735/44100,.5,1],
],1);
assert.equal(c.length,2);
assert.ok(c[0][735%72]>.2);
assert.ok(c[1][736%72]>.2);
assert.equal(c[0][(3*735)%72],0); // future crossing held, not emitted
const d=v.crossingLightingCells([[1,0,.5,1]],7);
assert.ok(d[1].every(x=>x===0)); // six-frame fade bounded
"""
    run=subprocess.run([node,"-e",program],text=True,capture_output=True)
    assert run.returncode==0,run.stderr


def test_audio_worklet_emits_before_735_sample_visual_deadline():
    """PCM worklet must dispatch in fewer than 735 samples at 44.1kHz.
    Visual drawing remains driven by output audio clock, not callback cadence.
    """
    node=shutil.which("node")
    if not node:
        pytest.skip("Node.js is not installed")
    program=r"""
const fs=require("fs"),assert=require("assert");
const source=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const m=source.match(/const WORKLET=\(([\s\S]*?)\);\s*async function installProcessor/);
assert.ok(m);
const workletCode=Function("return ("+m[1]+")")();
const messages=[];
class AudioWorkletProcessor {
 constructor(){this.port={postMessage(x){messages.push(x)}}}
}
let Worklet;
new Function("AudioWorkletProcessor","registerProcessor","currentFrame","sampleRate",workletCode)(
  AudioWorkletProcessor,(name,fn)=>{Worklet=fn},1000,44100);
const w=new Worklet();
for(let block=0;block<2;block++){
 const left=new Float32Array(128),right=new Float32Array(128);
 for(let i=0;i<128;i++){
  left[i]=i%2?1:-1;right[i]=-left[i];
 }
 const outL=new Float32Array(128),outR=new Float32Array(128);
 w.process([[left,right]],[[outL,outR]]);
 assert.equal(outL[1],left[1]);
 assert.equal(outR[0],right[0]);
}
assert.equal(messages.length,1,"Must flush after two 128-sample quanta");
assert.ok(messages[0].crossings.length>200);
assert.ok(128*2<735);
"""
    run=subprocess.run([node,"-e",program],text=True,capture_output=True)
    assert run.returncode==0,run.stderr


def test_audio_lighting_renders_only_at_sample_clock_frame_boundaries():
    """Even under a faster/repeated RAF, a new draw requires 735 audio samples."""
    node=shutil.which("node")
    if not node:
        pytest.skip("Node.js is not installed")
    program=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const bridge=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const nodes={},drawn=[];let callback,seconds=0;
class Element {
 constructor(id){this.id=id;this.style={};this.handlers={};this.paused=true;
  this.ended=false;this.currentTime=0;this.duration=.05;}
 addEventListener(k,cb){this.handlers[k]=cb;}
 setAttribute(k,v){this[k]=v;}
 getAttribute(k){return this[k]||null;}
 load(){}
 pause(){this.paused=true;this.handlers.pause?.();}
 play(){this.paused=false;this.handlers.play?.();return Promise.resolve();}
 getContext(){return ctx;}
}
const ctx={setTransform(){},clearRect(){drawn.push(seconds)},beginPath(){},
 moveTo(){},lineTo(){},closePath(){},stroke(){},fill(){},fillRect(){},
 createLinearGradient(){return {addColorStop(){}}}};
for(const id of ["audioVizPlayer","audioVizFile","audioVizPlay",
 "audioVizStop","audioVizGain","audioVizStatus","audioVizGainValue",
 "audioVizClock"])nodes[id]=new Element(id);
const doc={readyState:"complete",getElementById:id=>nodes[id],
  createElement:name=>new Element(name),body:{appendChild(){}}};
const win={
  innerWidth:800,innerHeight:600,devicePixelRatio:1,
  performance:{now:()=>1000},addEventListener(){},
  requestAnimationFrame(fn){callback=fn;},
  AudioContext:class {
    constructor(){this.sampleRate=44100;this.state="suspended";
      this.currentTime=1;this.destination={};
      this.audioWorklet={addModule:()=>new Promise(()=>{})};}
    createMediaElementSource(){return {connect(){}};}
    getOutputTimestamp(){return {contextTime:seconds,performanceTime:1000};}
    resume(){this.state="running";return Promise.resolve();}
  },
  OfflineAudioContext:class {
    decodeAudioData(){return Promise.resolve({numberOfChannels:2,
      sampleRate:44100,duration:.05,
      getChannelData(){return new Float32Array(3000).fill(.5);}});}
  }
};
const URLMock={createObjectURL:()=>"blob:fake",revokeObjectURL(){}};
vm.runInNewContext(bridge,{window:win,document:doc,
 URL:URLMock,Blob,AudioWorkletNode:class{},Float32Array,WeakMap,
 Array,Math,Number,Object,isFinite});
(async()=>{
 nodes.audioVizFile.files=[{name:"demo.wav",arrayBuffer:async()=>new ArrayBuffer(10)}];
 nodes.audioVizFile.handlers.change();
 for(let i=0;i<6;i++)await Promise.resolve();
 assert.ok(win.HHSAudioViz.active);
 nodes.audioVizPlay.handlers.click();
 for(const frame of [0,0,1,3,3,4]){
   seconds=frame/60;callback();
 }
 assert.deepStrictEqual(drawn.map(t=>Math.round(t*44100)),
  [0,735,2205,2940]);
 assert.equal(win.HHSAudioViz.diagnostics.visualFramesSkipped,1);
 assert.equal(win.HHSAudioViz.diagnostics.audioFrame,4);
 assert.equal(win.HHSAudioViz.diagnostics.clockSource,"output-timestamp");
 assert.ok(nodes.audioVizClock.textContent.includes("735 samples"));
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
    run=subprocess.run([node,"-e",program],text=True,capture_output=True)
    assert run.returncode==0,run.stderr
