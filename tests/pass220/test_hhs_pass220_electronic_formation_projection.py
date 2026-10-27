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
    assert 'formationView.canvas=true; /* pointer handlers only, no screen overlay */' in s
    assert 'physicsMutation:false' in s
    assert 'thChg[i]=1-2*(thPh4[i]&1)' in s
    assert 'const muLocal=mu*(1+FLD.gradG*(nbCount[i]/20));' in s

def test_formation_backlight_is_local_3d_and_depth_tested():
    s=(ROOT/"examples/ParticleSimulation.html").read_text(encoding="utf8")
    assert 'new THREE.SphereGeometry(1,16,12)' in s
    assert 'side:THREE.BackSide,blending:THREE.NormalBlending' in s
    assert 'transparent:true,depthTest:true,depthWrite:false' in s
    assert 'light.shell.position.set(g.x,g.y,g.z);' in s
    assert 'light.shell.scale.setScalar(r*1.8);' in s
    assert 'const coherent=g.magnitude/Math.max(g.weight,1);' in s
    assert 'ctx.createRadialGradient' not in s[s.index('function syncElectronicFormations()'):s.index('window.HHSElectronicFormations=')]
    assert 'hhsCoherentFormationOverlay' not in s
    assert 'const muLocal=mu*(1+FLD.gradG*(nbCount[i]/20));' in s

def test_light_projection_shares_particle_frame_gate():
    s=(ROOT/"examples/ParticleSimulation.html").read_text(encoding="utf8")
    assert 'if(renderGate){\\n        deriveElectronicFormations();' in s
    assert 'if(!renderGate && audioVisualFrame)' not in s
    assert 'light.shell.material.uniforms.uOpacity.value=0.035+0.09*coherent;' in s
    assert 'syncElectronicFormations();\\n        renderer.render(scene, camera);' in s

def test_adaptive_projection_skips_light_not_particle_physics():
    s=(ROOT/"examples/ParticleSimulation.html").read_text(encoding="utf8")
    assert 'const PROJECTION_BUDGET_MS=6,PROJECTION_MAX_SKIP=8;' in s
    assert 'const PHYSICS_TICK_MS=1000/60,MAX_PHYSICS_CATCHUP=4;' in s
    assert 'while(physicsDebtMs>=PHYSICS_TICK_MS&&advanced<MAX_PHYSICS_CATCHUP)' in s
    assert 'const physicsBehind=physicsDebtMs>=PHYSICS_TICK_MS;' in s
    assert 'const projectionDue=!physicsBehind && renderGate &&' in s
    assert 'projectionLastCostMs=performance.now()-projectionStart;' in s
    physics=s.index('function advanceExistingPhysicsTick(){')
    gated=s.index('const projectionDue=',physics)
    assert 'updateSpiralParticles();' in s[physics:gated]
    assert 'updatePhaseGeometry();' in s[physics:gated]
    assert 'collideBondMembranes();' in s[physics:gated]
    assert 'constructorScan();' in s[physics:gated]

def test_pointer_registration_waits_for_renderer_initialization():
    s=(ROOT/"examples/ParticleSimulation.html").read_text(encoding="utf8")
    formation=s.index("const formationView=")
    startup=s.index("const formationShellGeometry=",formation)
    assert "ensureFormationCanvas();" not in s[formation:startup]
    sync=s.index("function syncElectronicFormations()",startup)
    assert "ensureFormationCanvas();" in s[sync:sync+100]
