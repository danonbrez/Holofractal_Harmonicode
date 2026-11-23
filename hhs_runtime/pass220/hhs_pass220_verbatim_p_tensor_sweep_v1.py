"""Pass 220: source-locked, non-evaluating native P-sweep ingress.

Only immutable candidate proposals are produced. All equation semantics,
ordered List transport, dynamic p/q/a/b/c/A/B/m binding, VM81 execution,
Hash72/Hash216 commitment, and replay belong to the pre-existing native
HARMONICODE admission path, not to this module.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

SCHEMA = "HHS_PASS220_VERBATIM_P_TENSOR_SWEEP_V1"
BINDING_SCHEMA = "HHS_NATIVE_P_VM81_5184_BINDING_V1"
SOURCE_PATH = Path("contracts/pass220/PASS_220_VERBATIM_P_TENSOR_SWEEP_V1.harmonicode")
SOURCE_SHA256 = "092b8b397abee80abb0053f979f4a62dcdc4775dc559d45e321405742c332095"
SOURCE_BYTES = 180
SOURCE_CHARACTERS = 176
MAX_CANDIDATES = 72
REQUIRED_GLOBAL_ORDERED_CONSTRAINT = "P⁴=AB=c⁴"
GENESIS_REFERENCE = "P²=c² (GENESIS NUCLEUS ONLY; NOT A UNIVERSAL SWEEP CONSTRAINT)"


class VerbatimPSweepError(ValueError):
    """The caller supplied an invalid or non-native sweep candidate."""


def _reject_ieee(node: Any) -> None:
    if isinstance(node, float):
        raise VerbatimPSweepError("FLOAT_SCALAR_INPUT_FORBIDDEN")
    if isinstance(node, Mapping):
        for k, v in node.items():
            _reject_ieee(k)
            _reject_ieee(v)
    elif isinstance(node, (tuple, list)):
        for v in node:
            _reject_ieee(v)


def _diagnostic_digest(record: Mapping[str, Any]) -> str:
    """Ordinary SHA-256 for proposal integrity; never a Hash72/216 receipt."""
    _reject_ieee(record)
    payload = json.dumps(record, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(b"HHS:P_SWEEP:NONAUTHORITATIVE:V1\0" + payload).hexdigest()


def _repo_root(root: str | Path | None) -> Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parents[2]


def verify_verbatim_source(root: str | Path | None = None) -> dict[str, Any]:
    """Pin the exact UTF-8 source; do not parse it with scalarizing host syntax."""
    raw = (_repo_root(root) / SOURCE_PATH).read_bytes()
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    if (actual_sha256 != SOURCE_SHA256 or len(raw) != SOURCE_BYTES):
        raise VerbatimPSweepError("VERBATIM_SOURCE_IDENTITY_DRIFT")
    source = raw.decode("utf-8", errors="strict")
    if len(source) != SOURCE_CHARACTERS:
        raise VerbatimPSweepError("VERBATIM_SOURCE_WIDTH_DRIFT")

    # These are source spans only: no Boolean, scalar, or algebraic evaluation.
    list_starts = [m.start() for m in re.finditer(r"List\(", source)]
    if len(list_starts) != 2:
        raise VerbatimPSweepError("ORDERED_LIST_COUNT_DRIFT")
    list_spans: list[list[int]] = []
    for start in list_starts:
        depth = 0
        end = None
        for pos in range(start + 4, len(source)):
            if source[pos] == "(":
                depth += 1
            elif source[pos] == ")":
                depth -= 1
                if depth == 0:
                    end = pos + 1
                    break
        if end is None:
            raise VerbatimPSweepError("ORDERED_LIST_UNCLOSED")
        list_spans.append([start, end])
    equalities = [
        {"operator": match.group(), "start": match.start(), "end": match.end()}
        for match in re.finditer(r"(?<![=])(?:==|=)(?![=])", source)
    ]
    if [e["operator"] for e in equalities] != ["==", "==", "==", "=", "==", "=", "=="]:
        raise VerbatimPSweepError("ORDERED_RELATION_SEQUENCE_DRIFT")
    p_spans = [[m.start(), m.end()] for m in re.finditer(r"(?<![A-Za-z_])P(?![A-Za-z_])", source)]
    if len(p_spans) != 4:
        raise VerbatimPSweepError("P_OCCURRENCE_COUNT_DRIFT")
    return {
        "path": str(SOURCE_PATH),
        "source_sha256": actual_sha256,
        "source_bytes": len(raw),
        "source_characters": len(source),
        "source_preserved_verbatim": True,
        "ordered_list_spans": list_spans,
        "relation_spans": equalities,
        "P_symbol_spans": p_spans,
        "syntactic_spans_only": True,
        "scalar_interpretation_applied": False,
    }


def _binding(binding: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(binding, Mapping):
        raise VerbatimPSweepError("TYPED_NATIVE_P_BINDING_REQUIRED")
    _reject_ieee(binding)
    expected_fields = {"schema", "symbol", "vm81_cell", "vm81_opcode", "harmonicode_5184", "predecessor_hash216", "native_receipt_ref"}
    if set(binding) != expected_fields:
        raise VerbatimPSweepError("P_BINDING_FIELDS_NOT_TYPED_OR_COMPLETE")
    if binding.get("schema") != BINDING_SCHEMA or binding.get("symbol") != "P":
        raise VerbatimPSweepError("NATIVE_P_SCHEMA_OR_SYMBOL_MISMATCH")
    cell, opcode = binding.get("vm81_cell"), binding.get("vm81_opcode")
    if (type(cell) is not int or not 0 <= cell < 81
            or type(opcode) is not int or not 0 <= opcode < 64):
        raise VerbatimPSweepError("VM5184_ADDRESS_INVALID")
    state = binding.get("harmonicode_5184")
    if not isinstance(state, str) or len(state) != 5184:
        raise VerbatimPSweepError("HARMONICODE_5184_CHAR_STATE_REQUIRED")
    previous = binding.get("predecessor_hash216")
    if (not isinstance(previous, str) or len(previous) != 216
            or any(ord(ch) < 33 or ord(ch) > 126 for ch in previous)):
        raise VerbatimPSweepError("PREDECESSOR_HASH216_REQUIRED")
    receipt_ref = binding.get("native_receipt_ref")
    if not isinstance(receipt_ref, str) or not receipt_ref.strip():
        raise VerbatimPSweepError("NATIVE_PROVENANCE_REFERENCE_REQUIRED")
    # No attempt to validate receipt truth from its textual shape.
    return {
        "schema": BINDING_SCHEMA,
        "symbol": "P",
        "vm81_cell": cell,
        "vm81_opcode": opcode,
        "vm5184_address": 64 * cell + opcode,
        "harmonicode_5184": state,
        "predecessor_hash216": previous,
        "native_receipt_ref": receipt_ref,
        "binding_authenticity_verified": False,
        "scalarized": False,
    }


def stage_verbatim_p_sweep(
    p_bindings: Sequence[Mapping[str, Any]],
    *, root: str | Path | None = None,
) -> dict[str, Any]:
    """Stage typed P candidates; leave all native values/execution unresolved.

    Caller must submit actual native candidate bindings. Synthetic fixture strings
    pass shape validation only, never VM81 admission or canonical closure.
    """
    if isinstance(p_bindings, (str, bytes)) or not isinstance(p_bindings, Sequence):
        raise VerbatimPSweepError("ORDERED_NATIVE_P_BINDING_SEQUENCE_REQUIRED")
    if not 1 <= len(p_bindings) <= MAX_CANDIDATES:
        raise VerbatimPSweepError("SWEEP_CARDINALITY_OUT_OF_RANGE")
    source = verify_verbatim_source(root)
    candidates = []
    seen = set()
    for ordinal, item in enumerate(p_bindings):
        bind = _binding(item)
        diagnostic_id = _diagnostic_digest(bind)
        if diagnostic_id in seen:
            raise VerbatimPSweepError("DUPLICATE_TYPED_P_STATE")
        seen.add(diagnostic_id)
        candidates.append({
            "ordinal": ordinal,
            "typed_P_binding": bind,
            "binding_diagnostic_sha256": diagnostic_id,
            "native_values": None,
            "evaluation_status": "PENDING_SIGNED_VM81_WHOLE_EXPRESSION_EXECUTION",
            "hash72_receipt": None,
            "hash216_transition": None,
            "canonical_mutation": False,
        })
    return {
        "schema": SCHEMA,
        "source": source,
        "global_ordered_closure_constraint": REQUIRED_GLOBAL_ORDERED_CONSTRAINT,
        "genesis_reference": GENESIS_REFERENCE,
        "genesis_equality_universally_enforced": False,
        "p_sweep_is_native_typed": True,
        "ordered_product_AB_preserved": True,
        "ordered_List_transport_pending": True,
        "dependencies": ["p", "q", "a", "b", "c", "A", "B", "m"],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "hash72_commit_authority": False,
        "hash216_commit_authority": False,
        "canonical_vm81_mutation_authority": False,
        "requires_existing_singleton_mutation_authority": True,
        "status": "CANDIDATE_STAGED_NATIVE_EXECUTION_REQUIRED",
    }
