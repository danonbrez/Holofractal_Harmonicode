from __future__ import annotations

import ctypes
from ctypes import POINTER, Structure, c_char, c_int64, c_uint8, c_uint16, c_uint32, c_uint64

from hhs_python.runtime import hhs_exact_ctypes_bridge as exact_mod

HHS_EXACT_STATUS_OK = 0
HHS_PASS168_PARAMETER_COUNT = 40
HHS_PASS168_DERIVED_THREAD_COUNT = 24
HHS_PASS168_HASH216_STRLEN = 217
HHS_EXACT_HASH72_STRLEN = 73


class HHSPass168Rational(Structure):
    _fields_ = [("numerator", c_int64), ("denominator", c_uint64)]


class HHSPass168Matrix3(Structure):
    _fields_ = [("v", HHSPass168Rational * 9)]


class HHSPass168Address(Structure):
    _fields_ = [
        ("global_index", c_uint16),
        ("global_row", c_uint8),
        ("global_col", c_uint8),
        ("thread_id", c_uint8),
        ("thread_row", c_uint8),
        ("thread_col", c_uint8),
        ("local_index", c_uint8),
        ("local_row", c_uint8),
        ("local_col", c_uint8),
        ("bank_id", c_uint8),
        ("bank_row", c_uint8),
        ("bank_col", c_uint8),
        ("loshu_index", c_uint8),
        ("loshu_row", c_uint8),
        ("loshu_col", c_uint8),
    ]


class HHSPass168CircuitState(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("generation", c_uint64),
        ("raw", HHSPass168Rational * HHS_PASS168_PARAMETER_COUNT),
        ("derived", HHSPass168Rational * HHS_PASS168_DERIVED_THREAD_COUNT),
        ("upper", HHSPass168Matrix3),
        ("lower", HHSPass168Matrix3),
        ("successor", HHSPass168Matrix3),
        ("state_hash216", c_char * HHS_PASS168_HASH216_STRLEN),
        ("last_receipt_hash72", c_char * HHS_EXACT_HASH72_STRLEN),
        ("committed", c_uint8),
        ("reserved0", c_uint8 * 7),
    ]


class HHSPass168Candidate(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("update_mask", c_uint64),
        ("affected_thread_bitmap", c_uint64),
        ("values", HHSPass168Rational * HHS_PASS168_PARAMETER_COUNT),
        ("expected_prior_hash216", c_char * HHS_PASS168_HASH216_STRLEN),
    ]


class HHSPass168Transition(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("decision", c_uint32),
        ("reject_reason", c_uint32),
        ("generation_before", c_uint64),
        ("generation_after", c_uint64),
        ("update_mask", c_uint64),
        ("affected_thread_bitmap", c_uint64),
        ("before_raw", HHSPass168Rational * HHS_PASS168_PARAMETER_COUNT),
        ("after_raw", HHSPass168Rational * HHS_PASS168_PARAMETER_COUNT),
        ("prior_state_hash216", c_char * HHS_PASS168_HASH216_STRLEN),
        ("committed_state_hash216", c_char * HHS_PASS168_HASH216_STRLEN),
        ("prior_receipt_hash72", c_char * HHS_EXACT_HASH72_STRLEN),
        ("change_hash72", c_char * HHS_EXACT_HASH72_STRLEN),
        ("receipt_hash72", c_char * HHS_EXACT_HASH72_STRLEN),
        ("hash216_triplet", c_char * HHS_PASS168_HASH216_STRLEN),
        ("hash216_identity", c_char * HHS_PASS168_HASH216_STRLEN),
        ("committed", c_uint8),
        ("fallback_used", c_uint8),
        ("reserved0", c_uint8 * 6),
    ]


