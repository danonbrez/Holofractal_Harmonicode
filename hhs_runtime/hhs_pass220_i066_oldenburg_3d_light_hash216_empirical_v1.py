"""Pass 220 I066: Oldenburg 3D-light empirical Hash216 fixture.

This module binds the published 2026 Physical Review Research experiment
"Multiphoton ionization with three-dimensional light fields" to the inherited
HHS empirical-correspondence and Hash216 hydration surfaces.

It deliberately separates:
  * externally published experimental facts;
  * HHS internal formal geometry;
  * candidate-only Hash72/Hash216 projection.

No unreported numeric laser parameters are invented. Chiral sensing is stored
only as a stated route/application direction, not as a result demonstrated by
the potassium experiment.

I066 grants no VM81 mutation, Hash72 commit, Hash216 persistence, GPU canonical
state, or floating-point canonical authority.
"""
from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    EXPANDED_VERTICES,
    FULL_HASH216_COMPONENTS,
    HASH216_PLANES,
    HASH72_POSITIONS,
    hydrate_hash216_geometry,
)

SCHEMA = "HHS_PASS_220_I066_OLDENBURG_3D_LIGHT_HASH216_EMPIRICAL_V1"
VERSION = "1.0.0"
BASE_MAIN = "b99c434f691e5ac69a94e2d971e8ac877b6e167a"

SOURCE = {
    "title": "Multiphoton ionization with three-dimensional light fields",
    "authors": (
        "D. Köhnke",
        "H.-C. Ahlswede",
        "T. Bayer",
        "M. Wollenhaupt",
    ),
    "institution": "Carl von Ossietzky Universität Oldenburg",
    "journal": "Physical Review Research",
    "volume": 8,
    "article": "033048",
    "publication_date": "2026-07-13",
    "doi": "10.1103/r36b-vw82",
    "publisher_url": "https://journals.aps.org/prresearch/abstract/10.1103/r36b-vw82",
}

LANE_ORDER = ("PREVIOUS", "CHANGE", "RECEIPT")
FIELD_AXES = ("x", "y", "z")
DIPOLE_DELTA_M = (-1, 0, 1)


class I066EmpiricalFixtureError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _hash72(label: str, value: Any) -> str:
    return hash72_digest(
        {"domain": SCHEMA, "version": VERSION, "label": label},
        _canonical(value),
    )


def source_record() -> dict[str, Any]:
    record = deepcopy(SOURCE)
    record.update({
        "source_class": "PEER_REVIEWED_EXPERIMENTAL_PUBLICATION",
        "research_method": "EXPERIMENTAL_STUDY",
        "empirical_source_only": True,
        "hhs_formal_authority": False,
        "canonical_mutation_authority": False,
    })
    return record


def field_geometry_record() -> dict[str, Any]:
    """Published field-construction facts, without invented waveform numbers."""
    return {
        "field_class": "BICHROMATIC_3D_POLARIZATION_SHAPED_ULTRASHORT_FIELD",
        "pulse_count": 2,
        "different_colors": True,
        "noncollinear_superposition": True,
        "polarization_shaped": True,
        "supercontinuum_polarization_pulse_shaper": True,
        "electric_field_components": FIELD_AXES,
        "spatial_component_count": len(FIELD_AXES),
        "all_spatial_directions": True,
        "target": "POTASSIUM_ATOMS",
        "interaction": "ATOMIC_MULTIPHOTON_IONIZATION",
        "numeric_wavelengths_claimed_by_i066": False,
        "numeric_pulse_duration_claimed_by_i066": False,
        "numeric_field_amplitudes_claimed_by_i066": False,
        "numeric_relative_phases_claimed_by_i066": False,
        "source_scope": "PUBLISHED_ABSTRACT_LEVEL_FACTS",
    }


