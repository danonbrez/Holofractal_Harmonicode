"""Pass 220 I004/I012 Lane 5 gate for Genesis and harmonic coherence.

I004 returns before Lane 5 ranking when Genesis is already globally closed.
I012 additionally requires a nine-nucleus exact harmonic witness before any
unresolved state may enter the inherited candidate-ranking bridge.

This gate owns no canonical VM81, Hash72, Hash216, persistence, receipt, or
mutation authority.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass220_holographic_hash216_lane5_bridge_v1 import (
    Pass220HolographicLane5QueryBridge,
)
from hhs_runtime.hhs_pass220_genesis_zero_sum_halt_v1 import (
    genesis_zero_sum_halt_decision,
)
from hhs_runtime.hhs_pass220_mobius_quarter_phase_v1 import (
    Pass220MobiusError,
    vm81_harmonic_coherence,
)

SCHEMA = "HHS_PASS_220_I004_I012_GENESIS_HARMONIC_LANE5_GATE_V1"
HARMONIC_WITNESS_REQUIRED = "REJECT_HARMONIC_WITNESS_REQUIRED"
HARMONIC_WITNESS_INVALID = "REJECT_HARMONIC_WITNESS_INVALID"
HARMONIC_INCOHERENCE = "REJECT_HARMONIC_INCOHERENCE"


class Pass220GenesisZeroSumLane5Gate:
    """Block redundant or harmonically incoherent candidate expansion."""

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

    @staticmethod
    def _blocked(
        *,
        closure: Mapping[str, Any],
        candidates: Sequence[Mapping[str, Any]],
        reason: str,
        harmonic: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "halt": False,
            "reason": reason,
            "closure": closure,
            "harmonic_preflight_required": True,
            "harmonic_preflight": harmonic,
            "harmonic_preflight_admitted": False,
            "lane5_invoked": False,
            "candidate_count_input": len(candidates),
            "candidate_count_ranked": 0,
            "ranked": (),
            "candidate_expansion_blocked": True,
            "new_canonical_transition_blocked": True,
            "hash72_commit_authority": False,
            "hash216_commit_authority": False,
            "canonical_vm81_mutation_authority": False,
            "requires_existing_singleton_mutation_authority": True,
        }

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
        harmonic_nucleus_pairs: Sequence[Sequence[Any]] | None = None,
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
                "harmonic_preflight_required": False,
                "harmonic_preflight": None,
                "harmonic_preflight_admitted": None,
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
                "requires_existing_singleton_mutation_authority": True,
            }

        if harmonic_nucleus_pairs is None:
            return self._blocked(
                closure=closure,
                candidates=candidates,
                reason=HARMONIC_WITNESS_REQUIRED,
                harmonic=None,
            )

        try:
            harmonic = vm81_harmonic_coherence(
                tuple((pair[0], pair[1]) for pair in harmonic_nucleus_pairs)
            )
        except (Pass220MobiusError, IndexError, TypeError):
            return self._blocked(
                closure=closure,
                candidates=candidates,
                reason=HARMONIC_WITNESS_INVALID,
                harmonic=None,
            )

        if not harmonic["admitted"]:
            return self._blocked(
                closure=closure,
                candidates=candidates,
                reason=HARMONIC_INCOHERENCE,
                harmonic=harmonic,
            )

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
            "harmonic_preflight_required": True,
            "harmonic_preflight": harmonic,
            "harmonic_preflight_admitted": True,
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
            "requires_existing_singleton_mutation_authority": True,
        }


__all__ = [
    "HARMONIC_INCOHERENCE",
    "HARMONIC_WITNESS_INVALID",
    "HARMONIC_WITNESS_REQUIRED",
    "Pass220GenesisZeroSumLane5Gate",
    "SCHEMA",
]
