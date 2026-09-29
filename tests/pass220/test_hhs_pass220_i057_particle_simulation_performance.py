from pathlib import Path

HTML = Path("examples/ParticleSimulation.html")


def test_i057_targets_canonical_monolith_and_preserves_authority_surfaces():
    source = HTML.read_text(encoding="utf-8")

    for token in (
        "<title>Holofractal Hybrid QPU & Neural Swarm — HHS VM81 / I041</title>",
        'schema:"HHS_PASS_220_I057_PARTICLE_SIMULATION_ZERO_LOSS_PERF_V1"',
        'source:"examples/ParticleSimulation.html"',
        "const particleCount = 2592;",
        "const LAYER_SPLIT=CORE_N+8*EXC_N;",
        "const BOND_CAP=9600;",
        "function updateSwarmCoupling()",
        "function constructorScan()",
        "function virtualDecay(forceIdx)",
        "function hnanGate(a,b)",
        'MODULES["Pass219GlobalConservation166Test"]',
        'MODULES["QuadraticReciprocityTensorTest"]',
        'MODULES["FractalLayer2Test"]',
        "simulationLogicRemoved:false",
        "receiptLogicRemoved:false",
        "canonicalMutationAuthority:false",
    ):
        assert token in source, token


def test_i057_preserves_every_physics_substep_and_quartic_projection_gate():
    source = HTML.read_text(encoding="utf-8")

    assert (
        "for(let s=0;s<steps;s++){ updateSpiralParticles(); "
        "time += simParams.evolutionSpeed * simParams.timeDilationFactor; }"
    ) in source
    assert "renderGate=((renderTick%4)===0);" in source
    assert "syncParticleRenderBatches();" in source
    assert "renderer.render(scene, camera);" in source

    # Presentation serialization moved under the existing render gate, but the
    # direct get_state command remains fresh-on-demand.
    assert "state JSON is a presentation surface; get_state remains fresh on demand" in source
    assert 'jsonCommand.command === "get_state"' in source
    assert "compressedHash: computeManifoldHash()" in source


def test_i057_instanced_projection_keeps_logical_particle_meshes():
    source = HTML.read_text(encoding="utf-8")

    for token in (
        "const particleRenderBatches=[];",
        "new THREE.InstancedMesh(",
        "registerParticleRenderBatch(group,points,particleGeometry);",
        "for(let i=0;i<points.length;i++) points[i].visible=false;",
        "mesh.setMatrixAt(i,particleBatchMatrix);",
        "mesh.setColorAt(i,p.material.color);",
        "mesh.instanceMatrix.needsUpdate=true;",
        "mesh.instanceColor.needsUpdate=true;",
        'powerPreference:"high-performance"',
    ):
        assert token in source, token

    # Simulation and receipts still address the original logical particle array.
    assert "particles.push(particle);" in source
    assert "const P=particles[i];" in source
    assert "particles[i].getWorldPosition(w);" in source


def test_i057_bond_csr_preserves_original_incident_k_order():
    source = HTML.read_text(encoding="utf-8")

    for token in (
        "const bondAdjStart=new Int32Array(BOND_PARTICLE_N+1);",
        "const bondAdjIndex=new Int32Array(BOND_CAP*2);",
        "for(let k=0;k<bondN;k++){",
        "bondAdjIndex[bondAdjCursor[bi]++]=k;",
        "bondAdjIndex[bondAdjCursor[bj]++]=k;",
        "for(let ai=bondAdjStart[i], ae=bondAdjStart[i+1]; ai<ae; ai++){",
        "const k=bondAdjIndex[ai];",
    ):
        assert token in source, token

    # The former N*bondN membership scan is gone from the spring hot path.
    assert (
        "let j=-1; if(bondI[k]===i) j=bondJ[k]; "
        "else if(bondJ[k]===i) j=bondI[k];"
    ) not in source

    bonds = [(0, 2), (1, 3), (0, 1), (2, 3), (0, 3)]
    n = 4

    legacy = [
        [k for k, (a, b) in enumerate(bonds) if a == i or b == i]
        for i in range(n)
    ]

    counts = [0] * (n + 1)
    for a, b in bonds:
        counts[a + 1] += 1
        counts[b + 1] += 1
    for i in range(1, n + 1):
        counts[i] += counts[i - 1]

    cursor = counts[:-1].copy()
    index = [None] * (2 * len(bonds))
    for k, (a, b) in enumerate(bonds):
        index[cursor[a]] = k
        cursor[a] += 1
        index[cursor[b]] = k
        cursor[b] += 1

    csr = [index[counts[i] : counts[i + 1]] for i in range(n)]
    assert csr == legacy


def _legacy_triplet_encode(text: str) -> str:
    bits = "".join(f"{ord(ch):08b}" for ch in text)
    table = {
        "000": "0", "001": "1", "010": "2", "011": "3",
        "100": "4", "101": "5", "110": "6", "111": "7",
    }
    return "".join(table.get(bits[i : i + 3], "") for i in range(0, len(bits), 3))


def _stream_triplet_encode(text: str) -> str:
    out = []
    bits = 0
    bit_count = 0
    for ch in text:
        code = ord(ch)
        for bit in range(7, -1, -1):
            bits = (bits << 1) | ((code >> bit) & 1)
            bit_count += 1
            if bit_count == 3:
                out.append(str(bits))
                bits = 0
                bit_count = 0
    return "".join(out)


def test_i057_streaming_manifold_encoder_matches_legacy_triplet_encoding():
    source = HTML.read_text(encoding="utf-8")
    assert "without materializing concatStr + binaryStr" in source
    assert 'return out.join("");' in source

    fixtures = (
        "0_0_0",
        "1.2_-2.5_10",
        "-0.1_99.9_-12.3" * 137,
        "_".join(str(i / 10) for i in range(-100, 101)),
    )
    for text in fixtures:
        assert _stream_triplet_encode(text) == _legacy_triplet_encode(text)


def test_i057_tesseract_reuses_projection_scratch():
    source = HTML.read_text(encoding="utf-8")

    assert "projected:new Float64Array(verts.length*3)" in source
    assert "const {posArr,edges,verts,projected}=tessGeo;" in source
    assert ".setUsage(THREE.DynamicDrawUsage)" in source
    assert "const pr=verts.map(v=>" not in source
