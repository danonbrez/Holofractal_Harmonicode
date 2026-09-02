from hhs_runtime.pass179.backends import project_backend
from hhs_runtime.pass179.golden import lattice_run_scene
from hhs_runtime.pass179.runtime import command_stream


def test_all_browser_backends_are_projection_only_and_rebuildable():
    stream = command_stream(lattice_run_scene())
    packets = [project_backend(stream, name) for name in ("WEBGPU", "WEBGL2", "THREEJS")]
    assert {p["backend"] for p in packets} == {"WEBGPU", "WEBGL2", "THREEJS"}
    for packet in packets:
        assert packet["projection_only"] is True
        assert packet["renderer_feedback_authority"] is False
        assert packet["canonical_mutation_authority"] is False
        assert packet["hash72_commit_authority"] is False
        assert packet["context_loss_rebuild_source"] == "ADMITTED_COMMAND_STREAM"
