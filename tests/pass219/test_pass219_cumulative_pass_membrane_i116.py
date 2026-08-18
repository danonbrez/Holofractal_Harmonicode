from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import (
    BIND_SYMBOL,
    CLASSIFICATION,
    PASS218_CAPABILITIES,
    PASS_NUMBER,
    pass218_membrane_manifest,
    pass218_membrane_surface_declaration,
    preflight_pass218_membrane,
)


def main() -> None:
    declaration = pass218_membrane_surface_declaration()
    manifest = pass218_membrane_manifest()

    assert PASS_NUMBER == 218
    assert CLASSIFICATION == "WIRED"
    assert declaration["symbol"] == BIND_SYMBOL
    assert declaration["declared_operations"] == [BIND_SYMBOL]
    assert declaration["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert declaration["persistence_policy"] == "INHERITED_COMPLETION_IDENTITY_ONLY"
    assert manifest["classification"] == "WIRED"
    assert manifest["pass_number"] == 218
    assert tuple(manifest["capabilities"]) == PASS218_CAPABILITIES
    assert manifest["receipt_semantics_preserved"] is True
    assert manifest["pass219_handoff_authority_minted"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["next_pass_to_census"] == 217

    cache = {}
    first = preflight_pass218_membrane(cache=cache)
    second = preflight_pass218_membrane(cache=cache)
    assert first["ok"] is True
    assert second["ok"] is True
    assert first["status"] == "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"
    assert first["surface_id"] == declaration["surface_id"]
    assert first["operation"] == BIND_SYMBOL
    assert first["composition_plan"]["composition_allowed"] is True
    assert first["composition_plan"]["pipeline"]["execution_adapter"] == BIND_SYMBOL
    assert first["composition_plan"]["pipeline"]["handwired"] is False
    assert first["composition_plan"]["pipeline"]["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert second["cache"]["cache_hit"] is True


if __name__ == "__main__":
    main()
