"""Formation projection integration: live bond topology, phasor and physics boundary."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def test_coherent_formation_consumes_live_bonds_not_new_physics():
    s=(ROOT/"examples/ParticleSimulation.html").read_text(encoding="utf8")
    assert 'function deriveElectronicFormations(){' in s
    assert 'for(let k=0;k<bondN;k++)' in s
    assert 'const a=bondI[k],b=bondJ[k];' in s
    assert 'g.re+=m*Math.cos(phi);g.im+=m*Math.sin(phi);' in s
    assert 'g.magnitude=Math.hypot(g.re,g.im);' in s
    assert 'g.phase=Math.atan2(g.im,g.re);' in s
    assert 'if(formationView.groupSizes[p.userData.hhsGroupIndex]>1)' in s
    assert 'particleBatchMatrix.scale({x:0,y:0,z:0});' in s
    assert 'syncElectronicFormations();' in s
    assert 'renderer.domElement.addEventListener("click",e=>' in s
    assert 'pointer-events:none;z-index:3' in s
    assert 'physicsMutation:false' in s
    assert 'thChg[i]=1-2*(thPh4[i]&1)' in s
    assert 'const muLocal=mu*(1+FLD.gradG*(nbCount[i]/20));' in s

def test_gravity_thermal_field_is_distinct_from_ionic_spherical_formation():
    s=(ROOT/"examples/ParticleSimulation.html").read_text(encoding="utf8")
    assert 'g.thermal+=velocity.x*velocity.x+velocity.y*velocity.y+velocity.z*velocity.z;' in s
    assert 'const heading=Math.atan2(vy,vx);' in s
    assert '/* Existing velocity and orbital motion supply the diffuse field;' in s
    assert 'if(g.members.length<2)continue; // original instances draw unbonded bodies' in s
    assert s.index('const field=ctx.createRadialGradient') < s.index('const coherent=g.magnitude')
    assert 'const muLocal=mu*(1+FLD.gradG*(nbCount[i]/20));' in s

def test_light_projection_shares_quartic_particle_frame_gate():
    s=(ROOT/"examples/ParticleSimulation.html").read_text(encoding="utf8")
    assert 'if(renderGate){\n        deriveElectronicFormations();' in s
    assert 'if(!renderGate && audioVisualFrame)' not in s
    assert 'const opacity=0.055+0.15*coherent;' in s
    assert 'Math.min(0.28,opacity+0.06)' in s
    assert '0.008+0.025*thermal' in s
    assert 'ctx.globalCompositeOperation="source-over";' in s
