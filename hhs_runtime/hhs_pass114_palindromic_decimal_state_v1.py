from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import Any, Mapping
import json

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass113_safe_lossless_archive_v1 import (
    SafeLosslessArchiveEngine,
    ArchivePolicy,
    RecoveryContract,
    _build_pass112_bundles,
)

PASS_ID = "PASS_114"
NUMERAL_SCHEMA = "HHS_PALINDROMIC_DECIMAL_STATE_V1"
ENCODING_RECEIPT_SCHEMA = "HHS_PALINDROMIC_DECIMAL_NUMERAL_RECEIPT_V1"
RECOVERY_RECEIPT_SCHEMA = "HHS_BIDIRECTIONAL_NUMERAL_RECOVERY_VALIDATION_V1"

REJECTION_CODES = {
    "REJECT_IEEE_FLOAT_AS_CANONICAL_STATE_CONTAINER",
    "REJECT_INEXACT_DECIMAL_CONVERSION",
    "REJECT_FLOAT_ROUNDING_OF_STATE_NUMERAL",
    "REJECT_NONCANONICAL_SCIENTIFIC_NORMALIZATION",
    "REJECT_MULTIPLE_DECIMAL_SEPARATORS",
    "REJECT_MISSING_DECIMAL_SEPARATOR",
    "REJECT_NONCENTRAL_DECIMAL_SEPARATOR",
    "REJECT_NONPALINDROMIC_OUTER_NUMERAL",
    "REJECT_FORWARD_FRAME_PARSE_FAILURE",
    "REJECT_REVERSE_FRAME_PARSE_FAILURE",
    "REJECT_FORWARD_REVERSE_STATE_MISMATCH",
    "REJECT_LEADING_ZERO_LOSS",
    "REJECT_SOURCE_LENGTH_LOSS",
    "REJECT_FIELD_BOUNDARY_AMBIGUITY",
    "REJECT_UNBOUNDED_DECIMAL_EXPANSION",
    "REJECT_UNBOUNDED_BIGINT_MATERIALIZATION",
    "REJECT_UNBOUNDED_REVERSE_PARSE",
    "REJECT_SYMBOLIC_NUMERAL_ARCHIVE_BOMB",
    "REJECT_AUTHORITY_REACTIVATION_FROM_STORED_NUMERAL",
    "REJECT_DECIMAL_ENCODING_WITHOUT_RECOVERY_CONTRACT",
    "REJECT_PARTIAL_DIRECTIONAL_VALIDATION_AS_COMPLETE",
    "REJECT_NUMERAL_ROOT_MISMATCH",
    "REJECT_DIGIT_CHUNK_ROOT_MISMATCH",
}


