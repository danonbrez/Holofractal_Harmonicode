"""Governed singleton VM81 authority for Pass 213 Iteration 10."""
from __future__ import annotations

from dataclasses import replace
import threading
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT, FULL_HYDRATION_DOMAIN, VM5184_G243_DOMAIN, canonical_bytes, hash216,
)
from hhs_backend.runtime.hhs_pass213_native_dispatch_common_v1 import (
    DISPATCH_ABI_VERSION, DISPATCH_PROFILE, ITERATION, RUNTIME_CLASSIFICATION,
    SCOPE_DISPATCH_EXECUTE, SCOPE_DISPATCH_READ, UINT64_MAX,
    DispatchRuntimeState, NativeDispatchCapabilityAuthority,
    NativeDispatchRequest, ProtectedCompiledEntrySource,
    _NATIVE_DISPATCH_IDS, _canonical_access_set, _require_hash216, _strict_int,
    Pass213NativeDispatchIntegrityError,
    Pass213NativeDispatchUnavailableError,
    Pass213NativeDispatchValidationError,
)
from hhs_backend.runtime.hhs_pass213_native_dispatch_kernel_v1 import NativeDispatchKernel
from hhs_backend.runtime.hhs_pass213_native_dispatch_ledger_v1 import (
    NativeDispatchLedger, NativeDispatchReceipt,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest

class GovernedNativeDispatchAuthority:
    """Singleton VM81 admission and successor-state authority."""

    def __init__(
        self,
        *,
        protected_store: ProtectedCompiledEntrySource,
        native_kernel: NativeDispatchKernel,
        ledger: NativeDispatchLedger,
        runtime_state: DispatchRuntimeState,
    ) -> None:
        runtime_state.validate()
        self.protected_store = protected_store
        self.native_kernel = native_kernel
        self.ledger = ledger
        self._state = runtime_state
        self._lock = threading.RLock()
        self._active = False
        self._validate_ledger_state_alignment()

    @property
    def runtime_state(self) -> DispatchRuntimeState:
        return self._state

    def _validate_ledger_state_alignment(self) -> None:
        self.ledger.verify_chain()
        latest = self.ledger.latest()
        if latest is None:
            if (
                self._state.next_sequence != 1
                or self._state.current_state_root_hash216 != self.ledger.anchor_state_root_hash216
                or self._state.previous_receipt_hash72 != self.ledger.anchor_receipt_hash72
            ):
                raise Pass213NativeDispatchIntegrityError(
                    "PASS213_NATIVE_DISPATCH_EMPTY_LEDGER_STATE_MISMATCH"
                )
            return
        if (
            int(latest["sequence"]) + 1 != self._state.next_sequence
            or latest["receipt_hash72"] != self._state.previous_receipt_hash72
            or latest["successor_state_root_hash216"] != self._state.current_state_root_hash216
            or int(latest["timestamp_ns"]) != self._state.last_timestamp_ns
        ):
            raise Pass213NativeDispatchIntegrityError(
                "PASS213_NATIVE_DISPATCH_LEDGER_RUNTIME_STATE_MISMATCH"
            )

    def status(self) -> Mapping[str, Any]:
        self._validate_ledger_state_alignment()
        return {
            "schema": "HHS_PASS_213_NATIVE_DISPATCH_STATUS_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "runtime_classification": RUNTIME_CLASSIFICATION,
            "available": True,
            "native_abi_version": DISPATCH_ABI_VERSION,
            "dispatch_profile": DISPATCH_PROFILE,
            "supported_native_dispatch_ids": tuple(sorted(_NATIVE_DISPATCH_IDS)),
            "ledger_count": self.ledger.count(),
            "ledger_valid": True,
            "protected_inventory_root_hash216": self.protected_store.inventory_root(),
            "runtime_state": self._state.public_mapping(),
            "native_dynamic_allocation": False,
            "native_ambient_state": False,
            "physical_mapping_exposed": False,
        }

    def _validate_constraints(
        self,
        *,
        entry: CompiledROMEntry,
        request: NativeDispatchRequest,
    ) -> int:
        constraints = dict(entry.constraints)
        canonical_operation = dict(entry.canonical_operation)
        if (
            canonical_operation.get("dispatch_profile") != DISPATCH_PROFILE
            or canonical_operation.get("native_dispatch_id") != entry.native_dispatch_id
        ):
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_CANONICAL_OPERATION_PROFILE_INVALID"
            )
        if constraints.get("dispatch_profile") != DISPATCH_PROFILE:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_PROFILE_INVALID"
            )
        if _strict_int(
            constraints.get("input_count", -1),
            "PASS213_NATIVE_DISPATCH_COMPILED_INPUT_COUNT_INVALID",
        ) != len(request.operands):
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_INPUT_COUNT_MISMATCH"
            )
        if _strict_int(
            constraints.get("result_count", -1),
            "PASS213_NATIVE_DISPATCH_COMPILED_RESULT_COUNT_INVALID",
        ) != 1:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_RESULT_COUNT_INVALID"
            )
        expected_reads = _canonical_access_set(
            tuple(constraints.get("read_set", ())),
            "PASS213_NATIVE_DISPATCH_COMPILED_READ_SET_INVALID",
        )
        expected_writes = _canonical_access_set(
            tuple(constraints.get("write_set", ())),
            "PASS213_NATIVE_DISPATCH_COMPILED_WRITE_SET_INVALID",
        )
        if request.read_set != expected_reads or request.write_set != expected_writes:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_ACCESS_SET_MISMATCH"
            )
        max_operand = _strict_int(
            constraints.get("max_operand", UINT64_MAX),
            "PASS213_NATIVE_DISPATCH_COMPILED_MAX_OPERAND_INVALID",
        )
        if not 0 <= max_operand <= UINT64_MAX or any(value > max_operand for value in request.operands):
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_COMPILED_OPERAND_BOUND_EXCEEDED"
            )
        modulus = _strict_int(
            constraints.get("modulus", 0),
            "PASS213_NATIVE_DISPATCH_COMPILED_MODULUS_INVALID",
        )
        if entry.native_dispatch_id == "hhs.native.u64.mul_mod.v1":
            if not 1 < modulus <= UINT64_MAX:
                raise Pass213NativeDispatchValidationError(
                    "PASS213_NATIVE_DISPATCH_COMPILED_MODULUS_INVALID"
                )
        elif modulus != 0:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_UNEXPECTED_MODULUS"
            )
        return modulus

    def execute(self, request: NativeDispatchRequest | Mapping[str, Any]) -> NativeDispatchReceipt:
        candidate = request if isinstance(request, NativeDispatchRequest) else NativeDispatchRequest.from_mapping(request)
        candidate.validate()
        with self._lock:
            if self._active:
                raise Pass213NativeDispatchIntegrityError(
                    "PASS213_NATIVE_DISPATCH_SINGLETON_VM81_REENTRY"
                )
            self._active = True
            try:
                self._validate_ledger_state_alignment()
                state = self._state
                if candidate.expected_parent_hash216 != state.current_state_root_hash216:
                    raise Pass213NativeDispatchValidationError(
                        "PASS213_NATIVE_DISPATCH_STALE_PARENT"
                    )
                if candidate.expected_tensor_root_hash216 != state.tensor_state.tensor_root_hash216:
                    raise Pass213NativeDispatchValidationError(
                        "PASS213_NATIVE_DISPATCH_TENSOR_ROOT_MISMATCH"
                    )
                if candidate.timestamp_ns <= state.last_timestamp_ns:
                    raise Pass213NativeDispatchValidationError(
                        "PASS213_NATIVE_DISPATCH_TIMESTAMP_NOT_MONOTONIC"
                    )
                entry = self.protected_store.lookup_hash216(candidate.entry_hash216)
                entry.validate()
                if entry.operation_id != candidate.operation_id:
                    raise Pass213NativeDispatchValidationError(
                        "PASS213_NATIVE_DISPATCH_OPERATION_ID_MISMATCH"
                    )
                if entry.kernel_policy_hash216 != state.kernel_policy_hash216:
                    raise Pass213NativeDispatchValidationError(
                        "PASS213_NATIVE_DISPATCH_KERNEL_POLICY_MISMATCH"
                    )
                if state.lineage_root_hash216 != state.tensor_state.anchor.hash216_lineage_root:
                    raise Pass213NativeDispatchValidationError(
                        "PASS213_NATIVE_DISPATCH_CURRENT_LINEAGE_MISMATCH"
                    )
                if candidate.timestamp_ns < state.tensor_state.anchor.requested_timestamp_ns:
                    raise Pass213NativeDispatchValidationError(
                        "PASS213_NATIVE_DISPATCH_TIMESTAMP_BEFORE_TRUSTED_ANCHOR"
                    )
                if state.tensor_state.domain_size == VM5184_G243_DOMAIN:
                    if candidate.hydration_lane != 0:
                        raise Pass213NativeDispatchValidationError(
                            "PASS213_NATIVE_DISPATCH_VM_DOMAIN_LANE_MUST_BE_ZERO"
                        )
                    logical_route = entry.projection_id
                elif state.tensor_state.domain_size == FULL_HYDRATION_DOMAIN:
                    logical_route = (
                        candidate.hydration_lane * VM5184_G243_DOMAIN
                        + entry.projection_id
                    )
                else:
                    raise Pass213NativeDispatchValidationError(
                        "PASS213_NATIVE_DISPATCH_TENSOR_DOMAIN_INVALID"
                    )
                physical_route = state.tensor_state.physical_cell(logical_route)
                route_commitment = hash216(
                    "governed-native-dispatch-route",
                    canonical_bytes({
                        "entry_hash216": entry.entry_hash216,
                        "vm81_cell_id": entry.vm81_cell_id,
                        "operation_slot": entry.operation_slot,
                        "g243_control_id": entry.g243_control_id,
                        "hydration_lane": candidate.hydration_lane,
                        "logical_route": logical_route,
                        "physical_route": physical_route,
                        "tensor_root_hash216": state.tensor_state.tensor_root_hash216,
                        "tensor_closure_root_hash216": state.tensor_state.closure_proof.closure_root_hash216,
                    }),
                )
                read_set_root = hash216(
                    "governed-native-dispatch-read-set", canonical_bytes(candidate.read_set)
                )
                write_set_root = hash216(
                    "governed-native-dispatch-write-set", canonical_bytes(candidate.write_set)
                )
                modulus = self._validate_constraints(entry=entry, request=candidate)
                protected_inventory_root = _require_hash216(
                    self.protected_store.inventory_root(),
                    "PASS213_NATIVE_DISPATCH_PROTECTED_INVENTORY_ROOT_INVALID",
                )
                request_payload = {
                    **candidate.to_mapping(),
                    "sequence": state.next_sequence,
                    "native_dispatch_id": entry.native_dispatch_id,
                    "kernel_policy_hash216": state.kernel_policy_hash216,
                    "kernel_measurement_hash216": state.kernel_measurement_hash216,
                    "lineage_root_hash216": state.lineage_root_hash216,
                    "trusted_anchor_root_hash216": state.tensor_state.anchor.anchor_root_hash216,
                    "route_commitment_hash216": route_commitment,
                    "read_set_root_hash216": read_set_root,
                    "write_set_root_hash216": write_set_root,
                    "previous_receipt_hash72": state.previous_receipt_hash72,
                    "protected_inventory_root_hash216": protected_inventory_root,
                }
                request_root = hash216(
                    "governed-native-dispatch-request", canonical_bytes(request_payload)
                )
                result_values = self.native_kernel.execute(
                    entry=entry,
                    operands=candidate.operands,
                    request_sequence=state.next_sequence,
                    modulus=modulus,
                )
                result_root = hash216(
                    "governed-native-dispatch-result",
                    canonical_bytes({
                        "request_root_hash216": request_root,
                        "native_abi_version": DISPATCH_ABI_VERSION,
                        "native_dispatch_id": entry.native_dispatch_id,
                        "result_values": result_values,
                    }),
                )
                successor_root = hash216(
                    "governed-native-dispatch-successor",
                    canonical_bytes({
                        "sequence": state.next_sequence,
                        "timestamp_ns": candidate.timestamp_ns,
                        "prior_state_root_hash216": state.current_state_root_hash216,
                        "previous_receipt_hash72": state.previous_receipt_hash72,
                        "entry_hash216": entry.entry_hash216,
                        "request_root_hash216": request_root,
                        "result_root_hash216": result_root,
                        "route_commitment_hash216": route_commitment,
                        "read_set_root_hash216": read_set_root,
                        "write_set_root_hash216": write_set_root,
                        "tensor_root_hash216": state.tensor_state.tensor_root_hash216,
                        "kernel_policy_hash216": state.kernel_policy_hash216,
                        "kernel_measurement_hash216": state.kernel_measurement_hash216,
                        "lineage_root_hash216": state.lineage_root_hash216,
                        "protected_inventory_root_hash216": protected_inventory_root,
                    }),
                )
                receipt_hash72 = hash72_digest(
                    {
                        "domain": "HHS-P213-ITER10-NATIVE-DISPATCH-RECEIPT-V1",
                        "contract": CONTRACT,
                        "iteration": ITERATION,
                        "sequence": state.next_sequence,
                    },
                    bytes.fromhex(successor_root),
                )
                provisional = NativeDispatchReceipt(
                    sequence=state.next_sequence,
                    timestamp_ns=candidate.timestamp_ns,
                    entry_hash216=entry.entry_hash216,
                    operation_id=entry.operation_id,
                    native_dispatch_id=entry.native_dispatch_id,
                    vm81_cell_id=entry.vm81_cell_id,
                    operation_slot=entry.operation_slot,
                    g243_control_id=entry.g243_control_id,
                    hydration_lane=candidate.hydration_lane,
                    route_commitment_hash216=route_commitment,
                    read_set_root_hash216=read_set_root,
                    write_set_root_hash216=write_set_root,
                    request_root_hash216=request_root,
                    result_root_hash216=result_root,
                    prior_state_root_hash216=state.current_state_root_hash216,
                    successor_state_root_hash216=successor_root,
                    prior_receipt_hash72=state.previous_receipt_hash72,
                    receipt_hash72=receipt_hash72,
                    result_values=result_values,
                    tensor_root_hash216=state.tensor_state.tensor_root_hash216,
                    kernel_policy_hash216=state.kernel_policy_hash216,
                    kernel_measurement_hash216=state.kernel_measurement_hash216,
                    lineage_root_hash216=state.lineage_root_hash216,
                )
                committed = self.ledger.append(provisional)
                self._state = replace(
                    state,
                    next_sequence=state.next_sequence + 1,
                    current_state_root_hash216=successor_root,
                    previous_receipt_hash72=receipt_hash72,
                    last_timestamp_ns=candidate.timestamp_ns,
                )
                self._validate_ledger_state_alignment()
                return committed
            finally:
                self._active = False


