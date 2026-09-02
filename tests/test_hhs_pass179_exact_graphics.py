from fractions import Fraction

import pytest

from hhs_runtime.pass163.vmrc import VMRCRuntime
from hhs_runtime.pass179.runtime import GraphicsAuthority, scene_from_payload
from hhs_runtime.pass179.types import ExactGraphicsValueError, q16


def sample_scene():
    return scene_from_payload({
        "scene_id": "test:scene",
        "width": 32,
        "height": 24,
        "background": [0, 0, 0, 65535],
        "nodes": [
            {"node_id": "a", "kind": "RECT", "x": 2, "y": 3, "w": 8, "h": 4, "rgba16": [65535, 0, 0, 65535], "layer": 1},
            {"node_id": "b", "kind": "POINT", "x": 5, "y": 6, "w": 1, "h": 1, "rgba16": [0, 65535, 0, 65535], "layer": 2},
        ],
    })


def test_q16_requires_exact_representability_and_rejects_float():
    assert q16(2) == 131072
    assert q16(Fraction(1, 2)) == 32768
    with pytest.raises(ExactGraphicsValueError):
        q16(Fraction(1, 3))
    with pytest.raises(ExactGraphicsValueError):
        scene_from_payload({"scene_id": "float", "width": 8, "height": 8, "nodes": [{"x": 1.5}]})


def test_scene_commit_requires_vm81_and_preserves_singleton_boundary():
    missing = GraphicsAuthority(vm81=None)
    with pytest.raises(Exception, match="VM81_ADMISSION_AUTHORITY_REQUIRED"):
        missing.commit_scene(sample_scene())

    vm81 = VMRCRuntime()
    authority = GraphicsAuthority(vm81=vm81)
    before = vm81.epoch
    record = authority.commit_scene(sample_scene())
    assert vm81.epoch == before + 1
    assert record["vm81_admission"]["classification"] == "HHS_PASS179_VM81_SCENE_ADMISSION_VERIFIED"
    assert record["vm81_admission"]["singleton_authority"] is True
    assert record["vm81_admission"]["independent_vm81_authority"] is False
    assert record["vm81_admission"]["validation_mutation_authority"] is False
    assert len(record["post_vm81_hash72_evidence"]) == 72
    assert len(record["scene_hash216"]) == 216
    assert record["hash72_commit_authority"] is False
    assert record["hash216_mutation_authority"] is False


def test_scene_replay_is_exact():
    authority = GraphicsAuthority(vm81=VMRCRuntime())
    record = authority.commit_scene(sample_scene())
    replay = authority.replay_scene("test:scene", record["scene_hash216"])
    assert replay["deterministic_replay"] is True
    assert authority.replay_scene("test:scene", "x" * 216)["deterministic_replay"] is False
