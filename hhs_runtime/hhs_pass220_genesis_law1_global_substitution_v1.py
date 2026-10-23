"""Pass 220 I029: Genesis Law-of-1 and global substitution membrane.

This read-only exact reference layer binds the inherited Lane 5 / I014 / I028
surfaces to the user-declared Genesis semantics without widening VM81, Hash72,
Hash216, persistence, or mutation authority.

Core rules:
- Delta*e -> 0 is ordered closure; 0 is not substitutable for Delta*e.
- The distinguished global closure carrier is written 0/Delta and is preserved
  as a typed object. No cancellation, commutation, or scalar rewrite is implied.
- Global substitution authority is possible only when every global epsilon is
  phase-cancelled and complete branch/replay equivalence is independently
  proven with repository evidence.
- 0^5184 is represented as a constant-size logical Genesis descriptor whose
  5,184 trit positions all carry local code (000). The inherited canonical
  5,184-character serializer remains the authoritative physical serialization
  witness for the 81 VM81 offsets.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_g3_ouroboros_opcode_registry_v1 import (
    build_lane5_g3_pipeline_contract,
)
from hhs_runtime.hhs_pass220_g41_sudoku_fingerprint_algebra_v1 import (
    ordered_zero_cell_witness,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    SERIALIZED_CHARACTERS,
    VM81_CELLS,
    deserialize_offsets_5184,
    normalize_offsets,
    repeated_lo_shu_reference,
    serialize_offsets_5184,
)

SCHEMA = "HHS_PASS_220_I029_GENESIS_LAW1_GLOBAL_SUBSTITUTION_V1"
VERSION = "1.0.0"
PROFILE = "PASS220-I029-GENESIS-LAW1-GLOBAL-SUBSTITUTION-v1"

GENESIS_LOGICAL_TRITS = 5184
GENESIS_LOCAL_TRIT_CODE: Tuple[int, int, int] = (0, 0, 0)
GLOBAL_EPSILON_COUNT = 72
PALINDROMIC_PHASE_ROUTE: Tuple[str, ...] = (
    "x", "y", "z", "w", "x", "w", "z", "y", "x"
)

LAW1_CORRESPONDENCES: Tuple[str, ...] = (
    "a2=Delta",
    "a2=xy",
    "a2=zw",
    "a2=u^72",
    "a2=P^2-pq",
    "a2=P^4/c^4",
    "a2=b^2/2",
    "a2=((q-p)P/(p+q))",
    "a2=Delta/Bx^5184",
    "a2=5184/72^72",
    "a2=c^2-b^2",
    "a2=LoShuNucleusCell1",
)

COLLAPSE_CHAIN: Tuple[str, ...] = (
    "P^4/c^4",
    "c^2/(a^2+b^2)",
    "Deltae/Delta",
    "e",
)

REQUIRED_SUBSTITUTION_WITNESSES: Tuple[str, ...] = (
    "complete_global_branch_tree_equivalence",
    "deterministic_replay_equivalence",
    "lossless_interchangeability",
    "global_invariant_preservation",
    "ordered_provenance_preservation",
    "serialization_receipt_preservation",
    "no_unintended_downstream_delta",
    "repository_pr_proof_evidence",
)


class Pass220I029GenesisLawError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(
        _stable_json(record).encode("utf-8")
    ).hexdigest()
    return record


def _exact_trit(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value not in (-1, 0, 1):
        raise Pass220I029GenesisLawError(f"{name} must be one exact trit in -1,0,+1")
    return value


def _require_sha256(value: str, *, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass220I029GenesisLawError(f"{name} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass220I029GenesisLawError(f"{name} must be lowercase/uppercase hex") from exc
    return value.lower()


@dataclass(frozen=True)
class GenesisZeroRegisterDescriptor:
    logical_trit_count: int = GENESIS_LOGICAL_TRITS
    local_trit_code: Tuple[int, int, int] = GENESIS_LOCAL_TRIT_CODE
    symbolic_register: str = "0^5184"
    materialized_carrier_bits: int = GENESIS_LOGICAL_TRITS * 3

    def materialize(self) -> Tuple[Tuple[int, int, int], ...]:
        """Materialize only when a validation surface explicitly needs it."""
        return (self.local_trit_code,) * self.logical_trit_count


@dataclass(frozen=True)
class GlobalSubstitutionProof:
    left_branch_tree_sha256: str
    right_branch_tree_sha256: str
    left_replay_sha256: str
    right_replay_sha256: str
    lossless_interchangeability: bool
    global_invariant_preservation: bool
    ordered_provenance_preservation: bool
    serialization_receipt_preservation: bool
    no_unintended_downstream_delta: bool
    repository_pr_proof_evidence: bool


def genesis_serializer_witness() -> Dict[str, Any]:
    """Bind the logical 0^5184 state to the inherited canonical serializer.

    The fast path does not allocate 5,184 explicit (000) tuples. It constructs
    the already-canonical 81 zero offsets and lets the inherited fixed-width
    serializer prove the physical 5,184-character round trip.
    """
    reference = repeated_lo_shu_reference()
    offsets = normalize_offsets(reference, reference=reference, modulus=9)
    if len(offsets) != VM81_CELLS or any(offset != 0 for offset in offsets):
        raise Pass220I029GenesisLawError("Genesis VM81 offsets failed zero normalization")
    serialized = serialize_offsets_5184(offsets)
    decoded = deserialize_offsets_5184(serialized)
    if decoded != offsets:
        raise Pass220I029GenesisLawError("Genesis canonical serializer roundtrip failed")

    descriptor = GenesisZeroRegisterDescriptor()
    return _receipt({
        "schema": "HHS_PASS_220_I029_GENESIS_ZERO_REGISTER_WITNESS_V1",
        "symbolic_register": descriptor.symbolic_register,
        "logical_trit_count": descriptor.logical_trit_count,
        "local_trit_code": descriptor.local_trit_code,
        "materialized_carrier_bits_if_expanded": descriptor.materialized_carrier_bits,
        "constant_size_fast_path": True,
        "logical_trits_materialized_by_default": False,
        "vm81_offset_count": len(offsets),
        "all_vm81_offsets_zero": all(offset == 0 for offset in offsets),
        "canonical_serialized_characters": len(serialized),
        "canonical_serialized_sha256": sha256(serialized.encode("utf-8")).hexdigest(),
        "canonical_roundtrip": decoded == offsets,
        "serializer_authority": "INHERITED_I001_I014_FIXED_5184_CHARACTER_SERIALIZER",
        "physical_5184_character_offset_reinterpreted_as_logical_trit_index": False,
    })


def ordered_delta_e_witness(global_epsilons: Sequence[int]) -> Dict[str, Any]:
    eps = tuple(
        _exact_trit(value, name=f"global_epsilons[{index}]")
        for index, value in enumerate(global_epsilons)
    )
    if len(eps) != GLOBAL_EPSILON_COUNT:
        raise Pass220I029GenesisLawError(
            f"global epsilon vector must contain exactly {GLOBAL_EPSILON_COUNT} trits"
        )
    all_cancelled = all(value == 0 for value in eps)
    return _receipt({
        "schema": "HHS_PASS_220_I029_ORDERED_DELTA_E_WITNESS_V1",
        "ordered_object": ("Delta", "e"),
        "ordered_closure_direction": "Deltae->0",
        "reverse_object_identity_admitted": False,
        "zero_equals_delta_e_admitted": False,
        "delta_e_object_distinct_from_zero_tensor": True,
        "zero_over_delta_typed_state": ("ZeroTensor[x,y,z,w]", "Delta"),
        "cancel_delta_from_zero_over_delta_admitted": False,
        "commute_delta_and_e_admitted": False,
        "global_epsilon_count": len(eps),
        "global_epsilons": eps,
        "all_global_epsilons_phase_cancelled": all_cancelled,
        "delta_e_equals_zero_at_genesis_or_phase_lock": all_cancelled,
        "delta_e_nonzero_default_when_unlocked": not all_cancelled,
    })


def law1_hydration_witness(global_epsilons: Sequence[int] | None = None) -> Dict[str, Any]:
    eps = (0,) * GLOBAL_EPSILON_COUNT if global_epsilons is None else tuple(global_epsilons)
    lane5 = build_lane5_g3_pipeline_contract()
    zero_cell = ordered_zero_cell_witness()
    genesis = genesis_serializer_witness()
    delta_e = ordered_delta_e_witness(eps)
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "law_of_1_correspondence_path": LAW1_CORRESPONDENCES,
        "law_of_1_correspondence_count": len(LAW1_CORRESPONDENCES),
        "collapse_chain_ordered": COLLAPSE_CHAIN,
        "collapse_chain_commutation_authority": False,
        "collapse_chain_cancellation_authority": False,
        "ordered_zero_tensor_witness": zero_cell,
        "genesis_zero_register": genesis,
        "delta_e": delta_e,
        "palindromic_phase_route": PALINDROMIC_PHASE_ROUTE,
        "palindromic_phase_route_self_reverse": (
            PALINDROMIC_PHASE_ROUTE == tuple(reversed(PALINDROMIC_PHASE_ROUTE))
        ),
        "lane5_pipeline_root_hash72": lane5["pipeline_root_hash72"],
        "constructor_graph_root_hash72": lane5[
            "mandatory_constructor_graph_root_hash72"
        ],
        "lane5_relation": "MANDATORY_GLOBAL_5184_CONSTRUCTOR_GRAPH",
        "projection_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    })


def evaluate_global_substitution_authority(
    *,
    left: str,
    right: str,
    global_epsilons: Sequence[int],
    proof: GlobalSubstitutionProof,
) -> Dict[str, Any]:
    """Return a fail-closed global substitution decision.

    Local equality, matching normalized value, a shared residue, or a special
    branch can never grant authority. Both variables are evaluated over the
    complete global branch/replay surfaces.
    """
    if not isinstance(left, str) or not left or not isinstance(right, str) or not right:
        raise Pass220I029GenesisLawError("left/right variable identities are required")

    delta_e = ordered_delta_e_witness(global_epsilons)
    left_branch = _require_sha256(
        proof.left_branch_tree_sha256, name="left_branch_tree_sha256"
    )
    right_branch = _require_sha256(
        proof.right_branch_tree_sha256, name="right_branch_tree_sha256"
    )
    left_replay = _require_sha256(
        proof.left_replay_sha256, name="left_replay_sha256"
    )
    right_replay = _require_sha256(
        proof.right_replay_sha256, name="right_replay_sha256"
    )

    checks = {
        "genesis_or_global_phase_lock": delta_e[
            "all_global_epsilons_phase_cancelled"
        ],
        "complete_global_branch_tree_equivalence": left_branch == right_branch,
        "deterministic_replay_equivalence": left_replay == right_replay,
        "lossless_interchangeability": proof.lossless_interchangeability is True,
        "global_invariant_preservation": proof.global_invariant_preservation is True,
        "ordered_provenance_preservation": proof.ordered_provenance_preservation is True,
        "serialization_receipt_preservation": (
            proof.serialization_receipt_preservation is True
        ),
        "no_unintended_downstream_delta": (
            proof.no_unintended_downstream_delta is True
        ),
        "repository_pr_proof_evidence": proof.repository_pr_proof_evidence is True,
    }
    authorized = all(checks.values())

    return _receipt({
        "schema": "HHS_PASS_220_I029_GLOBAL_SUBSTITUTION_DECISION_V1",
        "left": left,
        "right": right,
        "global_scope_only": True,
        "special_condition_substitution_authority": False,
        "local_only_substitution_authority": False,
        "shared_local_value_substitution_authority": False,
        "typed_global_closure_state": "Deltae=0/Delta",
        "checks": checks,
        "required_witnesses": REQUIRED_SUBSTITUTION_WITNESSES,
        "authorized": authorized,
        "decision": (
            "GLOBAL_SUBSTITUTION_AUTHORIZED"
            if authorized
            else "GLOBAL_SUBSTITUTION_REJECTED"
        ),
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def genesis_law1_self_test() -> Dict[str, Any]:
    zero_hash = "0" * 64
    proof = GlobalSubstitutionProof(
        left_branch_tree_sha256=zero_hash,
        right_branch_tree_sha256=zero_hash,
        left_replay_sha256=zero_hash,
        right_replay_sha256=zero_hash,
        lossless_interchangeability=True,
        global_invariant_preservation=True,
        ordered_provenance_preservation=True,
        serialization_receipt_preservation=True,
        no_unintended_downstream_delta=True,
        repository_pr_proof_evidence=True,
    )
    decision = evaluate_global_substitution_authority(
        left="A",
        right="B",
        global_epsilons=(0,) * GLOBAL_EPSILON_COUNT,
        proof=proof,
    )
    witness = law1_hydration_witness()
    return _receipt({
        "schema": "HHS_PASS_220_I029_SELF_TEST_V1",
        "ok": (
            witness["law_of_1_correspondence_count"] == 12
            and witness["palindromic_phase_route_self_reverse"]
            and witness["genesis_zero_register"]["logical_trit_count"] == 5184
            and witness["genesis_zero_register"]["all_vm81_offsets_zero"]
            and witness["delta_e"]["all_global_epsilons_phase_cancelled"]
            and decision["authorized"]
        ),
        "law1_witness_sha256": witness["receipt_sha256"],
        "substitution_decision_sha256": decision["receipt_sha256"],
        "authority_expansion": False,
    })