class GovernedNativeDispatchService:
    """Shared HTTP/CLI transport surface for Iteration 10."""

    def __init__(
        self,
        *,
        authority: GovernedNativeDispatchAuthority,
        capabilities: NativeDispatchCapabilityAuthority,
    ) -> None:
        self.authority = authority
        self.capabilities = capabilities

    def invoke(
        self,
        operation: str,
        arguments: Mapping[str, Any] | None = None,
        *,
        capability: str | None = None,
    ) -> Mapping[str, Any]:
        args = dict(arguments or {})
        if operation == "native-dispatch.status":
            return {
                "schema": "HHS_PASS_213_NATIVE_DISPATCH_RESPONSE_V1",
                "ok": True,
                "operation": operation,
                "result": self.authority.status(),
                "canonical_runtime_mutated": False,
            }
        if operation == "native-dispatch.execute":
            claims = self.capabilities.validate(
                capability, required_scope=SCOPE_DISPATCH_EXECUTE
            )
            receipt = self.authority.execute(args)
            return {
                "schema": "HHS_PASS_213_NATIVE_DISPATCH_RESPONSE_V1",
                "ok": True,
                "operation": operation,
                "subject": claims.subject,
                "capability_id_hash216": claims.capability_id_hash216,
                "result": receipt.to_mapping(),
                "canonical_runtime_mutated": True,
            }
        if operation == "native-dispatch.receipt":
            claims = self.capabilities.validate(
                capability, required_scope=SCOPE_DISPATCH_READ
            )
            sequence = _strict_int(
                args["sequence"], "PASS213_NATIVE_DISPATCH_RECEIPT_SEQUENCE_INVALID"
            )
            return {
                "schema": "HHS_PASS_213_NATIVE_DISPATCH_RESPONSE_V1",
                "ok": True,
                "operation": operation,
                "subject": claims.subject,
                "capability_id_hash216": claims.capability_id_hash216,
                "result": self.authority.ledger.lookup(sequence),
                "canonical_runtime_mutated": False,
            }
        raise Pass213NativeDispatchValidationError(
            "PASS213_NATIVE_DISPATCH_OPERATION_NOT_EXPOSED"
        )

    def close(self) -> None:
        self.capabilities.close()
        self.authority.ledger.close()


_DEFAULT_LOCK = threading.RLock()
_DEFAULT_SERVICE: GovernedNativeDispatchService | None = None


def configure_default_native_dispatch_service(
    service: GovernedNativeDispatchService | None,
) -> GovernedNativeDispatchService | None:
    global _DEFAULT_SERVICE
    with _DEFAULT_LOCK:
        previous = _DEFAULT_SERVICE
        _DEFAULT_SERVICE = service
        return previous


def get_default_native_dispatch_service() -> GovernedNativeDispatchService:
    with _DEFAULT_LOCK:
        if _DEFAULT_SERVICE is None:
            raise Pass213NativeDispatchUnavailableError(
                "PASS213_NATIVE_DISPATCH_SERVICE_NOT_CONFIGURED"
            )
        return _DEFAULT_SERVICE




__all__ = [
    "GovernedNativeDispatchAuthority", "GovernedNativeDispatchService",
    "configure_default_native_dispatch_service",
    "get_default_native_dispatch_service",
]
