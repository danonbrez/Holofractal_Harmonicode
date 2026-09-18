"""Pass 220 I004 Lane 5 gate for Genesis zero-sum closure.

When the I004 closure decision proves global Genesis zero-sum closure with no
normalized state change, this gate returns before invoking I003/Lane 5 ranking.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass220_holographic_hash216_lane5_bridge_v1 import (
    Pass220HolographicLane5QueryBridge,
)
from hhs_runtime.hhs_pass220_genesis_zero_sum_halt_v1 import (
    genesis_zero_sum_halt_decision,
)

SCHEMA = "HHS_PASS_220_I004_GENESIS_ZERO_SUM_LANE5_GATE_V1"


class Pass220GenesisZeroSumLane5Gate:
    """Block redundant candidate expansion after exact Genesis closure."""

    def __init__(
        self,
        *,
        bridge: Pass220HolographicLane5QueryBridge | None = None,
        backend: str = "CPU_REFERENCE",
        require_physical_gpu: bool = False,
    ) -> None:
        self._owns_bridge = bridge is None
        self.bridge = bridge or Pass220HolographicLane5QueryBridge(
            backend=backend,
            require_physical_gpu=require_physical_gpu,
        )

    def close(self) -> None:
        if self._owns_bridge:
            self.bridge.close()

    def __enter__(self) -> "Pass220GenesisZeroSumLane5Gate":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def search_or_halt(
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
        sample_ordinal: int = 0,
        top_k: int = 32,
    ) -> dict[str, Any]:
        closure = genesis_zero_sum_halt_decision(
            current_offsets=current_offsets,
            next_offsets=next_offsets,
            nucleus_witnesses=nucleus_witnesses,
            global_modality_zero_closed=global_modality_zero_closed,
            raw_5184_bit_state_change_zero=raw_5184_bit_state_change_zero,
        )

        if closure["halt"]:
            return {
                "schema": SCHEMA,
                "halt": True,
                "reason": closure["reason"],
                "closure": closure,
                "lane5_invoked": False,
                "candidate_count_input": len(candidates),
                "candidate_count_ranked": 0,
                "ranked": (),
                "candidate_expansion_blocked": True,
                "new_canonical_transition_blocked": True,
                "hash72_commit_authority": False,
                "hash216_commit_authority": False,
                "canonical_vm81_mutation_authority": False,
                "halt_extends_hash72_ledger": False,
                "halt_mints_hash216_transition": False,
            }

        composition = self.bridge.search(
            phase=phase,
            query=query,
            candidates=candidates,
            tick=tick,
            cycle_index=cycle_index,
            sample_ordinal=sample_ordinal,
            top_k=top_k,
        )
        return {
            "schema": SCHEMA,
            "halt": False,
            "reason": closure["reason"],
            "closure": closure,
            "lane5_invoked": True,
            "candidate_count_input": len(candidates),
            "candidate_count_ranked": len(composition.get("baseline_ranked_ids", ())),
            "composition": composition,
            "candidate_expansion_blocked": False,
            "new_canonical_transition_blocked": False,
            "hash72_commit_authority": False,
            "hash216_commit_authority": False,
            "canonical_vm81_mutation_authority": False,
            "requires_exact_cpu_vm81_replay": True,
        }


__all__ = ["Pass220GenesisZeroSumLane5Gate", "SCHEMA"]
