from pathlib import Path

from hhs_runtime.pass163.vmrc import VMRCRuntime
from hhs_runtime.pass179.capture import capture_scene_png
from hhs_runtime.pass179.golden import lattice_run_scene
from hhs_runtime.pass179.runtime import GraphicsAuthority


def test_capture_derives_from_admitted_frame_stream(tmp_path: Path):
    authority = GraphicsAuthority(vm81=VMRCRuntime())
    scene = lattice_run_scene()
    authority.commit_scene(scene)
    first = capture_scene_png(authority, scene.scene_id, tmp_path / "a.png")
    second = capture_scene_png(authority, scene.scene_id, tmp_path / "b.png")
    assert first["frame_sha256"] == second["frame_sha256"]
    assert first["png_sha256"] == second["png_sha256"]
    assert first["capture_mutation_authority"] is False
    assert (tmp_path / "a.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
