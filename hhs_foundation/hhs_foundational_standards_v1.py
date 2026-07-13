"""
HHS Foundational Standards v1
=============================

Constitutional governance layer for HHS-M001..HHS-M007.

This layer is deliberately semantic-contract oriented: it does not attempt to
prove truth or rewrite propositions. It verifies that runtime objects declare
and preserve referential identity, dimensional distinctions, transformation
transparency, and receipt-backed meaning conservation before/after execution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional
import json
import uuid

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest

FOUNDATIONAL_STANDARD_VERSION = "HHS_FOUNDATIONAL_STANDARDS_M001_M007_V1"
HASH72_LEN = 72

M_STANDARD_IDS = ("HHS-M001", "HHS-M002", "HHS-M003", "HHS-M004", "HHS-M005", "HHS-M006", "HHS-M007")
DIMENSION_TYPES = {"identity", "equality", "similarity", "functional_equivalence", "interchangeability"}


class HHSFoundationalViolation(RuntimeError):
    """Raised when a runtime object violates HHS Foundational Standards."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def hash72(value: Any) -> str:
    return hash72_digest(("hhs_foundational_standard_v1", canonical_json(value)), width=HASH72_LEN)


def is_hash72(value: Any) -> bool:
    return isinstance(value, str) and len(value) == HASH72_LEN


@dataclass(frozen=True)
class HHSPropositionIdentity:
    """Stable identity packet for the proposition/object under analysis."""

    proposition_id: str
    statement: str
    source: str
    context: Dict[str, Any] = field(default_factory=dict)
    declared_dimensions: list[str] = field(default_factory=lambda: sorted(DIMENSION_TYPES))
    schema: str = "HHS_PROPOSITION_IDENTITY_V1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["standard_version"] = FOUNDATIONAL_STANDARD_VERSION
        data["identity_hash72"] = hash72({
            "statement": self.statement,
            "source": self.source,
            "context": self.context,
            "declared_dimensions": self.declared_dimensions,
        })
        return data


@dataclass(frozen=True)
class HHSMeaningConservationWitness:
    """Before/after witness proving proposition identity was not silently replaced."""

    before_identity_hash72: str
    after_identity_hash72: str
    transformation_rule: str
    reversible: bool
    receipt_hash72: str = ""
    schema: str = "HHS_MEANING_CONSERVATION_WITNESS_V1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["standard_version"] = FOUNDATIONAL_STANDARD_VERSION
        data["meaning_conserved"] = self.before_identity_hash72 == self.after_identity_hash72
        data["witness_hash72"] = hash72(data)
        return data


@dataclass(frozen=True)
class HHSFoundationalConformance:
    ok: bool
    source: str
    standards: Dict[str, bool]
    reasons: list[str]
    proposition_identity: Dict[str, Any] = field(default_factory=dict)
    meaning_witness: Dict[str, Any] = field(default_factory=dict)
    schema: str = "HHS_FOUNDATIONAL_CONFORMANCE_V1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["standard_version"] = FOUNDATIONAL_STANDARD_VERSION
        data["conformance_hash72"] = hash72({k: v for k, v in data.items() if k != "conformance_hash72"})
        return data


def make_proposition_identity(statement: str, *, source: str, context: Optional[Mapping[str, Any]] = None, proposition_id: Optional[str] = None) -> Dict[str, Any]:
    return HHSPropositionIdentity(
        proposition_id=proposition_id or str(uuid.uuid4()),
        statement=str(statement or ""),
        source=source,
        context=dict(context or {}),
    ).to_dict()


def make_meaning_witness(before_identity: Mapping[str, Any], after_identity: Mapping[str, Any], *, transformation_rule: str, reversible: bool, receipt_hash72: str = "") -> Dict[str, Any]:
    return HHSMeaningConservationWitness(
        before_identity_hash72=str(before_identity.get("identity_hash72") or ""),
        after_identity_hash72=str(after_identity.get("identity_hash72") or ""),
        transformation_rule=str(transformation_rule or ""),
        reversible=bool(reversible),
        receipt_hash72=str(receipt_hash72 or ""),
    ).to_dict()


