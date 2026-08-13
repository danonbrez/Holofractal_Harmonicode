from __future__ import annotations

from base64 import b64encode
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import subprocess

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CompiledROMEntry,
    FULL_HYDRATION_DOMAIN,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_governed_native_dispatch_v1 import (
    DISPATCH_PROFILE,
    DispatchRuntimeState,
    GovernedNativeDispatchAuthority,
    NativeDispatchKernel,
    NativeDispatchLedger,
    NativeDispatchRequest,
)
from hhs_backend.runtime.hhs_pass213_moving_tensor_v1 import MovingTensorState
from hhs_backend.runtime.hhs_pass213_native_protected_rom_v1 import NativeProtectedCompiledROMStore
from hhs_backend.runtime.hhs_pass213_recovery_admission_v1 import protect_compiled_rom_entry
from hhs_backend.runtime.hhs_pass213_trusted_timestamp_v1 import (
    RFC3161TimestampEvidence,
    TimestampAnchorIntent,
    TrustedTimestampAnchorRecord,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_pass217_checkpoint12_learning_tensor_native_v1 import (
    BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA,
    CHECKPOINT12_AUTHORITIES,
    CHECKPOINT12_REQUIRED_AUTHORITIES,
    MOVING_TENSOR_ROUTING_REQUEST_SCHEMA,
    NATIVE_DISPATCH_REQUEST_SCHEMA,
)
from hhs_runtime.hhs_pass217_runtime_route_composer_v1 import compose_bound_route_ingress
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache
from hhs_runtime.pass165.ingestion import MultimodalLearningService

ROOT = Path(__file__).resolve().parents[1]
SECURE_SOURCE = ROOT / "native/pass213/hhs_pass213_secure_arena.c"
DISPATCH_SOURCE = ROOT / "native/pass213/hhs_pass213_native_dispatch.c"
TENSOR_KEY = bytes((index * 37 + 5) % 256 for index in range(32))
ADMISSION_KEY = bytes((index * 11 + 3) % 256 for index in range(32))
MEMORY_KEY = bytes((index * 13 + 5) % 256 for index in range(32))
LEDGER_KEY = bytes((index * 17 + 7) % 256 for index in range(32))


def h(label: str) -> str:
    return hash216("pass217-checkpoint12-test", label.encode("utf-8"))


def synthetic_anchor(sequence: int = 1, timestamp_ns: int = 12_000_001) -> TrustedTimestampAnchorRecord:
    signed_root = hash216("checkpoint12-signed-checkpoint", str(sequence).encode())
    verifier_root = hash216("checkpoint12-verifier-bundle", b"public")
    intent = TimestampAnchorIntent.create(
        signed_sequence=sequence,
        signed_checkpoint_root_hash216=signed_root,
        verifier_bundle_root_hash216=verifier_root,
        prior_anchor_root_hash216="0" * 64,
        hash216_lineage_root=hash216("checkpoint12-lineage", str(sequence).encode()),
        requested_timestamp_ns=timestamp_ns,
        authority_id="HHS_PASS217_CHECKPOINT12_TEST_TSA",
    )
    request_der = f"checkpoint12-request-{sequence}".encode()
    response_der = f"checkpoint12-response-{sequence}".encode()
    unsigned = {
        "schema": "HHS_PASS_213_RFC3161_TIMESTAMP_EVIDENCE_V1",
        "contract": "HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243",
        "iteration": 7,
        "authority_id": intent.authority_id,
        "request_der_b64": b64encode(request_der).decode("ascii"),
        "response_der_b64": b64encode(response_der).decode("ascii"),
        "request_sha256": sha256(request_der).hexdigest(),
        "response_sha256": sha256(response_der).hexdigest(),
        "message_imprint_sha256": sha256(intent.anchor_message()).hexdigest(),
        "tsa_policy_oid": "1.2.3.4.12",
        "tsa_serial_hex": hex(sequence),
        "gen_time_utc": "2026-08-12T12:00:00.000000Z",
        "tsa_subject": "CN=HHS Pass 217 Checkpoint 12 Test TSA",
        "nonce_hex": hex(0x1200 + sequence),
        "trust_bundle_sha256": sha256(b"checkpoint12-trust-bundle").hexdigest(),
        "verification_receipt_hash216": hash216("checkpoint12-rfc3161-verification", str(sequence).encode()),
    }
    evidence = RFC3161TimestampEvidence(
        authority_id=intent.authority_id,
        request_der_b64=unsigned["request_der_b64"],
        response_der_b64=unsigned["response_der_b64"],
        request_sha256=unsigned["request_sha256"],
        response_sha256=unsigned["response_sha256"],
        message_imprint_sha256=unsigned["message_imprint_sha256"],
        tsa_policy_oid=unsigned["tsa_policy_oid"],
        tsa_serial_hex=unsigned["tsa_serial_hex"],
        gen_time_utc=unsigned["gen_time_utc"],
        tsa_subject=unsigned["tsa_subject"],
        nonce_hex=unsigned["nonce_hex"],
        trust_bundle_sha256=unsigned["trust_bundle_sha256"],
        verification_receipt_hash216=unsigned["verification_receipt_hash216"],
        evidence_root_hash216=hash216("rfc3161-timestamp-evidence", canonical_bytes(unsigned)),
    )
    provisional = TrustedTimestampAnchorRecord(
        intent=intent,
        signed_checkpoint={
            "schema": "HHS_PASS_213_SIGNED_INVENTORY_CHECKPOINT_V1",
            "signed_sequence": sequence,
            "signed_checkpoint_root_hash216": signed_root,
            "verifier_bundle_root_hash216": verifier_root,
        },
        evidence=evidence,
        anchor_root_hash216="",
    )
    return replace(
        provisional,
        anchor_root_hash216=hash216("trusted-external-timestamp-anchor", canonical_bytes(provisional.rooted_payload())),
    )


def compiled_entry(policy_root: str) -> CompiledROMEntry:
    return CompiledROMEntry.create(
        operation_id="PASS217_CP12_NATIVE_ADD",
        canonical_operation={
            "dispatch_profile": DISPATCH_PROFILE,
            "native_dispatch_id": "hhs.native.u64.add.v1",
            "semantic_operation": "PASS217_CP12_NATIVE_ADD",
        },
        constraints={
            "dispatch_profile": DISPATCH_PROFILE,
            "input_count": 2,
            "result_count": 1,
            "read_set": ("register.a", "register.b"),
            "write_set": ("register.result",),
            "max_operand": (1 << 64) - 1,
            "modulus": 0,
        },
        vm81_cell_id=17,
        operation_slot=23,
        g243_control_id=144,
        native_dispatch_id="hhs.native.u64.add.v1",
        kernel_policy_hash216=policy_root,
        creation_group_sequence=1,
        creation_open_boundary_hash216=h("creation-open"),
        creation_close_boundary_hash216=h("creation-close"),
        closure_path_root_hash216=h("creation-closure"),
        closure_position=77,
        parent_hash216=h("compiled-parent"),
    )


def compile_native(tmp_path: Path) -> tuple[Path, Path]:
    secure = tmp_path / "libhhs_pass213_secure_arena.so"
    dispatch = tmp_path / "libhhs_pass213_native_dispatch.so"
    for source, output in ((SECURE_SOURCE, secure), (DISPATCH_SOURCE, dispatch)):
        subprocess.run(
            ["cc", "-std=c11", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(output)],
            check=True,
            cwd=ROOT,
        )
    return secure, dispatch


def make_native_authority(tmp_path: Path, tensor: MovingTensorState):
    secure_lib, dispatch_lib = compile_native(tmp_path)
    store = NativeProtectedCompiledROMStore(
        library_path=secure_lib,
        admission_key=ADMISSION_KEY,
        memory_root_key=MEMORY_KEY,
        owner_id="PASS217_CHECKPOINT12_TEST",
    )
    policy_root = h("policy")
    entry = compiled_entry(policy_root)
    store.inspect_correct_protect_and_admit(protect_compiled_rom_entry(entry, ADMISSION_KEY))
    initial_root = h("initial-runtime-state")
    initial_receipt = hash72_digest({"domain": "HHS-P217-CP12-BASELINE"}, bytes.fromhex(initial_root))
    ledger = NativeDispatchLedger(
        database_path=tmp_path / "native-dispatch.sqlite3",
        root_key=LEDGER_KEY,
        anchor_state_root_hash216=initial_root,
        anchor_receipt_hash72=initial_receipt,
    )
    authority = GovernedNativeDispatchAuthority(
        protected_store=store,
        native_kernel=NativeDispatchKernel(library_path=dispatch_lib),
        ledger=ledger,
        runtime_state=DispatchRuntimeState(
            next_sequence=1,
            current_state_root_hash216=initial_root,
            previous_receipt_hash72=initial_receipt,
            kernel_policy_hash216=policy_root,
            kernel_measurement_hash216=h("kernel-measurement"),
            lineage_root_hash216=tensor.anchor.hash216_lineage_root,
            tensor_state=tensor,
            last_timestamp_ns=tensor.anchor.requested_timestamp_ns,
        ),
    )
    request = NativeDispatchRequest(
        entry_hash216=entry.entry_hash216,
        operation_id=entry.operation_id,
        expected_parent_hash216=initial_root,
        expected_tensor_root_hash216=tensor.tensor_root_hash216,
        timestamp_ns=tensor.anchor.requested_timestamp_ns + 1,
        hydration_lane=3,
        operands=(7, 9),
        read_set=("register.a", "register.b"),
        write_set=("register.result",),
    )
    return authority, store, ledger, request


def decisions(decision):
    return {row["authority_id"]: row for row in decision["inherited_execution_authority_reachability"]["decisions"]}


def test_checkpoint12_no_domains_are_mechanically_not_applicable(tmp_path) -> None:
    decision = compose_bound_route_ingress(
        "api.runtime.services",
        {"method": "GET"},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "none-semantic.json"),
    )
    assert decision is not None and decision["ok"] is True
    authority = decision["inherited_execution_authority_reachability"]
    assert authority["required_authority_count"] >= len(CHECKPOINT12_REQUIRED_AUTHORITIES)
    rows = decisions(decision)
    for authority_id in CHECKPOINT12_AUTHORITIES:
        assert rows[authority_id]["state"] == "NOT_APPLICABLE"
        assert rows[authority_id]["mechanically_proven"] is True


