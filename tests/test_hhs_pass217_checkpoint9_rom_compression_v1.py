from __future__ import annotations

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CompiledROMEntry,
    CompiledROMStore,
    TimestampBoundary,
)
from hhs_backend.runtime.hhs_pass213_parametric_delta_v1 import (
    ParametricConstraint,
    ParametricFieldSpec,
    ParametricROMTemplate,
)
from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import FULL_HYDRATION_BITS
from hhs_runtime.hhs_pass217_checkpoint9_rom_compression_v1 import (
    CHECKPOINT9_AUTHORITIES,
    CHECKPOINT9_AUTHORITY_MAP,
    COMPILED_ROM_REUSE_REQUEST_SCHEMA,
    GENERATOR_EXCEPTION_COMPRESSION_REQUEST_SCHEMA,
    PARAMETRIC_ADMISSION_REQUEST_SCHEMA,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import compose_bound_route_ingress
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache


def _decisions(decision):
    return {
        row["authority_id"]: row
        for row in decision["inherited_execution_authority_reachability"]["decisions"]
    }


def _pass213_fixture():
    opening = TimestampBoundary.create(
        kind="open",
        timestamp_ns=100,
        serial=1,
        genesis_epoch=7,
        group_sequence=3,
        parent_hash216="1" * 64,
        previous_receipt_hash72="2" * 72,
        kernel_measurement_hash216="3" * 64,
    )
    entry = CompiledROMEntry.create(
        operation_id="pass217.checkpoint9.parametric.add",
        canonical_operation={"opcode": "ADD", "numeric_authority": "EXACT_INTEGER"},
        constraints={"max_bits": 16},
        vm81_cell_id=5,
        operation_slot=7,
        g243_control_id=11,
        native_dispatch_id="native.pass217.checkpoint9.add",
        kernel_policy_hash216="4" * 64,
        creation_group_sequence=3,
        creation_open_boundary_hash216=opening.boundary_hash216,
        creation_close_boundary_hash216="5" * 64,
        closure_path_root_hash216="6" * 64,
        closure_position=17,
        parent_hash216="7" * 64,
    )
    store = CompiledROMStore()
    store.insert(entry)
    baseline = {"operands": {"x": 5}, "context": {"mode": "safe"}}
    template = ParametricROMTemplate.create(
        template_id="pass217-checkpoint9-template",
        base_entry_hash216=entry.entry_hash216,
        operation_id=entry.operation_id,
        field_specs=(
            ParametricFieldSpec("operands.x", "integer", True),
            ParametricFieldSpec("context.mode", "string", False),
        ),
        baseline_candidate=baseline,
        constraints=(
            ParametricConstraint(
                "c_x",
                "INT_RANGE",
                ("operands.x",),
                {"minimum": 0, "maximum": 100},
            ),
            ParametricConstraint(
                "c_mode",
                "ENUM",
                ("context.mode",),
                {"allowed": ["safe"]},
            ),
        ),
    )
    return opening, entry, store, template


def test_checkpoint9_maps_operational_repository_native_callables() -> None:
    assert CHECKPOINT9_AUTHORITIES == (
        "parametric_admission",
        "compiled_rom_reuse",
        "generator_exception_compression",
    )
    assert CHECKPOINT9_AUTHORITY_MAP["parametric_admission"]["symbol"] == (
        "create_parametric_admission"
    )
    assert CHECKPOINT9_AUTHORITY_MAP["parametric_admission"]["runtime_authority"] is True
    assert CHECKPOINT9_AUTHORITY_MAP["compiled_rom_reuse"]["symbol"] == (
        "CompiledROMStore.lookup_operation"
    )
    assert (
        CHECKPOINT9_AUTHORITY_MAP["compiled_rom_reuse"]
        ["pass215_descriptor_benchmark_analog_is_authority"]
        is False
    )
    compression = CHECKPOINT9_AUTHORITY_MAP["generator_exception_compression"]
    assert compression["origin_pass"] == 212
    assert compression["symbol"] == "FullHydrationRecoveryRuntime._compress"
    assert compression["replay_symbol"] == "FullHydrationRecoveryRuntime._decompress"
    assert compression["false_compression_claim_forbidden"] is True


def test_checkpoint9_no_domain_is_mechanically_not_applicable(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint9-none.json"),
    )
    assert decision is not None and decision["ok"] is True
    decisions = _decisions(decision)
    for authority_id in CHECKPOINT9_AUTHORITIES:
        row = decisions[authority_id]
        assert row["state"] == "NOT_APPLICABLE"
        assert row["mechanically_proven"] is True
    scope = decision["inherited_execution_authority_reachability"]["checkpoint_scope"]
    assert tuple(scope[-3:]) == CHECKPOINT9_AUTHORITIES
    assert decision["inherited_execution_authority_reachability"]["required_authority_count"] == 15


def test_checkpoint9_real_route_traverses_parametric_rom_and_generator_exception(tmp_path) -> None:
    opening, entry, store, template = _pass213_fixture()
    candidate = {"operands": {"x": 9}, "context": {"mode": "safe"}}
    validation_key = b"P217-CHECKPOINT9-PARAMETRIC-KEY-0001"
    exception_positions = [0, 5184 + 3, 2 * 5184 + 7]

    parametric = {
        "schema": PARAMETRIC_ADMISSION_REQUEST_SCHEMA,
        "template_hash216": template.template_hash216,
        "base_entry_hash216": entry.entry_hash216,
        "opening_boundary_hash216": opening.boundary_hash216,
        "candidate": candidate,
    }
    rom_reuse = {
        "schema": COMPILED_ROM_REUSE_REQUEST_SCHEMA,
        "operation_id": entry.operation_id,
        "expected_entry_hash216": entry.entry_hash216,
        "expected_inventory_root_hash216": store.inventory_root(),
    }
    compression = {
        "schema": GENERATOR_EXCEPTION_COMPRESSION_REQUEST_SCHEMA,
        "uniform_seed": 2,
        "exception_positions": exception_positions,
        "require_strict_compression": True,
    }

    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "parametric_admission": parametric,
            "compiled_rom_reuse": rom_reuse,
            "generator_exception_compression": compression,
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint9-active.json"),
        parametric_template=template,
        parametric_base_entry=entry,
        parametric_opening_boundary=opening,
        parametric_validation_key=validation_key,
        compiled_rom_store=store,
    )
    assert decision is not None and decision["ok"] is True
    assert decision["propagation_allowed"] is True
    decisions = _decisions(decision)
    for authority_id in CHECKPOINT9_AUTHORITIES:
        assert decisions[authority_id]["state"] == "ACTIVE_IN_PATH"
        assert decisions[authority_id]["witness_root"]

    admission = decisions["parametric_admission"]["traversal_witness"]
    assert admission["changed_paths"] == ["operands.x"]
    assert admission["affected_constraint_ids"] == ["c_x"]
    assert admission["reused_constraint_ids"] == ["c_mode"]
    assert admission["authentication_tag_present"] is True
    assert admission["vm81_admission_root_hash216"] == decisions[
        "parametric_admission"
    ]["witness_root"]

    rom = decisions["compiled_rom_reuse"]["traversal_witness"]
    assert rom["entry_hash216"] == entry.entry_hash216
    assert rom["inventory_root_hash216"] == store.inventory_root()
    assert rom["lookup_mutated_store"] is False
    assert rom["runtime_authority"] is True
    assert rom["benchmark_descriptor_analog_used"] is False

    compressed = decisions["generator_exception_compression"]["traversal_witness"]
    assert compressed["codec"] == "AFFINE_9720_LEAF_SEEDS_PLUS_SPARSE_XOR"
    assert compressed["exception_positions"] == exception_positions
    assert compressed["exception_count"] == len(exception_positions)
    assert compressed["full_hydration_bits"] == 50_388_480
    assert compressed["affine_seed_bytes"] == 2_430
    assert compressed["compressed_payload_bytes"] < compressed["full_hydration_bytes"]
    assert compressed["replay_verified"] is True
    assert compressed["raw_fallback_used"] is False
    assert compressed["false_compression_claim"] is False