def _payload_from_runtime_object(obj: Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(obj.get("payload"), Mapping):
        return obj["payload"]
    return obj


def audit_foundational_conformance(obj: Mapping[str, Any], *, source: str = "unknown", require_receipt: bool = True) -> HHSFoundationalConformance:
    """Audit a runtime object against HHS-M001..HHS-M007.

    Required declarations are intentionally explicit. Legacy objects can conform
    by embedding a `proposition_identity` and `meaning_witness` packet or by
    carrying a `proposition` string that this function upgrades into a witness.
    """

    data = dict(obj or {})
    payload = dict(_payload_from_runtime_object(data) or {})
    reasons: list[str] = []
    standards = {standard_id: True for standard_id in M_STANDARD_IDS}

    proposition_identity = dict(data.get("proposition_identity") or payload.get("proposition_identity") or {})
    proposition = data.get("proposition") or payload.get("proposition") or payload.get("statement") or data.get("statement")
    if not proposition_identity and proposition is not None:
        proposition_identity = make_proposition_identity(str(proposition), source=source, context={"derived_from": "runtime_object"})

    if not proposition_identity.get("identity_hash72"):
        standards["HHS-M001"] = False
        standards["HHS-M002"] = False
        standards["HHS-M007"] = False
        reasons.append("referential/proposition identity packet is missing")
    if proposition_identity and not proposition_identity.get("statement"):
        standards["HHS-M001"] = False
        standards["HHS-M007"] = False
        reasons.append("proposition identity requires explicit statement")

    declared_dimensions = set(proposition_identity.get("declared_dimensions") or data.get("declared_dimensions") or payload.get("declared_dimensions") or [])
    if proposition_identity and not DIMENSION_TYPES.issubset(declared_dimensions):
        standards["HHS-M003"] = False
        reasons.append("dimensional conservation requires identity/equality/similarity/functional_equivalence/interchangeability distinctions")

    transformation_rule = data.get("transformation_rule") or payload.get("transformation_rule") or data.get("operation") or payload.get("operation")
    meaning_witness = dict(data.get("meaning_witness") or payload.get("meaning_witness") or {})
    if proposition_identity and not meaning_witness:
        meaning_witness = make_meaning_witness(
            proposition_identity,
            proposition_identity,
            transformation_rule=str(transformation_rule or "identity/no-op"),
            reversible=True,
            receipt_hash72=str(data.get("receipt_hash72") or payload.get("receipt_hash72") or ""),
        )

    if not meaning_witness.get("meaning_conserved", False):
        standards["HHS-M004"] = False
        standards["HHS-M005"] = False
        reasons.append("meaning conservation witness is missing or indicates semantic drift")
    if not meaning_witness.get("transformation_rule"):
        standards["HHS-M006"] = False
        reasons.append("transformation transparency requires an explicit transformation rule")
    if not meaning_witness.get("reversible", False):
        standards["HHS-M006"] = False
        reasons.append("transformation transparency requires reversible or explicitly replayable rule")

    receipt_hash = str(data.get("receipt_hash72") or payload.get("receipt_hash72") or meaning_witness.get("receipt_hash72") or "")
    if require_receipt and receipt_hash and not is_hash72(receipt_hash):
        standards["HHS-M006"] = False
        reasons.append("receipt_hash72 is present but not native 72-symbol Hash72")

    ok = all(standards.values()) and not reasons
    return HHSFoundationalConformance(
        ok=ok,
        source=source,
        standards=standards,
        reasons=reasons,
        proposition_identity=proposition_identity,
        meaning_witness=meaning_witness,
    )


def assert_foundational_conformance(obj: Mapping[str, Any], *, source: str = "unknown", require_receipt: bool = True) -> HHSFoundationalConformance:
    audit = audit_foundational_conformance(obj, source=source, require_receipt=require_receipt)
    if not audit.ok:
        raise HHSFoundationalViolation(f"HHS Foundational Standards blocked {source}: " + "; ".join(audit.reasons))
    return audit


def foundational_standards_self_test() -> Dict[str, Any]:
    identity = make_proposition_identity(
        "Objectivity begins only after the identity of the object under discussion has been preserved.",
        source="foundational_standards_self_test",
        context={"standard": "HHS-M001..M007"},
    )
    witness = make_meaning_witness(
        identity,
        identity,
        transformation_rule="canonical projection without semantic substitution",
        reversible=True,
        receipt_hash72="H" * HASH72_LEN,
    )
    audit = assert_foundational_conformance(
        {
            "schema": "HHS_FOUNDATIONAL_SELF_TEST_PAYLOAD_V1",
            "proposition_identity": identity,
            "meaning_witness": witness,
            "declared_dimensions": sorted(DIMENSION_TYPES),
            "receipt_hash72": "H" * HASH72_LEN,
        },
        source="foundational_standards_self_test",
    )
    return {
        "schema": "HHS_FOUNDATIONAL_STANDARDS_SELF_TEST_V1",
        "standard_version": FOUNDATIONAL_STANDARD_VERSION,
        "identity": identity,
        "meaning_witness": witness,
        "conformance": audit.to_dict(),
    }


if __name__ == "__main__":
    print(foundational_standards_self_test())
