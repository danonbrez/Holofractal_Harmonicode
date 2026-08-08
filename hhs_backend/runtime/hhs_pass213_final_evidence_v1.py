"""Pass 213 final iteration: measured full-hydration and replay evidence.

This module closes the implementation evidence gap without converting
hardware-dependent timings into canonical authority.  It produces:

* a deterministic semantic proof over the exact 50,388,480-bit hydration;
* measured integer-nanosecond observations for encode, recovery, tensor route,
  protected compiled-ROM lookup, parametric admission, native dispatch, and
  ledger continuity;
* controlled damage detection and two-shard erasure recovery;
* interrupted-versus-uninterrupted native execution replay equality;
* a Hash216 semantic root and a separate Hash216 observation root;
* an ordered Hash72 final-evidence receipt.

No protected payload bytes, physical addresses, keys, or floating-point values
are included in the evidence mapping.
"""
from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass, replace
from hashlib import sha256
import math
import os
from pathlib import Path
import platform
import sys
from time import perf_counter_ns
from typing import Any, Callable, Mapping

from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import (
    AFFINE_SEED_BYTES,
    FULL_HYDRATION_BITS,
    FULL_HYDRATION_BYTES,
    HYDRATION_LANES,
    Pass212Error,
    generate_affine_hydration,
    get_pass212_runtime,
)
from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT,
    FULL_HYDRATION_DOMAIN,
    ZERO_HASH216,
    ZERO_HASH72,
    CompiledROMEntry,
    CompiledROMStore,
    TimestampBoundary,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_moving_tensor_v1 import MovingTensorState
