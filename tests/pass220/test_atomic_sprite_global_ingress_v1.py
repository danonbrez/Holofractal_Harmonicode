"""Pass 220 atomic/neural sprite direct ingress and negative corpus-admission tests."""
from fractions import Fraction as F
from pathlib import Path

import pytest

from hhs_runtime.pass220.atomic_sprite_whitepaper_gate_v1 import (
    CorpusConstraintError, corpus_snapshot,
)
from hhs_runtime.pass220.atomic_sprite_global_ingress_v1 import (
    REQUIRED, run_atomic_sprite_ingress,
)


VALUES = {
    "species_id": "Li", "atomic_number": 3, "mass_number": 7, "charge": 0,
    "electron_configuration": {"1s": 2, "2s": 1},
    "symbolic_fields": {"energy": "E_0"},
    "relative_atomic_mass_u": F(7, 1),
    "temperature_kelvin": F(300, 1),
    "internal_energy_joules": F(1, 1000),
    "material_phase": "UNRESOLVED",
    "ordered_phase": {
        "channel": "xy", "vm81_cell": 4, "operation64": 31,
        "parent_hash216": "0" * 216,
    },
    "gravity_controls": {"mu": F(16, 25), "soft": F(3, 5)},
    "ionic_controls": {"charge_gain": F(3, 50), "soft": F(1, 20)},
    "geometry": {"particle_id": 0, "local5184": 0, "bond_pairs": []},
    "neural_controls": {
        "thrust": F(0), "yaw": F(0), "pitch": F(0),
        "roll": F(0), "bond_request": False,
    },
    "tick": 143, "seed": "atomic-sprite-test", "P": 3, "m_pass": 6,
    "alpha": F(5, 4), "kappa": F(3, 4),
}


@pytest.fixture
def source(tmp_path):
    for name in ("whitepapers", "docs/whitepapers"):
        folder = tmp_path / name
        folder.mkdir()
        (folder / "proof.md").write_text("source identity\n", encoding="utf-8")
    return tmp_path


def _parameters():
    assert set(VALUES) == REQUIRED
    return {
        name: {
            "value": value, "kind": name.upper(),
            "status": "EXECUTED_EXACT",
            "role": "NATIVE_EXACT_CANDIDATE",
            "source_paths": ["whitepapers/proof.md", "docs/whitepapers/proof.md"],
            "constraint_id": "EXACT_COMPONENT_RUNTIME_CHECK_REQUIRED",
        } for name, value in VALUES.items()
    }


def _run(root, params):
    return run_atomic_sprite_ingress(
        root, params, expected_bundle_sha256=corpus_snapshot(root)["bundle_sha256"]
    )


def test_executes_real_inherited_physics_and_game_frame(source):
    candidate = _run(source, _parameters())
    assert candidate["status"] == "EXACT_COMPONENTS_VALIDATED_CANDIDATE_ONLY"
    assert candidate["source_bound_parameter_count"] == len(REQUIRED)
    assert len(candidate["component_witnesses"]["pass131_state_root_hash72"]) == 72
    assert len(candidate["component_witnesses"]["pass067_1_run_root_hash72"]) == 72
    assert candidate["component_witnesses"]["i058_validation"]["ok"] is True
    assert candidate["thermodynamic_material_state"]["material_phase"] == "UNRESOLVED"
    assert not candidate["thermodynamic_equation_of_state_validated"]
    assert not candidate["signed_vm81_admission_executed"]
    assert not candidate["browser_simulation_mutated"]
    assert candidate == _run(source, _parameters())


@pytest.mark.parametrize(("key", "value", "message"), [
    ("temperature_kelvin", F(-1), "RATIONAL_BOUND"),
    ("relative_atomic_mass_u", 0, "RATIONAL_BOUND"),
    ("atomic_number", F(3, 1), "REQUIRES_BIGINT"),
    ("material_phase", "xy", "INVALID_MATERIAL_PHASE"),
    ("ordered_phase", {**VALUES["ordered_phase"], "operation64": 64}, "VM81_ADDRESS"),
    ("ordered_phase", {**VALUES["ordered_phase"], "parent_hash216": "broken"}, "INVALID_INHERITED"),
    ("neural_controls", {**VALUES["neural_controls"], "thrust": F(2)}, "UNBOUNDED_ACTUATOR"),
    ("ionic_controls", {"charge_gain": F(-1)}, "RATIONAL_BOUND"),
    ("gravity_controls", {"mu": 0.5}, "FLOAT_CANONICAL"),
    ("neural_controls", {**VALUES["neural_controls"], "yaw": 0.25}, "FLOAT_CANONICAL"),
])
def test_atomic_neural_rejections(source, key, value, message):
    params = _parameters()
    params[key]["value"] = value
    with pytest.raises(CorpusConstraintError, match=message):
        _run(source, params)


def test_missing_or_undeclared_field_rejected(source):
    params = _parameters()
    del params["temperature_kelvin"]
    with pytest.raises(CorpusConstraintError, match="INCOMPLETE_OR_UNDECLARED"):
        _run(source, params)
    params = _parameters()
    params["unsourced"] = params["temperature_kelvin"]
    with pytest.raises(CorpusConstraintError, match="INCOMPLETE_OR_UNDECLARED"):
        _run(source, params)


def test_reference_only_cannot_drive_ionic_physics(source):
    params = _parameters()
    params["ionic_controls"]["status"] = "REFERENCE_ONLY"
    with pytest.raises(CorpusConstraintError, match="NONEXECUTABLE_SOURCE_AS_AUTHORITY"):
        _run(source, params)


def test_projection_only_cannot_drive_physics(source):
    params = _parameters()
    params["gravity_controls"]["role"] = "PROJECTION_ONLY"
    with pytest.raises(CorpusConstraintError, match="PROJECTION_PARAM_USED_AS_PHYSICS"):
        _run(source, params)


def test_atomic_accounting_cannot_be_bypassed(source):
    params = _parameters()
    params["electron_configuration"]["value"] = {"1s": 2}
    from hhs_runtime.hhs_pass131_electrochemical_atomic_physics_sandbox_v1 import Pass131Error
    with pytest.raises(Pass131Error, match="REJECT_INVALID_ORBITAL_OCCUPANCY"):
        _run(source, params)


def test_stale_corpus_snapshot_rejected_before_physics(source):
    params = _parameters()
    before = corpus_snapshot(source)["bundle_sha256"]
    (source / "whitepapers/proof.md").write_text("modified\n")
    with pytest.raises(CorpusConstraintError, match="STALE_OR_UNBOUND"):
        run_atomic_sprite_ingress(source, params, expected_bundle_sha256=before)
