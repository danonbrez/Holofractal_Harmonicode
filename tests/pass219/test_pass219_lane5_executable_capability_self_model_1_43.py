from __future__ import annotations

from pathlib import Path

from hhs_backend.runtime.hhs_pass219_lane5_executable_capability_self_model_1_43 import (
    CANONICAL_BOUNDARY_EXPORT,
    Pass219Lane5ExecutableCapabilitySelfModel,
)
from hhs_python.runtime.hhs_pass219_lane5_capability_self_model_bridge import (
    AUTH_CANONICAL_ADMISSION_BOUNDARY,
    AUTH_RESTRICTED_OR_UNAVAILABLE,
)


def test_live_repository_capability_self_model_is_exact_and_candidate_only() -> None:
    builder = Pass219Lane5ExecutableCapabilitySelfModel()
    model = builder.build()

    assert model["counts"]["public_registry"] > 0
    assert model["counts"]["native_exact_abi"] > 0
    assert model["counts"]["total"] == len(model["nodes"])
    assert model["counts"]["canonical_boundaries"] == 1
    assert model["scope"]["pass147_public_registry_complete"] is True
    assert model["scope"]["cumulative_exact_abi_complete"] is True
    assert model["scope"]["repository_total_historical_capability_complete"] is False

    node_ids = [node["node_id"] for node in model["nodes"]]
    signatures = [node["entry_signature64"] for node in model["nodes"]]
    assert len(node_ids) == len(set(node_ids))
    assert len(signatures) == len(set(signatures))

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
    assert receipt["public_entries"] == model["counts"]["public_registry"]
    assert receipt["native_entries"] == model["counts"]["native_exact_abi"]
    assert receipt["canonical_boundary_entries"] == 1
    assert receipt["candidate_only"] is True
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_authority"] is False
    assert receipt["canonical_hash216_authority"] is False
    assert receipt["canonical_persistence_authority"] is False
    assert receipt["requires_signed_environmental_vm81_admission"] is True

    authority = model["authority"]
    assert authority["global_capability_discovery"] == 1
    assert authority["public_registry_snapshot"] == 1
    assert authority["native_exact_abi_snapshot"] == 1
    assert authority["canonical_boundary_singleton"] == 1
    assert authority["candidate_only"] == 1
    assert authority["canonical_vm81_mutation_authority"] == 0
    assert authority["canonical_persistence_authority"] == 0
    assert authority["requires_signed_environmental_vm81_admission"] == 1


def test_capability_self_model_replays_to_identical_roots_and_native_receipt() -> None:
    builder = Pass219Lane5ExecutableCapabilitySelfModel()
    first = builder.build()
    second = builder.build()

    for key in (
        "public_catalog_root_hash72",
        "native_export_root_sha256",
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


def test_transitive_native_export_discovery_is_rooted_at_aggregate_header(tmp_path: Path) -> None:
    include = tmp_path / "hhs_runtime" / "include"
    include.mkdir(parents=True)
    (include / "hhs_runtime_exact_abi.h").write_text(
        '#include "child.h"\nHHS_EXACT_API int hhs_exact_root_probe(void);\n',
        encoding="utf-8",
    )
    (include / "child.h").write_text(
        '#include "grandchild.h"\nHHS_EXACT_API int hhs_exact_child_probe(void);\n',
        encoding="utf-8",
    )
    (include / "grandchild.h").write_text(
        'HHS_EXACT_API int hhs_exact_grandchild_probe(void);\n',
        encoding="utf-8",
    )
    (include / "unreachable.h").write_text(
        'HHS_EXACT_API int hhs_exact_unreachable_probe(void);\n',
        encoding="utf-8",
    )

    builder = Pass219Lane5ExecutableCapabilitySelfModel(tmp_path, bridge=object())  # type: ignore[arg-type]
    exports = builder._native_exports()
    names = [item["export_name"] for item in exports]
    assert names == [
        "hhs_exact_child_probe",
        "hhs_exact_grandchild_probe",
        "hhs_exact_root_probe",
    ]
    assert "hhs_exact_unreachable_probe" not in names


def test_restricted_public_classification_is_preserved_when_present() -> None:
    builder = Pass219Lane5ExecutableCapabilitySelfModel()
    catalog = builder._public_catalog()
    live_nodes = [builder._public_node(item)[0] for item in catalog]
    assert len(live_nodes) == len(catalog)

    synthetic = {
        "capability_id": "PUB-RESTRICTED-PROBE",
        "capability_hash72": "0" * 72,
        "surface_type": "CLI",
        "classification": "EXPLICITLY_RESTRICTED_BY_CONTRACT",
        "capabilities": [],
        "reversibility_class": "REJECTED_AS_UNSAFE",
        "mutating": False,
        "argv": ["restricted-probe"],
        "parameters": [],
        "description": "classification preservation probe",
    }
    node, edges = builder._public_node(synthetic)
    assert node["authority_class"] == AUTH_RESTRICTED_OR_UNAVAILABLE
    assert node["source_kind"] == "PUBLIC_REGISTRY"
    assert edges == []
