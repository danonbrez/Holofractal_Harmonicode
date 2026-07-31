"""Bounded Pass 175 operation adapter for the inherited Pass 174 authority.

Pass 175 retains its public operation identities while the singleton Pass 163
VMRC receives only operation classes that its canonical registry admits.  The
adapter is additive: all non-Pass-175 Pass 174 calls are delegated unchanged.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

from .runtime import Pass174Error, Pass174Runtime as CorePass174Runtime


@dataclass(frozen=True)
class Pass175AuthorityOperation:
    """One explicitly admitted Pass 175 operation at the Pass 174 boundary."""

    pass175_operation: str
    vmrc_operation_class: str
    capability_scope: str
    mutation_authority: bool


PASS175_AUTHORITY_OPERATIONS: dict[str, Pass175AuthorityOperation] = {
    "P175_COLD_HYDRATION_SEAL": Pass175AuthorityOperation(
        "P175_COLD_HYDRATION_SEAL",
        "VMRC_COMMIT",
        "P175_HASH216_MICROCODE_HYDRATION",
        True,
    ),
    "P175_WARM_HYDRATION_SEAL": Pass175AuthorityOperation(
        "P175_WARM_HYDRATION_SEAL",
        "VMRC_COMMIT",
        "P175_HASH216_MICROCODE_HYDRATION",
        True,
    ),
    "P175_PARALLEL_CANDIDATE_BATCH_COMMIT": Pass175AuthorityOperation(
        "P175_PARALLEL_CANDIDATE_BATCH_COMMIT",
        "VMRC_COMMIT",
        "P175_VM5184_G243_SINGLETON_VM81_COMMIT",
        True,
    ),
    "P175_X86_64_INGRESS_COMMIT": Pass175AuthorityOperation(
        "P175_X86_64_INGRESS_COMMIT",
        "VMRC_COMMIT",
        "P175_X86_64_INGRESS",
        True,
    ),
    "P175_PRIVILEGED_TRAP_RECEIPT": Pass175AuthorityOperation(
        "P175_PRIVILEGED_TRAP_RECEIPT",
        "VMRC_RECEIPT",
        "P175_PRIVILEGED_TRAP",
        False,
    ),
    "P175_DEVICE_EVENT_RECEIPT": Pass175AuthorityOperation(
        "P175_DEVICE_EVENT_RECEIPT",
        "VMRC_RECEIPT",
        "P175_VIRTUAL_DEVICE_EVENT",
        False,
    ),
    "P175_DETERMINISTIC_REPLAY_RECEIPT": Pass175AuthorityOperation(
        "P175_DETERMINISTIC_REPLAY_RECEIPT",
        "VMRC_REPLAY",
        "P175_DETERMINISTIC_REPLAY",
        False,
    ),
}


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


class Pass175AuthorityAdapter(CorePass174Runtime):
    """Pass 174 runtime with a fail-closed Pass 175 operation membrane."""

    ADAPTER_VERSION = "HHS-P174-P175-AUTHORITY-ADAPTER-1.0.0"

    @staticmethod
    def _resolve_pass175_operation(
        operation: str,
        capability_scope: str,
    ) -> Pass175AuthorityOperation:
        try:
            mapped = PASS175_AUTHORITY_OPERATIONS[operation]
        except KeyError as exc:
            raise Pass174Error(
                "HHS_P174_UNSUPPORTED_PASS175_OPERATION",
                operation,
            ) from exc
        if capability_scope != mapped.capability_scope:
            raise Pass174Error(
                "HHS_P174_PASS175_CAPABILITY_SCOPE_MISMATCH",
                f"{operation}:{capability_scope}",
            )
        return mapped

    def _nonmutating_witness(
        self,
        *,
        mapped: Pass175AuthorityOperation,
        thread: int,
    ) -> dict[str, Any]:
        if not isinstance(thread, int) or isinstance(thread, bool) or not 0 <= thread < 64:
            raise Pass174Error("HHS_P174_PASS175_THREAD_RANGE", str(thread))
        state_hash72 = self.vmrc.state_hash72
        epoch = self.vmrc.epoch
        body = {
            "schema": "P174_PASS175_NONMUTATING_AUTHORITY_WITNESS_V1",
            "adapter_version": self.ADAPTER_VERSION,
            "pass175_operation": mapped.pass175_operation,
            "vmrc_operation_class": mapped.vmrc_operation_class,
            "pass175_capability_scope": mapped.capability_scope,
            "thread": thread,
            "epoch_before": epoch,
            "epoch_after": epoch,
            "input_hash72": state_hash72,
            "output_hash72": state_hash72,
            "mutation_authority": False,
            "receipt_chain_mutated": False,
        }
        receipt_hash72 = hash72_digest(body, self.vmrc.snapshot().to_bytes())
        return {
            **body,
            "receipt_hash72": receipt_hash72,
            "receipt_sha256": sha256(
                b"HHS-P174-P175-NONMUTATING-WITNESS-V1\0"
                + receipt_hash72.encode("ascii")
                + _canonical(body)
            ).hexdigest(),
        }

    def execute(
        self,
        *,
        thread: int,
        writes: Mapping[int, int],
        operation: str = "VMRC_COMMIT",
        capability_scope: str = "P174_WHOLE_FRAME_STATE_WRITE",
        gate_identity: str | None = None,
        prefer_retrieval: bool = True,
    ) -> dict[str, Any]:
        if not operation.startswith("P175_"):
            return super().execute(
                thread=thread,
                writes=writes,
                operation=operation,
                capability_scope=capability_scope,
                gate_identity=gate_identity,
                prefer_retrieval=prefer_retrieval,
            )

        mapped = self._resolve_pass175_operation(operation, capability_scope)
        if not mapped.mutation_authority:
            if writes:
                raise Pass174Error(
                    "HHS_P174_PASS175_NONMUTATING_OPERATION_WRITES",
                    operation,
                )
            witness = self._nonmutating_witness(mapped=mapped, thread=thread)
            return {
                "classification": "HHS_PASS_174_PASS175_NONMUTATING_OPERATION_WITNESSED",
                "adapter_version": self.ADAPTER_VERSION,
                "pass175_operation": operation,
                "vmrc_operation_class": mapped.vmrc_operation_class,
                "pass175_capability_scope": capability_scope,
                "mutation_authority": False,
                "admitted": False,
                "receipt": witness,
            }

        epoch_before = self.vmrc.epoch
        input_hash72 = self.vmrc.state_hash72
        inherited = super().execute(
            thread=thread,
            writes=writes,
            operation=mapped.vmrc_operation_class,
            capability_scope=capability_scope,
            gate_identity=gate_identity,
            prefer_retrieval=prefer_retrieval,
        )
        epoch_after = self.vmrc.epoch
        output_hash72 = self.vmrc.state_hash72
        inherited_receipt = inherited.get("receipt")
        adapter_receipt = self._record_receipt(
            "P174_PASS175_AUTHORITY_ADAPTER_RECEIPT",
            {
                "adapter_version": self.ADAPTER_VERSION,
                "pass175_operation": operation,
                "vmrc_operation_class": mapped.vmrc_operation_class,
                "pass175_capability_scope": capability_scope,
                "thread": thread,
                "epoch_before": epoch_before,
                "epoch_after": epoch_after,
                "input_hash72": input_hash72,
                "output_hash72": output_hash72,
                "operation_key": inherited.get("operation_key"),
                "inherited_path": inherited.get("path"),
                "inherited_receipt_sha256": (
                    inherited_receipt.get("receipt_sha256")
                    if isinstance(inherited_receipt, Mapping)
                    else None
                ),
                "mutation_authority": True,
            },
        )
        return {
            **inherited,
            "classification": "HHS_PASS_174_PASS175_OPERATION_COMMITTED",
            "pass174_classification": inherited.get("classification"),
            "adapter_version": self.ADAPTER_VERSION,
            "pass175_operation": operation,
            "vmrc_operation_class": mapped.vmrc_operation_class,
            "pass175_capability_scope": capability_scope,
            "mutation_authority": True,
            "pass174_receipt": inherited_receipt,
            "receipt": adapter_receipt,
            "authority_mapping": asdict(mapped),
        }


__all__ = [
    "PASS175_AUTHORITY_OPERATIONS",
    "Pass175AuthorityAdapter",
    "Pass175AuthorityOperation",
]
