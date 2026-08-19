from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from hhs_runtime.pass219_quantization_constraint_reference_v1 import (
    A2,
    N36,
    N72,
    N5256,
    build_witness,
    quadratic_reciprocity_bit,
)

CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE = (
    "P^2/{(t^3-t=(P^3-P/(P^2-pq)=(t^3-t)/Delta=P^2(MOD)(pq))=m^2-m)-"
    "(({{b^4,c^4,c^2-u^72},{c^2,5/u^((s==(b^(2c^2)c^b^4)^2)/(72P^2)),"
    "((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)))},"
    "{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,(72*(pq+xy)))/Bt==AB/P^2==Sqrt[AB])"
    "==(AB/(pq+Delta)-P^2)/(t^3-t)*u^72} where Delta/P=Sqrt(pq+u^72)^x^2\n"
)

CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SHA256 = sha256(
    CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE.encode("utf-8")
).digest()

PROFILE_INTEGER_SYMMETRIC_V1 = "HHS-UCE-INTEGER-SYMMETRIC-V1"
PROFILE_FULL_SYMBOLIC_V1 = "HHS-UCE-FULL-SYMBOLIC-V1"

SYMBOLIC_RESIDUALS_V1 = (
    "t_m_harmonic_chain",
    "tensor_s_f_At_Bt_chain",
    "Delta_over_P_root_chain",
    "Mod_f_over_u_chain",
)


@dataclass(frozen=True)
class NativeUniversalConstraintWitness:
    P: int
    p: int
    q: int
    delta: int
    A: int
    B: int
    qr_bit: int
    qr_lane: str
    qr_phase: int
    metric_power: int
    full_cycle_metric_exponent: int
    source_sha256_hex: str
    profile: str
    symbolic_residuals: tuple[str, ...]

    @property
    def p_squared(self) -> int:
        return self.P * self.P

    @property
    def pq(self) -> int:
        return self.p * self.q

    @property
    def ab(self) -> int:
        return self.A * self.B

    @property
    def p_fourth(self) -> int:
        p2 = self.p_squared
        return p2 * p2

    def exact_core_valid(self) -> bool:
        return (
            self.P > 0
            and self.p > 0
            and self.q > 0
            and self.delta >= 0
            and self.p % 2 == 1
            and self.q % 2 == 1
            and self.p_squared == self.pq + self.delta
            and self.A == self.p_squared
            and self.B == self.p_squared
            and self.ab == self.p_fourth
            and self.qr_phase == (N36 if self.qr_bit == A2 else 0)
            and self.metric_power == N5256
            and self.full_cycle_metric_exponent == -66
            and bytes.fromhex(self.source_sha256_hex)
            == CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SHA256
        )


def build_integer_symmetric_witness(P: int, p: int, q: int) -> NativeUniversalConstraintWitness:
    for name, value in (("P", P), ("p", p), ("q", q)):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if p % 2 == 0 or q % 2 == 0:
        raise ValueError("p and q must lie in the positive odd reciprocity domain")
    p2 = P * P
    delta = p2 - (p * q)
    if delta < 0:
        raise ValueError("integer-symmetric UCE projection requires P^2 >= p*q")
    qr = build_witness(p, q)
    witness = NativeUniversalConstraintWitness(
        P=P,
        p=p,
        q=q,
        delta=delta,
        A=p2,
        B=p2,
        qr_bit=qr.qr_bit,
        qr_lane=qr.qr_lane,
        qr_phase=qr.qr_phase,
        metric_power=qr.u_power,
        full_cycle_metric_exponent=int(qr.full_cycle_b2_exponent),
        source_sha256_hex=CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SHA256.hex(),
        profile=PROFILE_INTEGER_SYMMETRIC_V1,
        symbolic_residuals=SYMBOLIC_RESIDUALS_V1,
    )
    if not witness.exact_core_valid():
        raise AssertionError("constructed UCE witness failed its exact core invariants")
    return witness


def expected_phase_basis_pair(witness: NativeUniversalConstraintWitness) -> tuple[int, int]:
    return (1, 0) if witness.qr_bit == A2 else (0, 1)


def reference_invariants() -> dict[str, bool]:
    xy = build_integer_symmetric_witness(4, 3, 5)
    yx = build_integer_symmetric_witness(5, 3, 7)
    return {
        "source_hash": CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SHA256.hex()
        == "7eb0cc5707a4a58a5a8e4879e0e2e3bdab22c15fe4503fb3a3b0e16596343d42",
        "xy_core": xy.exact_core_valid(),
        "xy_qr": xy.qr_bit == 0 and xy.qr_lane == "xy" and xy.qr_phase == 0,
        "yx_core": yx.exact_core_valid(),
        "yx_qr": yx.qr_bit == 1 and yx.qr_lane == "yx" and yx.qr_phase == N36,
        "phase_ring": N72 == 72,
        "metric": N5256 == 5256,
        "qr_formula": quadratic_reciprocity_bit(3, 7) == 1,
    }


__all__ = [
    "CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE",
    "CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SHA256",
    "PROFILE_INTEGER_SYMMETRIC_V1",
    "PROFILE_FULL_SYMBOLIC_V1",
    "SYMBOLIC_RESIDUALS_V1",
    "NativeUniversalConstraintWitness",
    "build_integer_symmetric_witness",
    "expected_phase_basis_pair",
    "reference_invariants",
]