def test_checkpoint12_real_route_replays_routes_and_executes_native_c(tmp_path) -> None:
    learning = MultimodalLearningService()
    learning.ingest_source(
        b"alpha alpha beta beta\nfeature=true\n",
        declared_media_type="TEXT",
        provenance="pass217-checkpoint12",
        authorization_scope="PASS217_CHECKPOINT12_TEST",
    )
    learning_request = {
        "schema": BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA,
        "expected_history_records": 1,
        "expected_weight_root_sha256": learning.weight_root,
        "expected_vm81_state_hash72": learning._vm81.state_hash72,
    }

    anchor = synthetic_anchor()
    tensor = MovingTensorState.derive(
        root_key=TENSOR_KEY,
        trusted_anchor=anchor,
        tensor_sequence=1,
        genesis_epoch=12,
        domain_size=FULL_HYDRATION_DOMAIN,
    )
    tensor_request = {
        "schema": MOVING_TENSOR_ROUTING_REQUEST_SCHEMA,
        "expected_tensor_root_hash216": tensor.tensor_root_hash216,
        "expected_domain_size": tensor.domain_size,
        "expected_receipt_hash72": tensor.receipt_hash72,
        "logical_positions": [0, 1, 5183, 5184],
    }

    authority, store, ledger, native_request = make_native_authority(tmp_path, tensor)
    native_wrapper = {
        "schema": NATIVE_DISPATCH_REQUEST_SCHEMA,
        "expected_ledger_count_before": 0,
        "expected_parent_hash216": authority.runtime_state.current_state_root_hash216,
        "request": native_request.to_mapping(),
    }
    try:
        decision = compose_bound_route_ingress(
            "api.runtime.services.dispatch",
            {
                "service": "example",
                "bounded_learning_replay": learning_request,
                "moving_tensor_routing": tensor_request,
                "native_dispatch": native_wrapper,
            },
            cache={},
            semantic_cache=SemanticCompositionCache(tmp_path / "semantic.json"),
            bounded_learning_service=learning,
            moving_tensor_state=tensor,
            moving_tensor_root_key=TENSOR_KEY,
            moving_tensor_trusted_anchor=anchor,
            native_dispatch_authority=authority,
        )
        assert decision is not None and decision["ok"] is True
        authority_summary = decision["inherited_execution_authority_reachability"]
        assert authority_summary["required_authority_count"] >= len(CHECKPOINT12_REQUIRED_AUTHORITIES)
        rows = decisions(decision)
        for authority_id in CHECKPOINT12_AUTHORITIES:
            assert rows[authority_id]["state"] == "ACTIVE_IN_PATH"
            assert rows[authority_id]["witness_root"]

        replay = rows["bounded_learning_replay"]["traversal_witness"]
        assert replay["deterministic_replay"] is True
        assert replay["history_records"] == 1
        assert replay["source_service_mutated"] is False

        routing = rows["moving_tensor_routing"]["traversal_witness"]
        assert routing["keyed_replay_verified"] is True
        assert routing["inverse_routes_verified"] is True
        assert routing["floating_projection_used"] is False
        assert [row["logical_position"] for row in routing["routes"]] == [0, 1, 5183, 5184]
        assert all(row["logical_position"] == row["inverse_logical_position"] for row in routing["routes"])

        native = rows["native_dispatch"]["traversal_witness"]
        assert native["native_dispatch_id"] == "hhs.native.u64.add.v1"
        assert native["result_values"] == [16]
        assert native["ledger_count_before"] == 0
        assert native["ledger_count_after"] == 1
        assert native["canonical_runtime_mutated"] is True
        assert native["singleton_vm81_admission"] is True
        assert native["physical_route_exposed"] is False
        assert ledger.count() == 1
        assert authority.runtime_state.next_sequence == 2
    finally:
        ledger.close()
        store.close()


