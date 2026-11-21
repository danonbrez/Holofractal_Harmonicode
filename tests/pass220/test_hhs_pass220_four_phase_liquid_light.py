"""Pass 220 four-phase PCM-driven liquid-light projection regression."""
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "examples/ParticleSimulationAudioBridge.js"
HTML = ROOT / "examples/ParticleSimulation.html"


def test_inline_bridge_parity():
    bridge = BRIDGE.read_text(encoding="utf-8").strip()
    html = HTML.read_text(encoding="utf-8")
    inline = re.search(r'<script id="hhsAudioInline">\s*([\s\S]*?)\s*</script>', html)
    assert inline, "Standalone HTML must contain the inline PCM bridge"
    assert inline.group(1).strip() == bridge


def test_four_tick_projection_packet():
    assert shutil.which("node"), "Node.js required for executable JS regression"
    script = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const window = {};
const document = {readyState:'loading',addEventListener(){}};
vm.runInNewContext(fs.readFileSync('examples/ParticleSimulationAudioBridge.js','utf8'),
                   {window,document,Float32Array,Uint8Array,WeakMap,Math,Number,
                    Object,Array,NaN,console});
const v = window.HHSAudioViz;
assert.equal(v.interlaceContract.period,4);
assert.equal(v.interlaceContract.canonicalMutationAuthority,false);
const packets = Array.from({length:9},(_,t)=>v.fourPhasePresentationPacket(t));
assert.deepEqual(packets.slice(0,4).map(p=>p.rotationPhase72),[0,18,36,54]);
assert.deepEqual(packets.slice(0,4).map(p=>p.topology),
                 ['concave','convex','concave','convex']);
assert.deepEqual(packets.slice(0,4).map(p=>p.colorPolarity),[1,-1,1,-1]);
assert.deepEqual(packets.slice(0,4).map(p=>p.depthSign),[-1,1,-1,1]);
assert.deepEqual(packets.slice(0,4).map(p=>p.horizontalInversion),
                 [false,true,false,true]);
assert.deepEqual(packets.slice(0,4).map(p=>p.verticalInversion),
                 [false,false,true,true]);
for(let t=0;t<5;t++){
  const a=packets[t],b=packets[t+4];
  for(const field of ['phase','rotationPhase72','topology','colorPolarity',
                       'depthSign','backlightReveal'])
    assert.equal(a[field],b[field],field);
}
assert.equal(v.fourPhasePresentationPacket(-1),null);
assert.equal(v.fourPhasePresentationPacket(1.5),null);
assert.equal(v.fourPhasePresentationPacket(Number.MAX_SAFE_INTEGER+1),null);
assert.equal(v.fourPhasePresentationPacket(0).source,'PCM_44100_FRAME_735');
assert.equal(v.audioClock.samplesPerFrame,735);
assert.equal(v.audioClock.canonicalRate,44100);
assert.equal(v.diagnostics.canonicalMutation,false);
assert.equal(v.diagnostics.fourPhaseInterlacing,true);
"""
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True, timeout=30)
