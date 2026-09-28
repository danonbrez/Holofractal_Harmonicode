"""Pass 219 Lane 5 1.70 — exact nine-loop feedback formalization.

Consumes only the frozen 1.69 relation/source witnesses and the connected
Wolfram exact receipt. This module is candidate-only and float-free.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "contracts/pass219/PASS_219_LANE5_NINE_LOOP_FEEDBACK_1_70.json"
WOLFRAM_RECEIPT_PATH = (
    ROOT / "evidence/pass219/lane5_nine_loop_feedback_1_70_wolfram_20260927_v1.output.json"
)
SCHEMA = "HHS_PASS219_LANE5_NINE_LOOP_FEEDBACK_1_70"
HASH216_LEN = 216

PARENT_RELATION_SHA256 = "4acc66c250129d5a42f976d673027313707633012b2de6f85d6491a4083ed73a"
PARENT_SUPPORT_SHA256 = "64cd7ae9027ef41969948efc35b1273ba03ba3f759c076700d8a09940ebbf54d"
WOLFRAM_MATERIAL_SHA256 = "ba58c70820f0f3e5bd3a352b89441face87d07ea7ce776b1b8481c21393c69e1"
FEEDBACK_PAYLOAD_SHA256 = "78f2cc37e9304017cf0b6a233f2cb5ab080757fec57e6eb5897295bf0d2bed70"
GENESIS_IDENTITY = "F(x,y,a,b)=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2"


class Lane5NineLoopFeedbackError(ValueError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Lane5NineLoopFeedbackError(f"floating value forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    _reject_float(contract)
    if contract.get("schema") != SCHEMA:
        raise Lane5NineLoopFeedbackError("1.70 contract schema mismatch")
    return contract


def load_wolfram_receipt() -> dict[str, Any]:
    receipt = json.loads(WOLFRAM_RECEIPT_PATH.read_text(encoding="utf-8"))
    _reject_float(receipt)
    if receipt.get("schema") != SCHEMA + "_WOLFRAM_V1":
        raise Lane5NineLoopFeedbackError("Wolfram receipt schema mismatch")
    if receipt.get("status") != "PASS":
        raise Lane5NineLoopFeedbackError("Wolfram receipt did not pass")
    if receipt.get("check_count") != 13 or receipt.get("pass_count") != 13:
        raise Lane5NineLoopFeedbackError("Wolfram receipt count mismatch")
    if not all(bool(value) for value in receipt.get("checks", {}).values()):
        raise Lane5NineLoopFeedbackError("Wolfram receipt contains a failed check")
    if receipt.get("feedback_material_sha256") != WOLFRAM_MATERIAL_SHA256:
        raise Lane5NineLoopFeedbackError("Wolfram material identity mismatch")
    if receipt.get("genesis_identity_verbatim") != GENESIS_IDENTITY:
        raise Lane5NineLoopFeedbackError("verbatim Genesis identity mismatch")
    return receipt


def _feedback_payload(contract: Mapping[str, Any]) -> dict[str, Any]:
    exact = contract["exact_feedback"]
    learning = contract["learning_feedback"]
    parent = contract["parent_evidence"]
    return {
        "schema": SCHEMA + "_PAYLOAD",
        "parent_relation_sha256": parent["relation_sha256"],
        "parent_support_sha256": parent["e0_nonzero_support_sha256"],
        "parent_source_sha256": parent["source_sha256"],
        "wolfram_feedback_material_sha256": contract["wolfram_receipt"][
            "feedback_material_sha256"
        ],
        "root_metadata_seed": {
            "numerator": exact["root_metadata_seed"]["numerator"],
            "denominator": exact["root_metadata_seed"]["denominator"],
        },
        "genesis_identity_verbatim": exact["genesis_identity_verbatim"],
        "deviation_vector": learning["deviation_vector"],
        "coverage": {
            "certified_rational": exact["foreign_reconstruction_coverage"][
                "certified_rational"
            ],
            "two_prime_only": exact["foreign_reconstruction_coverage"][
                "two_prime_only"
            ],
            "comparison_total": exact["comparison"]["total_rows"],
            "comparison_two_prime_only": exact["comparison"]["two_prime_only_rows"],
        },
        "validated_additions": learning["validated_additions"],
        "rejected_assumptions": learning["rejected_assumptions"],
        "candidate_only": True,
    }


def verify_contract(
    contract: Mapping[str, Any] | None = None,
    wolfram_receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    c = dict(load_contract() if contract is None else contract)
    _reject_float(c)
    w = dict(load_wolfram_receipt() if wolfram_receipt is None else wolfram_receipt)
    _reject_float(w)

    parent = c["parent_evidence"]
    exact = c["exact_feedback"]
    learning = c["learning_feedback"]
    gate = c["composition_gate"]

    coverage = exact["foreign_reconstruction_coverage"]
    certified = coverage["certified_rational"]
    two_prime = coverage["two_prime_only"]
    comparison = exact["comparison"]
    matrix = exact["matrix"]

    checks = {
        "parent_relation_identity": parent["relation_sha256"] == PARENT_RELATION_SHA256,
        "parent_support_identity": (
            parent["e0_nonzero_support_sha256"] == PARENT_SUPPORT_SHA256
        ),
        "matrix_entries_close": matrix["rows"] * matrix["columns"] == matrix["entries"],
        "coverage_partition_closes": (
            certified["numerator"] + two_prime["numerator"]
            == certified["denominator"]
            == two_prime["denominator"]
            == matrix["nonzero_coordinates"]
        ),
        "foreign_reconstruction_not_overclaimed": coverage["complete"] is False,
        "comparison_partition_closes": (
            sum(comparison["observed_pattern_partition"]) == comparison["total_rows"]
        ),
        "genesis_identity_verbatim": exact["genesis_identity_verbatim"] == GENESIS_IDENTITY,
        "root_seed_exact": exact["root_metadata_seed"] == {
            "numerator": 179971179971,
            "denominator": 1000000,
            "display": "179971.179971",
        },
        "wolfram_exact_receipt": (
            w.get("status") == "PASS"
            and w.get("check_count") == 13
            and w.get("pass_count") == 13
            and w.get("feedback_material_sha256") == WOLFRAM_MATERIAL_SHA256
        ),
        "rejected_container_assumption": (
            learning["deviation_vector"]["literal_container_identity_assumption"] == -1
            and learning["rejected_assumptions"] == [
                "literal_cross_prime_container_identity"
            ]
        ),
        "hash216_parent_feedback_additive": (
            learning["deviation_vector"]["hash216_replay"] == 1
            and learning["deviation_vector"]["logical_representation_equivalence"] == 1
            and learning["deviation_vector"]["support_geometry"] == 1
        ),
        "authority_boundary": (
            gate["candidate_only"] is True
            and gate["canonical_vm81_mutation_authority"] is False
            and gate["canonical_hash72_authority"] is False
            and gate["canonical_hash216_authority"] is False
            and gate["canonical_persistence_authority"] is False
            and gate["floating_point_canonical_authority"] is False
        ),
    }
    if not all(checks.values()):
        failed = sorted(key for key, value in checks.items() if not value)
        raise Lane5NineLoopFeedbackError(
            "1.70 contract verification failed: " + ",".join(failed)
        )

    payload = _feedback_payload(c)
    payload_sha256 = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    if payload_sha256 != c["feedback_payload_sha256"]:
        raise Lane5NineLoopFeedbackError("feedback payload SHA-256 mismatch")
    if payload_sha256 != FEEDBACK_PAYLOAD_SHA256:
        raise Lane5NineLoopFeedbackError("feedback payload frozen identity mismatch")

    return {
        "schema": SCHEMA + "_CONTRACT_RECEIPT",
        "checks": checks,
        "payload": payload,
        "feedback_payload_sha256": payload_sha256,
        "wolfram_feedback_material_sha256": WOLFRAM_MATERIAL_SHA256,
        "candidate_only": True,
        "canonical_transition_ready": False,
    }


def build_learning_feedback() -> dict[str, Any]:
    contract = load_contract()
    verified = verify_contract(contract)
    exact = contract["exact_feedback"]
    learning = contract["learning_feedback"]
    return {
        "schema": SCHEMA + "_LEARNING_FEEDBACK",
        "parent_relation_sha256": PARENT_RELATION_SHA256,
        "parent_support_sha256": PARENT_SUPPORT_SHA256,
        "deviation_vector": dict(learning["deviation_vector"]),
        "coverage_exact": {
            "certified_rational": dict(
                exact["foreign_reconstruction_coverage"]["certified_rational"]
            ),
            "two_prime_only": dict(
                exact["foreign_reconstruction_coverage"]["two_prime_only"]
            ),
        },
        "validated_additions": list(learning["validated_additions"]),
        "rejected_assumptions": list(learning["rejected_assumptions"]),
        "genesis_identity_verbatim": GENESIS_IDENTITY,
        "root_metadata_seed": {
            "numerator": 179971179971,
            "denominator": 1000000,
        },
        "feedback_payload_sha256": verified["feedback_payload_sha256"],
        "wolfram_feedback_material_sha256": WOLFRAM_MATERIAL_SHA256,
        "native_hash216_required": True,
        "native_hash216_replay_verified": False,
        "canonical_transition_ready": False,
        "candidate_only": True,
    }


def bind_native_hash216(
    feedback: Mapping[str, Any],
    *,
    candidate_hash216: str,
    replay_hash216: str,
    native_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    left = str(candidate_hash216)
    right = str(replay_hash216)
    if len(left) != HASH216_LEN or len(right) != HASH216_LEN:
        raise Lane5NineLoopFeedbackError("native Hash216 must contain 216 symbols")
    if left != right:
        raise Lane5NineLoopFeedbackError("native Hash216 replay mismatch")
    if str(native_receipt.get("feedback_candidate_hash216", "")) != left:
        raise Lane5NineLoopFeedbackError("native receipt Hash216 mismatch")

    required = (
        "accepted",
        "parent_1_69_verified",
        "relation_identity_verified",
        "wolfram_receipt_verified",
        "feedback_payload_verified",
        "coverage_verified",
        "genesis_identity_verified",
        "deviation_vector_verified",
        "hash216_replay_verified",
        "candidate_only",
    )
    if not all(bool(native_receipt.get(key, False)) for key in required):
        raise Lane5NineLoopFeedbackError("native 1.70 receipt is incomplete")

    for key in (
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "canonical_persistence_authority",
        "floating_point_canonical_authority",
    ):
        if bool(native_receipt.get(key, False)):
            raise Lane5NineLoopFeedbackError(f"forbidden authority exposed: {key}")

    bound = dict(feedback)
    bound["native_feedback_candidate_hash216"] = left
    bound["native_hash216_replay_verified"] = True
    bound["canonical_transition_ready"] = False
    bound["candidate_only"] = True
    return bound
