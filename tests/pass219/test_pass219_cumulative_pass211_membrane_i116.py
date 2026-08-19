from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116_pass211 import (
    FROZEN,
    REQUIRED_OPERATIONS,
    pass211_membrane_manifest,
    pass211_membrane_source_evidence,
    preflight_pass211_membrane,
)


def main() -> None:
    source = pass211_membrane_source_evidence()
    manifest = pass211_membrane_manifest()
    preflight = preflight_pass211_membrane()
    assert source["contract"]["pass"] == 211
    assert source["main_merge_head"] == FROZEN["main_merge_head"]
    assert source["evidence"]["deterministic_replay"]["equal"] is True
    assert manifest["classification"] == "WIRED"
    assert manifest["required_operations"] == list(REQUIRED_OPERATIONS)
    assert manifest["pass212_successor_bound"] is True
    assert manifest["pass219_new_canonical_mutation_authority"] is False
    assert manifest["cxx_mutation_authority"] is False
    assert manifest["vm81_mutation_authority"] is False
    assert manifest["next_pass_to_census"] == 210
    assert preflight["ok"] is True
    assert len(preflight["operations"]) == 6
    assert all(row["status"] == "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT" for row in preflight["operations"])


if __name__ == "__main__":
    main()