class HHSPass168SelfTest(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("source_preserved", c_uint32),
        ("parenthesis_parameters_registered", c_uint32),
        ("equality_half_gates_registered", c_uint32),
        ("threads_registered", c_uint32),
        ("raw_threads", c_uint32),
        ("derived_threads", c_uint32),
        ("cells_covered", c_uint32),
        ("duplicate_addresses", c_uint32),
        ("inverse_address_failures", c_uint32),
        ("banks_per_thread", c_uint32),
        ("cells_per_bank", c_uint32),
        ("exact_rational_authority", c_uint32),
        ("floating_point_canonical_authority", c_uint32),
        ("baseline_upper_equals_361L", c_uint32),
        ("baseline_lower_equals_360L", c_uint32),
        ("successor_residual_equals_L", c_uint32),
        ("loshu_square_identity", c_uint32),
        ("gauge_cancellation_verified", c_uint32),
        ("ratio_channels_verified", c_uint32),
        ("comparators_verified", c_uint32),
        ("sparse_dependency_updates_verified", c_uint32),
        ("single_vm81_commit_authority", c_uint32),
        ("hash72_receipts_verified", c_uint32),
        ("hash216_identity_verified", c_uint32),
        ("rollback_verified", c_uint32),
        ("repair_verified", c_uint32),
        ("deterministic_replay_verified", c_uint32),
        ("x86_64_verified", c_uint32),
        ("arm64_verified", c_uint32),
        ("fallback_used", c_uint32),
        ("deterministic_record_hash216", c_char * HHS_PASS168_HASH216_STRLEN),
    ]


_LIB = exact_mod._RUNTIME_LIB
_LIB.hhs_pass168_version.argtypes = []
_LIB.hhs_pass168_version.restype = c_uint32
_LIB.hhs_pass168_source_text.argtypes = []
_LIB.hhs_pass168_source_text.restype = ctypes.c_char_p
_LIB.hhs_pass168_source_sha256_hex.argtypes = []
_LIB.hhs_pass168_source_sha256_hex.restype = ctypes.c_char_p
_LIB.hhs_pass168_state_initialize.argtypes = [POINTER(HHSPass168CircuitState)]
_LIB.hhs_pass168_state_initialize.restype = ctypes.c_int
_LIB.hhs_pass168_address_decode.argtypes = [c_uint16, POINTER(HHSPass168Address)]
_LIB.hhs_pass168_address_decode.restype = ctypes.c_int
_LIB.hhs_pass168_cell_value.argtypes = [POINTER(HHSPass168CircuitState), c_uint16, POINTER(HHSPass168Rational)]
_LIB.hhs_pass168_cell_value.restype = ctypes.c_int
_LIB.hhs_pass168_candidate_begin.argtypes = [POINTER(HHSPass168CircuitState), POINTER(HHSPass168Candidate)]
_LIB.hhs_pass168_candidate_begin.restype = ctypes.c_int
_LIB.hhs_pass168_candidate_set.argtypes = [POINTER(HHSPass168Candidate), c_uint8, c_int64, c_uint64]
_LIB.hhs_pass168_candidate_set.restype = ctypes.c_int
_LIB.hhs_pass168_candidate_validate.argtypes = [POINTER(HHSPass168CircuitState), POINTER(HHSPass168Candidate), POINTER(c_uint32)]
_LIB.hhs_pass168_candidate_validate.restype = ctypes.c_int
_LIB.hhs_pass168_candidate_apply.argtypes = [POINTER(HHSPass168CircuitState), POINTER(HHSPass168Candidate), POINTER(HHSPass168CircuitState)]
_LIB.hhs_pass168_candidate_apply.restype = ctypes.c_int
_LIB.hhs_pass168_commit_candidate.argtypes = [POINTER(HHSPass168CircuitState), POINTER(HHSPass168Candidate), POINTER(HHSPass168CircuitState), POINTER(HHSPass168Transition)]
_LIB.hhs_pass168_commit_candidate.restype = ctypes.c_int
_LIB.hhs_pass168_replay_transition.argtypes = [POINTER(HHSPass168CircuitState), POINTER(HHSPass168Transition), POINTER(HHSPass168CircuitState)]
_LIB.hhs_pass168_replay_transition.restype = ctypes.c_int
_LIB.hhs_pass168_rollback_transition.argtypes = [POINTER(HHSPass168Transition), POINTER(HHSPass168CircuitState)]
_LIB.hhs_pass168_rollback_transition.restype = ctypes.c_int
_LIB.hhs_pass168_repair_transition.argtypes = [POINTER(HHSPass168Transition), POINTER(HHSPass168CircuitState)]
_LIB.hhs_pass168_repair_transition.restype = ctypes.c_int
_LIB.hhs_pass168_self_test.argtypes = [POINTER(HHSPass168SelfTest)]
_LIB.hhs_pass168_self_test.restype = ctypes.c_int


