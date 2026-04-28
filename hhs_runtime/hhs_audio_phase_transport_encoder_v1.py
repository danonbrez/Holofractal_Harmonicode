"""
HHS Audio Phase Transport Encoder v1
====================================

Encodes HHS symbolic phase items into deterministic PCM WAV stems.

Design rules
------------
- No floating-point authority inside symbolic state.
- Audio synthesis uses boundary floats only to render PCM samples.
- Every rendered file is tied to a Hash72 manifest.
- 72 phase bins map to phase offsets across one cycle.
- x/y/z/w map to bipolar / quadrature wave carriers.
- xy/yx/zw/wz map to closure/inversion carrier pairs.

This module does not depend on external audio libraries.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
import json
import math
import wave

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest

SAMPLE_RATE = 48_000
DEFAULT_BPM = 72
RING = 72
BASE_FREQ = Fraction(220, 1)
AMPLITUDE = 0.28

SYMBOL_PHASE_OFFSETS = {
    "x": Fraction(0, 1),
    "y": Fraction(1, 2),
    "z": Fraction(1, 4),
    "w": Fraction(-1, 4),
    "xy": Fraction(0, 1),
    "yx": Fraction(1, 2),
    "zw": Fraction(0, 1),
    "wz": Fraction(1, 2),
}

SYMBOL_GAIN = {
    "x": Fraction(1, 1),
    "y": Fraction(1, 1),
    "z": Fraction(3, 4),
    "w": Fraction(3, 4),
    "xy": Fraction(5, 4),
    "yx": Fraction(5, 4),
    "zw": Fraction(5, 4),
    "wz": Fraction(5, 4),
}


@dataclass(frozen=True)
class AudioPhaseItem:
    id: str
    text: str
    kind: str
    phase_index: int
    symbol: str
    frequency_hz: str
    start_sample: int
    duration_samples: int
    item_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AudioPhaseManifest:
    expression: str
    sample_rate: int
    bpm: int
    items: List[AudioPhaseItem]
    stems: Dict[str, str]
    manifest_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expression": self.expression,
            "sample_rate": self.sample_rate,
            "bpm": self.bpm,
            "items": [i.to_dict() for i in self.items],
            "stems": self.stems,
            "manifest_hash72": self.manifest_hash72,
        }


def _symbol_from_text(text: str) -> str:
    if text in SYMBOL_PHASE_OFFSETS:
        return text
    for symbol in ["xy", "yx", "zw", "wz", "x", "y", "z", "w"]:
        if symbol in text:
            return symbol
    return "x"


def phase_to_frequency(phase_index: int, base: Fraction = BASE_FREQ) -> Fraction:
    # Exact ratio approximation for 72-TET: 2^(p/72) approximated at boundary.
    # Stored as Fraction for manifest determinism.
    ratio = 2 ** ((phase_index % RING) / RING)
    return Fraction.from_float(float(base) * ratio).limit_denominator(1_000_000)


def _sine_sample(sample_index: int, sample_rate: int, freq: Fraction, phase_turns: Fraction, gain: Fraction) -> float:
    t = sample_index / sample_rate
    phase = 2.0 * math.pi * (float(freq) * t + float(phase_turns))
    return AMPLITUDE * float(gain) * math.sin(phase)


def _write_mono_wav(path: Path, samples: Iterable[float], sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for s in samples:
            clipped = max(-1.0, min(1.0, s))
            frames.extend(int(clipped * 32767).to_bytes(2, "little", signed=True))
        wf.writeframes(bytes(frames))


def encode_expression_to_wav_stems(
    expression: str,
    display_items: List[Dict[str, Any]],
    out_dir: str | Path,
    *,
    sample_rate: int = SAMPLE_RATE,
    bpm: int = DEFAULT_BPM,
    beats_per_item: Fraction = Fraction(1, 4),
) -> AudioPhaseManifest:
    out_path = Path(out_dir)
    seconds_per_beat = Fraction(60, bpm)
    item_duration = seconds_per_beat * beats_per_item
    duration_samples = int(item_duration * sample_rate)
    total_samples = max(1, duration_samples * max(1, len(display_items)))

    channels = {"x": [0.0] * total_samples, "y": [0.0] * total_samples, "z": [0.0] * total_samples, "w": [0.0] * total_samples, "closure": [0.0] * total_samples}
    items: List[AudioPhaseItem] = []

    for idx, raw in enumerate(display_items):
        text = str(raw.get("text", ""))
        kind = str(raw.get("kind", "TOKEN"))
        phase_index = int(raw.get("phaseIndex", raw.get("phase_index", 0))) % RING
        symbol = _symbol_from_text(text)
        freq = phase_to_frequency(phase_index)
        offset = SYMBOL_PHASE_OFFSETS.get(symbol, Fraction(0, 1)) + Fraction(phase_index, RING)
        gain = SYMBOL_GAIN.get(symbol, Fraction(1, 1))
        start = idx * duration_samples
        item_hash = hash72_digest(("hhs_audio_phase_item_v1", text, kind, phase_index, symbol, str(freq), start, duration_samples), width=24)
        items.append(AudioPhaseItem(str(raw.get("id", f"item_{idx}")), text, kind, phase_index, symbol, str(freq), start, duration_samples, item_hash))

        if symbol in {"x", "xy"}:
            stem = "x"
        elif symbol in {"y", "yx"}:
            stem = "y"
        elif symbol in {"z", "zw"}:
            stem = "z"
        elif symbol in {"w", "wz"}:
            stem = "w"
        else:
            stem = "closure"

        for local in range(duration_samples):
            global_i = start + local
            env = math.sin(math.pi * local / max(1, duration_samples - 1))
            val = _sine_sample(global_i, sample_rate, freq, offset, gain) * env
            channels[stem][global_i] += val
            if symbol in {"xy", "zw"}:
                channels["closure"][global_i] += abs(val) * 0.5
            if symbol in {"yx", "wz"}:
                channels["closure"][global_i] -= abs(val) * 0.5

    stems: Dict[str, str] = {}
    for name, samples in channels.items():
        wav_path = out_path / f"hhs_phase_transport_{name}.wav"
        _write_mono_wav(wav_path, samples, sample_rate)
        stems[name] = str(wav_path)

    manifest_hash = hash72_digest(("hhs_audio_phase_manifest_v1", expression, sample_rate, bpm, [i.to_dict() for i in items], stems), width=24)
    manifest = AudioPhaseManifest(expression, sample_rate, bpm, items, stems, manifest_hash)
    (out_path / "hhs_audio_phase_manifest.json").write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return manifest


def main() -> None:
    demo_items = [
        {"id": "0", "text": "xy", "kind": "ORDERED_PRODUCT", "phaseIndex": 0},
        {"id": "1", "text": "=", "kind": "OPERATOR", "phaseIndex": 12},
        {"id": "2", "text": "-1/yx", "kind": "ORDERED_PRODUCT", "phaseIndex": 36},
        {"id": "3", "text": "u^72", "kind": "INVARIANT", "phaseIndex": 0},
    ]
    manifest = encode_expression_to_wav_stems("xy=-1/yx;u^72=1", demo_items, "demo_reports/audio_phase_transport")
    print(json.dumps(manifest.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