from hhs_backend.runtime.hhs_pass213_native_dispatch_authority_v1 import (
    GovernedNativeDispatchAuthority,
)
from hhs_backend.runtime.hhs_pass213_native_dispatch_common_v1 import (
    DISPATCH_PROFILE,
    DispatchRuntimeState,
    NativeDispatchRequest,
)
from hhs_backend.runtime.hhs_pass213_native_dispatch_kernel_v1 import (
    NativeDispatchKernel,
)
from hhs_backend.runtime.hhs_pass213_native_dispatch_ledger_v1 import (
    NativeDispatchLedger,
)
from hhs_backend.runtime.hhs_pass213_native_protected_rom_v1 import (
    NativeProtectedCompiledROMStore,
)
from hhs_backend.runtime.hhs_pass213_parametric_delta_v1 import (
    ParametricConstraint,
    ParametricFieldSpec,
    ParametricROMTemplate,
    create_parametric_admission,
)
from hhs_backend.runtime.hhs_pass213_recovery_admission_v1 import (
    protect_compiled_rom_entry,
)
from hhs_backend.runtime.hhs_pass213_trusted_timestamp_v1 import (
    RFC3161TimestampEvidence,
    TimestampAnchorIntent,
    TrustedTimestampAnchorRecord,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest, verify_hash72

PASS_NUMBER = 213
ITERATION = 11
RUNTIME_CLASSIFICATION = "HHS_PASS_213_FINAL_FULL_HYDRATION_REPLAY_EVIDENCE_ITERATION11"
EVIDENCE_SCHEMA = "HHS_PASS_213_FINAL_EVIDENCE_V1"
SEMANTIC_DOMAIN = "pass213-final-semantic-evidence"
OBSERVATION_DOMAIN = "pass213-final-observation-evidence"
RECEIPT_DOMAIN = "HHS-P213-FINAL-EVIDENCE-RECEIPT-V1"
UINT64_MAX = (1 << 64) - 1

ADMISSION_KEY = bytes((index * 11 + 3) % 256 for index in range(32))
MEMORY_KEY = bytes((index * 13 + 5) % 256 for index in range(32))
LEDGER_KEY = bytes((index * 17 + 7) % 256 for index in range(32))
PARAMETRIC_KEY = bytes((index * 19 + 9) % 256 for index in range(32))
TENSOR_KEY = bytes((index * 37 + 5) % 256 for index in range(32))


class Pass213FinalEvidenceError(RuntimeError):
    """Raised when terminal evidence cannot be produced or verified."""


@dataclass(frozen=True)
class EvidenceProfile:
    """Bounded measurement counts; full hydration is always processed exactly."""

    exact_lookup_iterations: int = 2_048
    parametric_iterations: int = 512
    tensor_route_iterations: int = 8_192
    dispatch_iterations: int = 32

    def validate(self) -> None:
        for value, name in (
            (self.exact_lookup_iterations, "EXACT_LOOKUP"),
            (self.parametric_iterations, "PARAMETRIC"),
            (self.tensor_route_iterations, "TENSOR_ROUTE"),
            (self.dispatch_iterations, "DISPATCH"),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 2:
                raise Pass213FinalEvidenceError(
                    f"PASS213_FINAL_EVIDENCE_{name}_ITERATIONS_INVALID"
                )
        if self.dispatch_iterations % 2:
            raise Pass213FinalEvidenceError(
                "PASS213_FINAL_EVIDENCE_DISPATCH_ITERATIONS_MUST_BE_EVEN"
            )

    def to_mapping(self) -> dict[str, int]:
        self.validate()
        return {
            "exact_lookup_iterations": self.exact_lookup_iterations,
            "parametric_iterations": self.parametric_iterations,
            "tensor_route_iterations": self.tensor_route_iterations,
            "dispatch_iterations": self.dispatch_iterations,
        }


def _h(label: str) -> str:
    return hash216("pass213-final-evidence-fixture", label.encode("utf-8"))


def _rate(count: int, elapsed_ns: int) -> Mapping[str, int]:
    if elapsed_ns <= 0:
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_NONPOSITIVE_ELAPSED_TIME"
        )
    return {
        "numerator": int(count) * 1_000_000_000,
        "denominator": int(elapsed_ns),
    }


def _timed(operation: Callable[[], Any]) -> tuple[Any, int]:
    start = perf_counter_ns()
    value = operation()
    elapsed = perf_counter_ns() - start
    if elapsed <= 0:
        elapsed = 1
    return value, elapsed


def _assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_FLOAT_CANONICAL_VALUE"
        )
    if isinstance(value, Mapping):
        for child in value.values():
            _assert_no_float(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _assert_no_float(child)


def _synthetic_evidence_anchor() -> TrustedTimestampAnchorRecord:
    """Deterministic repository fixture; operational RFC3161 remains Iteration 7."""

    sequence = 11
    timestamp_ns = 11_000_001
    signed_root = _h("signed-checkpoint")
    verifier_root = _h("verifier-bundle")
    intent = TimestampAnchorIntent.create(
        signed_sequence=sequence,
        signed_checkpoint_root_hash216=signed_root,
        verifier_bundle_root_hash216=verifier_root,
        prior_anchor_root_hash216=_h("prior-anchor"),
        hash216_lineage_root=_h("hash216-lineage"),
        requested_timestamp_ns=timestamp_ns,
        authority_id="HHS_PASS213_FINAL_EVIDENCE_TSA_FIXTURE",
    )
    request_der = b"pass213-final-evidence-rfc3161-request"
    response_der = b"pass213-final-evidence-rfc3161-response"
    unsigned_evidence = {
        "schema": "HHS_PASS_213_RFC3161_TIMESTAMP_EVIDENCE_V1",
        "contract": CONTRACT,
        "iteration": 7,
        "authority_id": intent.authority_id,
        "request_der_b64": b64encode(request_der).decode("ascii"),
        "response_der_b64": b64encode(response_der).decode("ascii"),
        "request_sha256": sha256(request_der).hexdigest(),
        "response_sha256": sha256(response_der).hexdigest(),
        "message_imprint_sha256": sha256(intent.anchor_message()).hexdigest(),
        "tsa_policy_oid": "1.3.6.1.4.1.213.11",
        "tsa_serial_hex": "0x21311",
        "gen_time_utc": "2026-08-06T01:00:00.000000Z",
        "tsa_subject": "CN=HHS Pass 213 Final Evidence Fixture",
        "nonce_hex": "0x21311",
        "trust_bundle_sha256": sha256(
            b"pass213-final-evidence-trust-fixture"
        ).hexdigest(),
        "verification_receipt_hash216": _h("rfc3161-verification"),
    }
    evidence = RFC3161TimestampEvidence(
        authority_id=intent.authority_id,
        request_der_b64=unsigned_evidence["request_der_b64"],
        response_der_b64=unsigned_evidence["response_der_b64"],
        request_sha256=unsigned_evidence["request_sha256"],
        response_sha256=unsigned_evidence["response_sha256"],
        message_imprint_sha256=unsigned_evidence["message_imprint_sha256"],
        tsa_policy_oid=unsigned_evidence["tsa_policy_oid"],
        tsa_serial_hex=unsigned_evidence["tsa_serial_hex"],
        gen_time_utc=unsigned_evidence["gen_time_utc"],
        tsa_subject=unsigned_evidence["tsa_subject"],
        nonce_hex=unsigned_evidence["nonce_hex"],
        trust_bundle_sha256=unsigned_evidence["trust_bundle_sha256"],
        verification_receipt_hash216=unsigned_evidence[
            "verification_receipt_hash216"
        ],
        evidence_root_hash216=hash216(
            "rfc3161-timestamp-evidence",
            canonical_bytes(unsigned_evidence),
        ),
    )
    signed_checkpoint = {
        "schema": "HHS_PASS_213_SIGNED_INVENTORY_CHECKPOINT_V1",
        "signed_sequence": sequence,
        "signed_checkpoint_root_hash216": signed_root,
        "verifier_bundle_root_hash216": verifier_root,
    }
    provisional = TrustedTimestampAnchorRecord(
        intent=intent,
        signed_checkpoint=signed_checkpoint,
        evidence=evidence,
        anchor_root_hash216="",
    )
    return replace(
        provisional,
        anchor_root_hash216=hash216(
            "trusted-external-timestamp-anchor",
            canonical_bytes(provisional.rooted_payload()),
        ),
    )


def _compiled_entry() -> CompiledROMEntry:
    return CompiledROMEntry.create(
        operation_id="PASS213_FINAL_ADD",
        canonical_operation={
            "dispatch_profile": DISPATCH_PROFILE,
            "native_dispatch_id": "hhs.native.u64.add.v1",
            "semantic_operation": "unsigned_add",
        },
        constraints={
            "dispatch_profile": DISPATCH_PROFILE,
            "input_count": 2,
            "result_count": 1,
            "read_set": ("register.a", "register.b"),
            "write_set": ("register.result",),
            "max_operand": UINT64_MAX,
            "modulus": 0,
        },
        vm81_cell_id=17,
        operation_slot=23,
        g243_control_id=144,
        native_dispatch_id="hhs.native.u64.add.v1",
        kernel_policy_hash216=_h("kernel-policy"),
        creation_group_sequence=11,
        creation_open_boundary_hash216=_h("creation-open"),
        creation_close_boundary_hash216=_h("creation-close"),
        closure_path_root_hash216=_h("creation-closure"),
        closure_position=11,
        parent_hash216=_h("compiled-parent"),
    )


def _parametric_template(entry: CompiledROMEntry) -> ParametricROMTemplate:
    return ParametricROMTemplate.create(
        template_id="PASS213_FINAL_ADD_TEMPLATE",
        base_entry_hash216=entry.entry_hash216,
        operation_id=entry.operation_id,
        field_specs=(
            ParametricFieldSpec("operands.x", "bigint", True),
            ParametricFieldSpec("operands.y", "bigint", True),
            ParametricFieldSpec("context.mode", "string", False),
        ),
        baseline_candidate={
            "operands": {"x": 7, "y": 9},
            "context": {"mode": "u64"},
        },
        constraints=(
            ParametricConstraint(
                "x-range", "INT_RANGE", ("operands.x",),
                {"minimum": 0, "maximum": UINT64_MAX},
            ),
            ParametricConstraint(
                "y-range", "INT_RANGE", ("operands.y",),
                {"minimum": 0, "maximum": UINT64_MAX},
            ),
            ParametricConstraint(
                "sum-bits", "SUM_MAX_BITS",
                ("operands.x", "operands.y"), {"max_bits": 64},
            ),
            ParametricConstraint(
                "mode", "ENUM", ("context.mode",), {"allowed": ["u64"]},
            ),
        ),
    )


def _opening_boundary() -> TimestampBoundary:
    return TimestampBoundary.create(
        kind="open",
        timestamp_ns=11_000_002,
        serial=11,
        genesis_epoch=11,
        group_sequence=11,
        parent_hash216=_h("parametric-parent"),
        previous_receipt_hash72=ZERO_HASH72,
        kernel_measurement_hash216=_h("kernel-measurement"),
    )


def _full_hydration_evidence() -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    runtime = get_pass212_runtime()
    seed_bytes = bytes((index * 73 + 19) % 256 for index in range(AFFINE_SEED_BYTES))
    state, generate_ns = _timed(lambda: generate_affine_hydration(seed_bytes))
    if len(state) != FULL_HYDRATION_BYTES:
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_FULL_STATE_LENGTH_MISMATCH"
        )
    package, encode_ns = _timed(lambda: runtime.encode(state))
    if package.codec != "AFFINE_9720_LEAF_SEEDS_PLUS_SPARSE_XOR":
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_STRICT_CODEC_NOT_SELECTED"
        )
    first_stripe_data = [
        shard.ref
        for shard in package.protected.shards
        if shard.stripe == 0 and shard.role == "data"
    ]
    if len(first_stripe_data) < 2:
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_RECOVERY_SHARDS_UNAVAILABLE"
        )
    missing_refs = tuple(first_stripe_data[:2])
    damaged = runtime.without_shards(package, missing_refs)
    recovered, recovery_ns = _timed(lambda: runtime.decode(damaged))
    if recovered != state:
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_RECOVERED_STATE_MISMATCH"
        )
    corruption_detected = False
    corruption_code = ""
    corrupted = runtime.corrupt_shard(package, first_stripe_data[0])
    detection_start = perf_counter_ns()
    try:
        runtime.decode(corrupted)
    except Pass212Error as exc:
        corruption_detected = True
        corruption_code = str(exc)
    detection_ns = max(1, perf_counter_ns() - detection_start)
    if not corruption_detected:
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_CORRUPTION_NOT_DETECTED"
        )
    replay_package, replay_encode_ns = _timed(lambda: runtime.encode(state))
    deterministic_fields = (
        package.codec == replay_package.codec,
        package.state_hash216 == replay_package.state_hash216,
        package.lane_roots216 == replay_package.lane_roots216,
        package.full_root216 == replay_package.full_root216,
        package.compressed_payload_bytes == replay_package.compressed_payload_bytes,
        package.protected.root216 == replay_package.protected.root216,
        package.package_root216 == replay_package.package_root216,
        package.package_receipt_hash72 == replay_package.package_receipt_hash72,
    )
    if not all(deterministic_fields):
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_FULL_HYDRATION_REPLAY_MISMATCH"
        )
    semantic = {
        "full_hydration_bits": FULL_HYDRATION_BITS,
        "full_hydration_bytes": FULL_HYDRATION_BYTES,
        "hydration_lanes": HYDRATION_LANES,
        "affine_seed_bytes": AFFINE_SEED_BYTES,
        "codec": package.codec,
        "strict_compression_claim": bool(package.metrics["strict_compression_claim"]),
        "compressed_payload_bytes": package.compressed_payload_bytes,
        "compression_ratio": dict(package.metrics["compression_ratio"]),
        "exception_count": package.exception_count,
        "data_shard_count": package.protected.data_shard_count,
        "stripe_count": package.protected.stripe_count,
        "parity_shard_count": int(package.metrics["parity_shard_count"]),
        "missing_shard_count": len(missing_refs),
        "recovery_outcome": "RECOVERED",
        "recovered_state_matches": True,
        "corruption_detected_before_interpretation": corruption_detected,
        "corruption_error_code": corruption_code,
        "deterministic_replay": True,
        "state_hash216": package.state_hash216,
        "full_root216": package.full_root216,
        "package_root216": package.package_root216,
        "protected_root216": package.protected.root216,
        "package_receipt_hash72": package.package_receipt_hash72,
    }
    observations = {
        "state_generation_ns": generate_ns,
        "encode_ns": encode_ns,
        "recovery_decode_ns": recovery_ns,
        "corruption_detection_ns": detection_ns,
        "replay_encode_ns": replay_encode_ns,
        "encode_bytes_per_second": _rate(FULL_HYDRATION_BYTES, encode_ns),
        "recovery_bytes_per_second": _rate(FULL_HYDRATION_BYTES, recovery_ns),
    }
    return semantic, observations


