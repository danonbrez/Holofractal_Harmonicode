"""Verify the existing particles gain unique reciprocal spinor properties."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def test_particle_group_properties_are_initialized_before_physics():
    source=(ROOT/"examples/ParticleSimulation.html").read_text(encoding="utf8")
    start=source.index("particle.userData.hhsGroupIndex=particles.length-1;")
    stop=source.index("points.push(particle);",start)
    mapping=source[start:stop]
    assert "const carrierLocal=carrierIndex%5184" in mapping
    assert "const carrierConstraint=Math.floor(carrierLocal/648)" in mapping
    assert "const carrierScale=Math.floor(carrierLocal/72)%9" in mapping
    assert "const carrierQuarter=(carrierConstraint%4)" in mapping
    assert "reciprocalIndex:(1-carrierPopulation)*5184+carrierLocal" in mapping
    assert "orderedCarrier:carrierPopulation?" in mapping
    assert "particle.userData.phase+=carrierQuarter*Math.PI/2+" in mapping
    assert "particle.userData.q144=(2*carrierPhase+18*carrierQuarter+" in mapping
    assert source.index("function initThermoState()")>stop
    assert "const muLocal=mu*(1+FLD.gradG*(nbCount[i]/20));" in source
    assert "thPh4[i]=p.userData.q144%4; thChg[i]=1-2*(thPh4[i]&1)" in source

def test_population_and_relationship_coordinates_are_bijective():
    identifiers=set()
    for i in range(10368):
        p,n=divmod(i,5184)
        constraint, remainder=divmod(n,648)
        scale,phase=divmod(remainder,72)
        assert 0<=constraint<8 and 0<=scale<9 and 0<=phase<72
        assert (1-p)*5184+n != i
        assert (1-(1-p))*5184+n==i
        identifiers.add((p,constraint,scale,phase))
    assert len(identifiers)==10368