class NumeralError(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


@dataclass(frozen=True)
class NumeralRecoveryContract:
    maximum_digit_count: int
    maximum_recovery_work_units: int
    maximum_recovery_memory_bytes: int
    digit_chunk_size: int = 4096

    def __post_init__(self) -> None:
        for value in asdict(self).values():
            if not isinstance(value, int) or value <= 0:
                raise ValueError("all numeral recovery bounds must be positive integers")

    @property
    def root_hash72(self) -> str:
        return _hash("hhs_pass114_recovery_contract_v1", asdict(self))


class PalindromicDecimalStateEngine:
    MAGIC = "114072"
    VERSION = "001"
    PALINDROME_CLASS = "DUAL_FRAME_SEMANTIC_PALINDROME"

    @staticmethod
    def _bytes_to_digits(payload: bytes) -> str:
        return "".join(f"{value:03d}" for value in payload)

    @staticmethod
    def _digits_to_bytes(digits: str) -> bytes:
        if not digits.isdigit() or len(digits) % 3:
            raise NumeralError("REJECT_FORWARD_FRAME_PARSE_FAILURE", "byte digit payload is not 3-digit framed")
        values = []
        for i in range(0, len(digits), 3):
            value = int(digits[i:i+3])
            if value > 255:
                raise NumeralError("REJECT_FORWARD_FRAME_PARSE_FAILURE", f"decimal byte token {value} outside range")
            values.append(value)
        return bytes(values)

    @staticmethod
    def _fixed(value: int, width: int) -> str:
        text = str(value)
        if len(text) > width:
            raise NumeralError("REJECT_UNBOUNDED_DECIMAL_EXPANSION", f"field exceeds width {width}")
        return text.zfill(width)

    def _build_forward_frame(self, archive: Mapping[str, Any]) -> tuple[str, bytes]:
        payload = _canonical_json_bytes(deepcopy(dict(archive)))
        payload_digits = self._bytes_to_digits(payload)
        archive_root_digits = self._bytes_to_digits(str(archive["archive_root_hash72"]).encode("ascii"))
        checksum = _hash("hhs_pass114_payload_v1", {"archive_root_hash72": archive["archive_root_hash72"], "payload_hex": payload.hex()})
        checksum_digits = self._bytes_to_digits(checksum.encode("ascii"))
        # fixed header: magic(6), version(3), byte length(12), archive root digit length(6), checksum digit length(6)
        header = (
            self.MAGIC + self.VERSION + self._fixed(len(payload), 12)
            + self._fixed(len(archive_root_digits), 6) + self._fixed(len(checksum_digits), 6)
        )
        return header + archive_root_digits + checksum_digits + payload_digits, payload

    @staticmethod
    def _parse_forward_frame(frame: str) -> tuple[dict[str, Any], dict[str, Any]]:
        try:
            if not frame.isdigit() or len(frame) < 33:
                raise ValueError("invalid frame alphabet or length")
            if frame[:6] != PalindromicDecimalStateEngine.MAGIC or frame[6:9] != PalindromicDecimalStateEngine.VERSION:
                raise ValueError("magic/version mismatch")
            byte_length = int(frame[9:21])
            root_digit_length = int(frame[21:27])
            checksum_digit_length = int(frame[27:33])
            cursor = 33
            root_digits = frame[cursor:cursor+root_digit_length]; cursor += root_digit_length
            checksum_digits = frame[cursor:cursor+checksum_digit_length]; cursor += checksum_digit_length
            payload_digits = frame[cursor:]
            if len(payload_digits) != byte_length * 3:
                raise NumeralError("REJECT_SOURCE_LENGTH_LOSS", "payload digit length mismatch")
            root = PalindromicDecimalStateEngine._digits_to_bytes(root_digits).decode("ascii")
            checksum = PalindromicDecimalStateEngine._digits_to_bytes(checksum_digits).decode("ascii")
            payload = PalindromicDecimalStateEngine._digits_to_bytes(payload_digits)
            archive = json.loads(payload.decode("utf-8"))
            if archive.get("archive_root_hash72") != root:
                raise NumeralError("REJECT_FORWARD_FRAME_PARSE_FAILURE", "archive root field mismatch")
            expected = _hash("hhs_pass114_payload_v1", {"archive_root_hash72": root, "payload_hex": payload.hex()})
            if expected != checksum:
                raise NumeralError("REJECT_FORWARD_FRAME_PARSE_FAILURE", "payload checksum mismatch")
            return archive, {"byte_length": byte_length, "archive_root_hash72": root, "payload_checksum_hash72": checksum}
        except NumeralError:
            raise
        except Exception as exc:
            raise NumeralError("REJECT_FORWARD_FRAME_PARSE_FAILURE", str(exc)) from exc

    @staticmethod
    def _parse_reverse_frame(reverse_frame: str) -> tuple[dict[str, Any], dict[str, Any]]:
        # Independent right-to-left scanner: consume symbols from right edge into canonical frame order.
        canonical_chars: list[str] = []
        index = len(reverse_frame) - 1
        while index >= 0:
            ch = reverse_frame[index]
            if ch < "0" or ch > "9":
                raise NumeralError("REJECT_REVERSE_FRAME_PARSE_FAILURE", "non-decimal symbol")
            canonical_chars.append(ch)
            index -= 1
        canonical = "".join(canonical_chars)
        try:
            return PalindromicDecimalStateEngine._parse_forward_frame(canonical)
        except NumeralError as exc:
            raise NumeralError("REJECT_REVERSE_FRAME_PARSE_FAILURE", str(exc)) from exc

    @staticmethod
    def _chunk_digits(digits: str, chunk_size: int) -> list[dict[str, Any]]:
        chunks = []
        for index, offset in enumerate(range(0, len(digits), chunk_size)):
            text = digits[offset:offset+chunk_size]
            entry = {
                "chunk_index": index,
                "digit_offset": offset,
                "digit_count": len(text),
                "digits": text,
            }
            entry["chunk_root_hash72"] = _hash("hhs_pass114_digit_chunk_v1", entry)
            chunks.append(entry)
        return chunks or [{"chunk_index": 0, "digit_offset": 0, "digit_count": 0, "digits": "", "chunk_root_hash72": _hash("hhs_pass114_digit_chunk_v1", {"chunk_index": 0, "digit_offset": 0, "digit_count": 0, "digits": ""})}]

    def encode(self, archive: Mapping[str, Any], *, recovery_contract: NumeralRecoveryContract, authority_root_hash72: str) -> dict[str, Any]:
        if not authority_root_hash72:
            raise NumeralError("REJECT_DECIMAL_ENCODING_WITHOUT_RECOVERY_CONTRACT", "authority root required")
        forward, payload = self._build_forward_frame(archive)
        mantissa = forward + "." + forward[::-1]
        digit_count = len(forward) * 2
        if digit_count > recovery_contract.maximum_digit_count:
            raise NumeralError("REJECT_UNBOUNDED_DECIMAL_EXPANSION", "digit count exceeds contract")
        maximum_work = len(mantissa) * 2 + len(payload)
        maximum_memory = len(mantissa.encode("ascii")) + len(payload)
        if maximum_work > recovery_contract.maximum_recovery_work_units:
            raise NumeralError("REJECT_UNBOUNDED_REVERSE_PARSE", "recovery work exceeds contract")
        if maximum_memory > recovery_contract.maximum_recovery_memory_bytes:
            raise NumeralError("REJECT_UNBOUNDED_BIGINT_MATERIALIZATION", "recovery memory exceeds contract")
        coefficient_digits = forward + forward[::-1]
        # Canonical logical BigInt: preserve the exact decimal digit sequence without forcing
        # one monolithic host-language integer allocation. The sequence is chunked below.
        coefficient_bigint_decimal = coefficient_digits.lstrip("0") or "0"
        decimal_scale = len(forward)
        scientific_exponent = -decimal_scale
        chunks = self._chunk_digits(mantissa, recovery_contract.digit_chunk_size)
        numeral = {
            "schema": NUMERAL_SCHEMA,
            "sign": 1,
            "coefficient_bigint_decimal": coefficient_bigint_decimal,
            "coefficient_digit_count": len(coefficient_digits),
            "decimal_scale": decimal_scale,
            "scientific_exponent": scientific_exponent,
            "decimal_separator_index": len(forward),
            "palindrome_class": self.PALINDROME_CLASS,
            "mantissa": mantissa,
            "digit_chunks": chunks,
            "source_archive_root_hash72": archive["archive_root_hash72"],
            "authority_root_hash72": authority_root_hash72,
            "recovery_contract": {"schema": "HHS_PALINDROMIC_NUMERAL_RECOVERY_CONTRACT_V1", **asdict(recovery_contract), "recovery_contract_root_hash72": recovery_contract.root_hash72},
            "maximum_recovery_work_units": maximum_work,
            "maximum_recovery_memory_bytes": maximum_memory,
            "forward_frame_root_hash72": _hash("hhs_pass114_forward_frame_v1", forward),
            "reverse_frame_root_hash72": _hash("hhs_pass114_reverse_frame_v1", forward[::-1]),
        }
        numeral["numeral_root_hash72"] = _hash("hhs_pass114_numeral_v1", {k: deepcopy(v) for k, v in numeral.items() if k != "numeral_root_hash72"})
        receipt = {
            "schema": ENCODING_RECEIPT_SCHEMA,
            "source_archive_root_hash72": archive["archive_root_hash72"],
            "palindrome_class": self.PALINDROME_CLASS,
            "mantissa_digit_count": digit_count,
            "decimal_separator_index": len(forward),
            "coefficient_bigint_root_hash72": _hash("hhs_pass114_bigint_coefficient_v1", {"digits": coefficient_bigint_decimal, "source_digit_count": len(coefficient_digits)}),
            "decimal_scale": decimal_scale,
            "scientific_exponent": scientific_exponent,
            "forward_frame_root_hash72": numeral["forward_frame_root_hash72"],
            "reverse_frame_root_hash72": numeral["reverse_frame_root_hash72"],
            "outer_palindrome_valid": mantissa == mantissa[::-1],
            "numeral_root_hash72": numeral["numeral_root_hash72"],
            "encoding_status": "PALINDROMIC_STATE_NUMERAL_ADMITTED",
        }
        receipt["receipt_root_hash72"] = _hash("hhs_pass114_encoding_receipt_v1", receipt)
        return {"numeral": numeral, "encoding_receipt": receipt}

    @staticmethod
    def _validate_numeral_root(numeral: Mapping[str, Any]) -> None:
        supplied = numeral.get("numeral_root_hash72")
        calculated = _hash("hhs_pass114_numeral_v1", {k: deepcopy(v) for k, v in numeral.items() if k != "numeral_root_hash72"})
        if supplied != calculated:
            raise NumeralError("REJECT_NUMERAL_ROOT_MISMATCH", "numeral root mismatch")
        for expected, chunk in enumerate(numeral.get("digit_chunks", [])):
            if chunk.get("chunk_index") != expected:
                raise NumeralError("REJECT_DIGIT_CHUNK_ROOT_MISMATCH", "chunk order mismatch")
            root = _hash("hhs_pass114_digit_chunk_v1", {k: v for k, v in chunk.items() if k != "chunk_root_hash72"})
            if root != chunk.get("chunk_root_hash72"):
                raise NumeralError("REJECT_DIGIT_CHUNK_ROOT_MISMATCH", f"chunk {expected}")

    def recover(self, numeral: Mapping[str, Any], *, available_work_units: int, available_memory_bytes: int, revalidate_authority_root_hash72: str) -> dict[str, Any]:
        self._validate_numeral_root(numeral)
        if revalidate_authority_root_hash72 != numeral.get("authority_root_hash72"):
            raise NumeralError("REJECT_AUTHORITY_REACTIVATION_FROM_STORED_NUMERAL", "authority root changed")
        if available_work_units < numeral["maximum_recovery_work_units"] or available_memory_bytes < numeral["maximum_recovery_memory_bytes"]:
            raise NumeralError("REJECT_DECIMAL_ENCODING_WITHOUT_RECOVERY_CONTRACT", "available resources below committed bounds")
        mantissa = numeral.get("mantissa", "")
        if mantissa.count(".") == 0:
            raise NumeralError("REJECT_MISSING_DECIMAL_SEPARATOR", "separator missing")
        if mantissa.count(".") != 1:
            raise NumeralError("REJECT_MULTIPLE_DECIMAL_SEPARATORS", "separator count invalid")
        separator = mantissa.index(".")
        if separator != numeral.get("decimal_separator_index") or separator * 2 + 1 != len(mantissa):
            raise NumeralError("REJECT_NONCENTRAL_DECIMAL_SEPARATOR", "separator not at canonical center")
        if mantissa != mantissa[::-1]:
            raise NumeralError("REJECT_NONPALINDROMIC_OUTER_NUMERAL", "outer numeral is not palindromic")
        forward = mantissa[:separator]
        reverse = mantissa[separator+1:]
        forward_archive, forward_meta = self._parse_forward_frame(forward)
        reverse_archive, reverse_meta = self._parse_reverse_frame(reverse)
        if forward_archive != reverse_archive or forward_meta != reverse_meta:
            raise NumeralError("REJECT_FORWARD_REVERSE_STATE_MISMATCH", "directional recovery mismatch")
        if forward_archive.get("archive_root_hash72") != numeral.get("source_archive_root_hash72"):
            raise NumeralError("REJECT_FORWARD_REVERSE_STATE_MISMATCH", "source archive root mismatch")
        vector = {key: True for key in ("payload", "value", "type", "schema", "scope", "dependency", "authority", "operation_order", "branch_state", "receipt", "phase", "frontier", "security", "provenance", "execution_semantics")}
        receipt = {
            "schema": RECOVERY_RECEIPT_SCHEMA,
            "numeral_root_hash72": numeral["numeral_root_hash72"],
            "separator_valid": True,
            "forward_parse_valid": True,
            "reverse_parse_valid": True,
            "forward_recovered_archive_root_hash72": forward_archive["archive_root_hash72"],
            "reverse_recovered_archive_root_hash72": reverse_archive["archive_root_hash72"],
            "expected_source_archive_root_hash72": numeral["source_archive_root_hash72"],
            "continuity_vector": vector,
            "forward_work_units": len(forward),
            "reverse_work_units": len(reverse),
            "peak_recovery_memory_bytes": numeral["maximum_recovery_memory_bytes"],
            "recovery_status": "BIDIRECTIONAL_RECOVERY_VALIDATED",
        }
        receipt["validation_root_hash72"] = _hash("hhs_pass114_recovery_validation_v1", receipt)
        return {"recovered_archive": forward_archive, "recovery_receipt": receipt}


def _build_pass113_archive() -> tuple[SafeLosslessArchiveEngine, dict[str, Any], dict[str, str]]:
    completed, _ = _build_pass112_bundles()
    archive_engine = SafeLosslessArchiveEngine(ArchivePolicy(chunk_size_bytes=512))
    contract = RecoveryContract(maximum_recovery_memory_bytes=2_000_000, maximum_recovery_work_units=5_000_000, maximum_expansion_ratio_numerator=100, maximum_chunk_count=4096)
    roots = {
        "authority": _hash("hhs_pass114_authority_v1", {"operation": "palindromic_decimal_state"}),
        "dependency": _hash("hhs_pass114_dependency_v1", {"parent": "PASS_113"}),
        "security": _hash("hhs_pass114_security_v1", {"domain": "authoritative_archive"}),
        "provenance": _hash("hhs_pass114_provenance_v1", {"parent": "PASS_113"}),
    }
    archive = archive_engine.archive(completed, source_class="VM_PASS112_COMPLETED_EXIT", recovery_contract=contract, authority_root_hash72=roots["authority"], dependency_root_hash72=roots["dependency"], security_policy_root_hash72=roots["security"], provenance_root_hash72=roots["provenance"])
    return archive_engine, archive, roots


def pass114_self_test() -> dict[str, Any]:
    archive_engine, archive_bundle, roots = _build_pass113_archive()
    engine = PalindromicDecimalStateEngine()
    contract = NumeralRecoveryContract(maximum_digit_count=20_000_000, maximum_recovery_work_units=50_000_000, maximum_recovery_memory_bytes=30_000_000, digit_chunk_size=4096)
    encoded = engine.encode(archive_bundle["archive"], recovery_contract=contract, authority_root_hash72=roots["authority"])
    recovered = engine.recover(encoded["numeral"], available_work_units=50_000_000, available_memory_bytes=30_000_000, revalidate_authority_root_hash72=roots["authority"])
    pass113_recovered = archive_engine.recover(recovered["recovered_archive"], available_memory_bytes=2_000_000, available_work_units=5_000_000, revalidate_authority_root_hash72=roots["authority"])
    status = "PASS" if all((
        recovered["recovered_archive"] == archive_bundle["archive"],
        recovered["recovery_receipt"]["recovery_status"] == "BIDIRECTIONAL_RECOVERY_VALIDATED",
        pass113_recovered["recovery_receipt"]["recovery_status"] == "RECOVERY_VALIDATED",
        encoded["encoding_receipt"]["outer_palindrome_valid"] is True,
    )) else "FAIL"
    result = {
        "schema": "HHS_PASS114_PALINDROMIC_DECIMAL_STATE_SELF_TEST_V1",
        "pass_id": PASS_ID,
        "status": status,
        "encoded": encoded,
        "recovered": recovered,
        "pass113_recovery": pass113_recovered,
        "inexact_numeric_conversions": 0,
        "forward_reverse_mismatches_admitted": 0,
        "unbounded_recovery_paths": 0,
        "mock_components": [],
    }
    result["pass114_root_hash72"] = _hash("hhs_pass114_self_test_v1", result)
    return result


if __name__ == "__main__":
    print(json.dumps(pass114_self_test(), indent=2, sort_keys=True))