def _tensor_evidence(
    tensor: MovingTensorState,
    iterations: int,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    tensor.validate_structure()
    domain = tensor.domain_size
    checksum = 0
    sample_pairs: list[tuple[int, int]] = []

    def route_workload() -> None:
        nonlocal checksum
        for index in range(iterations):
            logical = (index * 1_000_003 + 17) % domain
            physical = tensor.physical_cell(logical)
            round_trip = tensor.logical_position_from_physical(physical)
            if round_trip != logical:
                raise Pass213FinalEvidenceError(
                    "PASS213_FINAL_EVIDENCE_TENSOR_ROUTE_ROUND_TRIP_FAILED"
                )
            checksum = (checksum + physical + (logical << 1)) & UINT64_MAX
            if index < 16:
                sample_pairs.append((logical, physical))

    _, elapsed_ns = _timed(route_workload)
    proof = tensor.closure_proof
    if (
        proof.domain_size != FULL_HYDRATION_DOMAIN
        or proof.gcd != 1
        or math.gcd(proof.multiplier, proof.domain_size) != 1
        or proof.multiplier * proof.inverse_multiplier % proof.domain_size != 1
        or proof.closing_successor != proof.first_cell
    ):
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_FULL_DOMAIN_CLOSURE_INVALID"
        )
    semantic = {
        "domain_size": domain,
        "tensor_root_hash216": tensor.tensor_root_hash216,
        "tensor_receipt_hash72": tensor.receipt_hash72,
        "anchor_root_hash216": tensor.anchor.anchor_root_hash216,
        "anchor_mode": "DETERMINISTIC_REPOSITORY_EVIDENCE_FIXTURE",
        "closure_algorithm": "AFFINE-MODULAR-BIJECTION-PROOF-V1",
        "closure_multiplier": proof.multiplier,
        "closure_offset": proof.offset,
        "closure_inverse_multiplier": proof.inverse_multiplier,
        "closure_gcd": proof.gcd,
        "closure_first_cell": proof.first_cell,
        "closure_last_cell": proof.last_cell,
        "closure_wrap_valid": True,
        "closure_proof_root_hash216": proof.proof_root_hash216,
        "sample_root_hash216": hash216(
            "pass213-final-tensor-route-samples",
            canonical_bytes(sample_pairs),
        ),
        "route_checksum_u64": checksum,
        "round_trip_valid": True,
    }
    observations = {
        "iterations": iterations,
        "elapsed_ns": elapsed_ns,
        "routes_per_second": _rate(iterations, elapsed_ns),
    }
    return semantic, observations


