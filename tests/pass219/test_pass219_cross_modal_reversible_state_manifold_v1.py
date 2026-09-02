from __future__ import annotations

import hashlib

from hhs_runtime.hhs_pass219_cross_modal_reversible_state_manifold_v1 import (
    ModalityProjectionWitness,
    ReversibleOperationWitness,
    exact_work_plan,
    make_branch_state,
    validate_branch_state,
    validate_replay,
    validate_sibling_merge,
)


MODALITIES = ("text", "image", "audio", "code", "graph")
GENESIS = "GENESIS-PASS219-5184"
CONSTRAINT_ROOT = "constraint-root-v1"
REGISTRY_ROOT = "modality-registry-root-v1"
HASH216 = "H" * 216


def root(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def projections(canonical_root: str, *, broken: str | None = None):
    out = []
    for modality in MODALITIES:
        recovered = canonical_root if modality != broken else root("wrong-root")
        out.append(
            ModalityProjectionWitness(
                modality_id=modality,
                canonical_root_sha256=canonical_root,
                projection_sha256=root(f"{modality}:{canonical_root}"),
                recovered_canonical_root_sha256=recovered,
                reversible=True,
            )
        )
    return out


def state(
    *,
    parent_id: str,
    depth: int,
    phase_path: tuple[str, ...],
    canonical_root: str,
    constraint_root: str = CONSTRAINT_ROOT,
    registry_root: str = REGISTRY_ROOT,
    broken: str | None = None,
):
    return make_branch_state(
        parent_id=parent_id,
        depth=depth,
        genesis_id=GENESIS,
        phase_path=phase_path,
        canonical_root_sha256=canonical_root,
        constraint_root=constraint_root,
        modality_registry_root=registry_root,
        hash216_lineage=HASH216,
        projections=projections(canonical_root, broken=broken),
    )


def validate(s):
    return validate_branch_state(
        s,
        required_modalities=MODALITIES,
        required_constraint_root=CONSTRAINT_ROOT,
        required_modality_registry_root=REGISTRY_ROOT,
    )


def test_full_cross_modal_state_maps_to_one_canonical_root():
    s = state(
        parent_id="parent-0",
        depth=1,
        phase_path=("x", "y", "xy"),
        canonical_root=root("semantic-object-A"),
    )
    result = validate(s)
    assert result["ok"] is True
    assert result["mapped_modalities"] == len(MODALITIES)
    assert result["vm81_addresses"] == 5184
    assert result["candidate_mutation_authority"] is False
    assert result["singleton_vm81_authority_required"] is True


def test_noncommutative_phase_order_changes_state_identity():
    canonical = root("semantic-object-A")
    a = state(
        parent_id="same-parent",
        depth=2,
        phase_path=("x", "y"),
        canonical_root=canonical,
    )
    b = state(
        parent_id="same-parent",
        depth=2,
        phase_path=("y", "x"),
        canonical_root=canonical,
    )
    assert a.node_id != b.node_id
    assert a.ordered_phase_identity != b.ordered_phase_identity


def test_missing_modality_and_roundtrip_failure_fail_closed():
    canonical = root("semantic-object-A")
    s = state(
        parent_id="parent-0",
        depth=1,
        phase_path=("x",),
        canonical_root=canonical,
        broken="audio",
    )
    result = validate(s)
    assert result["ok"] is False
    assert "ROUNDTRIP_MISMATCH:audio" in result["failures"]

    incomplete = make_branch_state(
        parent_id="parent-0",
        depth=1,
        genesis_id=GENESIS,
        phase_path=("x",),
        canonical_root_sha256=canonical,
        constraint_root=CONSTRAINT_ROOT,
        modality_registry_root=REGISTRY_ROOT,
        hash216_lineage=HASH216,
        projections=projections(canonical)[:-1],
    )
    result = validate(incomplete)
    assert result["ok"] is False
    assert "REQUIRED_MODALITY_COVERAGE_MISMATCH" in result["failures"]


def test_constraint_and_registry_drift_invalidate_mapping():
    canonical = root("semantic-object-A")
    s = state(
        parent_id="parent-0",
        depth=1,
        phase_path=("x",),
        canonical_root=canonical,
        constraint_root="stale-constraint-root",
    )
    result = validate(s)
    assert result["ok"] is False
    assert "GLOBAL_CONSTRAINT_ROOT_MISMATCH" in result["failures"]


def test_replay_is_git_like_parent_linked_and_deterministic():
    canonical = root("semantic-object-A")
    a = state(
        parent_id="genesis-node",
        depth=1,
        phase_path=("x",),
        canonical_root=canonical,
    )
    b = state(
        parent_id=a.node_id,
        depth=2,
        phase_path=("x", "y"),
        canonical_root=canonical,
    )
    c = state(
        parent_id=b.node_id,
        depth=3,
        phase_path=("x", "y", "xy"),
        canonical_root=canonical,
    )
    assert validate_replay((a, b, c))["ok"] is True

    broken = state(
        parent_id="wrong-parent",
        depth=3,
        phase_path=("x", "y", "xy"),
        canonical_root=canonical,
    )
    replay = validate_replay((a, b, broken))
    assert replay["ok"] is False
    assert "PARENT_LINK_MISMATCH:2" in replay["failures"]


def test_sibling_merge_requires_reconciled_global_roots():
    canonical = root("semantic-object-A")
    base = state(
        parent_id="genesis-node",
        depth=1,
        phase_path=("x",),
        canonical_root=canonical,
    )
    left = state(
        parent_id=base.node_id,
        depth=2,
        phase_path=("x", "y"),
        canonical_root=canonical,
    )
    right = state(
        parent_id=base.node_id,
        depth=2,
        phase_path=("x", "w"),
        canonical_root=canonical,
    )
    assert validate_sibling_merge(base, left, right)["mergeable"] is True

    conflicting = state(
        parent_id=base.node_id,
        depth=2,
        phase_path=("x", "w"),
        canonical_root=canonical,
        constraint_root="other-constraint-root",
    )
    result = validate_sibling_merge(base, left, conflicting)
    assert result["mergeable"] is False
    assert "CONSTRAINT_ROOT_CONFLICT" in result["conflicts"]
    assert result["candidate_merge_authority"] is False


def test_reversible_operation_witness_recovers_exact_parent():
    witness = ReversibleOperationWitness(
        forward_state_id="forward",
        inverse_state_id="inverse",
        recovered_parent_id="parent",
        expected_parent_id="parent",
        exact_roundtrip_verified=True,
    )
    assert witness.ok is True


def test_exact_work_plan_reuses_prefix_and_hub_without_authority_reduction():
    plan = exact_work_plan(
        depth=64,
        modalities=5,
        constraints_per_state=24,
        cached_prefix_depth=56,
        changed_constraints=2,
        prefix_proof_valid=True,
        hub_roundtrip_verified=True,
    )
    assert plan["baseline_total_work"] == 9024
    assert plan["candidate_total_work"] == 1124
    assert plan["exact_work_saved"] == 7900
    assert plan["optimization_selected"] is True
    assert plan["baseline_authority_checks"] == 64
    assert plan["candidate_authority_checks"] == 64
    assert plan["candidate_mutation_authority"] is False

    stale = exact_work_plan(
        depth=64,
        modalities=5,
        constraints_per_state=24,
        cached_prefix_depth=56,
        changed_constraints=2,
        prefix_proof_valid=False,
        hub_roundtrip_verified=True,
    )
    assert stale["complete_fallback"] is True
    assert stale["selected_total_work"] == stale["baseline_total_work"]
    assert stale["exact_work_saved"] == 0


def test_mandatory_data_ml_and_execution_composer_bind_cross_modal_guard():
    from hhs_runtime.hhs_pass219_cross_modal_reversible_state_registration_v1 import (
        MANDATORY_GUARD,
        SCHEMA,
        STATE_VALIDATE_SYMBOL,
        WORK_PLAN_SYMBOL,
    )
    from hhs_runtime.hhs_pass219_execution_composer_registration_v1 import (
        pass219_execution_registration_manifest,
        pass219_execution_surface_declaration,
    )
    from hhs_runtime.hhs_pass219_mandatory_data_ml_registration_v1 import (
        pass219_mandatory_data_ml_manifest,
        pass219_mandatory_data_ml_surface_declaration,
    )

    mandatory = pass219_mandatory_data_ml_surface_declaration()
    assert MANDATORY_GUARD in mandatory["guards"]
    assert SCHEMA in mandatory["contract_schemas"]
    assert STATE_VALIDATE_SYMBOL in mandatory["validators"]
    assert WORK_PLAN_SYMBOL in mandatory["validators"]

    mandatory_manifest = pass219_mandatory_data_ml_manifest()
    assert mandatory_manifest["mandatory_cross_modal_manifold_guard"] == MANDATORY_GUARD
    assert mandatory_manifest["mandatory_cross_modal_manifold_schema"] == SCHEMA

    composer = pass219_execution_surface_declaration()
    assert MANDATORY_GUARD in composer["guards"]
    assert SCHEMA in composer["contract_schemas"]
    assert STATE_VALIDATE_SYMBOL in composer["validators"]
    assert WORK_PLAN_SYMBOL in composer["validators"]

    composer_manifest = pass219_execution_registration_manifest()
    assert composer_manifest["mandatory_cross_modal_manifold_guard"] == MANDATORY_GUARD
    assert composer_manifest["mandatory_cross_modal_manifold_schema"] == SCHEMA
