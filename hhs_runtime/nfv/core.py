from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from fractions import Fraction
from typing import Any, Callable, Mapping
import json

from python.hhs_gfcc.core import inherited_hash72, inherited_hash216

CONTRACT_ID = "HHS-NFV-CEN-V1"
PASS_NUMBER = 154
IMPLEMENTATION_VERSION = "HHS_NFV_PASS154_V1"
GENESIS_HASH72 = "H72-NFV-GENESIS"
LOSHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
LOSHU_TRAVERSAL = (4, 9, 2, 3, 5, 7, 8, 1, 6)


class NFVError(ValueError):
    def __init__(self, code: str, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


def canonical(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    elif hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def hash72(value: Any) -> str:
    return inherited_hash72(canonical_bytes(value))


def hash216(value: Any) -> str:
    return inherited_hash216(canonical_bytes(value))


@dataclass(frozen=True)
class LocalizedModulus:
    residue: int
    carry: int
    modulus: int
    centered: bool = True
    recursive_scale: int = 0
    loshu_orientation: int = 5
    logical_version: int = 0
    allocation_generation: int = 0

    def __post_init__(self) -> None:
        if self.modulus <= 0:
            raise NFVError("NFV_INVALID_MODULUS", "modulus must be positive")
        if self.loshu_orientation not in LOSHU_TRAVERSAL:
            raise NFVError("NFV_INVALID_LOSHU_ORIENTATION", "orientation must be one of the Lo Shu values")
        low, high = self.bounds
        if not low <= self.residue < high:
            raise NFVError("NFV_NONCANONICAL_RESIDUE", "residue outside declared interval", {"residue": self.residue, "bounds": [low, high]})

    @property
    def bounds(self) -> tuple[int, int]:
        if not self.centered:
            return 0, self.modulus
        low = -(self.modulus // 2)
        return low, low + self.modulus

    @property
    def exact(self) -> int:
        return self.carry * self.modulus + self.residue

    @classmethod
    def normalize(cls, value: int, modulus: int, *, centered: bool = True, recursive_scale: int = 0, loshu_orientation: int = 5, logical_version: int = 0, allocation_generation: int = 0) -> "LocalizedModulus":
        if modulus <= 0:
            raise NFVError("NFV_INVALID_MODULUS", "modulus must be positive")
        if centered:
            low = -(modulus // 2)
            residue = ((int(value) - low) % modulus) + low
        else:
            residue = int(value) % modulus
        carry = (int(value) - residue) // modulus
        state = cls(residue, carry, modulus, centered, recursive_scale, loshu_orientation, logical_version, allocation_generation)
        if state.exact != int(value):
            raise NFVError("NFV_RECONSTRUCTION_FAILURE", "localized value failed exact reconstruction")
        return state

    def _compatible(self, other: "LocalizedModulus") -> None:
        if (self.modulus, self.centered, self.recursive_scale, self.loshu_orientation) != (other.modulus, other.centered, other.recursive_scale, other.loshu_orientation):
            raise NFVError("NFV_MODULUS_CHART_CONFLICT", "arithmetic requires a common declared chart")

    def add(self, other: "LocalizedModulus") -> "LocalizedModulus":
        self._compatible(other)
        return self.normalize(self.exact + other.exact, self.modulus, centered=self.centered, recursive_scale=self.recursive_scale, loshu_orientation=self.loshu_orientation, logical_version=max(self.logical_version, other.logical_version) + 1, allocation_generation=max(self.allocation_generation, other.allocation_generation))

    def subtract(self, other: "LocalizedModulus") -> "LocalizedModulus":
        self._compatible(other)
        return self.normalize(self.exact - other.exact, self.modulus, centered=self.centered, recursive_scale=self.recursive_scale, loshu_orientation=self.loshu_orientation, logical_version=max(self.logical_version, other.logical_version) + 1, allocation_generation=max(self.allocation_generation, other.allocation_generation))

    def multiply(self, other: "LocalizedModulus") -> "LocalizedModulus":
        self._compatible(other)
        return self.normalize(self.exact * other.exact, self.modulus, centered=self.centered, recursive_scale=self.recursive_scale, loshu_orientation=self.loshu_orientation, logical_version=max(self.logical_version, other.logical_version) + 1, allocation_generation=max(self.allocation_generation, other.allocation_generation))

    def rebase(self, modulus: int, *, centered: bool | None = None, loshu_orientation: int | None = None) -> "LocalizedModulus":
        return self.normalize(self.exact, modulus, centered=self.centered if centered is None else centered, recursive_scale=self.recursive_scale, loshu_orientation=self.loshu_orientation if loshu_orientation is None else loshu_orientation, logical_version=self.logical_version + 1, allocation_generation=self.allocation_generation)

    def promote_carry(self, parent_modulus: int) -> tuple["LocalizedModulus", "LocalizedModulus"]:
        parent = self.normalize(self.carry, parent_modulus, centered=self.centered, recursive_scale=self.recursive_scale + 1, loshu_orientation=self.loshu_orientation, logical_version=self.logical_version + 1, allocation_generation=self.allocation_generation)
        local = replace(self, carry=0, logical_version=self.logical_version + 1)
        return local, parent

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"exact": self.exact}


@dataclass(frozen=True)
class LocalizedRational:
    numerator: LocalizedModulus
    denominator: LocalizedModulus

    def __post_init__(self) -> None:
        if self.denominator.exact == 0:
            raise NFVError("NFV_ZERO_DENOMINATOR", "localized rational denominator reconstructs to zero")

    @property
    def exact(self) -> Fraction:
        return Fraction(self.numerator.exact, self.denominator.exact)

    @classmethod
    def localize(cls, numerator: int, denominator: int, *, numerator_modulus: int, denominator_modulus: int, centered: bool = True, loshu_orientation: int = 5) -> "LocalizedRational":
        if denominator == 0:
            raise NFVError("NFV_ZERO_DENOMINATOR", "denominator must not be zero")
        reduced = Fraction(numerator, denominator)
        return cls(LocalizedModulus.normalize(reduced.numerator, numerator_modulus, centered=centered, loshu_orientation=loshu_orientation), LocalizedModulus.normalize(reduced.denominator, denominator_modulus, centered=centered, loshu_orientation=loshu_orientation))

    def to_dict(self) -> dict[str, Any]:
        return {"numerator": self.numerator.to_dict(), "denominator": self.denominator.to_dict(), "exact": [self.exact.numerator, self.exact.denominator]}


@dataclass(frozen=True)
class NFVObject:
    object_type: str
    state: Mapping[str, Any]
    constraints: tuple[str, ...]
    dependencies: tuple[str, ...]
    authority_root: str
    version: int = 0
    generation: int = 0
    receipt_head: str = GENESIS_HASH72
    object_index: str = ""
    lifecycle: str = "COMMITTED"

    def __post_init__(self) -> None:
        if not self.authority_root:
            raise NFVError("NFV_MISSING_VM81_AUTHORITY", "authority root is mandatory")
        payload = self.identity_payload()
        expected = hash216(payload)
        if self.object_index and self.object_index != expected:
            raise NFVError("NFV_HASH216_IDENTITY_MISMATCH", "object index does not match canonical identity")
        object.__setattr__(self, "object_index", expected)

    def identity_payload(self) -> dict[str, Any]:
        return {"domain": "HHS-NFV-OBJECT-V1", "contract_id": CONTRACT_ID, "object_type": self.object_type, "state": canonical(self.state), "constraints": list(self.constraints), "dependencies": list(self.dependencies), "authority_root": self.authority_root, "version": self.version, "generation": self.generation, "receipt_head": self.receipt_head, "lifecycle": self.lifecycle}

    def to_dict(self) -> dict[str, Any]:
        return self.identity_payload() | {"object_index": self.object_index}


@dataclass(frozen=True)
class TransitionPackage:
    package_index: str
    target_index: str
    constructor: str
    prior_commitment: str
    candidate_state: Mapping[str, Any]
    inverse_state: Mapping[str, Any]
    authority_root: str
    status: str = "PROVISIONAL"
    receipt: str = ""

    @classmethod
    def prepare(cls, obj: NFVObject, constructor: str, candidate_state: Mapping[str, Any]) -> "TransitionPackage":
        payload = {"domain": "HHS-NFV-PACKAGE-V1", "target": obj.object_index, "constructor": constructor, "prior": hash72(obj.to_dict()), "candidate": canonical(candidate_state), "inverse": canonical(obj.state), "authority_root": obj.authority_root}
        return cls(hash216(payload), obj.object_index, constructor, payload["prior"], payload["candidate"], payload["inverse"], obj.authority_root)

    def commit(self, obj: NFVObject, *, vm81_admit: Callable[[NFVObject, Mapping[str, Any]], bool]) -> tuple[NFVObject, "TransitionPackage"]:
        if self.status != "PROVISIONAL" or obj.object_index != self.target_index or hash72(obj.to_dict()) != self.prior_commitment:
            raise NFVError("NFV_STALE_OR_INVALID_PACKAGE", "package cannot commit against the supplied object")
        if obj.authority_root != self.authority_root:
            raise NFVError("NFV_AUTHORITY_ROOT_MISMATCH", "package authority root changed")
        if not vm81_admit(obj, self.candidate_state):
            raise NFVError("NFV_VM81_REJECTED", "VM81 admission rejected candidate state")
        receipt = hash72({"domain": "HHS-NFV-HASH72-RECEIPT-V1", "parent": obj.receipt_head, "package": self.package_index, "candidate": canonical(self.candidate_state), "authority_root": self.authority_root})
        committed = NFVObject(obj.object_type, canonical(self.candidate_state), obj.constraints, obj.dependencies, obj.authority_root, obj.version + 1, obj.generation, receipt, lifecycle="COMMITTED")
        return committed, replace(self, status="COMMITTED", receipt=receipt)

    def reverse(self, committed: NFVObject, *, vm81_admit: Callable[[NFVObject, Mapping[str, Any]], bool]) -> NFVObject:
        if self.status != "COMMITTED" or not self.receipt or committed.receipt_head != self.receipt:
            raise NFVError("NFV_REVERSAL_EVIDENCE_MISMATCH", "committed receipt does not match package")
        if not vm81_admit(committed, self.inverse_state):
            raise NFVError("NFV_VM81_REVERSE_REJECTED", "VM81 rejected inverse state")
        receipt = hash72({"domain": "HHS-NFV-REVERSE-V1", "parent": committed.receipt_head, "package": self.package_index, "state": canonical(self.inverse_state)})
        return NFVObject(committed.object_type, canonical(self.inverse_state), committed.constraints, committed.dependencies, committed.authority_root, committed.version + 1, committed.generation, receipt, lifecycle="COMMITTED")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