def _exact_and_parametric_evidence(
    *,
    store: NativeProtectedCompiledROMStore,
    entry: CompiledROMEntry,
    profile: EvidenceProfile,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    exact_last = ""

    def exact_workload() -> None:
        nonlocal exact_last
        for _ in range(profile.exact_lookup_iterations):
            looked_up = store.lookup_hash216(entry.entry_hash216)
            looked_up.validate()
            exact_last = looked_up.entry_hash216

    _, exact_ns = _timed(exact_workload)
    if exact_last != entry.entry_hash216:
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_EXACT_LOOKUP_MISMATCH"
        )

    template = _parametric_template(entry)
    opening = _opening_boundary()
    candidate = {
        "operands": {"x": 11, "y": 9},
        "context": {"mode": "u64"},
    }
    last_admission = None

    def parametric_workload() -> None:
        nonlocal last_admission
        for _ in range(profile.parametric_iterations):
            last_admission = create_parametric_admission(
                template=template,
                base_entry=entry,
                candidate=candidate,
                opening_boundary=opening,
                validation_key=PARAMETRIC_KEY,
            )

    _, parametric_ns = _timed(parametric_workload)
    if last_admission is None:
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_PARAMETRIC_ADMISSION_MISSING"
        )
    last_admission.validate(PARAMETRIC_KEY, template, entry, opening)
    if (
        last_admission.changed_paths != ("operands.x",)
        or last_admission.affected_constraint_ids != ("sum-bits", "x-range")
        or last_admission.reused_constraint_ids != ("mode", "y-range")
    ):
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_PARAMETRIC_SCOPE_MISMATCH"
        )
    semantic = {
        "entry_hash216": entry.entry_hash216,
        "operation_id": entry.operation_id,
        "protected_inventory_root_hash216": store.inventory_root(),
        "exact_lookup_valid": True,
        "template_hash216": template.template_hash216,
        "candidate_hash216": last_admission.candidate_hash216,
        "changed_paths": last_admission.changed_paths,
        "affected_constraint_ids": last_admission.affected_constraint_ids,
        "reused_constraint_ids": last_admission.reused_constraint_ids,
        "delta_root_hash216": last_admission.delta_root_hash216,
        "vm81_admission_root_hash216": (
            last_admission.vm81_admission_root_hash216
        ),
        "dependency_scoped_revalidation": True,
    }
    observations = {
        "exact_lookup_iterations": profile.exact_lookup_iterations,
        "exact_lookup_elapsed_ns": exact_ns,
        "exact_lookups_per_second": _rate(
            profile.exact_lookup_iterations, exact_ns
        ),
        "parametric_iterations": profile.parametric_iterations,
        "parametric_elapsed_ns": parametric_ns,
        "parametric_admissions_per_second": _rate(
            profile.parametric_iterations, parametric_ns
        ),
    }
    return semantic, observations


