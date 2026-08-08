"""Pass 213 Iteration 8 exact moving tensor state authority."""
from __future__ import annotations

from dataclasses import dataclass
import hmac
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT, FULL_HYDRATION_DOMAIN, VM5184_G243_DOMAIN, ZERO_HASH216,
    canonical_bytes, derive_key, hash216,
)
from hhs_backend.runtime.hhs_pass213_tensor_boundary_v1 import (
    FloatingTensorProjection, Pass213TensorBoundaryError, TensorAnchorBinding,
)
from hhs_backend.runtime.hhs_pass213_tensor_closure_v1 import (
    Pass213TensorClosureError, TensorClosureProof,
)
from hhs_backend.runtime.hhs_pass213_tensor_geometry_v1 import (
    Pass213TensorGeometryError, SudokuTensor, TensorCoordinateMap,
    fibonacci_phase, lo_shu_grid, seed_word, validate_lo_shu,
)
from hhs_backend.runtime.hhs_pass213_trusted_timestamp_v1 import TrustedTimestampAnchorRecord
from hhs_runtime.core.hash72_digest_v1 import hash72_digest, verify_hash72

ITERATION = 8
RUNTIME_CLASSIFICATION = "HHS_PASS_213_EXACT_MOVING_TENSOR_AUTHORITY_ITERATION8"


class Pass213TensorError(RuntimeError):
    pass


def _raise_translated(exc: Exception) -> None:
    raise Pass213TensorError(str(exc)) from exc


