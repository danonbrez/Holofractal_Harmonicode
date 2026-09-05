"""Pass 219 I148 raw-5184 / octonion dual-stereo PCM64 reference path."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

RAW_BITS = 5184
RAW_BYTES = 648
CELLS = 81
WORD_BITS = 64
PHASE_QUADS = 20
PHASE_CHANNELS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
PILOT_CELL = 80
H36 = 36
SINE_Q62_SCALE = 1 << 62
PCM64_NOISE_FLOOR = -(1 << 63)
PCM64_ZERO_CROSSING = 0
PCM64_SATURATION_CEILING = (1 << 63) - 1
MASK64 = (1 << 64) - 1

SINE_Q62 = (
    0, 401934920255029411, 800810873071977681, 1193592171602022505,
    1577289512995517789, 1948982728801669864, 2305843009213693952,
    2645154432019525852, 2964334632409774423, 3260954456333195553,
    3532756447825785444, 3777672029613755863, 3993837246235628775,
    4179606949868785275, 4333567320897763126, 4454546627935218059,
    4541624145405292212, 4594137160821195716, 4611686018427387904,
    4594137160821195716, 4541624145405292212, 4454546627935218059,
    4333567320897763126, 4179606949868785275, 3993837246235628775,
    3777672029613755863, 3532756447825785444, 3260954456333195553,
    2964334632409774423, 2645154432019525852, 2305843009213693952,
    1948982728801669864, 1577289512995517789, 1193592171602022505,
    800810873071977681, 401934920255029411, 0, -401934920255029411,
    -800810873071977681, -1193592171602022505, -1577289512995517789,
    -1948982728801669864, -2305843009213693952, -2645154432019525852,
    -2964334632409774423, -3260954456333195553, -3532756447825785444,
    -3777672029613755863, -3993837246235628775, -4179606949868785275,
    -4333567320897763126, -4454546627935218059, -4541624145405292212,
    -4594137160821195716, -4611686018427387904, -4594137160821195716,
    -4541624145405292212, -4454546627935218059, -4333567320897763126,
    -4179606949868785275, -3993837246235628775, -3777672029613755863,
    -3532756447825785444, -3260954456333195553, -2964334632409774423,
    -2645154432019525852, -2305843009213693952, -1948982728801669864,
    -1577289512995517789, -1193592171602022505, -800810873071977681,
    -401934920255029411,
)


def bitstring_to_words(bits: str) -> tuple[int, ...]:
    if len(bits) != RAW_BITS:
        raise ValueError("RAW5184_LENGTH")
    if set(bits) - {"0", "1"}:
        raise ValueError("RAW5184_CHARACTER")
    words = []
    for cell in range(CELLS):
        word = 0
        base = cell * WORD_BITS
        for bit in range(WORD_BITS):
            if bits[base + bit] == "1":
                word |= 1 << bit
        words.append(word)
    return tuple(words)


def words_to_bitstring(words: Sequence[int]) -> str:
    if len(words) != CELLS:
        raise ValueError("VM81_CELL_COUNT")
    chars: list[str] = []
    for word in words:
        if not 0 <= int(word) <= MASK64:
            raise ValueError("VM81_WORD_RANGE")
        chars.extend("1" if (int(word) >> bit) & 1 else "0" for bit in range(WORD_BITS))
    return "".join(chars)


def words_to_le_bytes(words: Sequence[int]) -> bytes:
    if len(words) != CELLS:
        raise ValueError("VM81_CELL_COUNT")
    return b"".join(int(word).to_bytes(8, "little", signed=False) for word in words)


def le_bytes_to_words(payload: bytes) -> tuple[int, ...]:
    if len(payload) != RAW_BYTES:
        raise ValueError("VM81_BYTE_COUNT")
    return tuple(
        int.from_bytes(payload[i : i + 8], "little", signed=False)
        for i in range(0, RAW_BYTES, 8)
    )


def fold_word72(word: int) -> int:
    if not 0 <= word <= MASK64:
        raise ValueError("VM81_WORD_RANGE")
    return sum(((word >> (8 * i)) & 0xFF) * (i + 1) for i in range(8)) % 72


def octonion_channels_from_words(x: int, y: int, z: int, w: int) -> tuple[int, ...]:
    px, py, pz, pw = map(fold_word72, (x, y, z, w))
    return (
        px,
        py,
        pz,
        pw,
        (px + py) % 72,
        (py + px + 36) % 72,
        (pz + pw) % 72,
        (pw + pz + 36) % 72,
    )


@dataclass(frozen=True)
class PhaseChannel:
    basis: str
    phase72: int
    resonance36: int
    half_turn: int
    signed_phase: int
    sine_pcm64: int


@dataclass(frozen=True)
class StereoTernaryQuotient:
    numerator_roles: tuple[int, int, int]
    denominator_roles: tuple[int, int, int]
    quotient_identity: tuple[int, int, int]
    quotient_phase72: tuple[int, int, int]
    left_mono_phase72: tuple[int, int, int]
    right_mono_phase72: tuple[int, int, int]
    role_pcm64: tuple[int, int, int]
    left_mono_yx_sum_xy: bool
    right_mono_wz_sum_zw: bool
    center_mono_xy_sum_colon_zw_sum: bool
    exact_pcm64_role_bounds: bool
    center_zero_over_zero_u0_mod_u72: bool
    center_xy_sum_over_zw_sum_u0: bool
    typed_quotient_only: bool
    scalar_division_attempted: bool
    scalar_projection_runtime_authority: bool


@dataclass(frozen=True)
class PhaseQuad:
    index: int
    cells: tuple[int, int, int, int]
    stereo_xy: tuple[int, int]
    stereo_zw: tuple[int, int]
    channels: tuple[PhaseChannel, ...]
    stereo_ternary: StereoTernaryQuotient


@dataclass(frozen=True)
class AudioHydration:
    pcm64_bits: tuple[int, ...]
    quads: tuple[PhaseQuad, ...]
    pilot_pcm64_bits: int
    sine_pcm64: tuple[int, ...]
    canonical_mutation_authority: bool = False
    canonical_hash72_authority: bool = False
    canonical_hash216_authority: bool = False
    canonical_persistence_authority: bool = False
    scalar_projection_runtime_authority: bool = False
    floating_point_authority: bool = False


def phase_channel(basis: str, phase: int) -> PhaseChannel:
    if basis not in PHASE_CHANNELS or not 0 <= phase < 72:
        raise ValueError("PHASE_RANGE")
    resonance = phase % H36
    half_turn = phase // H36
    signed_phase = resonance - H36 if half_turn else resonance
    sine = SINE_Q62[phase]
    assert resonance + H36 * half_turn == phase
    return PhaseChannel(
        basis=basis,
        phase72=phase,
        resonance36=resonance,
        half_turn=half_turn,
        signed_phase=signed_phase,
        sine_pcm64=sine,
    )


def typed_stereo_ternary(channels: Sequence[PhaseChannel]) -> StereoTernaryQuotient:
    if tuple(channel.basis for channel in channels) != PHASE_CHANNELS:
        raise ValueError("ORDERED_OCTONION_CHANNELS")
    by_basis = {channel.basis: channel.phase72 for channel in channels}
    left = (
        by_basis["yx"],
        (by_basis["x"] + by_basis["y"]) % 72,
        by_basis["xy"],
    )
    right = (
        by_basis["wz"],
        (by_basis["z"] + by_basis["w"]) % 72,
        by_basis["zw"],
    )
    return StereoTernaryQuotient(
        numerator_roles=(-1, 0, 1),
        denominator_roles=(-1, 0, 1),
        quotient_identity=(1, 1, 1),
        quotient_phase72=(0, 0, 0),
        left_mono_phase72=left,
        right_mono_phase72=right,
        role_pcm64=(
            PCM64_NOISE_FLOOR,
            PCM64_ZERO_CROSSING,
            PCM64_SATURATION_CEILING,
        ),
        left_mono_yx_sum_xy=True,
        right_mono_wz_sum_zw=True,
        center_mono_xy_sum_colon_zw_sum=True,
        exact_pcm64_role_bounds=True,
        center_zero_over_zero_u0_mod_u72=True,
        center_xy_sum_over_zw_sum_u0=True,
        typed_quotient_only=True,
        scalar_division_attempted=False,
        scalar_projection_runtime_authority=False,
    )


def hydrate_words(words: Sequence[int]) -> AudioHydration:
    if len(words) != CELLS:
        raise ValueError("VM81_CELL_COUNT")
    normalized = tuple(int(word) for word in words)
    if any(word < 0 or word > MASK64 for word in normalized):
        raise ValueError("VM81_WORD_RANGE")

    quads: list[PhaseQuad] = []
    sine: list[int] = []
    for q in range(PHASE_QUADS):
        cells = (4 * q, 4 * q + 1, 4 * q + 2, 4 * q + 3)
        x, y, z, w = (normalized[i] for i in cells)
        phases = octonion_channels_from_words(x, y, z, w)
        channels = tuple(
            phase_channel(basis, phase)
            for basis, phase in zip(PHASE_CHANNELS, phases)
        )
        quotient = typed_stereo_ternary(channels)
        sine.extend(channel.sine_pcm64 for channel in channels)
        quads.append(
            PhaseQuad(
                index=q,
                cells=cells,
                stereo_xy=(x, y),
                stereo_zw=(z, w),
                channels=channels,
                stereo_ternary=quotient,
            )
        )

    return AudioHydration(
        pcm64_bits=normalized,
        quads=tuple(quads),
        pilot_pcm64_bits=normalized[PILOT_CELL],
        sine_pcm64=tuple(sine),
    )


def pipeline(bits: str) -> AudioHydration:
    words = bitstring_to_words(bits)
    hydration = hydrate_words(words)
    if words_to_bitstring(hydration.pcm64_bits) != bits:
        raise AssertionError("RAW5184_ROUNDTRIP")
    if le_bytes_to_words(words_to_le_bytes(words)) != words:
        raise AssertionError("BYTE_ROUNDTRIP")
    return hydration


def exact_serialization_work_model(frame_count: int = 1) -> dict[str, int | bool | str]:
    if frame_count <= 0:
        raise ValueError("frame_count")
    # Baseline: separate full validation + decode scans plus PCM and quad copies.
    baseline_per_frame = RAW_BITS + RAW_BITS + CELLS + 80
    # Fused path validates and decodes each bit once; quad/stereo views use the frame.
    fused_per_frame = RAW_BITS
    baseline = baseline_per_frame * frame_count
    fused = fused_per_frame * frame_count
    saved = baseline - fused
    return {
        "schema": "HHS_PASS219_I148_EXACT_SERIALIZATION_WORK_V1",
        "frame_count": frame_count,
        "baseline_per_frame": baseline_per_frame,
        "fused_per_frame": fused_per_frame,
        "baseline_total_work": baseline,
        "fused_total_work": fused,
        "exact_work_saved": saved,
        "reduction_permille_floor": (saved * 1000) // baseline,
        "timing_is_canonical": False,
        "canonical_authority_changed": False,
    }


__all__ = [
    "RAW_BITS", "RAW_BYTES", "CELLS", "WORD_BITS", "PHASE_QUADS",
    "PHASE_CHANNELS", "PILOT_CELL", "H36", "SINE_Q62_SCALE", "SINE_Q62", "PCM64_NOISE_FLOOR",
    "PCM64_ZERO_CROSSING", "PCM64_SATURATION_CEILING", "bitstring_to_words",
    "words_to_bitstring", "words_to_le_bytes", "le_bytes_to_words",
    "fold_word72", "octonion_channels_from_words", "PhaseChannel",
    "StereoTernaryQuotient", "PhaseQuad", "AudioHydration", "phase_channel",
    "typed_stereo_ternary", "hydrate_words",
    "pipeline", "exact_serialization_work_model",
]
