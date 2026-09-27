"""Pass 219 Lane 5 1.68 — streaming source attestation for Cosmic9 sample data."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "contracts/pass219/PASS_219_LANE5_NINE_LOOP_SOURCE_ATTESTATION_1_68.json"

P1 = 2147483647
P2 = 2147483629
ALPHABET = frozenset(("ah", "bh", "ch", "dh", "eh", "fh", "yu", "yv", "yw"))
WEIGHT = 18
EXPECTED_NONZERO = 20400
EXPECTED_ZERO = 230
EXPECTED_TOTAL = EXPECTED_NONZERO + EXPECTED_ZERO
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class Lane5NineLoopSourceAttestationError(ValueError):
    pass


@dataclass(frozen=True)
class SampleRow:
    word: tuple[str, ...]
    residue_p1: int
    residue_p2: int
    rational: Fraction
    zero_section: bool


def load_contract() -> dict:
    value = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if value.get("schema") != "HHS_PASS219_LANE5_NINE_LOOP_SOURCE_ATTESTATION_1_68":
        raise Lane5NineLoopSourceAttestationError("1.68 contract schema mismatch")
    return value


def exact_rational_residue(value: Fraction, modulus: int) -> int:
    denominator = value.denominator % modulus
    if denominator == 0:
        raise Lane5NineLoopSourceAttestationError("rational denominator not invertible")
    return (value.numerator % modulus) * pow(denominator, -1, modulus) % modulus


def parse_manifest_sample_sha256(manifest_text: str) -> str:
    matches: list[str] = []
    for raw in manifest_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        digest, name = parts
        name = name.lstrip("*")
        if name.endswith("samples/E9_sample_coefficients.txt") or name == "E9_sample_coefficients.txt":
            digest = digest.lower()
            if not _SHA256_RE.fullmatch(digest):
                raise Lane5NineLoopSourceAttestationError("invalid sample SHA-256 in upstream manifest")
            matches.append(digest)
    if len(matches) != 1:
        raise Lane5NineLoopSourceAttestationError(
            f"expected one sample checksum in upstream manifest, got {len(matches)}"
        )
    return matches[0]


def _parse_rational(token: str) -> Fraction:
    if token == "not_certified":
        raise Lane5NineLoopSourceAttestationError(
            "1.68 sample contract requires every nonzero row rational to be certified"
        )
    try:
        if "/" in token:
            num_text, den_text = token.split("/", 1)
            value = Fraction(int(num_text), int(den_text))
        else:
            value = Fraction(int(token), 1)
    except Exception as exc:
        raise Lane5NineLoopSourceAttestationError(f"invalid rational token: {token}") from exc
    return value


def parse_sample_rows(text: str) -> list[SampleRow]:
    rows: list[SampleRow] = []
    zero_section = False
    saw_nonzero_marker = False
    saw_zero_marker = False

    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            if line == "## NONZERO WORDS":
                saw_nonzero_marker = True
                zero_section = False
            elif line == "## ZERO WORDS":
                saw_zero_marker = True
                zero_section = True
            continue

        fields = line.split()
        if len(fields) != WEIGHT + 3:
            raise Lane5NineLoopSourceAttestationError(
                f"line {line_number}: expected {WEIGHT + 3} fields, got {len(fields)}"
            )
        word = tuple(fields[:WEIGHT])
        if any(letter not in ALPHABET for letter in word):
            raise Lane5NineLoopSourceAttestationError(
                f"line {line_number}: foreign alphabet violation"
            )

        try:
            r1 = int(fields[WEIGHT])
            r2 = int(fields[WEIGHT + 1])
        except ValueError as exc:
            raise Lane5NineLoopSourceAttestationError(
                f"line {line_number}: non-integer residue"
            ) from exc

        if not (0 <= r1 < P1 and 0 <= r2 < P2):
            raise Lane5NineLoopSourceAttestationError(
                f"line {line_number}: residue outside prime field"
            )

        rational = _parse_rational(fields[WEIGHT + 2])
        row = SampleRow(
            word=word,
            residue_p1=r1,
            residue_p2=r2,
            rational=rational,
            zero_section=zero_section,
        )

        if zero_section:
            if r1 != 0 or r2 != 0 or rational != 0:
                raise Lane5NineLoopSourceAttestationError(
                    f"line {line_number}: ZERO section row is not exact zero"
                )
        else:
            if not saw_nonzero_marker:
                raise Lane5NineLoopSourceAttestationError(
                    f"line {line_number}: data before NONZERO marker"
                )
            if rational == 0:
                raise Lane5NineLoopSourceAttestationError(
                    f"line {line_number}: NONZERO section carries zero rational"
                )
            if exact_rational_residue(rational, P1) != r1:
                raise Lane5NineLoopSourceAttestationError(
                    f"line {line_number}: p1 rational/residue mismatch"
                )
            if exact_rational_residue(rational, P2) != r2:
                raise Lane5NineLoopSourceAttestationError(
                    f"line {line_number}: p2 rational/residue mismatch"
                )
            den = rational.denominator
            if den >= 2**30 or den & (den - 1):
                raise Lane5NineLoopSourceAttestationError(
                    f"line {line_number}: rational denominator violates sample contract"
                )
            if abs(rational.numerator) >= 2**30:
                raise Lane5NineLoopSourceAttestationError(
                    f"line {line_number}: rational numerator violates sample contract"
                )

        rows.append(row)

    if not saw_nonzero_marker or not saw_zero_marker:
        raise Lane5NineLoopSourceAttestationError("missing sample section marker")
    return rows


def attest_sample(
    raw_bytes: bytes,
    *,
    manifest_text: str | None = None,
    require_full_contract: bool = True,
) -> dict:
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Lane5NineLoopSourceAttestationError("sample must be UTF-8 text") from exc

    rows = parse_sample_rows(text)
    nonzero = sum(not row.zero_section for row in rows)
    zero = sum(row.zero_section for row in rows)
    raw_sha256 = hashlib.sha256(raw_bytes).hexdigest()

    manifest_sha256 = None
    manifest_member_verified = False
    if manifest_text is not None:
        manifest_sha256 = hashlib.sha256(manifest_text.encode("utf-8")).hexdigest()
        expected = parse_manifest_sample_sha256(manifest_text)
        if raw_sha256 != expected:
            raise Lane5NineLoopSourceAttestationError(
                "sample SHA-256 does not match upstream MANIFEST.sha256"
            )
        manifest_member_verified = True

    if require_full_contract:
        if (nonzero, zero, len(rows)) != (EXPECTED_NONZERO, EXPECTED_ZERO, EXPECTED_TOTAL):
            raise Lane5NineLoopSourceAttestationError(
                "sample row counts do not match frozen 1.68 contract"
            )

    unique_words = len({row.word for row in rows})
    if require_full_contract and unique_words != EXPECTED_TOTAL:
        raise Lane5NineLoopSourceAttestationError(
            "sample contains duplicate words under full contract"
        )

    summary = {
        "schema": "HHS_PASS219_LANE5_NINE_LOOP_SOURCE_ATTESTATION_1_68_RECEIPT",
        "raw_sha256": raw_sha256,
        "manifest_sha256": manifest_sha256,
        "manifest_member_verified": manifest_member_verified,
        "nonzero_rows": nonzero,
        "zero_rows": zero,
        "total_rows": len(rows),
        "unique_words": unique_words,
        "weight": WEIGHT,
        "alphabet": sorted(ALPHABET),
        "prime_moduli": [P1, P2],
        "all_nonzero_rationals_exact": True,
        "all_zero_rows_exact": True,
        "floating_point_authority": False,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
    }
    summary_bytes = json.dumps(
        summary, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    summary["summary_sha256"] = hashlib.sha256(summary_bytes).hexdigest()
    return summary


def compare_predictions(
    rows: Sequence[SampleRow],
    predictions: Mapping[tuple[str, ...], tuple[int, int]],
) -> dict:
    matched = 0
    missing = 0
    mismatched = 0
    for row in rows:
        predicted = predictions.get(row.word)
        if predicted is None:
            missing += 1
            continue
        p1, p2 = map(int, predicted)
        if p1 == row.residue_p1 and p2 == row.residue_p2:
            matched += 1
        else:
            mismatched += 1
    return {
        "matched": matched,
        "missing": missing,
        "mismatched": mismatched,
        "coverage_numerator": matched + mismatched,
        "coverage_denominator": len(rows),
        "exact_prediction_match": missing == 0 and mismatched == 0,
        "trinary": 0 if missing == 0 and mismatched == 0 else -1,
    }
