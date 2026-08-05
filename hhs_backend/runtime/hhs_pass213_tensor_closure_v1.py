"""Exact affine closure proofs for Pass 213 Iteration 8."""
from __future__ import annotations

from dataclasses import dataclass
import hmac
import math
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    FULL_HYDRATION_DOMAIN,
    VM5184_G243_DOMAIN,
    VM5184_STATES,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_tensor_geometry_v1 import seed_word

CLOSURE_DOMAINS = {VM5184_STATES, VM5184_G243_DOMAIN, FULL_HYDRATION_DOMAIN}


class Pass213TensorClosureError(RuntimeError):
    pass


def _path_root(domain_size: int, multiplier: int, offset: int) -> str:
    return hash216("closure-path", canonical_bytes({
        "algorithm": "AFFINE-FULL-CYCLE-V1",
        "domain_size": domain_size,
        "multiplier": multiplier,
        "offset": offset,
    }))


def _coprime(seed: bytes, modulus: int) -> int:
    value = seed_word(seed, "closure/multiplier", 0) % modulus or 1
    while math.gcd(value, modulus) != 1:
        value = (value + 1) % modulus or 1
    return value


@dataclass(frozen=True)
class TensorClosureProof:
    domain_size: int
    multiplier: int
    offset: int
    inverse_multiplier: int
    gcd: int
    first_cell: int
    last_cell: int
    closing_successor: int
    sample_root_hash216: str
    path_root_hash216: str
    proof_root_hash216: str

    @classmethod
    def derive(cls, seed: bytes, domain_size: int) -> "TensorClosureProof":
        if domain_size not in CLOSURE_DOMAINS:
            raise Pass213TensorClosureError("PASS213_TENSOR_CLOSURE_DOMAIN_INVALID")
        multiplier = _coprime(seed, domain_size)
        offset = seed_word(seed, "closure/offset", 0) % domain_size
        inverse = pow(multiplier, -1, domain_size)
        samples = [
            {
                "position": position,
                "cell": (multiplier * position + offset) % domain_size,
                "round_trip": inverse * (((multiplier * position + offset) % domain_size) - offset) % domain_size,
            }
            for position in sorted({0, 1, 2, domain_size // 3, domain_size // 2, domain_size - 2, domain_size - 1})
        ]
        sample_root = hash216("moving-tensor-closure-samples", canonical_bytes(samples))
        path_root = _path_root(domain_size, multiplier, offset)
        unsigned = {
            "algorithm": "AFFINE-MODULAR-BIJECTION-PROOF-V1",
            "domain_size": domain_size,
            "multiplier": multiplier,
            "offset": offset,
            "inverse_multiplier": inverse,
            "gcd": 1,
            "first_cell": offset,
            "last_cell": (multiplier * (domain_size - 1) + offset) % domain_size,
            "closing_successor": offset,
            "sample_root_hash216": sample_root,
            "path_root_hash216": path_root,
        }
        proof = cls(
            domain_size=domain_size, multiplier=multiplier, offset=offset,
            inverse_multiplier=inverse, gcd=1, first_cell=offset,
            last_cell=(multiplier * (domain_size - 1) + offset) % domain_size,
            closing_successor=offset, sample_root_hash216=sample_root,
            path_root_hash216=path_root,
            proof_root_hash216=hash216(
                "moving-tensor-closure-proof", canonical_bytes(unsigned)
            ),
        )
        proof.validate()
        return proof

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "algorithm": "AFFINE-MODULAR-BIJECTION-PROOF-V1",
            "domain_size": self.domain_size,
            "multiplier": self.multiplier,
            "offset": self.offset,
            "inverse_multiplier": self.inverse_multiplier,
            "gcd": self.gcd,
            "first_cell": self.first_cell,
            "last_cell": self.last_cell,
            "closing_successor": self.closing_successor,
            "sample_root_hash216": self.sample_root_hash216,
            "path_root_hash216": self.path_root_hash216,
        }

    def to_mapping(self) -> dict[str, Any]:
        return {**self.unsigned_payload(), "proof_root_hash216": self.proof_root_hash216}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "TensorClosureProof":
        proof = cls(
            int(value["domain_size"]), int(value["multiplier"]), int(value["offset"]),
            int(value["inverse_multiplier"]), int(value["gcd"]), int(value["first_cell"]),
            int(value["last_cell"]), int(value["closing_successor"]),
            str(value["sample_root_hash216"]), str(value["path_root_hash216"]),
            str(value["proof_root_hash216"]),
        )
        proof.validate()
        return proof

    def cell(self, position: int) -> int:
        if not 0 <= int(position) < self.domain_size:
            raise Pass213TensorClosureError("PASS213_TENSOR_CLOSURE_POSITION_INVALID")
        return (self.multiplier * int(position) + self.offset) % self.domain_size

    def position(self, cell: int) -> int:
        if not 0 <= int(cell) < self.domain_size:
            raise Pass213TensorClosureError("PASS213_TENSOR_CLOSURE_CELL_INVALID")
        return self.inverse_multiplier * (int(cell) - self.offset) % self.domain_size

    def validate(self) -> None:
        if self.domain_size not in CLOSURE_DOMAINS or self.gcd != 1 or math.gcd(self.multiplier, self.domain_size) != 1:
            raise Pass213TensorClosureError("PASS213_TENSOR_CLOSURE_NOT_BIJECTIVE")
        if self.multiplier * self.inverse_multiplier % self.domain_size != 1:
            raise Pass213TensorClosureError("PASS213_TENSOR_CLOSURE_INVERSE_INVALID")
        if self.first_cell != self.cell(0) or self.last_cell != self.cell(self.domain_size - 1) or self.closing_successor != self.first_cell:
            raise Pass213TensorClosureError("PASS213_TENSOR_CLOSURE_ENDPOINT_INVALID")
        if self.path_root_hash216 != _path_root(self.domain_size, self.multiplier, self.offset):
            raise Pass213TensorClosureError("PASS213_TENSOR_CLOSURE_PATH_ROOT_MISMATCH")
        expected = hash216("moving-tensor-closure-proof", canonical_bytes(self.unsigned_payload()))
        if not hmac.compare_digest(expected, self.proof_root_hash216):
            raise Pass213TensorClosureError("PASS213_TENSOR_CLOSURE_PROOF_ROOT_MISMATCH")

    def materialized_check(self, limit: int = 2_000_000) -> Mapping[str, Any]:
        if self.domain_size > limit:
            raise Pass213TensorClosureError("PASS213_TENSOR_CLOSURE_MATERIALIZE_LIMIT")
        visited = [self.cell(position) for position in range(self.domain_size)]
        return {
            "visited_count": len(visited),
            "unique_count": len(set(visited)),
            "first_cell": visited[0],
            "last_cell": visited[-1],
            "wrap_valid": self.closing_successor == visited[0],
        }
