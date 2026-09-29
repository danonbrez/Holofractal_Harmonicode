"""ElevenLabs narration generation with bounded 88-second fit.

Secrets remain server-side. The client uses the current ElevenLabs
/v1/text-to-speech/{voice_id}/with-timestamps endpoint and returns provider
alignment unchanged so the storyboard timeline can use measured timing rather
than estimated reading speed.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Mapping, Optional

from hhs_backend.runtime.hhs_storyboard_voice_sync_v1 import (
    MASTER_SECONDS,
    alignment_duration,
    choose_alignment,
    estimate_required_text_reduction,
    plan_next_speed,
    production_manifest,
)

API_ROOT = "https://api.elevenlabs.io"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"
DEFAULT_SPEED = Decimal("1.000")
DEFAULT_MAX_ATTEMPTS = 3


@dataclass(frozen=True)
class VoiceoverResult:
    audio: bytes
    alignment: Mapping[str, Any]
    provider_response: Mapping[str, Any]
    manifest: Mapping[str, Any]
    output_format: str
    speed: Decimal


class ElevenLabsVoiceoverClient:
    def __init__(self, api_key: Optional[str] = None, *, timeout_seconds: int = 180) -> None:
        self.api_key = str(api_key or os.environ.get("ELEVENLABS_API_KEY") or "").strip()
        self.timeout_seconds = int(timeout_seconds)

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def _request(
        self,
        *,
        text: str,
        voice_id: str,
        model_id: str,
        speed: Decimal,
        output_format: str,
        stability: float,
        similarity_boost: float,
        style: float,
        use_speaker_boost: bool,
    ) -> Mapping[str, Any]:
        if not self.configured:
            raise RuntimeError("ELEVENLABS_API_KEY is not configured")
        voice = urllib.parse.quote(voice_id, safe="")
        fmt = urllib.parse.quote(output_format, safe="")
        url = f"{API_ROOT}/v1/text-to-speech/{voice}/with-timestamps?output_format={fmt}"
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": float(stability),
                "similarity_boost": float(similarity_boost),
                "style": float(style),
                "use_speaker_boost": bool(use_speaker_boost),
                "speed": float(speed),
            },
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "xi-api-key": self.api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"ElevenLabs TTS failed with HTTP {exc.code}: {detail[:1000]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"ElevenLabs TTS request failed: {exc.reason}") from exc
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("ElevenLabs TTS returned invalid JSON") from exc
        if not isinstance(decoded, Mapping):
            raise RuntimeError("ElevenLabs TTS response is not an object")
        return decoded

    def synthesize_fitted(
        self,
        *,
        text: str,
        voice_id: str,
        model_id: str = DEFAULT_MODEL_ID,
        initial_speed: Any = DEFAULT_SPEED,
        output_format: str = DEFAULT_OUTPUT_FORMAT,
        stability: float = 0.50,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        target_seconds: Any = MASTER_SECONDS,
        storyboard_frames: Optional[list[Mapping[str, Any]]] = None,
    ) -> VoiceoverResult:
        source = str(text or "")
        if not source.strip():
            raise ValueError("voiceover text is required")
        voice = str(voice_id or "").strip()
        if not voice:
            raise ValueError("ElevenLabs voice_id is required")
        attempts = max(1, min(5, int(max_attempts)))
        speed = Decimal(str(initial_speed))
        target = Decimal(str(target_seconds))
        history: list[Dict[str, Any]] = []
        final_response: Optional[Mapping[str, Any]] = None
        final_alignment: Optional[Mapping[str, Any]] = None
        final_audio: Optional[bytes] = None

        for attempt_index in range(attempts):
            response = self._request(
                text=source,
                voice_id=voice,
                model_id=model_id,
                speed=speed,
                output_format=output_format,
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=use_speaker_boost,
            )
            alignment = choose_alignment(response, source)
            duration = alignment_duration(alignment)
            decision = plan_next_speed(speed, duration, target_seconds=target)
            history.append({"attempt": attempt_index + 1, **decision.to_dict()})
            audio_base64 = response.get("audio_base64")
            if not isinstance(audio_base64, str) or not audio_base64:
                raise RuntimeError("ElevenLabs response is missing audio_base64")
            try:
                audio = base64.b64decode(audio_base64, validate=True)
            except ValueError as exc:
                raise RuntimeError("ElevenLabs audio_base64 is invalid") from exc
            if not audio:
                raise RuntimeError("ElevenLabs returned empty audio")

            final_response = response
            final_alignment = alignment
            final_audio = audio

            if decision.status == "FIT":
                break
            if decision.status == "REGENERATE" and attempt_index + 1 < attempts:
                speed = decision.next_speed
                continue
            if duration <= target:
                break

            reduction = estimate_required_text_reduction(source, duration, target)
            raise ValueError(
                "voiceover remains longer than the 88-second master at the supported speed boundary; "
                f"revise approximately {reduction['characters']} characters and regenerate"
            )

        if final_response is None or final_alignment is None or final_audio is None:
            raise RuntimeError("voiceover generation produced no result")

        duration = alignment_duration(final_alignment)
        if duration > target + Decimal("0.350"):
            reduction = estimate_required_text_reduction(source, duration, target)
            raise ValueError(
                "voiceover exceeds the master after bounded fitting; "
                f"revise approximately {reduction['characters']} characters"
            )

        manifest = production_manifest(
            text=source,
            alignment=final_alignment,
            voice_id=voice,
            model_id=model_id,
            speed=speed,
            storyboard_frames=storyboard_frames,
            master_seconds=target,
            fit_attempts=history,
        )
        manifest = dict(manifest)
        manifest["output_format"] = output_format
        manifest["voice_settings"] = {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost,
        }
        return VoiceoverResult(
            audio=final_audio,
            alignment=final_alignment,
            provider_response=final_response,
            manifest=manifest,
            output_format=output_format,
            speed=speed,
        )


__all__ = [
    "API_ROOT",
    "DEFAULT_MAX_ATTEMPTS",
    "DEFAULT_MODEL_ID",
    "DEFAULT_OUTPUT_FORMAT",
    "DEFAULT_SPEED",
    "ElevenLabsVoiceoverClient",
    "VoiceoverResult",
]
