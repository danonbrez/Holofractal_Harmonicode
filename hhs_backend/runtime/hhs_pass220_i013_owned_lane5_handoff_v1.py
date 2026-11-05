"""Pass 220 I013 composed gate: I012 candidate admission -> HHS-I013 ownership witness.

The wrapper composes existing gates only.  It never invokes the native mutation
ABI and therefore never owns VM81, Hash72, Hash216, persistence, or receipt
authority.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass220_genesis_zero_sum_lane5_gate_v1 import (
    Pass220GenesisZeroSumLane5Gate,
)
from hhs_runtime.hhs_pass220_explicit_mutation_ownership_v1 import (
    build_mutation_ownership_witness,
)

SCHEMA = "HHS_PASS_220_I013_OWNED_LANE5_HANDOFF_GATE_V1"


class Pass220OwnedLane5HandoffGate:
    def __init__(
        self,
        *,
        gate: Pass220GenesisZeroSumLane5Gate | None = None,
        backend: str = "CPU_REFERENCE",
        require_physical_gpu: bool = False,
    ) -> None:
        self._owns_gate = gate is None
        self.gate = gate or Pass220GenesisZeroSumLane5Gate(
            backend=backend,
            require_physical_gpu=require_physical_gpu,
        )

    def close(self) -> None:
        if self._owns_gate:
            self.gate.close()

    def __enter__(self) -> "Pass220OwnedLane5HandoffGate":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def search_and_bind_owner(
        self,
        *,
        current_offsets: Sequence[int],
        next_offsets: Sequence[int],
        nucleus_witnesses: Sequence[Mapping[str, Any]],
        global_modality_zero_closed: bool,
        raw_5184_bit_state_change_zero: bool,
        phase: str,
        query: Mapping[str, Any],
        candidates: Sequence[Mapping[str, Any]],
        tick: int,
        cycle_index: int,
        harmonic_nucleus_pairs: Sequence[Sequence[Any]] | None = None,
        sample_ordinal: int = 0,
        top_k: int = 32,
        request_canonical_handoff: bool = False,
        owner_surface: str | None = None,
        persistence_policy: str | None = None,
        rollback_behavior: str | None = None,
        ledger_effect: str | None = None,
    ) -> dict[str, Any]:
        i012 = self.gate.search_or_halt(
            current_offsets=current_offsets,
            next_offsets=next_offsets,
            nucleus_witnesses=nucleus_witnesses,
            global_modality_zero_closed=global_modality_zero_closed,
            raw_5184_bit_state_change_zero=raw_5184_bit_state_change_zero,
            phase=phase,
            query=query,
            candidates=candidates,
            tick=tick,
            cycle_index=cycle_index,
            harmonic_nucleus_pairs=harmonic_nucleus_pairs,
            sample_ordinal=sample_ordinal,
            top_k=top_k,
        )

        ownership = build_mutation_ownership_witness(
            i012_result=i012,
            request_canonical_handoff=request_canonical_handoff,
            owner_surface=owner_surface,
            persistence_policy=persistence_policy,
            rollback_behavior=rollback_behavior,
            ledger_effect=ledger_effect,
        )

        return {
            "schema": SCHEMA,
            "i012": i012,
            "mutation_ownership": ownership,
            "canonical_handoff_contract_valid": ownership["handoff_contract_valid"],
            "mutation_performed": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_receipt_authority": False,
        }


__all__ = ["Pass220OwnedLane5HandoffGate", "SCHEMA"]
