import time

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import AuditedRunner
from hhs_runtime.core_sandbox.hhs_state_layer_v1 import HHSStateLayerV1
from hhs_runtime.core_sandbox.hhs_physics_model_v1 import PhysicalObservation, map_observation_to_symbolic, build_state_patch
from hhs_runtime.core_sandbox.hhs_database_integration_layer_v1 import HHSDatabase


def test_runner_basic_math():
    r = AuditedRunner()
    out = r.execute("ADD", 2, 3)
    assert out["ok"] is True
    assert "receipt" in out


def test_state_set_and_replay():
    s = HHSStateLayerV1()
    r1 = s.set("a.b", 5)
    assert r1["ok"] is True
    replay = s.replay_from_history()
    assert replay["ok"] is True


def test_physics_to_state():
    obs = PhysicalObservation("sensor1", 3.5, time.time())
    symbolic = map_observation_to_symbolic(obs)
    patch = build_state_patch(symbolic)
    assert patch["op"] == "SET"


def test_database_roundtrip(tmp_path):
    db = HHSDatabase(tmp_path / "test.json")
    data = {"x": 1}
    db.save(data)
    loaded = db.load()
    assert loaded == data
