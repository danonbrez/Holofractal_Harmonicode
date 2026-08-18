from hhs_runtime.hhs_pass219_execution_composer_registration_v1 import (
    BYPASS_REASONS,
    EXECUTION_SYMBOL,
    pass219_execution_registration_manifest,
    pass219_execution_surface_declaration,
    preflight_pass219_execution_composer,
)


def main() -> None:
    declaration = pass219_execution_surface_declaration()
    manifest = pass219_execution_registration_manifest()

    assert declaration["symbol"] == EXECUTION_SYMBOL
    assert declaration["declared_operations"] == [EXECUTION_SYMBOL]
    assert declaration["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert manifest["default_eligible_route"] == "INDEXED_CONTINUATION"
    assert manifest["genesis_replay_default"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] == "INHERITED_C_ONLY"
    assert tuple(manifest["typed_bypass_reasons"]) == BYPASS_REASONS

    cache = {}
    first = preflight_pass219_execution_composer(cache=cache)
    second = preflight_pass219_execution_composer(cache=cache)

    assert first["ok"] is True
    assert second["ok"] is True
    assert first["status"] == "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"
    assert first["surface_id"] == declaration["surface_id"]
    assert first["operation"] == EXECUTION_SYMBOL
    plan = first["composition_plan"]
    assert plan["composition_allowed"] is True
    assert plan["pipeline"]["execution_adapter"] == EXECUTION_SYMBOL
    assert plan["pipeline"]["handwired"] is False
    assert plan["pipeline"]["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert plan["decision"]["ok"] is True
    assert first["expanded_metadata_persisted"] is False
    assert second["cache"]["cache_hit"] is True


if __name__ == "__main__":
    main()