def observation_record() -> dict[str, Any]:
    """Published demonstrated outcomes and explicit non-demonstrated scope."""
    return {
        "measurement": "VELOCITY_MAP_IMAGING",
        "observed_output": "PHOTOELECTRON_MOMENTUM_DISTRIBUTIONS",
        "electronic_state_result": (
            "PREVIOUSLY_INACCESSIBLE_FREE_ELECTRON_ANGULAR_MOMENTUM_WAVE_PACKETS"
        ),
        "dipole_selection_delta_m": DIPOLE_DELTA_M,
        "all_three_dipole_selection_rules_unlocked": True,
        "control_scope": "3D_ELECTRONIC_SUPERPOSITION_STATE_CONTROL",
        "pump_probe_application": (
            "MAP_SPIN_ORBIT_DYNAMICS_OF_POTASSIUM_3D_FINE_STRUCTURE_DOUBLET"
        ),
        "chiral_sensitive_light_matter_interactions": {
            "status": "ROUTE_OR_FUTURE_APPLICATION",
            "demonstrated_by_this_potassium_experiment": False,
        },
        "empirical_claims_do_not_establish_hhs_formal_validity": True,
        "hhs_formal_validity_does_not_substitute_for_empirical_evidence": True,
    }


def build_empirical_hash216_fixture() -> dict[str, Any]:
    """Build SOURCE -> FIELD -> OBSERVATION as PREVIOUS/CHANGE/RECEIPT."""
    source = source_record()
    field = field_geometry_record()
    observation = observation_record()

    if field["electric_field_components"] != FIELD_AXES:
        raise I066EmpiricalFixtureError("3D field axis order drift")
    if observation["dipole_selection_delta_m"] != DIPOLE_DELTA_M:
        raise I066EmpiricalFixtureError("dipole selection order drift")
    if observation["chiral_sensitive_light_matter_interactions"][
        "demonstrated_by_this_potassium_experiment"
    ]:
        raise I066EmpiricalFixtureError("chiral application overstated as demonstrated")

    previous_hash72 = _hash72("published-source", source)
    change_hash72 = _hash72("3d-field-construction", field)
    receipt_hash72 = _hash72("observed-transition-receipt", observation)
    lanes = (previous_hash72, change_hash72, receipt_hash72)
    if not all(validate_hash72(lane) for lane in lanes):
        raise I066EmpiricalFixtureError("fixture lane is not canonical Hash72")

    hash216 = "".join(lanes)
    hydrated = hydrate_hash216_geometry(hash216)
    if hydrated["roundtrip_exact"] is not True:
        raise I066EmpiricalFixtureError("I065 Hash216 hydration roundtrip failed")

    fixture = {
        "schema": SCHEMA,
        "version": VERSION,
        "base_main": BASE_MAIN,
        "source": source,
        "field_geometry": field,
        "observation": observation,
        "hash216_binding": {
            "lane_order": LANE_ORDER,
            "previous_role": "PUBLISHED_SOURCE_IDENTITY",
            "change_role": "3D_FIELD_CONSTRUCTION",
            "receipt_role": "OBSERVED_TRANSITION_SELECTION_AND_MEASUREMENT",
            "previous_hash72": previous_hash72,
            "change_hash72": change_hash72,
            "receipt_hash72": receipt_hash72,
            "hash216": hash216,
            "hash216_length": len(hash216),
            "vertex72_count": hydrated["three_dimensional_vertex_count"],
            "components_per_vertex": hydrated["components_per_vertex"],
            "fully_hydrated_attached_components": hydrated[
                "full_attached_components"
            ],
            "hydration_roundtrip_exact": hydrated["roundtrip_exact"],
        },
        "empirical_formal_separation": {
            "publication_is_external_empirical_evidence": True,
            "publication_is_hhs_proof": False,
            "hhs_theorem_is_empirical_measurement": False,
            "numeric_i061_calibration_satisfied_by_this_fixture_alone": False,
            "reason": (
                "I066 binds published categorical experimental facts; it does not "
                "invent numeric measured/predicted calibration records."
            ),
        },
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
        "gpu_canonical_state_authority": False,
        "floating_point_authority": False,
    }
    fixture["fixture_hash72"] = _hash72("complete-empirical-fixture", fixture)
    return fixture


