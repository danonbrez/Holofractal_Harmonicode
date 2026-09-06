"""Legacy plus-v1 compatibility adapter over the canonical Pass170 gateway.

Pass219 I175 migrates the audio-language HTTP route into canonical Pass170
composition.  This module preserves its historical Python names but no longer
registers an independent route or self-launches a legacy application object.
"""
from __future__ import annotations

from hhs_backend.pass170_audio_language_routes import (
    AudioLanguageRunRequest,
    execute_audio_language_feedback_request as api_audio_language_run,
)
from hhs_backend.public_api_server import app
from hhs_runtime.hhs_audio_language_feedback_orchestrator_v1 import (
    run_audio_language_feedback_cycle,
)


def main() -> None:
    import uvicorn

    uvicorn.run(
        "hhs_backend.public_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()


__all__ = [
    "AudioLanguageRunRequest",
    "api_audio_language_run",
    "app",
    "main",
    "run_audio_language_feedback_cycle",
]
