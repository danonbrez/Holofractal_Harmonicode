"""Pass 220 V161 — Module 194 -> inherited HNAN/Lane 5 read-only witness.

This is evidence composition, not a competing HNAN gate: original bytes are
validated by V160; the inherited exact candidate verifies its existing
Lo Shu/phase/Hash72/address obligations; the source-frozen course provenance
checker identifies its own proof requirements. No caller-controlled receipt
can turn an unexecuted course obligation into an admitted one.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from hhs_runtime.hhs_pass220_v160_module194_source_address_preflight_v1 import (
    audit_source,
)
from hhs_runtime.pass220.hnan_lane5_exact_witness_v1 import (
    verify_read_only_candidate,
)
from hhs_runtime.hhs_pass220_course_module_gate_provenance_v1 import (
    course_module_gate_inventory,
)

SCHEMA = "HHS_PASS_220_V161_MODULE194_INHERITED_HNAN_WITNESS_V1"
REQUIRED_COURSE_GATES = (0, 3, 4, 5, 9, 11)


class V161WitnessError(ValueError):
    pass


def inspect_module194_hnan_boundary(
    source: bytes, *, repository_root: Path = Path("."),
    require_upload_identity: bool = True,
) -> dict[str, Any]:
    """Compute inherited read-only witnesses; no mutable runtime arguments."""
    audited = audit_source(source, require_upload_identity=require_upload_identity)
    inherited = verify_read_only_candidate()
    if not isinstance(inherited, dict) or (
        inherited.get("candidate_only") is not True
        or inherited.get("vm81_mutation_authority") is not False
        or inherited.get("matrix_factorization_exact") is not True
        or inherited.get("hash72_reciprocal_exact") is not True
        or inherited.get("bigint_5184_addresses_bijective") is not True
    ):
        raise V161WitnessError("V161_INHERITED_READ_ONLY_GATE_REJECTED")
    inventory = course_module_gate_inventory(Path(repository_root))
    if (inventory.get("whole_course_proved") is not False
        or inventory.get("verified_native_modules") != 0
        or inventory.get("hash216_minted") is not False
        or inventory.get("module_count") != 13):
        raise V161WitnessError("V161_UNEXPECTED_COURSE_PROOF_AUTHORITY")
    modules = inventory["ordered_modules"]
    requirements = []
    for i in REQUIRED_COURSE_GATES:
        module = modules[i]
        if module["index"] != i or module["native_verification"] != "NOT_EXECUTED":
            raise V161WitnessError("V161_COURSE_PROVENANCE_DRIFT")
        requirements.append({
            "module_index": i,
            "source_section_sha256": module["byte_sha256"],
            "native_verification": "NOT_EXECUTED",
        })
    return {
        "schema": SCHEMA,
        "module194_source_sha256": audited["source_sha256"],
        "module194_source_shape_checked": True,
        "module194_reciprocal_pairs": audited["reciprocal_pairs"],
        "module194_groups": audited["groups"],
        "module194_particle_count": audited["particles"],
        "course_source_sha256": inventory["source_sha256"],
        "course_required_gate_modules": requirements,
        "inherited_hnan_witness_schema": inherited["schema"],
        "inherited_lo_shu_phase_factorization_exact":
            inherited["matrix_factorization_exact"],
        "inherited_phase_gradient_offsets_constant":
            inherited["gradient_offsets_constant"],
        "inherited_hash72_reciprocal_exact":
            inherited["hash72_reciprocal_exact"],
        "inherited_5184_addresses_bijective":
            inherited["bigint_5184_addresses_bijective"],
        "course_ordered_ab_ba_native_proof_executed": False,
        "course_hnan_passthrough_native_proof_executed": False,
        "module194_hnan_center_native_gate_executed": False,
        "module194_force_equivalence_verified": False,
        "lane5_physical_source_provenance_verified": False,
        "vm81_mutation_authority": False,
        "hash72_hash216_minted": False,
    }
