"""Regression tests: visible PCM-derived particle and illumination projection.

Tests operate on the full canonical 10,368-particle HTML and its mirrored
bridge. No test supplies canonical physics or receipt mutation authority.
"""
from pathlib import Path
import shutil
import subprocess
import re
import pytest

HTML=Path("examples/ParticleSimulation.html")
BRIDGE=Path("examples/ParticleSimulationAudioBridge.js")

def test_visual_projection_is_reachable_in_canonical_renderer():
    html=HTML.read_text(encoding="utf-8")
    bridge=BRIDGE.read_text(encoding="utf-8")
    embedded=re.search(r'<script id="hhsAudioInline">\s*([\s\S]*?)\s*</script>',html)
    assert embedded and embedded.group(1).strip()==bridge.strip()
    for token in (
        "const particleAudioColor=new THREE.Color();",
        "audioVisual.projectMatrix(p,particleBatchMatrix);",
        "audioVisual.projectColor(p,particleAudioColor);",
        "mesh.setColorAt(i,particleAudioColor);",
        "const audioVisualFrame=!!(window.HHSAudioViz &&",
        "window.HHSAudioViz.needsProjectionFrame());",
        "if(!renderGate && audioVisualFrame){",
        "syncParticleRenderBatches();",
        "renderer.render(scene,camera);",
        "renderGate=((renderTick%4)===0);",
        "compressedHash: computeManifoldHash()",
        "const particleCount = 2592;",
        "const LAYER_SPLIT=CORE_N+8*EXC_N;",
    ):
        assert token in html,token
    for token in (
        "function attachLiveStereo(context,source)",
        "function decodedWindow(player)",
        "function liveWindow()",
        "function prepareVisualFrame(clock)",
        "function projectColor(p,color)",
        "function needsProjectionFrame()",
        'state.frameSignalReady=decodedWindow(state.audio) ||',
        'state.renderSource="live-analyser";',
        'ctx.globalCompositeOperation="lighter";',
        'const x=W*(bus===0?.37:.63)',
        'state.frameCrossings=frameCrossingEvents',
    ):
        assert token in bridge,token
    assert "p.position." not in bridge
    assert 'source.connect(ctx.destination); // SPEAKER PATH' in bridge


def _node_run(script):
    node=shutil.which("node")
    if not node:
        pytest.skip("Node.js unavailable")
    run=subprocess.run([node,"-e",script],text=True,capture_output=True)
    assert run.returncode==0,run.stdout+"\n"+run.stderr