def _c_text(value: object) -> str:
    return bytes(value).split(b"\x00", 1)[0].decode("ascii")


def rational_dict(value: HHSPass168Rational) -> dict[str, int]:
    return {"numerator": int(value.numerator), "denominator": int(value.denominator)}


def matrix_dict(value: HHSPass168Matrix3) -> list[list[dict[str, int]]]:
    return [[rational_dict(value.v[3 * r + c]) for c in range(3)] for r in range(3)]


def state_dict(value: HHSPass168CircuitState) -> dict[str, object]:
    return {
        "generation": int(value.generation),
        "raw": [rational_dict(item) for item in value.raw],
        "derived": [rational_dict(item) for item in value.derived],
        "upper": matrix_dict(value.upper),
        "lower": matrix_dict(value.lower),
        "successor": matrix_dict(value.successor),
        "state_hash216": _c_text(value.state_hash216),
        "last_receipt_hash72": _c_text(value.last_receipt_hash72),
        "committed": bool(value.committed),
    }


def transition_dict(value: HHSPass168Transition) -> dict[str, object]:
    return {
        "decision": int(value.decision),
        "reject_reason": int(value.reject_reason),
        "generation_before": int(value.generation_before),
        "generation_after": int(value.generation_after),
        "update_mask": int(value.update_mask),
        "affected_thread_bitmap": int(value.affected_thread_bitmap),
        "prior_state_hash216": _c_text(value.prior_state_hash216),
        "committed_state_hash216": _c_text(value.committed_state_hash216),
        "prior_receipt_hash72": _c_text(value.prior_receipt_hash72),
        "change_hash72": _c_text(value.change_hash72),
        "receipt_hash72": _c_text(value.receipt_hash72),
        "hash216_triplet": _c_text(value.hash216_triplet),
        "hash216_identity": _c_text(value.hash216_identity),
        "committed": bool(value.committed),
        "fallback_used": bool(value.fallback_used),
    }


