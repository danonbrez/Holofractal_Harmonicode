from __future__ import annotations

from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass210 import (
    REQUIRED_OPERATIONS,
    pass210_membrane_manifest,
    pass210_membrane_source_evidence,
    pass210_surface_declaration,
    preflight_pass210_membrane,
)


def main() -> None:
    source = pass210_membrane_source_evidence()
    contract = source["contract"]
    evidence = source["evidence"]
    successor = source["successor_pass211"]
    assert contract["pass"] == 210
    assert contract["contract_identifier"] == "HHS-P210-HFC-VM81-H72-H216"
    assert tuple(contract["operations"]) == REQUIRED_OPERATIONS
    assert evidence["runtime_classification"] == "HHS_PASS_210_HOLOGRAPHIC_FRAME_COMPRESSION_RUNTIME_VERIFIED"
    assert evidence["canonical_float_authority"] is False
    assert len(evidence["erasure_drills"]) == 36
    assert len(evidence["corruption_drills"]) == 5
    assert evidence["clean_multimodal_agreement"]["agreement"] is True
    strict = evidence["strict_compression"]["package"]
    assert strict["admissible_domain_witness"]["domain"] == "HFC_ADMISSIBLE_AFFINE_FIBONACCI_MOD2_V1"
    assert successor["contract"]["pass"] == 211
    declaration = pass210_surface_declaration()
    assert declaration["mutation_policy"] == "NO_NEW_PASS219_CANONICAL_RUNTIME_MUTATION"
    assert declaration["declared_operations"] == list(REQUIRED_OPERATIONS)
    preflight = preflight_pass210_membrane()
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == 11
    manifest = pass210_membrane_manifest()
    assert manifest["classification"] == "WIRED"
    assert manifest["register_len"] == 5184
    assert manifest["snapshot_count"] == 36
    assert manifest["pass211_successor_bound"] is True
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False
    assert manifest["next_pass_to_census"] == 209


if __name__ == "__main__":
    main()
