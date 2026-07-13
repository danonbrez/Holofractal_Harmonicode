"""
HHS Validation Residue Compressor v1
====================================

Pass 040 closes the memory-artifact accumulation surface.  Validation expansion
caches, diagnostic residues, and intermediate validator elaborations may not
persist as unbounded shadow memory.  They must compress into the u^72/Hash72
multimodal state-machine chain:

    previous_state_root -> compressed_state -> receipt

The compressor preserves causal witnessability while discarding raw expansion
residue from persistent form.  It stores commitments and receipts, not duplicate
payloads or parallel cache objects.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload
from hhs_runtime.hhs_repo_paths_v1 import repo_root


VERSION = "PASS_040_VALIDATION_RESIDUE_COMPRESSOR_V1"
CHAIN_SCHEMA = "HHS_VALIDATION_RESIDUE_STATE_CHAIN_V1"
STATE_SCHEMA = "HHS_VALIDATION_RESIDUE_COMPRESSED_STATE_V1"
RECEIPT_SCHEMA = "HHS_VALIDATION_RESIDUE_RECEIPT_V1"
GENESIS_STATE_ROOT = "H72-VALIDATION-RESIDUE-GENESIS"
HASH72_AUTHORITY = "HASH72_U72_C_KERNEL"
STATE_MACHINE = "u^72_hash72_multimodal_state_machine"

ADMIT_VALIDATION_RESIDUE_STATE_CHAIN = "ADMIT_VALIDATION_RESIDUE_STATE_CHAIN"
REJECT_VALIDATION_RESIDUE_FLOAT = "REJECT_VALIDATION_RESIDUE_FLOAT"
REJECT_VALIDATION_RESIDUE_RAW_CACHE_RETAINED = "REJECT_VALIDATION_RESIDUE_RAW_CACHE_RETAINED"
REJECT_VALIDATION_RESIDUE_PARALLEL_MEMORY_LANE = "REJECT_VALIDATION_RESIDUE_PARALLEL_MEMORY_LANE"
REJECT_VALIDATION_RESIDUE_MISSING_RECEIPT = "REJECT_VALIDATION_RESIDUE_MISSING_RECEIPT"
REJECT_VALIDATION_RESIDUE_CHAIN_MISMATCH = "REJECT_VALIDATION_RESIDUE_CHAIN_MISMATCH"
REJECT_VALIDATION_RESIDUE_PREVIOUS_STATE_MISMATCH = "REJECT_VALIDATION_RESIDUE_PREVIOUS_STATE_MISMATCH"

FORBIDDEN_RESIDUE_FIELDS = {
    "raw_payload",
    "payload_copy",
    "duplicate_payload",
    "raw_cache",
    "cache_blob",
    "expansion_cache",
    "validation_expansion_cache",
    "intermediate_artifacts",
    "parallel_memory",
    "shadow_memory",
    "unbounded_diagnostic_trace",
}

FORBIDDEN_PERSISTENCE_LANES = {
    "raw_validation_cache",
    "parallel_validation_cache",
    "shadow_memory_lane",
    "external_sidecar_cache",
    "duplicate_diagnostic_store",
}

CANONICAL_COMPRESSED_STATE_FIELD_ORDER: Tuple[str, ...] = (
    "schema",
    "version",
    "state_index",
    "previous_state_root",
    "residue_class",
    "modality_type",
    "validation_surface",
    "validation_status",
    "residue_commitment_hash72",
    "source_receipt_hash72",
    "receipt_chain_mode",
    "raw_cache_retained",
    "parallel_memory_lane_allowed",
    "state_machine",
    "hash_authority",
)

CANONICAL_RESIDUE_RECEIPT_FIELD_ORDER: Tuple[str, ...] = (
    "schema",
    "version",
    "state_index",
    "previous_state_root",
    "state_root_hash72",
    "residue_commitment_hash72",
    "source_receipt_hash72",
    "transition_receipt_hash72",
    "state_machine",
    "hash_authority",
)

CANONICAL_CHAIN_FIELD_ORDER: Tuple[str, ...] = (
    "schema",
    "version",
    "previous_state_root",
    "final_state_root",
    "residue_count",
    "receipt_count",
    "residue_classes",
    "modality_types",
    "raw_cache_retained",
    "parallel_memory_lane_allowed",
    "state_machine",
    "hash_authority",
)


def _pass040_ledger_path():
    # Pass 041 repair: validation-residue compression is itself the anti-residue
    # path, so resolving its private receipt ledger must not expand the filesystem
    # path ledger on every validation.
    path = repo_root() / "data" / "runtime" / "hhs_pass040_validation_residue_state_chain_ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _reject(status: str, reason: str, *, details: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {"schema": "HHS_VALIDATION_RESIDUE_REJECTION_V1", "ok": False, "status": status, "reason": reason, "details": dict(details or {})}


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, Mapping):
        return any(_contains_float(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_contains_float(v) for v in value)
    return False


def _contains_forbidden_key(value: Any, forbidden: Iterable[str]) -> Optional[str]:
    forbidden_set = set(forbidden)
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in forbidden_set:
                return str(key)
            nested = _contains_forbidden_key(item, forbidden_set)
            if nested:
                return nested
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            nested = _contains_forbidden_key(item, forbidden_set)
            if nested:
                return nested
    return None


def _normalize_list(values: Optional[Iterable[Any]]) -> List[str]:
    output: List[str] = []
    for value in values or []:
        text = str(value).strip()
        if text:
            output.append(text)
    return sorted(dict.fromkeys(output))


def _hash72(label: str, value: Any, *, width: int = 72) -> str:
    return make_hash72_kernel_witness(label, value, width=width).digest


def _canonical_subset(fields: Mapping[str, Any], order: Tuple[str, ...]) -> Dict[str, Any]:
    return {key: fields.get(key) for key in order}


def commit_validation_residue(residue: Mapping[str, Any]) -> str:
    """Commit to residue content without retaining it in the compressed chain."""
    if _contains_float(residue):
        raise ValueError("validation residue commitments reject floats; use exact rational/symbolic values")
    forbidden = _contains_forbidden_key(residue, FORBIDDEN_RESIDUE_FIELDS)
    if forbidden:
        raise ValueError(f"raw validation residue field cannot persist: {forbidden}")
    lanes = set(str(x) for x in residue.get("persistence_lanes", []) if str(x).strip()) if isinstance(residue, Mapping) else set()
    forbidden_lanes = sorted(lanes & FORBIDDEN_PERSISTENCE_LANES)
    if forbidden_lanes:
        raise ValueError(f"parallel validation residue memory lanes are forbidden: {forbidden_lanes}")
    return _hash72("HHS_VALIDATION_RESIDUE_COMMITMENT_V1", residue, width=72)


def canonical_compressed_state_fields(
    *,
    residue: Mapping[str, Any],
    state_index: int,
    previous_state_root: str,
) -> Dict[str, Any]:
    if _contains_float(residue):
        raise ValueError("compressed validation residue states reject floats")
    commitment = commit_validation_residue(residue)
    fields = {
        "schema": STATE_SCHEMA,
        "version": VERSION,
        "state_index": int(state_index),
        "previous_state_root": str(previous_state_root),
        "residue_class": str(residue.get("residue_class", residue.get("validation_class", "validation_expansion_residue"))),
        "modality_type": str(residue.get("modality_type", "multimodal")),
        "validation_surface": str(residue.get("validation_surface", residue.get("source", "unknown_validation_surface"))),
        "validation_status": str(residue.get("validation_status", residue.get("status", "observed"))),
        "residue_commitment_hash72": commitment,
        "source_receipt_hash72": str(residue.get("source_receipt_hash72", residue.get("receipt_hash72", "NO_SOURCE_RECEIPT_DECLARED"))),
        "receipt_chain_mode": "previous_state_receipt",
        "raw_cache_retained": False,
        "parallel_memory_lane_allowed": False,
        "state_machine": STATE_MACHINE,
        "hash_authority": HASH72_AUTHORITY,
    }
    return _canonical_subset(fields, CANONICAL_COMPRESSED_STATE_FIELD_ORDER)


def make_residue_receipt(state_fields: Mapping[str, Any]) -> Dict[str, Any]:
    state_root = _hash72("HHS_VALIDATION_RESIDUE_COMPRESSED_STATE_V1", _canonical_subset(state_fields, CANONICAL_COMPRESSED_STATE_FIELD_ORDER), width=72)
    receipt_core = {
        "schema": RECEIPT_SCHEMA,
        "version": VERSION,
        "state_index": int(state_fields.get("state_index", 0)),
        "previous_state_root": str(state_fields.get("previous_state_root")),
        "state_root_hash72": state_root,
        "residue_commitment_hash72": str(state_fields.get("residue_commitment_hash72")),
        "source_receipt_hash72": str(state_fields.get("source_receipt_hash72")),
        "transition_receipt_hash72": "PENDING",
        "state_machine": STATE_MACHINE,
        "hash_authority": HASH72_AUTHORITY,
    }
    transition = _hash72("HHS_VALIDATION_RESIDUE_TRANSITION_RECEIPT_V1", {k: v for k, v in receipt_core.items() if k != "transition_receipt_hash72"}, width=72)
    receipt_core["transition_receipt_hash72"] = transition
    return _canonical_subset(receipt_core, CANONICAL_RESIDUE_RECEIPT_FIELD_ORDER)


@dataclass(frozen=True)
class HHSValidationResidueStateChain:
    schema: str
    version: str
    canonical_chain_fields: Dict[str, Any]
    compressed_states: List[Dict[str, Any]]
    receipts: List[Dict[str, Any]]
    final_state_root: str
    chain_root_hash72: str
    kernel_witness: Dict[str, Any]
    unified_ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def make_validation_residue_state_chain(
    residues: Iterable[Mapping[str, Any]],
    *,
    previous_state_root: str = GENESIS_STATE_ROOT,
) -> Dict[str, Any]:
    residue_list = [dict(item) for item in residues]
    if _contains_float(residue_list):
        raise ValueError("validation residue state chains reject floats")
    compressed_states: List[Dict[str, Any]] = []
    receipts: List[Dict[str, Any]] = []
    current_previous = str(previous_state_root)
    residue_classes: List[str] = []
    modality_types: List[str] = []

    for index, residue in enumerate(residue_list):
        state = canonical_compressed_state_fields(residue=residue, state_index=index, previous_state_root=current_previous)
        receipt = make_residue_receipt(state)
        compressed_states.append(state)
        receipts.append(receipt)
        residue_classes.append(str(state["residue_class"]))
        modality_types.append(str(state["modality_type"]))
        current_previous = str(receipt["state_root_hash72"])

    chain_fields = {
        "schema": CHAIN_SCHEMA,
        "version": VERSION,
        "previous_state_root": str(previous_state_root),
        "final_state_root": current_previous,
        "residue_count": len(compressed_states),
        "receipt_count": len(receipts),
        "residue_classes": _normalize_list(residue_classes),
        "modality_types": _normalize_list(modality_types),
        "raw_cache_retained": False,
        "parallel_memory_lane_allowed": False,
        "state_machine": STATE_MACHINE,
        "hash_authority": HASH72_AUTHORITY,
    }
    canonical_chain = _canonical_subset(chain_fields, CANONICAL_CHAIN_FIELD_ORDER)
    kernel = make_hash72_kernel_witness("HHS_VALIDATION_RESIDUE_STATE_CHAIN_V1", {"chain": canonical_chain, "receipts": receipts}, width=72).to_dict()
    ledger = append_payload(
        "VALIDATION_RESIDUE_STATE_CHAIN",
        "hhs_validation_residue_compressor_v1.make_validation_residue_state_chain",
        {"canonical_chain_fields": canonical_chain, "chain_root_hash72": kernel.get("digest"), "receipt_count": len(receipts)},
        ledger_path=_pass040_ledger_path(),
    )
    chain = HHSValidationResidueStateChain(
        schema=CHAIN_SCHEMA,
        version=VERSION,
        canonical_chain_fields=canonical_chain,
        compressed_states=compressed_states,
        receipts=receipts,
        final_state_root=current_previous,
        chain_root_hash72=str(kernel.get("digest")),
        kernel_witness=kernel,
        unified_ledger={"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True},
    ).to_dict()
    validation = validate_validation_residue_state_chain(chain)
    if not validation.get("ok"):
        raise ValueError(validation.get("status", "validation residue chain failed"))
    chain["validation"] = validation
    return chain


def validate_validation_residue_state_chain(chain: Mapping[str, Any]) -> Dict[str, Any]:
    if _contains_float(chain):
        return _reject(REJECT_VALIDATION_RESIDUE_FLOAT, "Validation residue state chains reject floats.")
    forbidden = _contains_forbidden_key(chain, FORBIDDEN_RESIDUE_FIELDS)
    if forbidden:
        return _reject(REJECT_VALIDATION_RESIDUE_RAW_CACHE_RETAINED, "Raw validation expansion cache residue may not persist in the compressed chain.", details={"field": forbidden})

    fields = chain.get("canonical_chain_fields", {})
    if not isinstance(fields, Mapping):
        return _reject(REJECT_VALIDATION_RESIDUE_CHAIN_MISMATCH, "Missing canonical chain fields.")
    if bool(fields.get("raw_cache_retained")):
        return _reject(REJECT_VALIDATION_RESIDUE_RAW_CACHE_RETAINED, "Raw validation expansion cache must be discarded after commitment.")
    if bool(fields.get("parallel_memory_lane_allowed")):
        return _reject(REJECT_VALIDATION_RESIDUE_PARALLEL_MEMORY_LANE, "Parallel validation cache lanes are forbidden.")

    states = list(chain.get("compressed_states", []))
    receipts = list(chain.get("receipts", []))
    if len(states) != int(fields.get("residue_count", -1)) or len(receipts) != int(fields.get("receipt_count", -1)):
        return _reject(REJECT_VALIDATION_RESIDUE_CHAIN_MISMATCH, "Residue count and receipt count must match canonical chain fields.")
    if len(states) != len(receipts):
        return _reject(REJECT_VALIDATION_RESIDUE_MISSING_RECEIPT, "Every compressed validation residue state requires exactly one receipt.")

    expected_previous = str(fields.get("previous_state_root", GENESIS_STATE_ROOT))
    for index, (state, receipt) in enumerate(zip(states, receipts)):
        if str(state.get("previous_state_root")) != expected_previous:
            return _reject(REJECT_VALIDATION_RESIDUE_PREVIOUS_STATE_MISMATCH, "Compressed state previous pointer mismatch.", details={"index": index, "expected": expected_previous, "actual": state.get("previous_state_root")})
        if bool(state.get("raw_cache_retained")) or bool(state.get("parallel_memory_lane_allowed")):
            return _reject(REJECT_VALIDATION_RESIDUE_RAW_CACHE_RETAINED, "Compressed state cannot retain raw cache or parallel memory lanes.", details={"index": index})
        expected_receipt = make_residue_receipt(state)
        if dict(receipt) != expected_receipt:
            return _reject(REJECT_VALIDATION_RESIDUE_CHAIN_MISMATCH, "Residue receipt does not match canonical previous/state/receipt transition.", details={"index": index})
        expected_previous = str(expected_receipt["state_root_hash72"])

    if str(fields.get("final_state_root")) != expected_previous or str(chain.get("final_state_root")) != expected_previous:
        return _reject(REJECT_VALIDATION_RESIDUE_CHAIN_MISMATCH, "Final state root must equal the last receipt state root.")

    expected_chain_root = _hash72("HHS_VALIDATION_RESIDUE_STATE_CHAIN_V1", {"chain": _canonical_subset(fields, CANONICAL_CHAIN_FIELD_ORDER), "receipts": receipts}, width=72)
    if chain.get("chain_root_hash72") and str(chain.get("chain_root_hash72")) != expected_chain_root:
        return _reject(REJECT_VALIDATION_RESIDUE_CHAIN_MISMATCH, "Validation residue chain root mismatch.")

    record = {
        "schema": "HHS_VALIDATION_RESIDUE_STATE_CHAIN_VALIDATION_V1",
        "ok": True,
        "status": ADMIT_VALIDATION_RESIDUE_STATE_CHAIN,
        "admitted": True,
        "residue_count": len(states),
        "receipt_count": len(receipts),
        "previous_state_root": fields.get("previous_state_root"),
        "final_state_root": expected_previous,
        "chain_root_hash72": expected_chain_root,
        "raw_cache_retained": False,
        "parallel_memory_lane_allowed": False,
        "state_machine": STATE_MACHINE,
    }
    kernel = make_hash72_kernel_witness("HHS_VALIDATION_RESIDUE_STATE_CHAIN_VALIDATION_V1", record, width=72).to_dict()
    ledger = append_payload(
        "VALIDATION_RESIDUE_STATE_CHAIN_VALIDATION",
        "hhs_validation_residue_compressor_v1.validate_validation_residue_state_chain",
        {**record, "kernel_digest72": kernel.get("digest")},
        ledger_path=_pass040_ledger_path(),
    )
    record["kernel_witness"] = kernel
    record["unified_ledger"] = {"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True}
    return record


def validation_residue_compressor_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    residues = [
        {"residue_class": "hhfs_capsule_validation", "modality_type": "image", "validation_surface": "hhfs_carrier_capsule", "validation_status": "admitted", "source_receipt_hash72": "A" * 72},
        {"residue_class": "udfp_frame_validation", "modality_type": "multimodal", "validation_surface": "udfp_frame", "validation_status": "admitted", "source_receipt_hash72": "B" * 72},
    ]
    chain = make_validation_residue_state_chain(residues)
    valid = validate_validation_residue_state_chain(chain)
    bad = dict(chain)
    bad["raw_cache"] = {"unbounded": True}
    rejected = validate_validation_residue_state_chain(bad)
    ok = bool(
        valid.get("status") == ADMIT_VALIDATION_RESIDUE_STATE_CHAIN
        and rejected.get("status") == REJECT_VALIDATION_RESIDUE_RAW_CACHE_RETAINED
        and valid.get("receipt_count") == 2
        and valid.get("unified_ledger", {}).get("verified") is True
    )
    return {
        "schema": "HHS_VALIDATION_RESIDUE_COMPRESSOR_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "valid_status": valid.get("status"),
        "raw_cache_rejection_status": rejected.get("status"),
        "residue_count": valid.get("residue_count"),
        "receipt_count": valid.get("receipt_count"),
        "final_state_root": valid.get("final_state_root"),
        "chain_root_hash72": valid.get("chain_root_hash72"),
        "state_machine": STATE_MACHINE,
        "ledger_verified": valid.get("unified_ledger", {}).get("verified") is True,
    }


if __name__ == "__main__":
    print(json.dumps(validation_residue_compressor_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