def test_checkpoint9_partial_applicable_context_fails_closed(tmp_path) -> None:
    opening, entry, store, template = _pass213_fixture()
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "parametric_admission": {
                "schema": PARAMETRIC_ADMISSION_REQUEST_SCHEMA,
                "template_hash216": template.template_hash216,
                "base_entry_hash216": entry.entry_hash216,
                "opening_boundary_hash216": opening.boundary_hash216,
                "candidate": {"operands": {"x": 8}, "context": {"mode": "safe"}},
            },
            "compiled_rom_reuse": {
                "schema": COMPILED_ROM_REUSE_REQUEST_SCHEMA,
                "operation_id": entry.operation_id,
                "expected_entry_hash216": entry.entry_hash216,
                "expected_inventory_root_hash216": store.inventory_root(),
            },
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint9-fail.json"),
    )
    assert decision is not None and decision["ok"] is False
    assert decision["propagation_allowed"] is False
    decisions = _decisions(decision)
    assert decisions["parametric_admission"]["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in decisions["parametric_admission"]["reasons"]
    assert "REJECT_PASS213_PARAMETRIC_TEMPLATE_MISSING" in decisions[
        "parametric_admission"
    ]["traversal_witness"]["reason"]
    assert decisions["compiled_rom_reuse"]["state"] is None
    assert "REJECT_PASS213_COMPILED_ROM_STORE_MISSING" in decisions[
        "compiled_rom_reuse"
    ]["traversal_witness"]["reason"]


def test_checkpoint9_invalid_exception_position_fails_closed(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {
            "service": "example",
            "generator_exception_compression": {
                "schema": GENERATOR_EXCEPTION_COMPRESSION_REQUEST_SCHEMA,
                "uniform_seed": 1,
                "exception_positions": [0, FULL_HYDRATION_BITS],
                "require_strict_compression": True,
            },
        },
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "checkpoint9-compression-fail.json"),
    )
    assert decision is not None and decision["ok"] is False
    row = _decisions(decision)["generator_exception_compression"]
    assert row["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in row["reasons"]
    assert "REJECT_PASS212_EXCEPTION_POSITION_OUT_OF_RANGE" in row[
        "traversal_witness"
    ]["reason"]