class HHSPass168RuntimeBridge:
    @staticmethod
    def version() -> int:
        return int(_LIB.hhs_pass168_version())

    @staticmethod
    def source() -> str:
        raw = _LIB.hhs_pass168_source_text()
        if raw is None:
            raise RuntimeError("Pass168 source unavailable")
        return raw.decode("utf-8")

    @staticmethod
    def source_sha256() -> str:
        raw = _LIB.hhs_pass168_source_sha256_hex()
        if raw is None:
            raise RuntimeError("Pass168 source SHA256 unavailable")
        return raw.decode("ascii")

    @staticmethod
    def initialize() -> HHSPass168CircuitState:
        state = HHSPass168CircuitState()
        status = int(_LIB.hhs_pass168_state_initialize(ctypes.byref(state)))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Pass168 state initialization failed: {status}")
        return state

    @staticmethod
    def begin(state: HHSPass168CircuitState) -> HHSPass168Candidate:
        candidate = HHSPass168Candidate()
        status = int(_LIB.hhs_pass168_candidate_begin(ctypes.byref(state), ctypes.byref(candidate)))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Pass168 candidate begin failed: {status}")
        return candidate

    @staticmethod
    def set(candidate: HHSPass168Candidate, parameter_index: int, numerator: int, denominator: int = 1) -> None:
        if not 0 <= parameter_index < HHS_PASS168_PARAMETER_COUNT:
            raise ValueError("parameter_index out of range")
        if denominator <= 0:
            raise ValueError("denominator must be positive")
        status = int(_LIB.hhs_pass168_candidate_set(
            ctypes.byref(candidate), parameter_index, numerator, denominator
        ))
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError(f"Pass168 candidate set failed: {status}")

    @staticmethod
    def validate(state: HHSPass168CircuitState, candidate: HHSPass168Candidate) -> dict[str, int | bool]:
        reason = c_uint32()
        status = int(_LIB.hhs_pass168_candidate_validate(
            ctypes.byref(state), ctypes.byref(candidate), ctypes.byref(reason)
        ))
        return {"status": status, "valid": status == HHS_EXACT_STATUS_OK, "reject_reason": int(reason.value)}

    @staticmethod
    def evaluate(state: HHSPass168CircuitState, candidate: HHSPass168Candidate) -> HHSPass168CircuitState:
        output = HHSPass168CircuitState()
        status = int(_LIB.hhs_pass168_candidate_apply(
            ctypes.byref(state), ctypes.byref(candidate), ctypes.byref(output)
        ))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Pass168 candidate evaluation failed: {status}")
        return output

    @staticmethod
    def commit(state: HHSPass168CircuitState, candidate: HHSPass168Candidate) -> tuple[HHSPass168CircuitState, HHSPass168Transition]:
        output = HHSPass168CircuitState()
        transition = HHSPass168Transition()
        status = int(_LIB.hhs_pass168_commit_candidate(
            ctypes.byref(state), ctypes.byref(candidate), ctypes.byref(output), ctypes.byref(transition)
        ))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Pass168 candidate commit failed: {status}:{int(transition.reject_reason)}")
        return output, transition

    @staticmethod
    def replay(prior: HHSPass168CircuitState, transition: HHSPass168Transition) -> HHSPass168CircuitState:
        output = HHSPass168CircuitState()
        status = int(_LIB.hhs_pass168_replay_transition(
            ctypes.byref(prior), ctypes.byref(transition), ctypes.byref(output)
        ))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Pass168 replay failed: {status}")
        return output

    @staticmethod
    def rollback(transition: HHSPass168Transition) -> HHSPass168CircuitState:
        output = HHSPass168CircuitState()
        status = int(_LIB.hhs_pass168_rollback_transition(ctypes.byref(transition), ctypes.byref(output)))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Pass168 rollback failed: {status}")
        return output

    @staticmethod
    def self_test() -> dict[str, object]:
        proof = HHSPass168SelfTest()
        status = int(_LIB.hhs_pass168_self_test(ctypes.byref(proof)))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"Pass168 native self-test failed: {status}")
        return {
            "status": status,
            "source_preserved": bool(proof.source_preserved),
            "parenthesis_parameters_registered": int(proof.parenthesis_parameters_registered),
            "equality_half_gates_registered": int(proof.equality_half_gates_registered),
            "threads_registered": int(proof.threads_registered),
            "raw_threads": int(proof.raw_threads),
            "derived_threads": int(proof.derived_threads),
            "cells_covered": int(proof.cells_covered),
            "duplicate_addresses": int(proof.duplicate_addresses),
            "inverse_address_failures": int(proof.inverse_address_failures),
            "comparators_verified": int(proof.comparators_verified),
            "sparse_dependency_updates_verified": bool(proof.sparse_dependency_updates_verified),
            "hash72_receipts_verified": bool(proof.hash72_receipts_verified),
            "hash216_identity_verified": bool(proof.hash216_identity_verified),
            "rollback_verified": bool(proof.rollback_verified),
            "repair_verified": bool(proof.repair_verified),
            "deterministic_replay_verified": bool(proof.deterministic_replay_verified),
            "floating_point_canonical_authority": bool(proof.floating_point_canonical_authority),
            "fallback_used": bool(proof.fallback_used),
            "deterministic_record_hash216": _c_text(proof.deterministic_record_hash216),
        }