def validate_empirical_hash216_fixture(
    fixture: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(fixture, Mapping):
        raise I066EmpiricalFixtureError("fixture must be a mapping")
    if fixture.get("schema") != SCHEMA:
        raise I066EmpiricalFixtureError("fixture schema mismatch")
    if fixture.get("base_main") != BASE_MAIN:
        raise I066EmpiricalFixtureError("fixture base-main lineage mismatch")

    expected = build_empirical_hash216_fixture()
    if dict(fixture) != expected:
        raise I066EmpiricalFixtureError(
            "fixture differs from source/field/observation canonical construction"
        )

    binding = fixture["hash216_binding"]
    if binding["hash216_length"] != 216:
        raise I066EmpiricalFixtureError("Hash216 width drift")
    if binding["vertex72_count"] != HASH72_POSITIONS:
        raise I066EmpiricalFixtureError("Hash216 72-vertex geometry drift")
    if binding["components_per_vertex"] != HASH216_PLANES:
        raise I066EmpiricalFixtureError("Hash216 plane count drift")
    if binding["fully_hydrated_attached_components"] != FULL_HASH216_COMPONENTS:
        raise I066EmpiricalFixtureError("Hash216 hydrated component count drift")
    if EXPANDED_VERTICES != 5184:
        raise I066EmpiricalFixtureError("inherited 5184 geometry drift")

    return {
        "schema": f"{SCHEMA}_VALIDATION",
        "ok": True,
        "fixture_hash72": fixture["fixture_hash72"],
        "hash216": binding["hash216"],
        "hydration_roundtrip_exact": binding["hydration_roundtrip_exact"],
        "empirical_formal_separation": True,
        "candidate_only": True,
    }


def lane5_empirical_projection_witness() -> dict[str, Any]:
    fixture = build_empirical_hash216_fixture()
    binding = fixture["hash216_binding"]
    return {
        "schema": f"{SCHEMA}_LANE5_PROJECTION_V1",
        "source_doi": SOURCE["doi"],
        "field_axes": FIELD_AXES,
        "field_dimension": len(FIELD_AXES),
        "dipole_delta_m": DIPOLE_DELTA_M,
        "selection_cardinality": len(DIPOLE_DELTA_M),
        "hash216_vertex_count": binding["vertex72_count"],
        "hash216_components_per_vertex": binding["components_per_vertex"],
        "fully_hydrated_attached_components": binding[
            "fully_hydrated_attached_components"
        ],
        "candidate_search_features": (
            "SOURCE_IDENTITY",
            "BICHROMATIC",
            "NONCOLLINEAR",
            "XYZ_FIELD_COMPONENTS",
            "POTASSIUM",
            "MULTIPHOTON_IONIZATION",
            "DELTA_M_MINUS1_0_PLUS1",
            "VELOCITY_MAP_IMAGING",
            "3D_FINE_STRUCTURE_SPIN_ORBIT",
        ),
        "chiral_sensing_class": "FUTURE_ROUTE_NOT_DEMONSTRATED_RESULT",
        "i061_numeric_calibration_substituted": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
        "gpu_canonical_state_authority": False,
    }


def i066_self_test() -> dict[str, Any]:
    fixture = build_empirical_hash216_fixture()
    validation = validate_empirical_hash216_fixture(fixture)
    lane5 = lane5_empirical_projection_witness()
    return {
        "schema": f"{SCHEMA}_SELF_TEST_V1",
        "ok": (
            validation["ok"]
            and validation["hydration_roundtrip_exact"]
            and lane5["field_dimension"] == 3
            and lane5["dipole_delta_m"] == DIPOLE_DELTA_M
            and lane5["selection_cardinality"] == 3
            and lane5["fully_hydrated_attached_components"] == 15552
            and lane5["i061_numeric_calibration_substituted"] is False
        ),
        "fixture_hash72": fixture["fixture_hash72"],
        "hash216": fixture["hash216_binding"]["hash216"],
    }


__all__ = [
    "BASE_MAIN",
    "DIPOLE_DELTA_M",
    "FIELD_AXES",
    "I066EmpiricalFixtureError",
    "SCHEMA",
    "SOURCE",
    "VERSION",
    "build_empirical_hash216_fixture",
    "field_geometry_record",
    "i066_self_test",
    "lane5_empirical_projection_witness",
    "observation_record",
    "source_record",
    "validate_empirical_hash216_fixture",
]