def test_checkpoint12_learning_domain_without_service_fails_closed(tmp_path) -> None:
    request = {
        "schema": BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA,
        "expected_history_records": 1,
        "expected_weight_root_sha256": "0" * 64,
        "expected_vm81_state_hash72": "x" * 72,
    }
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "bounded_learning_replay": request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "missing-learning.json"),
    )
    assert decision is not None and decision["ok"] is False
    row = decisions(decision)["bounded_learning_replay"]
    assert row["state"] is None
    assert "REJECT_ACTIVE_AUTHORITY_NOT_OBSERVED" in row["reasons"]
    assert "REJECT_BOUNDED_LEARNING_REPLAY_SERVICE_MISSING" in row["traversal_witness"]["reason"]


def test_checkpoint12_native_dispatch_rejected_on_read_only_surface(tmp_path) -> None:
    wrapper = {
        "schema": NATIVE_DISPATCH_REQUEST_SCHEMA,
        "expected_ledger_count_before": 0,
        "expected_parent_hash216": "0" * 64,
        "request": {"expected_parent_hash216": "0" * 64},
    }
    decision = compose_bound_route_ingress(
        "api.runtime.services",
        {"native_dispatch": wrapper},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "readonly-native.json"),
    )
    assert decision is not None and decision["ok"] is False
    row = decisions(decision)["native_dispatch"]
    assert row["state"] is None
    assert "REJECT_NATIVE_DISPATCH_CONTROLLED_MUTATION_SURFACE_REQUIRED" in row["traversal_witness"]["reason"]


