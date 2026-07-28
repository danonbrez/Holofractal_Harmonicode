from __future__ import annotations

import asyncio
import json
from pathlib import Path

from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import LiteRTLMConfig
from hhs_backend.runtime.hhs_vm81_creative_novel_v1 import (
    CreativeOptimizedTransport,
    NovelRequest,
    VM81CreativeNovelGenerator,
)


class FakeCreativeService:
    def __init__(self):
        self.config = LiteRTLMConfig(model_id="gemma4-test")
        self.request_model_id = "gemma4-test,cpu,4096"
        self.prompts = []
        self._thread = 0

    def create_thread(self, **_):
        self._thread += 1
        return {"thread_id": f"thread-{self._thread}"}

    async def send_message(self, thread_id, *, content, tools=None, response_format=None):
        self.prompts.append({
            "thread_id": thread_id,
            "content": content,
            "tools": tools,
            "response_format": response_format,
        })
        if "Return one JSON object" in content:
            outline = {
                "title": "The Ninth Archive",
                "logline": "An archivist must decide whether a future receipt is a warning or a command.",
                "themes": ["memory", "choice"],
                "setting": "The receipt-bound city of Orison",
                "style": "precise speculative fiction",
                "characters": [
                    {"name": "Mara Venn", "role": "maintenance archivist"},
                    {"name": "Ilan Roe", "role": "receipt auditor"},
                ],
                "continuity_rules": ["The ninth archive cannot alter a sealed past."],
                "chapters": [
                    {
                        "number": number,
                        "title": f"Receipt {number}",
                        "objective": f"advance objective {number}",
                        "conflict": f"face conflict {number}",
                        "turn": f"discover turn {number}",
                        "continuity_in": f"state {number - 1}",
                        "continuity_out": f"state {number}",
                        "image_motif": "silver paper",
                    }
                    for number in range(1, 4)
                ],
            }
            response = json.dumps(outline)
        else:
            marker = "CURRENT_CHAPTER_JSON:\n"
            chapter_json = content.split(marker, 1)[1].split("\n\nCONTRACT:", 1)[0]
            chapter = json.loads(chapter_json)
            number = chapter["number"]
            response = (
                f"## Chapter {number}: {chapter['title']}\n\n"
                f"Mara entered scene {number}. The conflict developed and closed "
                f"with continuity state {number}."
            )
        return {"ok": True, "assistant_message": {"content": response}}


def _fake_export(path: Path, text: str, *, source: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return {"schema": "TEST_EXPORT_V1", "path": str(path), "source": source, "ok": True}


def test_creative_transport_encodes_engine_token_bound():
    transport = CreativeOptimizedTransport(
        LiteRTLMConfig(model_id="gemma4-test"),
        backend="cpu",
        max_engine_tokens=4096,
    )
    assert transport.request_model_id == "gemma4-test,cpu,4096"
    assert transport.max_engine_tokens == 4096


def test_vm81_novel_generator_uses_compacted_parallel_single_turn_threads(tmp_path):
    service = FakeCreativeService()
    generator = VM81CreativeNovelGenerator(
        service=service,
        exporter=_fake_export,
        output_root=tmp_path,
    )
    result = asyncio.run(generator.generate({
        "title": "The Ninth Archive",
        "premise": "A future archive appears.",
        "chapter_count": 3,
        "target_words": 3000,
        "filename": "THE_NINTH_ARCHIVE.md",
        "max_concurrency": 2,
    }))

    artifact = tmp_path / "THE_NINTH_ARCHIVE.md"
    assert result["ok"] is True
    assert result["artifact_path"] == str(artifact.resolve())
    assert result["artifact_persistence_admitted"] is True
    assert result["direct_model_filesystem_mutation_allowed"] is False
    assert result["performance"]["full_prior_chapter_replay"] is False
    assert artifact.exists()
    manuscript = artifact.read_text(encoding="utf-8")
    assert manuscript.count("## Chapter") == 3
    assert result["novel_root_hash72"]
    assert result["result_root_hash72"]

    chapter_prompts = [
        item["content"]
        for item in service.prompts
        if "CURRENT_CHAPTER_JSON:" in item["content"]
    ]
    assert len(chapter_prompts) == 3
    assert all("Mara entered scene" not in prompt for prompt in chapter_prompts)
    assert len({item["thread_id"] for item in service.prompts}) == 4
    assert all(item["tools"] is None for item in service.prompts)


def test_api_payload_cannot_override_creative_output_root():
    try:
        NovelRequest.from_mapping(
            {"output_root": "/tmp/outside"},
            output_root="creative_writing/novels",
        )
    except ValueError as exc:
        assert "runtime-configured" in str(exc)
    else:
        raise AssertionError("caller-controlled output_root was not rejected")