def test_visible_particles_and_scene_lighting_from_stereo_decoded_pcm():
    _node_run(r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const src=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const els={},stats={glow:[],draw:0,analyserCalls:0};let raf;
class El {
 constructor(id){this.id=id;this.style={};this.handlers={};this.src="";
  this.currentTime=.2;this.duration=1;this.paused=true;this.ended=false;}
 addEventListener(name,fn){this.handlers[name]=fn}
 setAttribute(name,v){this[name]=v}
 getAttribute(name){return this[name]||null}
 load(){}
 pause(){this.paused=true;this.handlers.pause?.()}
 play(){this.paused=false;this.handlers.play?.();this.handlers.playing?.();return Promise.resolve()}
 getContext(){return canvasCtx}
}
const canvasCtx={
 setTransform(){},clearRect(){stats.draw++},beginPath(){},moveTo(){},lineTo(){},stroke(){},
 fillRect(){},createRadialGradient(...p){stats.glow.push(p);return {addColorStop(){}}}
};
for(const id of ["audioVizPlayer","audioVizFile","audioVizPlay","audioVizStop",
 "audioVizGain","audioVizStatus","audioVizClock","audioVizGainValue"])
 els[id]=new El(id);
const L=new Float32Array(44100),R=new Float32Array(44100);
for(let i=0;i<L.length;i++){
 L[i]=Math.sin(2*Math.PI*110*i/44100)*.6;
 R[i]=Math.sin(2*Math.PI*220*i/44100)*.6;
}
class AudioCtx {
 constructor(){this.sampleRate=44100;this.currentTime=.2;this.state="suspended";
  this.destination={};this.audioWorklet={addModule:()=>new Promise(()=>{})}}
 createMediaElementSource(){return {connect(){}}}
 createChannelSplitter(){return {connect(){}}}
 createGain(){return {gain:{value:0},connect(){}}}
 createAnalyser(){return {fftSize:2048,getFloatTimeDomainData(x){
  stats.analyserCalls++;x.fill(0)}}}
 getOutputTimestamp(){return {contextTime:.2,performanceTime:1000}}
 resume(){this.state="running";return Promise.resolve()}
}
const win={
 AudioContext:AudioCtx,
 OfflineAudioContext:class {decodeAudioData(){return Promise.resolve({
  numberOfChannels:2,sampleRate:44100,duration:1,getChannelData(i){return i?R:L}
 })}},
 innerWidth:900,innerHeight:600,devicePixelRatio:1,
 performance:{now:()=>1000},addEventListener(){},requestAnimationFrame(fn){raf=fn}
};
const doc={readyState:"complete",getElementById:id=>els[id],
 createElement:name=>new El(name),body:{appendChild(){}}};
const URLMock={createObjectURL:()=>"blob:demo",revokeObjectURL(){}};
vm.runInNewContext(src,{
 window:win,document:doc,URL:URLMock,Blob:class{},
 AudioWorkletNode:class{},Float32Array,WeakMap,Array,Math,Number,Object,isFinite
});
(async()=>{
 els.audioVizFile.files=[{name:"stereo.wav",arrayBuffer:async()=>new ArrayBuffer(4)}];
 els.audioVizFile.handlers.change();
 for(let i=0;i<8;i++)await Promise.resolve();
 els.audioVizPlay.handlers.click();
 for(let i=0;i<4;i++)await Promise.resolve();
 const viz=win.HHSAudioViz;
 assert.ok(viz.needsProjectionFrame());
 assert.ok(!viz.needsProjectionFrame(),"must not repeat same audio frame");
 const pL={position:{x:10,y:4,z:2},material:{color:{r:.15,g:.3,b:.55}}};
 const pR={position:{x:10,y:4,z:2},material:{color:{r:.15,g:.3,b:.55}}};
 const list=Array.from({length:10368},()=>({}));
 list[0]=pL;list[5184]=pR;
 viz.bindParticles(list);
 const matrix=()=>({elements:[1,0,0,0,0,1,0,0,0,0,1,0,10,4,2,1]});
 const left=matrix(),right=matrix();
 const color=()=>({setRGB(r,g,b){this.r=r;this.g=g;this.b=b}});
 const a=color(),b=color();
 viz.projectMatrix(pL,left);
 viz.projectMatrix(pR,right);
 viz.projectColor(pL,a);
 viz.projectColor(pR,b);
 raf();
 assert.ok(left.elements[0]>1.1);
 assert.ok(right.elements[0]>1.1);
 assert.notEqual(left.elements[12],10);
 assert.notEqual(right.elements[12],10);
 assert.notEqual(a.r,b.r);
 assert.ok(stats.glow.some(args=>args[2]===0 &&
  args[0]>150 && args[0]<750),"glow must be in full scene");
 assert.ok(stats.glow.length>=2);
 assert.ok(viz.diagnostics.frameRmsL>.1);
 assert.ok(viz.diagnostics.frameRmsR>.1);
 assert.equal(viz.diagnostics.visualSource,"decoded");
 assert.equal(pL.position.x,10);
 assert.equal(pR.material.color.r,.15);
 els.audioVizStop.handlers.click();
 viz.projectColor(pL,a);
 assert.equal(a.r,.15);
 assert.equal(a.g,.3);
 assert.equal(a.b,.55);
})().catch(e=>{console.error(e);process.exitCode=1});
""")


def test_unsupported_offline_decode_still_drives_live_pcm_visuals():
    _node_run(r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const src=fs.readFileSync("examples/ParticleSimulationAudioBridge.js","utf8");
const els={};let raf,glow=0;
class El {
 constructor(id){this.id=id;this.style={};this.handlers={};this.src="";
  this.currentTime=.5;this.duration=1;this.paused=true;this.ended=false;}
 addEventListener(name,fn){this.handlers[name]=fn}
 setAttribute(name,v){this[name]=v}
 getAttribute(name){return this[name]||null}
 load(){}
 pause(){this.paused=true;this.handlers.pause?.()}
 play(){this.paused=false;this.handlers.play?.();this.handlers.playing?.();return Promise.resolve()}
 getContext(){return canvas}
}
const canvas={setTransform(){},clearRect(){},beginPath(){},moveTo(){},
 lineTo(){},stroke(){},fillRect(){},createRadialGradient(){
 glow++;return {addColorStop(){}}}};
for(const id of ["audioVizPlayer","audioVizFile","audioVizPlay","audioVizStop",
 "audioVizGain","audioVizStatus","audioVizClock","audioVizGainValue"])
 els[id]=new El(id);
class AudioCtx{
 constructor(){this.sampleRate=48000;this.currentTime=.5;this.state="suspended";
 this.destination={};this.analyserNumber=0;
 this.audioWorklet={addModule:()=>new Promise(()=>{})}}
 createMediaElementSource(){return {connect(){}}}
 createChannelSplitter(){return {connect(){}}}
 createGain(){return {gain:{value:0},connect(){}}}
 createAnalyser(){
  const bus=this.analyserNumber++;
  return {fftSize:2048,getFloatTimeDomainData(d){
   for(let i=0;i<d.length;i++)
    d[i]=.72*Math.sin(2*Math.PI*(bus?19:11)*i/2048)}}}
 getOutputTimestamp(){return {contextTime:.5,performanceTime:1000}}
 resume(){this.state="running";return Promise.resolve()}
}
const win={
 AudioContext:AudioCtx,
 OfflineAudioContext:class{
  decodeAudioData(){return Promise.reject(new Error("offline decode unsupported"))}},
 innerWidth:1000,innerHeight:700,devicePixelRatio:1,
 performance:{now:()=>1000},addEventListener(){},requestAnimationFrame(fn){raf=fn}
};
const doc={readyState:"complete",getElementById:id=>els[id],
 createElement:name=>new El(name),body:{appendChild(){}}};
const URLMock={createObjectURL:()=>"blob:demo",revokeObjectURL(){}};
vm.runInNewContext(src,{window:win,document:doc,URL:URLMock,
 Blob:class{},AudioWorkletNode:class{},Float32Array,WeakMap,
 Array,Math,Number,Object,isFinite});
(async()=>{
 els.audioVizFile.files=[{name:"stream.m4a",arrayBuffer:async()=>new ArrayBuffer(4)}];
 els.audioVizFile.handlers.change();
 for(let i=0;i<7;i++)await Promise.resolve();
 els.audioVizPlay.handlers.click();
 for(let i=0;i<7;i++)await Promise.resolve();
 const viz=win.HHSAudioViz;
 assert.ok(viz.needsProjectionFrame());
 raf();
 assert.equal(viz.diagnostics.visualSource,"live-analyser");
 assert.ok(viz.diagnostics.liveFrameCount>0);
 assert.ok(viz.diagnostics.frameRmsL>.1);
 assert.ok(viz.diagnostics.frameRmsR>.1);
 assert.ok(glow>2);
 assert.equal(els.audioVizPlayer.paused,false);
})().catch(e=>{console.error(e);process.exitCode=1});
""")
