from hhs_runtime.pass179.animation import LinearTrack, scene_at_frame
from hhs_runtime.pass179.golden import lattice_run_scene
from hhs_runtime.pass179.types import q16


def test_linear_animation_is_exact_reversible_by_frame_selection():
    base = lattice_run_scene()
    track = LinearTrack("player", 0, 10, dx_q16_per_frame=q16(2))
    f3 = scene_at_frame(base, [track], 3)
    f10 = scene_at_frame(base, [track], 10)
    f3_again = scene_at_frame(base, [track], 3)
    p0 = next(n for n in base.nodes if n.node_id == "player")
    p3 = next(n for n in f3.nodes if n.node_id == "player")
    p10 = next(n for n in f10.nodes if n.node_id == "player")
    assert p3.x_q16 == p0.x_q16 + q16(6)
    assert p10.x_q16 == p0.x_q16 + q16(20)
    assert f3 == f3_again
