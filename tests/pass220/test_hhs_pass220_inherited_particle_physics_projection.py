"""Check that particle physics metadata is observed, not synthesized from layout."""
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "examples" / "ParticleSimulationAudioBridge.js"


def test_inherited_physical_metadata_projection():
    source = SOURCE.read_text(encoding="utf-8")
    assert "particlePhysicalProjection(p)" in source
    assert "chargeFromAddress:false" in source
    assert "normalizedKineticEnergy" in source
    assert "const physical=particlePhysicalProjection(p);" in source
    assert "particlePhysicalProjection,peakEnvelope" in source
    match = re.search(
        r"(  function particlePhysicalProjection\(p\)\{[\s\S]*?\n  \})\n  function projectColor",
        source,
    )
    assert match, "physics projection must remain inside the live color module"
    node = shutil.which("node")
    assert node, "Node required for executable projection regression"
    script = r"""
const assert=require('node:assert/strict');
const state={particleIndex:new WeakMap()};
""" + match.group(1) + r"""
const a={position:{x:1,y:2,z:3},userData:{}};
const b={position:{x:4,y:5,z:6},userData:{
  hhsPhysicalState:{charge:-2,mass:4,normalizedKineticEnergy:3}}};
state.particleIndex.set(a,0);
state.particleIndex.set(b,5184);
const pa=particlePhysicalProjection(a),pb=particlePhysicalProjection(b);
assert.equal(pa.charge,null);
assert.equal(pa.mass,null);
assert.equal(pa.source,'unavailable');
assert.equal(pb.charge,-2);
assert.equal(pb.mass,4);
assert.equal(pb.kineticEnergy,3);
assert.equal(pb.reciprocalIndex,0);
assert.equal(pb.physicsMutation,false);
assert.equal(pb.chargeFromAddress,false);
assert.equal(particlePhysicalProjection({userData:{}}),null);
assert.equal(pa.position[0],1);
assert.equal(pb.position[0],4);
"""
    subprocess.run([node, "-e", script], cwd=ROOT, check=True, timeout=30)