def test_checkpoint12_tensor_domain_without_key_fails_closed(tmp_path) -> None:
    anchor = synthetic_anchor()
    tensor = MovingTensorState.derive(
        root_key=TENSOR_KEY,
        trusted_anchor=anchor,
        tensor_sequence=1,
        genesis_epoch=12,
        domain_size=FULL_HYDRATION_DOMAIN,
    )
    request = {
        "schema": MOVING_TENSOR_ROUTING_REQUEST_SCHEMA,
        "expected_tensor_root_hash216": tensor.tensor_root_hash216,
        "expected_domain_size": tensor.domain_size,
        "expected_receipt_hash72": tensor.receipt_hash72,
        "logical_positions": [0],
    }
    decision = compose_bound_route_ingress(
        "api.runtime.services.dispatch",
        {"service": "example", "moving_tensor_routing": request},
        cache={},
        semantic_cache=SemanticCompositionCache(tmp_path / "missing-tensor-key.json"),
        moving_tensor_state=tensor,
        moving_tensor_trusted_anchor=anchor,
    )
    assert decision is not None and decision["ok"] is False
    row = decisions(decision)["moving_tensor_routing"]
    assert row["state"] is None
    assert "REJECT_MOVING_TENSOR_ROUTING_KEY_OR_ANCHOR_MISSING" in row["traversal_witness"]["reason"]
