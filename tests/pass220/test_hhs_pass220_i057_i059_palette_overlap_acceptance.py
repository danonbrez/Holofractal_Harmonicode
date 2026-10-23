"""Dependency-scoped regression for palette purity and radius-aware overlap."""
from pathlib import Path
import re
import subprocess

HTML = Path(__file__).resolve().parents[2] / "examples" / "ParticleSimulation.html"


def source():
    return HTML.read_text(encoding="utf-8")


def test_theme_refresh_does_not_invoke_audio_wrapped_render_batch():
    html = source()
    handler = re.search(r'get\("membraneTheme"\)\.addEventListener\("change",e=>\{(.*?)\n  \}\);', html, re.S)
    assert handler, "missing theme-change handler"
    assert "syncParticleRenderBatches(" not in handler.group(1)
    assert "window.HHSLiquidLight.sync()" in handler.group(1)


def test_overlap_search_preserves_radius_and_ordered_tie_break():
    html = source()
    body = html.split("function setOverlapRecords(){", 1)[1].split("\nfunction sync(){", 1)[0]
    for required in (
        "r.radius+maxRadius",
        "r.radius+p.radius",
        "ordered=fieldRecords.map",
        "d2===bestScore&&j>=bestIndex",
        'getAttribute("partnerSphere")',
        'getAttribute("partnerTint")',
        "needsUpdate=true",
    ):
        assert required in body


def test_overlap_search_executable_large_solid_and_ties():
    html = source()
    body = "function setOverlapRecords(){" + html.split("function setOverlapRecords(){", 1)[1].split("\nfunction sync(){", 1)[0]
    js = r"""
const assert=require("node:assert/strict");
const attr=(n)=>({array:new Float32Array(n),needsUpdate:false});
const mesh=()=>({geometry:{attrs:{partnerSphere:attr(16),partnerTint:attr(12)},getAttribute(k){return this.attrs[k];}}});
const particleField=mesh(),solidField=mesh();
const fieldRecords=[
 {mesh:particleField,index:0,x:0,y:0,z:0,radius:1.75,r:1,g:0,b:0},
 {mesh:solidField,index:0,x:13,y:0,z:0,radius:12,r:0,g:1,b:0},
 {mesh:particleField,index:1,x:2,y:0,z:0,radius:1.75,r:0,g:0,b:1},
 {mesh:particleField,index:2,x:-2,y:0,z:0,radius:1.75,r:0,g:1,b:1}
];
const fieldBuckets=new Map(),GRID=3.5;
""" + BODY + r"""
setOverlapRecords();
assert.equal(particleField.geometry.attrs.partnerSphere.array[0],2,
 "equal-distance tie must retain lower record index");
assert.equal(solidField.geometry.attrs.partnerSphere.array[0],0,
 "large solid must see the distant overlapping particle");
assert.equal(solidField.geometry.attrs.partnerSphere.array[3],1.75);
assert.equal(particleField.geometry.attrs.partnerSphere.needsUpdate,true);
"""
    result = subprocess.run(["node", "-e", js.replace("BODY", body)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
