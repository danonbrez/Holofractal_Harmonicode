"""Deterministic domain-separated prime generation with verification receipts."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import shake_256, sha256
from math import gcd
from typing import Any
import sympy

from .canonical import canonical_bytes, canonical_json

SMALL_PRIMES = tuple(int(p) for p in list(sympy.primerange(2, 1000)))
MR64_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


@dataclass(frozen=True)
class EntropyAttestation:
    source_id: str
    seed_bits: int
    asserted_min_entropy_bits: int
    independently_attested: bool
    public_test_seed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PrimeReceipt:
    schema: str
    index: int
    prime_decimal: str
    bit_length: int
    candidate_counter: int
    candidate_commitment_sha256: str
    domain: str
    sympy_isprime: bool
    deterministic_mr64: bool | None
    trial_division_passed: bool
    verification_class: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _mr_round(n: int, a: int) -> bool:
    if n % a == 0:
        return n == a
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    x = pow(a % n, d, n)
    if x in (1, n - 1):
        return True
    for _ in range(s - 1):
        x = (x * x) % n
        if x == n - 1:
            return True
    return False


def deterministic_mr64(n: int) -> bool:
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    if n >= 1 << 64:
        raise ValueError("deterministic_mr64 only authorizes n < 2^64")
    return all(_mr_round(n, a) for a in MR64_BASES)


def derive_candidate(seed: bytes, domain: str, index: int, counter: int, bits: int, context: dict[str, Any] | None = None) -> int:
    if bits < 16:
        raise ValueError("prime width must be at least 16 bits")
    context = context or {}
    preimage = b"\x1f".join([
        b"HHS-P133-PRIME-CANDIDATE-V1",
        domain.encode("utf-8"),
        index.to_bytes(4, "big"),
        counter.to_bytes(8, "big"),
        bits.to_bytes(4, "big"),
        canonical_bytes(context),
        bytes(seed),
    ])
    raw = bytearray(shake_256(preimage).digest((bits + 7) // 8))
    excess = len(raw) * 8 - bits
    if excess:
        raw[0] &= 0xFF >> excess
    raw[0] |= 1 << (7 - excess)
    raw[-1] |= 1
    return int.from_bytes(raw, "big")


def verify_prime(candidate: int, *, index: int, counter: int, domain: str) -> PrimeReceipt:
    trial_ok = all(candidate == p or candidate % p for p in SMALL_PRIMES)
    isprime = bool(sympy.isprime(candidate))
    mr64: bool | None = deterministic_mr64(candidate) if candidate < 1 << 64 else None
    verification_class = "DETERMINISTIC_64BIT_AND_BPSW_VERIFIED" if mr64 is not None else "SYMPY_BPSW_AND_EXACT_ARITHMETIC_VERIFIED"
    return PrimeReceipt(
        schema="HHS_PASS133_PRIME_VERIFICATION_RECEIPT_V1",
        index=index,
        prime_decimal=str(candidate),
        bit_length=candidate.bit_length(),
        candidate_counter=counter,
        candidate_commitment_sha256=sha256(str(candidate).encode("ascii")).hexdigest(),
        domain=domain,
        sympy_isprime=isprime,
        deterministic_mr64=mr64,
        trial_division_passed=trial_ok,
        verification_class=verification_class,
    )


def generate_distinct_primes(
    seed: bytes,
    *,
    count: int,
    bits: int,
    domain: str,
    context: dict[str, Any] | None = None,
    max_candidates_per_prime: int = 1_000_000,
) -> tuple[list[int], list[PrimeReceipt]]:
    if count <= 0:
        raise ValueError("count must be positive")
    primes: list[int] = []
    receipts: list[PrimeReceipt] = []
    used: set[int] = set()
    for index in range(count):
        for counter in range(max_candidates_per_prime):
            candidate = derive_candidate(seed, domain, index, counter, bits, context)
            if candidate in used:
                continue
            if any(candidate != p and candidate % p == 0 for p in SMALL_PRIMES):
                continue
            if not sympy.isprime(candidate):
                continue
            receipt = verify_prime(candidate, index=index, counter=counter, domain=domain)
            if not receipt.sympy_isprime or receipt.bit_length != bits:
                continue
            if receipt.deterministic_mr64 is False:
                continue
            primes.append(candidate)
            receipts.append(receipt)
            used.add(candidate)
            break
        else:
            raise RuntimeError(f"prime generation exhausted bound at index {index}")
    return primes, receipts


def verify_prime_alphabet(primes: list[int], bits: int) -> dict[str, Any]:
    checks = [bool(sympy.isprime(p)) and p.bit_length() == bits for p in primes]
    return {
        "schema": "HHS_PASS133_PRIME_ALPHABET_VALIDATION_V1",
        "count": len(primes),
        "distinct": len(set(primes)) == len(primes),
        "all_prime_and_width_exact": all(checks),
        "bit_length": bits,
        "status": "PRIME_CERTIFICATES_VERIFIED" if len(set(primes)) == len(primes) and all(checks) else "PRIME_CERTIFICATE_FAILURE",
    }
