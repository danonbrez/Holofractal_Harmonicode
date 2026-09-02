from hhs_runtime.pass179.golden import golden_scene_manifest, lattice_run_scene, motion_5184_scene


def test_golden_nuclei_preserve_inherited_shapes_without_false_terminal_claim():
    lattice = lattice_run_scene()
    motion = motion_5184_scene()
    manifest = golden_scene_manifest()
    assert lattice.width == 360 and lattice.height == 180
    assert len(motion.nodes) == 5184
    assert len({node.node_id for node in motion.nodes}) == 5184
    assert manifest["terminal_golden_scene_parity"] is False