def _initial_runtime_state(tensor: MovingTensorState) -> DispatchRuntimeState:
    state_root = _h("native-initial-state")
    receipt = hash72_digest(
        {"domain": "HHS-P213-FINAL-EVIDENCE-BASELINE"},
        bytes.fromhex(state_root),
    )
    return DispatchRuntimeState(
        next_sequence=1,
        current_state_root_hash216=state_root,
        previous_receipt_hash72=receipt,
        kernel_policy_hash216=_h("kernel-policy"),
        kernel_measurement_hash216=_h("kernel-measurement"),
        lineage_root_hash216=tensor.anchor.hash216_lineage_root,
        tensor_state=tensor,
        last_timestamp_ns=tensor.anchor.requested_timestamp_ns,
    )


def _run_dispatch_sequence(
    *,
    authority: GovernedNativeDispatchAuthority,
    entry: CompiledROMEntry,
    count: int,
    pause_after: int | None = None,
    pause_hook: Callable[[], None] | None = None,
) -> tuple[list[Mapping[str, Any]], int]:
    receipts: list[Mapping[str, Any]] = []

    def workload() -> None:
        for index in range(count):
            state = authority.runtime_state
            request = NativeDispatchRequest(
                entry_hash216=entry.entry_hash216,
                operation_id=entry.operation_id,
                expected_parent_hash216=state.current_state_root_hash216,
                expected_tensor_root_hash216=state.tensor_state.tensor_root_hash216,
                timestamp_ns=state.tensor_state.anchor.requested_timestamp_ns + index + 1,
                hydration_lane=index % HYDRATION_LANES,
                operands=(index, index + 1),
                read_set=("register.a", "register.b"),
                write_set=("register.result",),
            )
            receipt = authority.execute(request)
            if receipt.result_values != (index + index + 1,):
                raise Pass213FinalEvidenceError(
                    "PASS213_FINAL_EVIDENCE_NATIVE_RESULT_MISMATCH"
                )
            receipts.append(receipt.to_mapping())
            if pause_after is not None and index + 1 == pause_after:
                if pause_hook is None:
                    raise Pass213FinalEvidenceError(
                        "PASS213_FINAL_EVIDENCE_PAUSE_HOOK_MISSING"
                    )
                pause_hook()

    _, elapsed_ns = _timed(workload)
    return receipts, elapsed_ns


