"""Pass 220 V169: bind concrete Module194 Lean structural instance to V168.

The new Lean theorems are finite-domain/type/direction structural instances.
Full ordered tensor algebra and I051 admitted hypotheses remain unproved here.
No runtime Lean invocation or canonical VM81 admission is claimed.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import re
from typing import Any

from hhs_runtime.hhs_pass220_v168_module194_i051_lean_closure_dependency_v1 import (
    inspect_module194_i051_dependency,
)

SCHEMA="HHS_PASS220_V169_MODULE194_CONCRETE_LEAN_INSTANCE_V1"
LEAN_PATH="formal/lean/HHS/Pass220/Module194TypedClosure.lean"
REQUIRED=(
    "group_address_count", "group_slot_count",
    "lhs_ne_rhs", "all_source_leaves_are_lhs",
    "rhs_not_source_leaf", "ab_ba_directions_distinct",
    "direct_polarity", "mirror_polarity",
    "inverse_polarity", "trinary_exact",
)


class V169LeanInstanceError(ValueError):
    pass


def bind_concrete_structural_instance(
    source: bytes, native_library: Any, *,
    repository_root: Path = Path("."),
    require_upload_identity: bool = True,
) -> dict:
    previous=inspect_module194_i051_dependency(
        source, native_library,
        repository_root=repository_root,
        require_upload_identity=require_upload_identity,
    )
    if (previous.get("module194_specific_ab_ba_closure_proved") is not False or
        previous.get("vm81_admission") is not False or
        previous.get("lean_kernel_executed_in_this_check") is not False):
        raise V169LeanInstanceError("V169_UPSTREAM_PROOF_AUTHORITY_DRIFT")
    try:
        data=(Path(repository_root)/LEAN_PATH).read_bytes()
        code=data.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise V169LeanInstanceError("V169_LEAN_SOURCE_UNAVAILABLE") from exc
    if "namespace HHS.Pass220.Module194TypedClosure" not in code:
        raise V169LeanInstanceError("V169_LEAN_NAMESPACE_DRIFT")
    for theorem in REQUIRED:
        if not re.search(r"(?m)^theorem\s+"+re.escape(theorem)+r"\b",code):
            raise V169LeanInstanceError("V169_LEAN_DECLARATION_MISSING:"+theorem)
    for definition in ("abbrev GroupAddress := Fin 81",
                       "abbrev GroupSlot := Fin 128",
                       "inductive Operand", "inductive ProductDirection",
                       "def trinary : List Int := [-1, 0, 1]"):
        if definition not in code:
            raise V169LeanInstanceError("V169_LEAN_TYPED_SOURCE_DRIFT")
    if re.search(r"\b(sorry|admit)\b", code, re.I):
        raise V169LeanInstanceError("V169_LEAN_PROOF_PLACEHOLDER")
    return {
        "schema":SCHEMA,
        "module194_source_sha256":previous["module194_source_sha256"],
        "typed_packet_sha256":previous["module194_typed_packet_sha256"],
        "inherited_i051_lean_source_sha256":previous["i051_lean_source_sha256"],
        "inherited_native_hnan_signature64":
            previous["inherited_native_hnan_signature64"],
        "concrete_lean_source_path":LEAN_PATH,
        "concrete_lean_source_sha256":sha256(data).hexdigest(),
        "structural_theorem_names":list(REQUIRED),
        "source_81_group_domain_bound":True,
        "source_128_slot_domain_bound":True,
        "source_typed_A_B_distinction_bound":True,
        "source_direct_mirror_phase_order_bound":True,
        "lean_kernel_executed_in_this_function":False,
        "lean_kernel_job_required":"Pass 220 V169 Module194 Concrete Lean Typed Closure",
        "noncommutative_AB_BA_product_identity_proved":False,
        "input_specific_HNAN_delta_e_closure_proved":False,
        "i051_admitted_hypothesis_discharged":False,
        "physical_producer_equivalence_verified":False,
        "canonical_VM81_admission":False,
        "hash72_hash216_minted":False,
    }
