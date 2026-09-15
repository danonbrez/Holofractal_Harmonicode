from __future__ import annotations

from pathlib import Path
import subprocess

from hhs_backend.runtime.hhs_pass214_python_operation_registry_v1 import (
    extract_python_operation_registry_keys,
)
from hhs_backend.runtime.hhs_pass219_lane5_executable_capability_self_model_1_43 import (
    CANONICAL_BOUNDARY_EXPORT,
    Pass219Lane5ExecutableCapabilitySelfModel,
)
from hhs_backend.runtime.hhs_pass219_lane5_repository_capability_reverse_discovery_1_44 import (
    Pass219Lane5RepositoryCapabilityReverseDiscovery,
)
from hhs_python.runtime.hhs_pass219_lane5_repository_capability_reverse_discovery_bridge import (
    AUTH_CANONICAL_ADMISSION_BOUNDARY,
    AUTH_OBSERVATION,
    SOURCE_PYTHON_OPERATION_REGISTRY,
)


def test_live_repository_reverse_discovery_adds_structural_python_registry_surface() -> None:
    model = Pass219Lane5RepositoryCapabilityReverseDiscovery().build()

    assert model["counts"]["public_registry"] > 0
    assert model["counts"]["native_exact_abi"] > 0
    assert model["counts"]["python_operation_registry"] > 0
    assert model["counts"]["total"] == len(model["nodes"])
    assert model["counts"]["canonical_boundaries"] == 1
    assert model["scope"]["pass147_public_registry_complete"] is True
    assert model["scope"]["cumulative_exact_abi_complete"] is True
    assert model["scope"]["pass214_structural_python_operation_registry_complete"] is True
    assert model["scope"]["repository_total_historical_capability_complete"] is False
    assert model["python_registry_manifest"]["python_registry_parse_errors"] == []
    assert model["python_registry_manifest"]["policy"] == (
        "STRUCTURAL_KEYS_ONLY_STRICT_OPERATION_REGISTRY_NAMES"
    )

    python_nodes = [
        node
        for node in model["nodes"]
        if node["source_kind_code"] == SOURCE_PYTHON_OPERATION_REGISTRY
    ]
    assert len(python_nodes) == model["counts"]["python_operation_registry"]
    assert all(node["authority_class"] == AUTH_OBSERVATION for node in python_nodes)
    assert all(node["execution_authority"] == "DISCOVERY_ONLY_UNCLASSIFIED" for node in python_nodes)
    assert all(node["hash216_composition_eligible"] is False for node in python_nodes)
    assert all(node["superedge_promotion_eligible"] is False for node in python_nodes)

    boundary = [
        node
        for node in model["nodes"]
        if node["authority_class"] == AUTH_CANONICAL_ADMISSION_BOUNDARY
    ]
    assert len(boundary) == 1
    assert boundary[0]["export_name"] == CANONICAL_BOUNDARY_EXPORT

    receipt = model["native_receipt"]
    assert receipt["accepted"] is True
    assert receipt["total_entries"] == model["counts"]["total"]
    assert receipt["python_registry_entries"] == model["counts"]["python_operation_registry"]
    assert receipt["canonical_boundary_entries"] == 1
    assert receipt["candidate_only"] is True
    assert receipt["auto_hash216_composition_promotion"] is False
    assert receipt["auto_superedge_promotion"] is False
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_authority"] is False
    assert receipt["canonical_hash216_authority"] is False
    assert receipt["canonical_persistence_authority"] is False

    authority = model["authority"]
    assert authority["python_operation_registry_snapshot"] == 1
    assert authority["structural_registry_keys_only"] == 1
    assert authority["auto_hash216_composition_promotion"] == 0
    assert authority["auto_superedge_promotion"] == 0
    assert authority["requires_signed_environmental_vm81_admission"] == 1


def test_reverse_discovery_replays_to_identical_roots_and_native_receipt() -> None:
    builder = Pass219Lane5RepositoryCapabilityReverseDiscovery()
    first = builder.build()
    second = builder.build()

    for key in (
        "public_catalog_root_hash72",
        "native_export_root_sha256",
        "python_registry_root_sha256",
        "dependency_root_sha256",
        "model_root_sha256",
    ):
        assert first[key] == second[key]

    for key in (
        "descriptor_signature64",
        "receipt_signature64",
        "canonical_boundary_signature64",
    ):
        assert first["native_receipt"][key] == second["native_receipt"][key]


def test_reverse_discovery_preserves_inherited_143_source_roots_on_same_tree() -> None:
    inherited = Pass219Lane5ExecutableCapabilitySelfModel().build()
    successor = Pass219Lane5RepositoryCapabilityReverseDiscovery().build()
    assert successor["public_catalog_root_hash72"] == inherited["public_catalog_root_hash72"]
    assert successor["native_export_root_sha256"] == inherited["native_export_root_sha256"]


def test_structural_registry_extractor_ignores_dynamic_and_unrelated_assignments(
    tmp_path: Path,
) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    source = tmp_path / "registry_probe.py"
    source.write_text(
        "def build_ops():\n"
        "    return {'dynamic.op': object()}\n\n"
        "OPERATIONS = {'alpha.op': object(), 'beta.op': 2}\n"
        "DYNAMIC_OPERATIONS = build_ops()\n"
        "NOTES = {'not-a-capability': 1}\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "-C", str(tmp_path), "add", "registry_probe.py"], check=True)

    rows, manifest = extract_python_operation_registry_keys(tmp_path)
    assert sorted(row["raw_name"] for row in rows) == ["alpha.op", "beta.op"]
    assert manifest["python_operation_registry_keys"] == 2
    assert manifest["python_registry_parse_errors"] == []


def test_discovery_topology_never_auto_promotes_composition_or_superedges() -> None:
    model = Pass219Lane5RepositoryCapabilityReverseDiscovery().build()
    forbidden = {"HASH216_COMPOSITION", "HASH216_COMPOSITION_EDGE", "SUPEREDGE"}
    assert not any(edge["type"] in forbidden for edge in model["edges"])
    assert model["promotion_policy"] == {
        "discovery_auto_promotes_hash216_composition": False,
        "discovery_auto_promotes_superedges": False,
        "typed_replay_proof_required_before_composition": True,
    }
