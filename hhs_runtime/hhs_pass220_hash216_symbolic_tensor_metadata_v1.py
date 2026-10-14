"""Read-only symbolic tensor operations over P metadata and bound Hash216 ancestry.

Operators manipulate typed references, not expanded 5184 cells. The complete
Hash216 lineage is supplied by existing authority; this candidate never
mints an authoritative Hash72/Hash216 identity or proves HNAN closure.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

SCHEMA = "HHS_PASS220_HASH216_SYMBOLIC_TENSOR_METADATA_V1"

class SymbolicTensorError(ValueError):
    pass

@dataclass(frozen=True)
class TensorRef:
    P: int
    modality: str
    hash216_lineage: str
    constraint_root: str

    def __post_init__(self):
        if type(self.P) is not int or self.P < 0:
            raise SymbolicTensorError("EXACT_NONNEGATIVE_P_REQUIRED")
        if not isinstance(self.modality, str) or not self.modality:
            raise SymbolicTensorError("TYPED_MODALITY_REQUIRED")
        if not isinstance(self.hash216_lineage, str) or len(self.hash216_lineage) != 216:
            raise SymbolicTensorError("INHERITED_HASH216_LINEAGE_REQUIRED")
        if not isinstance(self.constraint_root, str) or not self.constraint_root:
            raise SymbolicTensorError("GLOBAL_CONSTRAINT_ROOT_REQUIRED")


def compose_metadata(operation: str, left: TensorRef, right: TensorRef) -> dict:
    if left.constraint_root != right.constraint_root:
        raise SymbolicTensorError("GLOBAL_CONSTRAINT_ROOT_MISMATCH")
    if operation not in ("ORDERED_MUL", "ADD"):
        raise SymbolicTensorError("UNREGISTERED_TENSOR_OPERATOR")
    if operation == "ORDERED_MUL":
        P = left.P * right.P
    else:
        P = left.P + right.P
    # The result is only a derived index/constructor. No new runtime state.
    record = {
        "schema": SCHEMA,
        "operator": operation,
        "ordered_inputs": [
            {"P": str(item.P), "modality": item.modality,
             "hash216_lineage": item.hash216_lineage}
            for item in (left, right)
        ],
        "derived_P": str(P),
        "global_constraint_root": left.constraint_root,
        "metadata_link_only": True,
        "same_governing_tensor_geometry": True,
        "new_canonical_state_minted": False,
        "result_hash216_authoritative": False,
        "global_hnan_closure_proved": False,
        "vm81_admission": False,
        "full_tensor_materialized": False,
    }
    record["constructor_witness_sha256"] = sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":")
    ).encode("ascii")).hexdigest()
    return record
