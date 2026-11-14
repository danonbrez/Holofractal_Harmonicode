"""Pass 220 V170: source-bound Module194 ordered-product proof obligations.

The Lean certificate requires externally established exact AB=P4 and
BA=-P4 equations. This binding deliberately cannot construct such a
certificate from browser source text, a digest, or the inherited C 1.63
rule checks. The inherited C checks cover ordering and HNAN rules, not
the complete 81-entry input-specific multiplication.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
from typing import Any

from hhs_runtime.hhs_pass220_v169_module194_concrete_lean_instance_v1 import (
    bind_concrete_structural_instance,
)
from hhs_runtime.hhs_pass220_v167_module194_typed_closure_packet_v1 import (
    typed_packet, validate_packet,
)

SCHEMA = "HHS_PASS220_V170_MODULE194_ORDERED_PRODUCT_PROOF_DEPENDENCY_V1"
LEAN_PATH = "formal/lean/HHS/Pass220/Module194OrderedProduct.lean"
REQUIRED = (
    "typed_pair_not_equal",
    "direct_product",
    "reverse_product",
    "signed_pair_zero_sum",
    "nonzero_quartic_forbids_commutation",
    "typed_distinction_independent_of_quartic",
)


class V170OrderedProductError(ValueError):
    pass


def inspect_ordered_product_dependency(
    source: bytes,
    native_library: Any,
    *,
    repository_root: Path = Path("."),
    require_upload_identity: bool = True,
) -> dict:
    inherited = bind_concrete_structural_instance(
        source,
        native_library,
        repository_root=repository_root,
        require_upload_identity=require_upload_identity,
    )
    if (inherited.get("canonical_VM81_admission") is not False or
        inherited.get("noncommutative_AB_BA_product_identity_proved") is not False or
        inherited.get("input_specific_HNAN_delta_e_closure_proved") is not False):
        raise V170OrderedProductError("V170_INHERITED_PROOF_SCOPE_REJECTED")
    packet = typed_packet()
    source_hash = validate_packet(packet)
    if inherited["typed_packet_sha256"] != source_hash:
        raise V170OrderedProductError("V170_MODULE194_TYPED_PACKET_DRIFT")
    if not all(x in packet["relations"] for x in (
        ("OrderedProduct", ("A", "B"), "+P^4"),
        ("OrderedProduct", ("B", "A"), "-P^4"),
        ("DistinctIdentity", "A", "B"),
    )):
        raise V170OrderedProductError("V170_ORDERED_PRODUCT_RELATIONS_REQUIRED")
    try:
        data = (Path(repository_root) / LEAN_PATH).read_bytes()
        text = data.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise V170OrderedProductError("V170_LEAN_SOURCE_UNAVAILABLE") from exc
    if "namespace HHS.Pass220.Module194OrderedProduct" not in text:
        raise V170OrderedProductError("V170_LEAN_NAMESPACE_DRIFT")
    for theorem in REQUIRED:
        if not re.search(r"(?m)^theorem\s+" + re.escape(theorem) + r"\b", text):
            raise V170OrderedProductError("V170_LEAN_THEOREM_MISSING:" + theorem)
    for condition in (
        "directEquation : abValue = p4",
        "mirrorEquation : baValue = -p4",
        "(h : c.p4 ≠ 0)",
        "structure TypedOperandPair",
        "structure OrderedProductCertificate",
    ):
        if condition not in text:
            raise V170OrderedProductError("V170_LEAN_PREMISE_DRIFT")
    if re.search(r"\b(?:sorry|admit)\b", text, re.I):
        raise V170OrderedProductError("V170_LEAN_PLACEHOLDER")
    return {
        "schema": SCHEMA,
        "module194_source_sha256": inherited["module194_source_sha256"],
        "module194_typed_packet_sha256": source_hash,
        "inherited_structural_lean_source_sha256":
            inherited["concrete_lean_source_sha256"],
        "ordered_product_lean_source_sha256": sha256(data).hexdigest(),
        "required_theorems": list(REQUIRED),
        "input_specific_AB_value_required": True,
        "input_specific_BA_value_required": True,
        "nonzero_P4_witness_required_for_distinct_products": True,
        "inherited_native_hnan_signature64":
            inherited["inherited_native_hnan_signature64"],
        "lean_kernel_executed_in_this_function": False,
        "input_specific_direct_product_equation_proved": False,
        "input_specific_reverse_product_equation_proved": False,
        "input_specific_lean_certificate_constructed": False,
        "interior_outer_delta_e_closure_proved": False,
        "full_196_module_course_coverage_verified": False,
        "module194_force_equivalence_verified": False,
        "canonical_vm81_admission": False,
        "hash72_hash216_minted": False,
    }