@dataclass(frozen=True)
class MovingTensorState:
    tensor_sequence: int
    genesis_epoch: int
    prior_tensor_root_hash216: str
    domain_size: int
    anchor: TensorAnchorBinding
    seed_commitment_hash216: str
    lo_shu_transform_index: int
    lo_shu_grid: tuple[tuple[int, ...], ...]
    lo_shu_root_hash216: str
    sudoku: SudokuTensor
    fibonacci_phase: tuple[int, ...]
    coordinate_map: TensorCoordinateMap
    closure_proof: TensorClosureProof
    tensor_root_hash216: str
    receipt_hash72: str

    @classmethod
    def derive(
        cls, *, root_key: bytes, trusted_anchor: TrustedTimestampAnchorRecord,
        tensor_sequence: int, genesis_epoch: int,
        prior_tensor_root_hash216: str = ZERO_HASH216,
        domain_size: int = FULL_HYDRATION_DOMAIN,
    ) -> "MovingTensorState":
        if not isinstance(root_key, bytes) or len(root_key) < 32:
            raise Pass213TensorError("PASS213_TENSOR_ROOT_KEY_TOO_SHORT")
        if tensor_sequence < 1 or genesis_epoch < 1 or domain_size not in {VM5184_G243_DOMAIN, FULL_HYDRATION_DOMAIN}:
            raise Pass213TensorError("PASS213_TENSOR_SEQUENCE_EPOCH_OR_DOMAIN_INVALID")
        if len(prior_tensor_root_hash216) != 64:
            raise Pass213TensorError("PASS213_TENSOR_PRIOR_ROOT_INVALID")
        try:
            anchor = TensorAnchorBinding.from_trusted_anchor(trusted_anchor)
        except Pass213TensorBoundaryError as exc:
            _raise_translated(exc)
        seed_context = canonical_bytes({
            "contract": CONTRACT, "iteration": ITERATION,
            "tensor_sequence": tensor_sequence, "genesis_epoch": genesis_epoch,
            "prior_tensor_root_hash216": prior_tensor_root_hash216,
            "domain_size": domain_size, "anchor": anchor.to_mapping(),
        })
        seed = derive_key(root_key, "ITER8-MOVING-TENSOR", seed_context)
        transform = seed_word(seed, "lo-shu/transform", 0) % 8
        lo_shu = lo_shu_grid(transform)
        lo_shu_root = hash216("lo-shu-tensor", canonical_bytes({
            "transform_index": transform, "grid": lo_shu, "magic_sum": 15,
        }))
        phase = fibonacci_phase(tensor_sequence)
        sudoku = SudokuTensor.derive(seed)
        coordinate_map = TensorCoordinateMap.derive(seed, sudoku, phase)
        closure = TensorClosureProof.derive(seed, domain_size)
        unsigned = {
            "schema": "HHS_PASS_213_MOVING_TENSOR_STATE_V1", "contract": CONTRACT,
            "iteration": ITERATION, "tensor_sequence": tensor_sequence,
            "genesis_epoch": genesis_epoch, "prior_tensor_root_hash216": prior_tensor_root_hash216,
            "domain_size": domain_size, "anchor": anchor.to_mapping(),
            "seed_commitment_hash216": hash216("moving-tensor-seed-commitment", seed),
            "lo_shu_transform_index": transform, "lo_shu_grid": lo_shu,
            "lo_shu_root_hash216": lo_shu_root, "sudoku": sudoku.to_mapping(),
            "fibonacci_phase": phase, "coordinate_map": coordinate_map.to_mapping(),
            "closure_proof": closure.to_mapping(),
        }
        tensor_root = hash216("moving-tensor-state", canonical_bytes(unsigned))
        receipt = hash72_digest({
            "domain": "HHS-P213-ITER8-MOVING-TENSOR-RECEIPT-V1",
            "contract": CONTRACT, "iteration": ITERATION,
        }, bytes.fromhex(tensor_root))
        state = cls(
            tensor_sequence, genesis_epoch, prior_tensor_root_hash216, domain_size, anchor,
            unsigned["seed_commitment_hash216"], transform, lo_shu, lo_shu_root,
            sudoku, phase, coordinate_map, closure, tensor_root, receipt,
        )
        state.validate_structure()
        return state

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "schema": "HHS_PASS_213_MOVING_TENSOR_STATE_V1", "contract": CONTRACT,
            "iteration": ITERATION, "tensor_sequence": self.tensor_sequence,
            "genesis_epoch": self.genesis_epoch, "prior_tensor_root_hash216": self.prior_tensor_root_hash216,
            "domain_size": self.domain_size, "anchor": self.anchor.to_mapping(),
            "seed_commitment_hash216": self.seed_commitment_hash216,
            "lo_shu_transform_index": self.lo_shu_transform_index,
            "lo_shu_grid": self.lo_shu_grid, "lo_shu_root_hash216": self.lo_shu_root_hash216,
            "sudoku": self.sudoku.to_mapping(), "fibonacci_phase": self.fibonacci_phase,
            "coordinate_map": self.coordinate_map.to_mapping(),
            "closure_proof": self.closure_proof.to_mapping(),
        }

    def to_mapping(self) -> dict[str, Any]:
        return {**self.unsigned_payload(), "tensor_root_hash216": self.tensor_root_hash216, "receipt_hash72": self.receipt_hash72}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "MovingTensorState":
        try:
            state = cls(
                int(value["tensor_sequence"]), int(value["genesis_epoch"]),
                str(value["prior_tensor_root_hash216"]), int(value["domain_size"]),
                TensorAnchorBinding.from_mapping(dict(value["anchor"])),
                str(value["seed_commitment_hash216"]), int(value["lo_shu_transform_index"]),
                tuple(tuple(int(item) for item in row) for row in value["lo_shu_grid"]),
                str(value["lo_shu_root_hash216"]), SudokuTensor.from_mapping(dict(value["sudoku"])),
                tuple(int(item) for item in value["fibonacci_phase"]),
                TensorCoordinateMap.from_mapping(dict(value["coordinate_map"])),
                TensorClosureProof.from_mapping(dict(value["closure_proof"])),
                str(value["tensor_root_hash216"]), str(value["receipt_hash72"]),
            )
        except (Pass213TensorBoundaryError, Pass213TensorGeometryError, Pass213TensorClosureError) as exc:
            _raise_translated(exc)
        state.validate_structure()
        return state

    def validate_structure(self) -> None:
        try:
            if self.tensor_sequence < 1 or self.genesis_epoch < 1 or self.domain_size not in {VM5184_G243_DOMAIN, FULL_HYDRATION_DOMAIN}:
                raise Pass213TensorError("PASS213_TENSOR_SEQUENCE_EPOCH_OR_DOMAIN_INVALID")
            self.anchor.validate()
            if len(self.prior_tensor_root_hash216) != 64 or len(self.seed_commitment_hash216) != 64:
                raise Pass213TensorError("PASS213_TENSOR_ROOT_LENGTH_INVALID")
            if self.lo_shu_grid != lo_shu_grid(self.lo_shu_transform_index):
                raise Pass213TensorError("PASS213_TENSOR_LO_SHU_DERIVATION_MISMATCH")
            validate_lo_shu(self.lo_shu_grid)
            expected_lo_shu = hash216("lo-shu-tensor", canonical_bytes({
                "transform_index": self.lo_shu_transform_index, "grid": self.lo_shu_grid, "magic_sum": 15,
            }))
            if not hmac.compare_digest(expected_lo_shu, self.lo_shu_root_hash216):
                raise Pass213TensorError("PASS213_TENSOR_LO_SHU_ROOT_MISMATCH")
            self.sudoku.validate()
            if self.fibonacci_phase != fibonacci_phase(self.tensor_sequence):
                raise Pass213TensorError("PASS213_TENSOR_FIBONACCI_PHASE_MISMATCH")
            self.coordinate_map.validate()
            self.closure_proof.validate()
            if self.closure_proof.domain_size != self.domain_size:
                raise Pass213TensorError("PASS213_TENSOR_CLOSURE_DOMAIN_MISMATCH")
        except (Pass213TensorBoundaryError, Pass213TensorGeometryError, Pass213TensorClosureError) as exc:
            _raise_translated(exc)
        expected = hash216("moving-tensor-state", canonical_bytes(self.unsigned_payload()))
        if not hmac.compare_digest(expected, self.tensor_root_hash216):
            raise Pass213TensorError("PASS213_TENSOR_ROOT_MISMATCH")
        if not verify_hash72(self.receipt_hash72, {
            "domain": "HHS-P213-ITER8-MOVING-TENSOR-RECEIPT-V1",
            "contract": CONTRACT, "iteration": ITERATION,
        }, bytes.fromhex(self.tensor_root_hash216)):
            raise Pass213TensorError("PASS213_TENSOR_RECEIPT_HASH72_MISMATCH")

    def validate_with_key(self, *, root_key: bytes, trusted_anchor: TrustedTimestampAnchorRecord) -> bool:
        expected = MovingTensorState.derive(
            root_key=root_key, trusted_anchor=trusted_anchor,
            tensor_sequence=self.tensor_sequence, genesis_epoch=self.genesis_epoch,
            prior_tensor_root_hash216=self.prior_tensor_root_hash216,
            domain_size=self.domain_size,
        )
        if not hmac.compare_digest(canonical_bytes(expected.to_mapping()), canonical_bytes(self.to_mapping())):
            raise Pass213TensorError("PASS213_TENSOR_KEYED_REPLAY_MISMATCH")
        return True

    def physical_cell(self, position: int) -> int:
        return self.coordinate_map.map_index(self.closure_proof.cell(position), self.domain_size)

    def logical_position_from_physical(self, physical_cell: int) -> int:
        logical = self.coordinate_map.unmap_index(physical_cell, self.domain_size)
        return self.closure_proof.position(logical)

    def floating_projection(self) -> FloatingTensorProjection:
        try:
            return FloatingTensorProjection.derive(self.tensor_root_hash216, self.fibonacci_phase)
        except Pass213TensorBoundaryError as exc:
            _raise_translated(exc)