def _dispatch_evidence(
    *,
    workdir: Path,
    store: NativeProtectedCompiledROMStore,
    dispatch_library_path: str | Path,
    entry: CompiledROMEntry,
    tensor: MovingTensorState,
    dispatch_iterations: int,
    recovered_full_state_matches: bool,
    recovered_package_root216: str,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    initial = _initial_runtime_state(tensor)
    kernel = NativeDispatchKernel(library_path=dispatch_library_path)
    baseline_ledger = NativeDispatchLedger(
        database_path=workdir / "baseline-dispatch.sqlite3",
        root_key=LEDGER_KEY,
        anchor_state_root_hash216=initial.current_state_root_hash216,
        anchor_receipt_hash72=initial.previous_receipt_hash72,
    )
    resumed_ledger = NativeDispatchLedger(
        database_path=workdir / "resumed-dispatch.sqlite3",
        root_key=LEDGER_KEY,
        anchor_state_root_hash216=initial.current_state_root_hash216,
        anchor_receipt_hash72=initial.previous_receipt_hash72,
    )
    baseline = GovernedNativeDispatchAuthority(
        protected_store=store,
        native_kernel=kernel,
        ledger=baseline_ledger,
        runtime_state=initial,
    )
    resumed = GovernedNativeDispatchAuthority(
        protected_store=store,
        native_kernel=kernel,
        ledger=resumed_ledger,
        runtime_state=initial,
    )
    pause_checked = False

    def recovery_boundary() -> None:
        nonlocal pause_checked
        if not recovered_full_state_matches or len(recovered_package_root216) != 64:
            raise Pass213FinalEvidenceError(
                "PASS213_FINAL_EVIDENCE_RECOVERY_BOUNDARY_INVALID"
            )
        pause_checked = True

    try:
        baseline_receipts, baseline_ns = _run_dispatch_sequence(
            authority=baseline,
            entry=entry,
            count=dispatch_iterations,
        )
        resumed_receipts, resumed_ns = _run_dispatch_sequence(
            authority=resumed,
            entry=entry,
            count=dispatch_iterations,
            pause_after=dispatch_iterations // 2,
            pause_hook=recovery_boundary,
        )
        if not pause_checked:
            raise Pass213FinalEvidenceError(
                "PASS213_FINAL_EVIDENCE_RECOVERY_BOUNDARY_NOT_REACHED"
            )
        if baseline_receipts != resumed_receipts:
            raise Pass213FinalEvidenceError(
                "PASS213_FINAL_EVIDENCE_DISPATCH_REPLAY_MISMATCH"
            )
        if (
            baseline.runtime_state.current_state_root_hash216
            != resumed.runtime_state.current_state_root_hash216
            or baseline.runtime_state.previous_receipt_hash72
            != resumed.runtime_state.previous_receipt_hash72
            or not baseline_ledger.verify_chain()
            or not resumed_ledger.verify_chain()
        ):
            raise Pass213FinalEvidenceError(
                "PASS213_FINAL_EVIDENCE_DISPATCH_FINAL_STATE_MISMATCH"
            )
        semantic = {
            "dispatch_iterations": dispatch_iterations,
            "singleton_vm81_admission": True,
            "recovery_boundary_sequence": dispatch_iterations // 2,
            "recovery_boundary_package_root216": recovered_package_root216,
            "resumed_after_recovery": True,
            "uninterrupted_and_resumed_receipts_equal": True,
            "ledger_chains_valid": True,
            "final_sequence": baseline.runtime_state.next_sequence - 1,
            "final_state_root_hash216": (
                baseline.runtime_state.current_state_root_hash216
            ),
            "final_receipt_hash72": baseline.runtime_state.previous_receipt_hash72,
            "receipt_sequence_root_hash216": hash216(
                "pass213-final-dispatch-receipt-sequence",
                canonical_bytes(baseline_receipts),
            ),
            "physical_route_exposed": False,
            "protected_payload_exposed": False,
        }
        observations = {
            "baseline_dispatch_elapsed_ns": baseline_ns,
            "resumed_dispatch_elapsed_ns": resumed_ns,
            "baseline_dispatches_per_second": _rate(
                dispatch_iterations, baseline_ns
            ),
            "resumed_dispatches_per_second": _rate(
                dispatch_iterations, resumed_ns
            ),
        }
        return semantic, observations
    finally:
        baseline_ledger.close()
        resumed_ledger.close()


def _environment_mapping() -> Mapping[str, Any]:
    return {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "cpu_count": os.cpu_count() or 0,
        "byteorder": sys.byteorder,
        "timer": "time.perf_counter_ns",
        "timings_canonical": False,
        "integer_nanoseconds_only": True,
    }


def run_final_evidence(
    *,
    secure_library_path: str | Path,
    dispatch_library_path: str | Path,
    workdir: str | Path,
    profile: EvidenceProfile | None = None,
) -> Mapping[str, Any]:
    """Execute and verify the terminal measured evidence workload."""

    selected = profile or EvidenceProfile()
    selected.validate()
    root = Path(workdir)
    root.mkdir(parents=True, exist_ok=True)
    entry = _compiled_entry()
    anchor = _synthetic_evidence_anchor()
    tensor = MovingTensorState.derive(
        root_key=TENSOR_KEY,
        trusted_anchor=anchor,
        tensor_sequence=11,
        genesis_epoch=11,
        prior_tensor_root_hash216=ZERO_HASH216,
        domain_size=FULL_HYDRATION_DOMAIN,
    )
    store = NativeProtectedCompiledROMStore(
        library_path=secure_library_path,
        admission_key=ADMISSION_KEY,
        memory_root_key=MEMORY_KEY,
        owner_id="PASS213_FINAL_EVIDENCE",
    )
    try:
        carrier = protect_compiled_rom_entry(entry, ADMISSION_KEY)
        store.inspect_correct_protect_and_admit(carrier)
        hydration_semantic, hydration_observation = _full_hydration_evidence()
        tensor_semantic, tensor_observation = _tensor_evidence(
            tensor, selected.tensor_route_iterations
        )
        compiled_semantic, compiled_observation = _exact_and_parametric_evidence(
            store=store,
            entry=entry,
            profile=selected,
        )
        dispatch_semantic, dispatch_observation = _dispatch_evidence(
            workdir=root,
            store=store,
            dispatch_library_path=dispatch_library_path,
            entry=entry,
            tensor=tensor,
            dispatch_iterations=selected.dispatch_iterations,
            recovered_full_state_matches=bool(
                hydration_semantic["recovered_state_matches"]
            ),
            recovered_package_root216=str(
                hydration_semantic["package_root216"]
            ),
        )
    finally:
        store.close()

    semantic = {
        "schema": "HHS_PASS_213_FINAL_SEMANTIC_EVIDENCE_V1",
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "correction_before_interpretation": True,
        "correction_before_execution": True,
        "no_float_canonical_authority": True,
        "full_hydration": hydration_semantic,
        "moving_tensor": tensor_semantic,
        "compiled_reuse": compiled_semantic,
        "native_dispatch": dispatch_semantic,
    }
    semantic_root = hash216(SEMANTIC_DOMAIN, canonical_bytes(semantic))
    observations = {
        "schema": "HHS_PASS_213_FINAL_PERFORMANCE_OBSERVATION_V1",
        "profile": selected.to_mapping(),
        "environment": _environment_mapping(),
        "full_hydration": hydration_observation,
        "moving_tensor": tensor_observation,
        "compiled_reuse": compiled_observation,
        "native_dispatch": dispatch_observation,
    }
    observation_root = hash216(
        OBSERVATION_DOMAIN, canonical_bytes(observations)
    )
    receipt = hash72_digest(
        {
            "domain": RECEIPT_DOMAIN,
            "contract": CONTRACT,
            "pass": PASS_NUMBER,
            "iteration": ITERATION,
        },
        bytes.fromhex(semantic_root),
    )
    evidence = {
        "schema": EVIDENCE_SCHEMA,
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "semantic": semantic,
        "performance_observations": observations,
        "semantic_root_hash216": semantic_root,
        "observation_root_hash216": observation_root,
        "receipt_hash72": receipt,
        "canonical_runtime_closed": True,
        "timings_are_observational": True,
        "protected_material_exposed": False,
        "physical_addresses_exposed": False,
    }
    validate_final_evidence(evidence)
    return evidence


def validate_final_evidence(value: Mapping[str, Any]) -> bool:
    if (
        value.get("schema") != EVIDENCE_SCHEMA
        or value.get("contract") != CONTRACT
        or value.get("pass") != PASS_NUMBER
        or value.get("iteration") != ITERATION
        or value.get("runtime_classification") != RUNTIME_CLASSIFICATION
    ):
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_SCHEMA_OR_CONTRACT_INVALID"
        )
    semantic = value.get("semantic")
    observations = value.get("performance_observations")
    if not isinstance(semantic, Mapping) or not isinstance(observations, Mapping):
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_SECTIONS_INVALID"
        )
    _assert_no_float(value)
    expected_semantic = hash216(SEMANTIC_DOMAIN, canonical_bytes(semantic))
    expected_observation = hash216(
        OBSERVATION_DOMAIN, canonical_bytes(observations)
    )
    if value.get("semantic_root_hash216") != expected_semantic:
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_SEMANTIC_ROOT_MISMATCH"
        )
    if value.get("observation_root_hash216") != expected_observation:
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_OBSERVATION_ROOT_MISMATCH"
        )
    if not verify_hash72(
        str(value.get("receipt_hash72", "")),
        {
            "domain": RECEIPT_DOMAIN,
            "contract": CONTRACT,
            "pass": PASS_NUMBER,
            "iteration": ITERATION,
        },
        bytes.fromhex(expected_semantic),
    ):
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_RECEIPT_MISMATCH"
        )
    if not all(
        value.get(field) is expected
        for field, expected in (
            ("canonical_runtime_closed", True),
            ("timings_are_observational", True),
            ("protected_material_exposed", False),
            ("physical_addresses_exposed", False),
        )
    ):
        raise Pass213FinalEvidenceError(
            "PASS213_FINAL_EVIDENCE_BOUNDARY_FLAGS_INVALID"
        )
    return True


__all__ = [
    "PASS_NUMBER",
    "ITERATION",
    "RUNTIME_CLASSIFICATION",
    "EVIDENCE_SCHEMA",
    "Pass213FinalEvidenceError",
    "EvidenceProfile",
    "run_final_evidence",
    "validate_final_evidence",
]
