"""I090 optional RGB cluster candidate: frozen default and exact ingress guards."""
from pathlib import Path
import re

SRC=Path(__file__).resolve().parents[2] / "examples" / "ParticleSimulation.html"

def test_rgb_cluster_opt_in_and_original_path():
    s=SRC.read_text()
    for x in (
        'rgbClusterOn: false', 'rgbClusterStrength: 0.05',
        'rgbClusterColors: false', 'id="rgbClusterEnable"',
        'id="rgbClusterStrength"', 'id="rgbClusterColors"',
        'rgbActive=simParams.rgbClusterOn && simParams.rgbClusterStrength>0',
        'if(rgbActive){', 'if(renderGate){',
        'updateSwarmCoupling();', 'const shrD=1+shared;',
        'const gD=hnanGate(1,shrD);',
        'MODULES["RGBParticlePartitionTest"]',
        'hash72_append_performed:false','canonical_mutation_authority:false',
        '"#ifdef USE_INSTANCING_COLOR",', '"vTint=vec3(1.0);",'
    ):
        assert x in s, x

def test_exact_matrix_and_kernel_identity():
    s=SRC.read_text()
    match=re.search(r'matrix:\[\[8,4,4,0\],\[4,14,9,19\],\[4,9,13,18\],\[4,15,14,25\]\]',s)
    assert match
    m=[[8,4,4,0],[4,14,9,19],[4,9,13,18],[4,15,14,25]]
    v=[1,-1,-1,1]
    assert [sum(x*y for x,y in zip(row,v)) for row in m] == [0]*4
    assert 10368//72==144 and 10368//81==128
    assert 4*2592==2*5184==10368
