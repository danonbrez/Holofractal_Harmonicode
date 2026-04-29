from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel

from hhs_runtime_api_server_v1 import app
from hhs_runtime.hhs_audio_language_feedback_orchestrator_v1 import run_audio_language_feedback_cycle


class AudioLanguageRunRequest(BaseModel):
    expression: str
    items: List[Dict[str, Any]]
    audio_manifest: Dict[str, Any]
    audio_roundtrip_receipt: Dict[str, Any] | None = None


@app.post("/api/audio-language/run")
async def api_audio_language_run(req: AudioLanguageRunRequest) -> Dict[str, Any]:
    result = run_audio_language_feedback_cycle(
        expression=req.expression,
        display_items=req.items,
        audio_manifest=req.audio_manifest,
        audio_roundtrip_receipt=req.audio_roundtrip_receipt,
    )
    return result.to_dict()


def main() -> None:
    import uvicorn
    uvicorn.run("hhs_runtime_api_server_plus_v1:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
