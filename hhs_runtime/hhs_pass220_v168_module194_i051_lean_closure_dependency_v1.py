"""Pass 220 V168: typed Module194 closure -> existing I051 Lean proof identity.

Read-only *dependency binding*:
- executes V167 through the existing Pass219 C ABI;
- checks the I051 contract's closure names against actual Lean declarations;
- fingerprints the complete native Lean source bytes;
- never represents conditional Lean theorems as proof that the concrete
  Module194 A/B tensor satisfies their hypotheses.

The complete canonical 196-module course and VM81 admission remain distinct.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any
import json
import re

from hhs_runtime.hhs_pass220_v167_module194_typed_closure_packet_v1 import (
    inspect_typed_closure,
    typed_packet,
    validate_packet,
)
from hhs_runtime.hhs_pass220_i051_native_lean_alignment_v1 import (
    LEAN_MODULE, LEAN_THEOREMS, native_lean_alignment_contract,
)

SCHEMA = "HHS_PASS220_V168_MODULE194_I051_LEAN_CLOSURE_DEPENDENCY_V1"
LEAN_PATH = "formal/lean/HHS/Alignment/ReciprocalTensor.lean"
REQUIRED_THEOREMS = (
    "admitted_requires_ab_p4",
    "admitted_requires_ba_negative_p4",
    "admitted_forbids_unproved_commutation",
)
EXPECTED_CLOSURES = ("AB=P^4", "BA=-P^4")


class V168LeanBindingError(ValueError):
    pass


def _fingerprint(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")).hexdigest()


def inspect_module194_i051_dependency(
    source: bytes,
    native_library: Any,
    *,
    repository_root: Path = Path("."),
    require_upload_identity: bool = True,
) -> dict:
    inherited = inspect_typed_closure(
        source, native_library, require_upload_identity=require_upload_identity,
    )
    if (inherited.get("source_leaf_count") != 81 or
        inherited.get("input_specific_ab_ba_proof_executed") is not False or
        inherited.get("canonical_vm81_admission") is not False):
        raise V168LeanBindingError("V168_INHERITED_CLOSURE_SCOPE_REJECTED")
    packet = typed_packet()
    if inherited["typed_packet_sha256"] != validate_packet(packet):
        raise V168LeanBindingError("V168_TYPED_PACKET_IDENTITY_DRIFT")
    relations = packet["relations"]
    if (("OrderedProduct", ("A", "B"), "+P^4") not in relations or
        ("OrderedProduct", ("B", "A"), "-P^4") not in relations or
        ("DistinctIdentity", "A", "B") not in relations):
        raise V168LeanBindingError("V168_AB_BA_SOURCE_OBLIGATION_MISSING")
    contract = native_lean_alignment_contract()
    if (contract.get("lean_module") != LEAN_MODULE or
        contract.get("direct_closure") != EXPECTED_CLOSURES[0] or
        contract.get("mirror_closure") != EXPECTED_CLOSURES[1] or
        contract.get("runtime_live_kernel_claim") is not False or
        contract.get("vm81_mutation_authority") != "VM81_ONLY" or
        contract.get("hash72_commit_authority") is not False or
        contract.get("hash216_persistence_authority") is not False):
        raise V168LeanBindingError("V168_I051_CONTRACT_DRIFT")
    if not set(REQUIRED_THEOREMS).issubset(LEAN_THEOREMS):
        raise V168LeanBindingError("V168_I051_THEOREM_IDENTITY_MISSING")
    root = Path(repository_root)
    try:
        lean = (root / LEAN_PATH).read_bytes()
        code = lean.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise V168LeanBindingError("V168_NATIVE_LEAN_SOURCE_UNAVAILABLE") from exc
    if "namespace HHS.Alignment.ReciprocalTensor" not in code:
        raise V168LeanBindingError("V168_NATIVE_LEAN_MODULE_MISMATCH")
    for theorem in REQUIRED_THEOREMS:
        if not re.search(r"(?m)^theorem\s+" + re.escape(theorem) + r"\b", code):
            raise V168LeanBindingError("V168_I051_DECLARATION_MISSING:" + theorem)
    # Both declarations are conditionally proven from an existing t.admitted;
    # the condition is not discharged by source matching or by native rules.
    for theorem in REQUIRED_THEOREMS:
        p = code.index("theorem " + theorem)
        next_decl = code.find("\ntheorem ", p + 8)
        section = code[p:next_decl if next_decl >= 0 else len(code)]
        if "(h : t.admitted)" not in section:
            raise V168LeanBindingError("V168_I051_CONDITIONAL_HYPOTHESIS_MISSING")
    if re.search(r"\b(sorry|admit)\b", code, flags=re.IGNORECASE):
        raise V168LeanBindingError("V168_I051_UNVERIFIED_PROOF_PLACEHOLDER")
    return {
        "schema": SCHEMA,
        "module194_source_sha256": inherited["module194_source_sha256"],
        "module194_typed_packet_sha256": inherited["typed_packet_sha256"],
        "module194_exact_tensor_sha256": inherited["ordered_tensor_ast_sha256"],
        "i051_lean_module": LEAN_MODULE,
        "i051_lean_source_sha256": sha256(lean).hexdigest(),
        "i051_required_conditional_theorems": list(REQUIRED_THEOREMS),
        "i051_contract_closure_names": list(EXPECTED_CLOSURES),
        "lean_dependency_binding_sha256": _fingerprint([
            inherited["typed_packet_sha256"], sha256(lean).hexdigest(),
            REQUIRED_THEOREMS, inherited["native_inherited_hnan_signature64"],
        ]),
        "inherited_native_hnan_signature64":
            inherited["native_inherited_hnan_signature64"],
        "inherited_native_order_rejections_observed": True,
        "lean_source_declarations_matched": True,
        "lean_kernel_executed_in_this_check": False,
        "module194_specific_lean_hypotheses_discharged": False,
        "module194_specific_ab_ba_closure_proved": False,
        "module194_interior_outer_closure_proved": False,
        "complete_canonical_course_coverage_verified": False,
        "physical_producer_equivalence_verified": False,
        "vm81_admission": False,
        "hash72_hash216_minted": False,
    }
