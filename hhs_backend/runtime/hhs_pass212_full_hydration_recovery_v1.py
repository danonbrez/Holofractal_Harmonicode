"""Pass 212 full-hydration compression and physical shard-erasure recovery.

The 5,184-bit Pass 210 register is a local leaf, not the total information
envelope.  Pass 212 binds the complete 40-lane VM5184 x G243 hydration:

    40 * 243 * 5,184 = 50,388,480 bits = 6,298,560 bytes.

Each of the 9,720 local leaves is one 5,184-bit frame for a fixed ordered
lane/magnitude coordinate and G243 control.  The strict affine-leaf codec stores
two generator bits per leaf (19,440 bits / 2,430 bytes) plus exact sparse XOR
exceptions.  Arbitrary states fall back to raw packed bytes without a false
compression claim.  The encoded payload is protected by two independent
GF(256) parity shards per 243-data-shard stripe and can reconstruct any two
missing physical shards in each stripe.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

CONTRACT = "HHS-P212-FULL-HYDRATION-SUPERFRAME-COMPRESSION-PHYSICAL-ERASURE-RECOVERY-H72-H216"
PASS_NUMBER = 212
CONTRACT_VERSION = "1.0.0"
RUNTIME_CLASSIFICATION = "HHS_PASS_212_FULL_HYDRATION_PHYSICAL_RECOVERY_RUNTIME_VERIFIED"

VM81_CELLS = 81
ORDERED_OPCODES = 64
LOCAL_FRAME_BITS = VM81_CELLS * ORDERED_OPCODES  # 5,184
LOCAL_FRAME_BYTES = LOCAL_FRAME_BITS // 8  # 648
G243_CONTROLS = 243
ORDERED_BASIS_LANES = 8
LO_SHU_LOCAL_MAGNITUDES = 5
HYDRATION_LANES = ORDERED_BASIS_LANES * LO_SHU_LOCAL_MAGNITUDES  # 40
FULL_FRAME_COUNT = HYDRATION_LANES * G243_CONTROLS  # 9,720
FULL_HYDRATION_BITS = FULL_FRAME_COUNT * LOCAL_FRAME_BITS  # 50,388,480
FULL_HYDRATION_BYTES = FULL_HYDRATION_BITS // 8  # 6,298,560
AFFINE_SEED_BITS = FULL_FRAME_COUNT * 2  # 19,440
AFFINE_SEED_BYTES = AFFINE_SEED_BITS // 8  # 2,430
STRIPE_DATA_SHARDS = G243_CONTROLS
PARITY_SHARDS_PER_STRIPE = 2
MAX_SPARSE_EXCEPTION_BITS = 1_000_000
ZERO_HASH72 = "0" * 72

COMPRESSED_MAGIC = b"HHS-P212-COMPRESSED-HYDRATION-V1\0"
CODEC_RAW = 0
CODEC_AFFINE_SPARSE = 1


class Pass212Error(RuntimeError):
    pass


class Pass212ValidationError(Pass212Error):
    pass


class Pass212UnrecoverableError(Pass212Error):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _hash216(domain: str, payload: bytes) -> str:
    framed = b"HHS-P212-HASH216-V1\0" + domain.encode("utf-8") + b"\0" + len(payload).to_bytes(8, "big") + payload
    return sha256(framed).hexdigest()


def _uleb128_encode(value: int) -> bytes:
    value = int(value)
    if value < 0:
        raise Pass212ValidationError("PASS212_ULEB128_NEGATIVE")
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _uleb128_decode(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    start = offset
    while offset < len(data):
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            if _uleb128_encode(value) != data[start:offset]:
                raise Pass212ValidationError("PASS212_ULEB128_NONCANONICAL")
            return value, offset
        shift += 7
        if shift > 63:
            raise Pass212ValidationError("PASS212_ULEB128_OVERFLOW")
    raise Pass212ValidationError("PASS212_ULEB128_TRUNCATED")


def _gf_tables() -> tuple[tuple[int, ...], tuple[int, ...]]:
    exp = [0] * 512
    log = [0] * 256
    x = 1
    for i in range(255):
        exp[i] = x
        log[x] = i
        x <<= 1
        if x & 0x100:
            x ^= 0x11D
    for i in range(255, 512):
        exp[i] = exp[i - 255]
    return tuple(exp), tuple(log)


_GF_EXP, _GF_LOG = _gf_tables()
_GF_MUL = tuple(
    bytes(0 if a == 0 or b == 0 else _GF_EXP[_GF_LOG[a] + _GF_LOG[b]] for b in range(256))
    for a in range(256)
)


def _gf_mul(a: int, b: int) -> int:
    return _GF_MUL[int(a)][int(b)]


def _gf_inv(a: int) -> int:
    a = int(a)
    if a == 0:
        raise Pass212ValidationError("PASS212_GF_ZERO_INVERSE")
    return _GF_EXP[255 - _GF_LOG[a]]


def _gf_div(a: int, b: int) -> int:
    return _gf_mul(a, _gf_inv(b))


def _xor_into(target: bytearray, source: bytes) -> None:
    for i, value in enumerate(source):
        target[i] ^= value


def _weighted_xor_into(target: bytearray, source: bytes, coefficient: int) -> None:
    table = _GF_MUL[coefficient]
    for i, value in enumerate(source):
        target[i] ^= table[value]


def _seed_pattern(seed: int) -> bytes:
    seed = int(seed)
    if seed not in range(4):
        raise Pass212ValidationError("PASS212_AFFINE_SEED_INVALID")
    a = (seed >> 1) & 1
    b = seed & 1
    bits = [a, b]
    while len(bits) < 24:
        bits.append(bits[-1] ^ bits[-2] ^ 1)
    period = bits[:3] if (a, b) != (1, 1) else [1]
    packed = bytearray(LOCAL_FRAME_BYTES)
    for position in range(LOCAL_FRAME_BITS):
        bit = period[position % len(period)]
        if bit:
            packed[position // 8] |= 1 << (7 - position % 8)
    return bytes(packed)


_AFFINE_PATTERNS = tuple(_seed_pattern(seed) for seed in range(4))
_AFFINE_PATTERN_INTS = tuple(int.from_bytes(pattern, "big") for pattern in _AFFINE_PATTERNS)


def pack_frame_seeds(seeds: Sequence[int]) -> bytes:
    if len(seeds) != FULL_FRAME_COUNT:
        raise Pass212ValidationError("PASS212_SEED_COUNT_INVALID")
    out = bytearray(AFFINE_SEED_BYTES)
    for index, seed in enumerate(seeds):
        seed = int(seed)
        if seed not in range(4):
            raise Pass212ValidationError(f"PASS212_AFFINE_SEED_INVALID:{index}")
        out[index // 4] |= seed << (6 - 2 * (index % 4))
    return bytes(out)


def unpack_frame_seeds(raw: bytes | bytearray | memoryview) -> tuple[int, ...]:
    data = bytes(raw)
    if len(data) != AFFINE_SEED_BYTES:
        raise Pass212ValidationError("PASS212_SEED_BYTES_LENGTH_INVALID")
    seeds: list[int] = []
    for value in data:
        seeds.extend(((value >> 6) & 3, (value >> 4) & 3, (value >> 2) & 3, value & 3))
    return tuple(seeds[:FULL_FRAME_COUNT])


def generate_affine_hydration(seed_bytes: bytes | bytearray | memoryview) -> bytes:
    seeds = unpack_frame_seeds(seed_bytes)
    return b"".join(_AFFINE_PATTERNS[seed] for seed in seeds)


def apply_bit_exceptions(state: bytes, positions: Iterable[int]) -> bytes:
    if len(state) != FULL_HYDRATION_BYTES:
        raise Pass212ValidationError("PASS212_FULL_HYDRATION_LENGTH_INVALID")
    changed = bytearray(state)
    previous = -1
    for raw_position in positions:
        position = int(raw_position)
        if not 0 <= position < FULL_HYDRATION_BITS:
            raise Pass212ValidationError("PASS212_EXCEPTION_POSITION_OUT_OF_RANGE")
        if position <= previous:
            raise Pass212ValidationError("PASS212_EXCEPTION_POSITIONS_NOT_STRICTLY_ASCENDING")
        changed[position // 8] ^= 1 << (7 - position % 8)
        previous = position
    return bytes(changed)


def _encode_exception_positions(positions: Sequence[int]) -> bytes:
    out = bytearray()
    out += _uleb128_encode(len(positions))
    previous = -1
    for position in positions:
        delta = int(position) - previous
        if delta <= 0:
            raise Pass212ValidationError("PASS212_EXCEPTION_DELTA_INVALID")
        out += _uleb128_encode(delta)
        previous = int(position)
    return bytes(out)


def _decode_exception_positions(data: bytes, offset: int) -> tuple[tuple[int, ...], int]:
    count, offset = _uleb128_decode(data, offset)
    positions: list[int] = []
    previous = -1
    for _ in range(count):
        delta, offset = _uleb128_decode(data, offset)
        position = previous + delta
        if not 0 <= position < FULL_HYDRATION_BITS:
            raise Pass212ValidationError("PASS212_EXCEPTION_POSITION_OUT_OF_RANGE")
        positions.append(position)
        previous = position
    return tuple(positions), offset


@dataclass(frozen=True)
class PhysicalShard:
    stripe: int
    role: str
    index: int
    payload_length: int
    payload_hash216: str
    payload: bytes | None

    @property
    def ref(self) -> str:
        return f"{self.stripe}:{self.role}:{self.index}"

    def metadata(self) -> dict[str, Any]:
        return {
            "stripe": self.stripe,
            "role": self.role,
            "index": self.index,
            "payload_length": self.payload_length,
            "payload_hash216": self.payload_hash216,
        }

    def to_dict(self, include_payload: bool = True) -> dict[str, Any]:
        record = self.metadata()
        record["payload_hex"] = None if self.payload is None else self.payload.hex() if include_payload else "OMITTED"
        return record

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "PhysicalShard":
        raw = value.get("payload_hex")
        payload = None if raw is None else bytes.fromhex(str(raw))
        return cls(
            stripe=int(value["stripe"]),
            role=str(value["role"]),
            index=int(value["index"]),
            payload_length=int(value["payload_length"]),
            payload_hash216=str(value["payload_hash216"]),
            payload=payload,
        )


@dataclass(frozen=True)
class ProtectedPayload:
    original_length: int
    data_shard_count: int
    stripe_count: int
    shards: tuple[PhysicalShard, ...]
    root216: str
    receipt_hash72: str

    def to_dict(self, include_payloads: bool = True) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_212_PROTECTED_PAYLOAD_V1",
            "original_length": self.original_length,
            "data_shard_count": self.data_shard_count,
            "stripe_count": self.stripe_count,
            "shards": [shard.to_dict(include_payloads) for shard in self.shards],
            "root216": self.root216,
            "receipt_hash72": self.receipt_hash72,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ProtectedPayload":
        if value.get("schema") != "HHS_PASS_212_PROTECTED_PAYLOAD_V1":
            raise Pass212ValidationError("PASS212_PROTECTED_PAYLOAD_SCHEMA_INVALID")
        return cls(
            original_length=int(value["original_length"]),
            data_shard_count=int(value["data_shard_count"]),
            stripe_count=int(value["stripe_count"]),
            shards=tuple(PhysicalShard.from_mapping(item) for item in value["shards"]),
            root216=str(value["root216"]),
            receipt_hash72=str(value["receipt_hash72"]),
        )


@dataclass(frozen=True)
class FullHydrationPackage:
    codec: str
    state_hash216: str
    lane_roots216: tuple[str, ...]
    full_root216: str
    compressed_payload_bytes: int
    exception_count: int
    protected: ProtectedPayload
    package_root216: str
    package_receipt_hash72: str
    metrics: Mapping[str, Any]

    def to_dict(self, include_payloads: bool = True) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_212_FULL_HYDRATION_PACKAGE_V1",
            "contract": CONTRACT,
            "pass": PASS_NUMBER,
            "codec": self.codec,
            "state_hash216": self.state_hash216,
            "lane_roots216": list(self.lane_roots216),
            "full_root216": self.full_root216,
            "compressed_payload_bytes": self.compressed_payload_bytes,
            "exception_count": self.exception_count,
            "protected": self.protected.to_dict(include_payloads),
            "package_root216": self.package_root216,
            "package_receipt_hash72": self.package_receipt_hash72,
            "metrics": dict(self.metrics),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "FullHydrationPackage":
        if value.get("schema") != "HHS_PASS_212_FULL_HYDRATION_PACKAGE_V1" or value.get("contract") != CONTRACT:
            raise Pass212ValidationError("PASS212_PACKAGE_SCHEMA_INVALID")
        return cls(
            codec=str(value["codec"]),
            state_hash216=str(value["state_hash216"]),
            lane_roots216=tuple(str(item) for item in value["lane_roots216"]),
            full_root216=str(value["full_root216"]),
            compressed_payload_bytes=int(value["compressed_payload_bytes"]),
            exception_count=int(value["exception_count"]),
            protected=ProtectedPayload.from_mapping(value["protected"]),
            package_root216=str(value["package_root216"]),
            package_receipt_hash72=str(value["package_receipt_hash72"]),
            metrics=dict(value["metrics"]),
        )


class FullHydrationRecoveryRuntime:
    @staticmethod
    def _state_roots(state: bytes) -> tuple[tuple[str, ...], str]:
        lane_roots: list[str] = []
        for lane in range(HYDRATION_LANES):
            frame_hashes = []
            lane_start = lane * G243_CONTROLS * LOCAL_FRAME_BYTES
            for control in range(G243_CONTROLS):
                start = lane_start + control * LOCAL_FRAME_BYTES
                frame = state[start : start + LOCAL_FRAME_BYTES]
                frame_hashes.append(_hash216("PASS212_LOCAL_HFC_LEAF", lane.to_bytes(1, "big") + control.to_bytes(2, "big") + frame))
            lane_roots.append(_hash216("PASS212_LANE_ROOT", b"".join(bytes.fromhex(item) for item in frame_hashes)))
        full_root = _hash216("PASS212_FULL_HYDRATION_ROOT", b"".join(bytes.fromhex(item) for item in lane_roots))
        return tuple(lane_roots), full_root

    @staticmethod
    def _compress(state: bytes) -> tuple[bytes, str, int]:
        if len(state) != FULL_HYDRATION_BYTES:
            raise Pass212ValidationError("PASS212_FULL_HYDRATION_LENGTH_INVALID")
        seeds: list[int] = []
        selected_diffs: list[int] = []
        total_distance = 0
        for frame_index in range(FULL_FRAME_COUNT):
            start = frame_index * LOCAL_FRAME_BYTES
            frame_int = int.from_bytes(state[start : start + LOCAL_FRAME_BYTES], "big")
            distances = tuple((frame_int ^ pattern).bit_count() for pattern in _AFFINE_PATTERN_INTS)
            seed = min(range(4), key=lambda item: (distances[item], item))
            seeds.append(seed)
            total_distance += distances[seed]
            selected_diffs.append(frame_int ^ _AFFINE_PATTERN_INTS[seed])
            if total_distance > MAX_SPARSE_EXCEPTION_BITS:
                return state, "RAW_PACKED_FALLBACK", 0
        positions: list[int] = []
        for frame_index, difference in enumerate(selected_diffs):
            local_positions: list[int] = []
            while difference:
                lsb = difference & -difference
                lsb_index = lsb.bit_length() - 1
                local_positions.append(LOCAL_FRAME_BITS - 1 - lsb_index)
                difference ^= lsb
            for local in reversed(local_positions):
                positions.append(frame_index * LOCAL_FRAME_BITS + local)
        seed_bytes = pack_frame_seeds(seeds)
        payload = (
            COMPRESSED_MAGIC
            + bytes([CODEC_AFFINE_SPARSE])
            + FULL_HYDRATION_BITS.to_bytes(8, "big")
            + seed_bytes
            + _encode_exception_positions(positions)
        )
        if len(payload) >= len(state):
            return state, "RAW_PACKED_FALLBACK", 0
        return payload, "AFFINE_9720_LEAF_SEEDS_PLUS_SPARSE_XOR", len(positions)

    @staticmethod
    def _decompress(payload: bytes, expected_codec: str) -> tuple[bytes, str, int]:
        if expected_codec == "RAW_PACKED_FALLBACK":
            if len(payload) != FULL_HYDRATION_BYTES:
                raise Pass212ValidationError("PASS212_RAW_PAYLOAD_LENGTH_INVALID")
            return bytes(payload), expected_codec, 0
        if expected_codec != "AFFINE_9720_LEAF_SEEDS_PLUS_SPARSE_XOR":
            raise Pass212ValidationError("PASS212_CODEC_INVALID")
        if not payload.startswith(COMPRESSED_MAGIC):
            raise Pass212ValidationError("PASS212_COMPRESSED_MAGIC_INVALID")
        offset = len(COMPRESSED_MAGIC)
        codec = payload[offset]
        offset += 1
        if codec != CODEC_AFFINE_SPARSE:
            raise Pass212ValidationError("PASS212_COMPRESSED_CODEC_TAG_INVALID")
        bit_length = int.from_bytes(payload[offset : offset + 8], "big")
        offset += 8
        if bit_length != FULL_HYDRATION_BITS:
            raise Pass212ValidationError("PASS212_FULL_HYDRATION_BIT_LENGTH_INVALID")
        seed_end = offset + AFFINE_SEED_BYTES
        seeds = payload[offset:seed_end]
        offset = seed_end
        positions, offset = _decode_exception_positions(payload, offset)
        if offset != len(payload):
            raise Pass212ValidationError("PASS212_COMPRESSED_PAYLOAD_LENGTH_INVALID")
        state = apply_bit_exceptions(generate_affine_hydration(seeds), positions)
        return state, expected_codec, len(positions)

    @staticmethod
    def _protected_root(original_length: int, data_count: int, stripe_count: int, shards: Sequence[PhysicalShard]) -> str:
        metadata = {
            "original_length": original_length,
            "data_shard_count": data_count,
            "stripe_count": stripe_count,
            "shards": [shard.metadata() for shard in shards],
        }
        return _hash216("PASS212_PROTECTED_PAYLOAD_ROOT", _canonical_bytes(metadata))

    @staticmethod
    def _protected_receipt(root216: str) -> str:
        return hash72_digest(
            {"contract": CONTRACT, "event": "PASS212_PROTECTED_PAYLOAD_COMMIT"},
            {"sequence": 1, "parent_hash72": ZERO_HASH72, "root216": root216},
        )

    def protect_payload(self, payload: bytes) -> ProtectedPayload:
        raw = bytes(payload)
        if not raw:
            raise Pass212ValidationError("PASS212_EMPTY_PROTECTED_PAYLOAD")
        chunks = [raw[offset : offset + LOCAL_FRAME_BYTES] for offset in range(0, len(raw), LOCAL_FRAME_BYTES)]
        shards: list[PhysicalShard] = []
        stripe_count = (len(chunks) + STRIPE_DATA_SHARDS - 1) // STRIPE_DATA_SHARDS
        for stripe in range(stripe_count):
            stripe_chunks = chunks[stripe * STRIPE_DATA_SHARDS : (stripe + 1) * STRIPE_DATA_SHARDS]
            padded = [chunk + b"\x00" * (LOCAL_FRAME_BYTES - len(chunk)) for chunk in stripe_chunks]
            parity0 = bytearray(LOCAL_FRAME_BYTES)
            parity1 = bytearray(LOCAL_FRAME_BYTES)
            for index, chunk in enumerate(padded):
                _xor_into(parity0, chunk)
                _weighted_xor_into(parity1, chunk, index + 1)
                shards.append(PhysicalShard(stripe, "data", index, len(stripe_chunks[index]), _hash216("PASS212_PHYSICAL_DATA_SHARD", stripe.to_bytes(2, "big") + index.to_bytes(2, "big") + stripe_chunks[index]), stripe_chunks[index]))
            for parity_index, parity in enumerate((bytes(parity0), bytes(parity1))):
                role = f"parity{parity_index}"
                shards.append(PhysicalShard(stripe, role, parity_index, LOCAL_FRAME_BYTES, _hash216("PASS212_PHYSICAL_PARITY_SHARD", stripe.to_bytes(2, "big") + parity_index.to_bytes(1, "big") + parity), parity))
        root = self._protected_root(len(raw), len(chunks), stripe_count, shards)
        return ProtectedPayload(len(raw), len(chunks), stripe_count, tuple(shards), root, self._protected_receipt(root))

    @staticmethod
    def _verify_present_shard(shard: PhysicalShard) -> None:
        if shard.payload is None:
            return
        payload = bytes(shard.payload)
        if len(payload) != shard.payload_length:
            raise Pass212ValidationError(f"PASS212_PHYSICAL_SHARD_LENGTH_MISMATCH:{shard.ref}")
        if shard.role == "data":
            expected = _hash216("PASS212_PHYSICAL_DATA_SHARD", shard.stripe.to_bytes(2, "big") + shard.index.to_bytes(2, "big") + payload)
        else:
            expected = _hash216("PASS212_PHYSICAL_PARITY_SHARD", shard.stripe.to_bytes(2, "big") + shard.index.to_bytes(1, "big") + payload)
        if expected != shard.payload_hash216:
            raise Pass212ValidationError(f"PASS212_PHYSICAL_SHARD_HASH_MISMATCH:{shard.ref}")

    def recover_payload(self, protected: ProtectedPayload | Mapping[str, Any]) -> bytes:
        value = protected if isinstance(protected, ProtectedPayload) else ProtectedPayload.from_mapping(protected)
        if value.data_shard_count <= 0 or value.stripe_count <= 0:
            raise Pass212ValidationError("PASS212_PROTECTED_COUNTS_INVALID")
        expected_root = self._protected_root(value.original_length, value.data_shard_count, value.stripe_count, value.shards)
        if expected_root != value.root216 or self._protected_receipt(expected_root) != value.receipt_hash72:
            raise Pass212ValidationError("PASS212_PROTECTED_ROOT_OR_RECEIPT_MISMATCH")
        for shard in value.shards:
            self._verify_present_shard(shard)
        recovered_data: list[bytes] = []
        for stripe in range(value.stripe_count):
            stripe_shards = [shard for shard in value.shards if shard.stripe == stripe]
            data_records = sorted((shard for shard in stripe_shards if shard.role == "data"), key=lambda item: item.index)
            parity0 = next((shard for shard in stripe_shards if shard.role == "parity0"), None)
            parity1 = next((shard for shard in stripe_shards if shard.role == "parity1"), None)
            if parity0 is None or parity1 is None:
                raise Pass212ValidationError("PASS212_PARITY_RECORD_MISSING")
            expected_data_count = min(STRIPE_DATA_SHARDS, value.data_shard_count - stripe * STRIPE_DATA_SHARDS)
            if len(data_records) != expected_data_count or [record.index for record in data_records] != list(range(expected_data_count)):
                raise Pass212ValidationError("PASS212_DATA_RECORD_SET_INVALID")
            missing_data = [record.index for record in data_records if record.payload is None]
            missing_parity = int(parity0.payload is None) + int(parity1.payload is None)
            if len(missing_data) + missing_parity > PARITY_SHARDS_PER_STRIPE:
                raise Pass212UnrecoverableError(f"PASS212_ERASURE_BUDGET_EXCEEDED:{stripe}")
            padded: list[bytes | None] = [None if record.payload is None else bytes(record.payload) + b"\x00" * (LOCAL_FRAME_BYTES - len(record.payload)) for record in data_records]
            p0 = None if parity0.payload is None else bytes(parity0.payload)
            p1 = None if parity1.payload is None else bytes(parity1.payload)
            if len(missing_data) == 1:
                missing = missing_data[0]
                if p0 is not None:
                    recovered = bytearray(p0)
                    for index, chunk in enumerate(padded):
                        if index != missing and chunk is not None:
                            _xor_into(recovered, chunk)
                elif p1 is not None:
                    recovered_weighted = bytearray(p1)
                    for index, chunk in enumerate(padded):
                        if index != missing and chunk is not None:
                            _weighted_xor_into(recovered_weighted, chunk, index + 1)
                    inverse = _gf_inv(missing + 1)
                    table = _GF_MUL[inverse]
                    recovered = bytearray(table[value] for value in recovered_weighted)
                else:
                    raise Pass212UnrecoverableError(f"PASS212_NO_PARITY_FOR_DATA_RECOVERY:{stripe}")
                padded[missing] = bytes(recovered)
            elif len(missing_data) == 2:
                if p0 is None or p1 is None:
                    raise Pass212UnrecoverableError(f"PASS212_TWO_DATA_ERASURES_REQUIRE_TWO_PARITIES:{stripe}")
                first, second = missing_data
                s0 = bytearray(p0)
                s1 = bytearray(p1)
                for index, chunk in enumerate(padded):
                    if chunk is not None:
                        _xor_into(s0, chunk)
                        _weighted_xor_into(s1, chunk, index + 1)
                a = first + 1
                b = second + 1
                denominator = a ^ b
                if denominator == 0:
                    raise Pass212UnrecoverableError("PASS212_GF_COEFFICIENT_COLLISION")
                first_bytes = bytearray(LOCAL_FRAME_BYTES)
                second_bytes = bytearray(LOCAL_FRAME_BYTES)
                for offset in range(LOCAL_FRAME_BYTES):
                    # y = (S1 + a*S0) / (a+b); x = S0 + y
                    y = _gf_div(s1[offset] ^ _gf_mul(a, s0[offset]), denominator)
                    x = s0[offset] ^ y
                    first_bytes[offset] = x
                    second_bytes[offset] = y
                padded[first] = bytes(first_bytes)
                padded[second] = bytes(second_bytes)
            if any(chunk is None for chunk in padded):
                raise Pass212UnrecoverableError(f"PASS212_DATA_RECOVERY_INCOMPLETE:{stripe}")
            recomputed0 = bytearray(LOCAL_FRAME_BYTES)
            recomputed1 = bytearray(LOCAL_FRAME_BYTES)
            for index, chunk in enumerate(padded):
                assert chunk is not None
                _xor_into(recomputed0, chunk)
                _weighted_xor_into(recomputed1, chunk, index + 1)
            computed_parities = (bytes(recomputed0), bytes(recomputed1))
            for parity_record, computed in ((parity0, computed_parities[0]), (parity1, computed_parities[1])):
                if parity_record.payload is not None and bytes(parity_record.payload) != computed:
                    raise Pass212ValidationError(f"PASS212_{parity_record.role.upper()}_MISMATCH:{stripe}")
                expected_hash = _hash216(
                    "PASS212_PHYSICAL_PARITY_SHARD",
                    stripe.to_bytes(2, "big") + parity_record.index.to_bytes(1, "big") + computed,
                )
                if expected_hash != parity_record.payload_hash216:
                    raise Pass212ValidationError(f"PASS212_RECOVERED_PARITY_HASH_MISMATCH:{parity_record.ref}")
            for record, chunk in zip(data_records, padded):
                assert chunk is not None
                recovered = chunk[: record.payload_length]
                expected_hash = _hash216(
                    "PASS212_PHYSICAL_DATA_SHARD",
                    stripe.to_bytes(2, "big") + record.index.to_bytes(2, "big") + recovered,
                )
                if expected_hash != record.payload_hash216:
                    raise Pass212ValidationError(f"PASS212_RECOVERED_DATA_SHARD_HASH_MISMATCH:{record.ref}")
                recovered_data.append(recovered)
        payload = b"".join(recovered_data)
        if len(payload) != value.original_length:
            raise Pass212ValidationError("PASS212_RECOVERED_PAYLOAD_LENGTH_MISMATCH")
        return payload

    @staticmethod
    def _package_root_payload(codec: str, state_hash216: str, lane_roots: Sequence[str], full_root: str, compressed_bytes: int, exception_count: int, protected_root: str) -> dict[str, Any]:
        return {
            "contract": CONTRACT,
            "version": CONTRACT_VERSION,
            "codec": codec,
            "state_hash216": state_hash216,
            "lane_roots216": list(lane_roots),
            "full_root216": full_root,
            "compressed_payload_bytes": compressed_bytes,
            "exception_count": exception_count,
            "protected_root216": protected_root,
        }

    @staticmethod
    def _package_receipt(root216: str) -> str:
        return hash72_digest(
            {"contract": CONTRACT, "event": "PASS212_FULL_HYDRATION_COMMIT"},
            {"sequence": 1, "parent_hash72": ZERO_HASH72, "package_root216": root216},
        )

    def encode(self, state: bytes | bytearray | memoryview) -> FullHydrationPackage:
        raw = bytes(state)
        if len(raw) != FULL_HYDRATION_BYTES:
            raise Pass212ValidationError("PASS212_FULL_HYDRATION_LENGTH_INVALID")
        compressed, codec, exception_count = self._compress(raw)
        protected = self.protect_payload(compressed)
        lane_roots, full_root = self._state_roots(raw)
        state_hash = _hash216("PASS212_FULL_STATE", raw)
        root_payload = self._package_root_payload(codec, state_hash, lane_roots, full_root, len(compressed), exception_count, protected.root216)
        package_root = _hash216("PASS212_PACKAGE_ROOT", _canonical_bytes(root_payload))
        protected_storage = sum(shard.payload_length for shard in protected.shards)
        metrics = {
            "full_hydration_bits": FULL_HYDRATION_BITS,
            "full_hydration_bytes": FULL_HYDRATION_BYTES,
            "local_hfc_leaf_bits": LOCAL_FRAME_BITS,
            "local_hfc_leaf_bytes": LOCAL_FRAME_BYTES,
            "local_hfc_leaf_count": FULL_FRAME_COUNT,
            "affine_seed_bits": AFFINE_SEED_BITS,
            "affine_seed_bytes": AFFINE_SEED_BYTES,
            "compressed_payload_bytes": len(compressed),
            "compression_ratio": {"numerator": FULL_HYDRATION_BYTES, "denominator": len(compressed)},
            "data_shard_count": protected.data_shard_count,
            "parity_shard_count": protected.stripe_count * PARITY_SHARDS_PER_STRIPE,
            "protected_storage_bytes": protected_storage,
            "physical_erasure_tolerance_per_stripe": PARITY_SHARDS_PER_STRIPE,
            "stripe_data_shards": STRIPE_DATA_SHARDS,
            "strict_compression_claim": codec != "RAW_PACKED_FALLBACK",
        }
        return FullHydrationPackage(codec, state_hash, lane_roots, full_root, len(compressed), exception_count, protected, package_root, self._package_receipt(package_root), metrics)

    def decode(self, package: FullHydrationPackage | Mapping[str, Any]) -> bytes:
        value = package if isinstance(package, FullHydrationPackage) else FullHydrationPackage.from_mapping(package)
        payload = self.recover_payload(value.protected)
        state, codec, exception_count = self._decompress(payload, value.codec)
        if codec != value.codec or exception_count != value.exception_count or len(payload) != value.compressed_payload_bytes:
            raise Pass212ValidationError("PASS212_CODEC_METADATA_MISMATCH")
        state_hash = _hash216("PASS212_FULL_STATE", state)
        lane_roots, full_root = self._state_roots(state)
        if state_hash != value.state_hash216 or lane_roots != value.lane_roots216 or full_root != value.full_root216:
            raise Pass212ValidationError("PASS212_FULL_HYDRATION_ROOT_MISMATCH")
        root_payload = self._package_root_payload(value.codec, value.state_hash216, value.lane_roots216, value.full_root216, value.compressed_payload_bytes, value.exception_count, value.protected.root216)
        root = _hash216("PASS212_PACKAGE_ROOT", _canonical_bytes(root_payload))
        if root != value.package_root216 or self._package_receipt(root) != value.package_receipt_hash72:
            raise Pass212ValidationError("PASS212_PACKAGE_ROOT_OR_RECEIPT_MISMATCH")
        return state

    @staticmethod
    def without_shards(package: FullHydrationPackage, refs: Iterable[str]) -> FullHydrationPackage:
        missing = set(str(item) for item in refs)
        known = {shard.ref for shard in package.protected.shards}
        if not missing <= known:
            raise Pass212ValidationError("PASS212_UNKNOWN_SHARD_REFERENCE")
        shards = tuple(replace(shard, payload=None) if shard.ref in missing else shard for shard in package.protected.shards)
        protected = replace(package.protected, shards=shards)
        return replace(package, protected=protected)

    @staticmethod
    def corrupt_shard(package: FullHydrationPackage, ref: str, offset: int = 0) -> FullHydrationPackage:
        changed: list[PhysicalShard] = []
        found = False
        for shard in package.protected.shards:
            if shard.ref != ref:
                changed.append(shard)
                continue
            found = True
            if shard.payload is None or not 0 <= offset < len(shard.payload):
                raise Pass212ValidationError("PASS212_CORRUPTION_TARGET_INVALID")
            payload = bytearray(shard.payload)
            payload[offset] ^= 1
            changed.append(replace(shard, payload=bytes(payload)))
        if not found:
            raise Pass212ValidationError("PASS212_UNKNOWN_SHARD_REFERENCE")
        return replace(package, protected=replace(package.protected, shards=tuple(changed)))

    @staticmethod
    def status() -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_212_FULL_HYDRATION_STATUS_V1",
            "contract": CONTRACT,
            "pass": PASS_NUMBER,
            "runtime_classification": RUNTIME_CLASSIFICATION,
            "dimensions": {
                "vm81_cells": VM81_CELLS,
                "ordered_opcodes": ORDERED_OPCODES,
                "local_frame_bits": LOCAL_FRAME_BITS,
                "g243_controls": G243_CONTROLS,
                "ordered_basis_lanes": ORDERED_BASIS_LANES,
                "lo_shu_local_magnitudes": LO_SHU_LOCAL_MAGNITUDES,
                "hydration_lanes": HYDRATION_LANES,
                "full_frame_count": FULL_FRAME_COUNT,
                "full_hydration_bits": FULL_HYDRATION_BITS,
                "full_hydration_bytes": FULL_HYDRATION_BYTES,
                "affine_seed_bits": AFFINE_SEED_BITS,
                "affine_seed_bytes": AFFINE_SEED_BYTES,
            },
            "protection": {
                "data_shards_per_stripe": STRIPE_DATA_SHARDS,
                "parity_shards_per_stripe": PARITY_SHARDS_PER_STRIPE,
                "recoverable_missing_physical_shards_per_stripe": PARITY_SHARDS_PER_STRIPE,
                "gf": "GF(256)/0x11d",
            },
            "claim_boundary": {
                "full_state_processing": True,
                "physical_shard_reconstruction": True,
                "strict_compression": "affine 9,720-leaf seeds plus sparse XOR exceptions only",
                "arbitrary_state": "raw packed fallback, protected but not described as compressed",
            },
        }


_RUNTIME = FullHydrationRecoveryRuntime()


def get_pass212_runtime() -> FullHydrationRecoveryRuntime:
    return _RUNTIME
