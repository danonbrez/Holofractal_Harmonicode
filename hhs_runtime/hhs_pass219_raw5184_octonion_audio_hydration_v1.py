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
MONITOR_SCALE = 1 << 56
TRIT_SCALE = 1 << 48
MASK64 = (1 << 64) - 1


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
    trit: int
    signed_phase: int
    monitor_pcm64: int


@dataclass(frozen=True)
class PhaseQuad:
    index: int
    cells: tuple[int, int, int, int]
    stereo_xy: tuple[int, int]
    stereo_zw: tuple[int, int]
    channels: tuple[PhaseChannel, ...]


@dataclass(frozen=True)
class AudioHydration:
    pcm64_bits: tuple[int, ...]
    quads: tuple[PhaseQuad, ...]
    pilot_pcm64_bits: int
    monitor_pcm64: tuple[int, ...]
    canonical_mutation_authority: bool = False
    canonical_hash72_authority: bool = False
    canonical_hash216_authority: bool = False
    canonical_persistence_authority: bool = False
    floating_point_authority: bool = False


def phase_channel(basis: str, phase: int) -> PhaseChannel:
    if basis not in PHASE_CHANNELS or not 0 <= phase < 72:
        raise ValueError("PHASE_RANGE")
    resonance = phase % H36
    half_turn = phase // H36
    trit = (phase % 3) - 1
    signed_phase = resonance - H36 if half_turn else resonance
    monitor = signed_phase * MONITOR_SCALE + trit * TRIT_SCALE
    assert resonance + H36 * half_turn == phase
    assert trit in (-1, 0, 1)
    return PhaseChannel(
        basis=basis,
        phase72=phase,
        resonance36=resonance,
        half_turn=half_turn,
        trit=trit,
        signed_phase=signed_phase,
        monitor_pcm64=monitor,
    )


def hydrate_words(words: Sequence[int]) -> AudioHydration:
    if len(words) != CELLS:
        raise ValueError("VM81_CELL_COUNT")
    normalized = tuple(int(word) for word in words)
    if any(word < 0 or word > MASK64 for word in normalized):
        raise ValueError("VM81_WORD_RANGE")

    quads: list[PhaseQuad] = []
    monitor: list[int] = []
    for q in range(PHASE_QUADS):
        cells = (4 * q, 4 * q + 1, 4 * q + 2, 4 * q + 3)
        x, y, z, w = (normalized[i] for i in cells)
        phases = octonion_channels_from_words(x, y, z, w)
        channels = tuple(
            phase_channel(basis, phase)
            for basis, phase in zip(PHASE_CHANNELS, phases)
        )
        monitor.extend(channel.monitor_pcm64 for channel in channels)
        quads.append(
            PhaseQuad(
                index=q,
                cells=cells,
                stereo_xy=(x, y),
                stereo_zw=(z, w),
                channels=channels,
            )
        )

    return AudioHydration(
        pcm64_bits=normalized,
        quads=tuple(quads),
        pilot_pcm64_bits=normalized[PILOT_CELL],
        monitor_pcm64=tuple(monitor),
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
    "PHASE_CHANNELS", "PILOT_CELL", "H36", "bitstring_to_words",
    "words_to_bitstring", "words_to_le_bytes", "le_bytes_to_words",
    "fold_word72", "octonion_channels_from_words", "PhaseChannel",
    "PhaseQuad", "AudioHydration", "phase_channel", "hydrate_words",
    "pipeline", "exact_serialization_work_model",
]
