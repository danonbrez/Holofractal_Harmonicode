"""Receipt-governed novel generation behind the VM81 runtime API.

External callers use only ``POST /api/runtime/creative/novel``. Provider
execution is mediated by ``HHSAssistantService`` and persistence by the HHS
persistence guard; the model receives neither VM81 nor filesystem authority.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from collections import OrderedDict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence

from hhs_backend.runtime.hhs_litert_lm_accelerated_transport_v1 import (
    LiteRTLMAcceleratedTransport,
    backend_from_env,
)
from hhs_backend.runtime.hhs_litert_lm_assistant_v1 import (
    HHSAssistantService,
    LiteRTLMConfig,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_runtime.hhs_persistence_guard_v1 import export_text_artifact

VERSION = "HHS_VM81_CREATIVE_NOVEL_RUNTIME_V1"
AUTHORITY = "HHS_VM81_CREATIVE_WRITING_AUTHORITY_V1"
REQUEST_SCHEMA = "HHS_VM81_CREATIVE_NOVEL_REQUEST_V1"
RESULT_SCHEMA = "HHS_VM81_CREATIVE_NOVEL_RESULT_V1"
OUTLINE_SCHEMA = "HHS_VM81_CREATIVE_NOVEL_OUTLINE_V1"
CACHE_SCHEMA = "HHS_VM81_CREATIVE_PROMPT_CACHE_KEY_V1"
DEFAULT_PREMISE = (
    "In a city where every public action must be sealed into an immutable "
    "receipt, a maintenance archivist discovers a ninth archive containing "
    "events that have not happened yet."
)
CREATIVE_SYSTEM_INSTRUCTION = """You are the creative-writing provider inside
HHS VM81. Produce original long-form fiction with concrete scenes, causal
continuity, distinct voices, restrained exposition, and a closed dramatic arc.
Preserve the supplied story bible and chapter contract. Return only requested
story material. Never claim runtime mutation, admission, receipt, or file I/O."""


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", str(text), flags=re.UNICODE))


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").upper() or "NOVEL"


def _safe_output_path(root: str | Path, filename: str) -> Path:
    base = Path(root).expanduser().resolve()
    candidate = (base / filename).resolve()
    if candidate != base and base not in candidate.parents:
        raise ValueError("creative-writing output escaped the configured root")
    return candidate


@dataclass(frozen=True)
class NovelRequest:
    title: str = "The Ninth Archive"
    premise: str = DEFAULT_PREMISE
    chapter_count: int = 9
    target_words: int = 9000
    filename: str = "THE_NINTH_ARCHIVE.md"
    max_concurrency: int = 2
    persist: bool = True
    output_root: str = "creative_writing/novels"
    project_id: str = "project:creative-writing"
    request_class: str = "canonical_full_witness_chain"

    @classmethod
    def from_mapping(
        cls,
        payload: Optional[Mapping[str, Any]] = None,
        *,
        output_root: str | Path = "creative_writing/novels",
    ) -> "NovelRequest":
        data = dict(payload or {})
        if "output_root" in data:
            raise ValueError("output_root is runtime-configured and cannot be set by API callers")
        title = str(data.get("title") or cls.title).strip()
        premise = str(data.get("premise") or cls.premise).strip()
        chapters = int(data.get("chapter_count", cls.chapter_count))
        words = int(data.get("target_words", cls.target_words))
        concurrency = int(data.get("max_concurrency", cls.max_concurrency))
        filename = str(data.get("filename") or f"{_slug(title)}.md").strip()
        if not title or len(title) > 160:
            raise ValueError("title must contain 1..160 characters")
        if not premise or len(premise) > 8000:
            raise ValueError("premise must contain 1..8000 characters")
        if not 3 <= chapters <= 24:
            raise ValueError("chapter_count must be between 3 and 24")
        if not 3000 <= words <= 120000:
            raise ValueError("target_words must be between 3000 and 120000")
        if not 1 <= concurrency <= 4:
            raise ValueError("max_concurrency must be between 1 and 4")
        if not filename.lower().endswith(".md"):
            filename += ".md"
        if Path(filename).name != filename:
            raise ValueError("filename must not contain directory components")
        return cls(
            title=title,
            premise=premise,
            chapter_count=chapters,
            target_words=words,
            filename=filename,
            max_concurrency=concurrency,
            persist=bool(data.get("persist", True)),
            output_root=str(output_root),
            project_id=str(data.get("project_id") or cls.project_id),
            request_class=str(data.get("request_class") or cls.request_class),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"schema": REQUEST_SCHEMA, **self.__dict__, "authority": AUTHORITY}


class CreativeOptimizedTransport(LiteRTLMAcceleratedTransport):
    """Encode the bounded LiteRT-LM engine context in the request model ID."""

    def __init__(
        self,
        config: LiteRTLMConfig,
        *,
        backend: Optional[str] = None,
        max_engine_tokens: Optional[int] = None,
    ):
        super().__init__(config, backend=backend)
        bound = int(max_engine_tokens or os.getenv(
            "HHS_LITERT_LM_CREATIVE_MAX_ENGINE_TOKENS", "8192"
        ))
        if not 1024 <= bound <= 131072:
            raise ValueError("creative max engine tokens must be between 1024 and 131072")
        self.max_engine_tokens = bound
        self.request_model_id = f"{config.model_id},{self.backend},{bound}"


class _PromptCache:
    def __init__(self, max_entries: int = 64):
        self.max_entries = max(1, int(max_entries))
        self.entries: "OrderedDict[str, str]" = OrderedDict()
        self.hits = self.misses = 0

    def get(self, key: str) -> Optional[str]:
        value = self.entries.get(key)
        if value is None:
            self.misses += 1
            return None
        self.entries.move_to_end(key)
        self.hits += 1
        return value

    def put(self, key: str, value: str) -> None:
        self.entries[key] = value
        self.entries.move_to_end(key)
        while len(self.entries) > self.max_entries:
            self.entries.popitem(last=False)

    def status(self) -> Dict[str, int]:
        return {
            "entries": len(self.entries),
            "max_entries": self.max_entries,
            "hits": self.hits,
            "misses": self.misses,
        }


class VM81CreativeNovelGenerator:
    def __init__(
        self,
        service: Optional[Any] = None,
        *,
        exporter: Callable[..., Dict[str, Any]] = export_text_artifact,
        cache_entries: int = 64,
        output_root: Optional[str | Path] = None,
    ):
        if service is None:
            base = LiteRTLMConfig.from_env()
            config = replace(
                base,
                max_threads=max(base.max_threads, 32),
                max_messages_per_thread=4,
                max_output_tokens=int(os.getenv(
                    "HHS_LITERT_LM_CREATIVE_MAX_OUTPUT_TOKENS", "4096"
                )),
                temperature=float(os.getenv(
                    "HHS_LITERT_LM_CREATIVE_TEMPERATURE", "0.68"
                )),
                top_p=float(os.getenv("HHS_LITERT_LM_CREATIVE_TOP_P", "0.92")),
                top_k=int(os.getenv("HHS_LITERT_LM_CREATIVE_TOP_K", "40")),
                reasoning_effort=os.getenv(
                    "HHS_LITERT_LM_CREATIVE_REASONING_EFFORT", "low"
                ),
                system_instruction=CREATIVE_SYSTEM_INSTRUCTION,
            )
            transport = CreativeOptimizedTransport(config, backend=backend_from_env())
            service = HHSAssistantService(config=config, transport=transport)
        self.service = service
        self.exporter = exporter
        self.output_root = str(output_root or os.getenv(
            "HHS_CREATIVE_WRITING_ROOT", "creative_writing/novels"
        ))
        self.cache = _PromptCache(cache_entries)

    @property
    def request_model_id(self) -> str:
        transport = getattr(self.service, "transport", None)
        config = getattr(self.service, "config", None)
        return str(getattr(
            self.service,
            "request_model_id",
            getattr(transport, "request_model_id", getattr(config, "model_id", "unknown")),
        ))

    async def _completion(
        self,
        *,
        project_id: str,
        title: str,
        prompt: str,
        response_format: Optional[Mapping[str, Any]] = None,
    ) -> str:
        cache_key = hash72(CACHE_SCHEMA, {
            "version": VERSION,
            "request_model_id": self.request_model_id,
            "project_id": project_id,
            "prompt": prompt,
            "response_format": dict(response_format or {}),
        })
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        thread = self.service.create_thread(
            project_id=project_id,
            title=title,
            metadata={
                "surface": "api.runtime.creative.novel",
                "history_mode": "single_turn_compacted",
                "cache_key_hash72": cache_key,
            },
        )
        turn = await self.service.send_message(
            thread["thread_id"],
            content=prompt,
            tools=None,
            response_format=dict(response_format or {}) or None,
        )
        if not turn.get("ok"):
            raise RuntimeError(
                f"creative provider turn rejected: {turn.get('status')}: "
                f"{turn.get('error') or turn.get('reason') or 'unknown error'}"
            )
        text = str(turn.get("assistant_message", {}).get("content") or "").strip()
        if not text:
            raise RuntimeError("creative provider returned an empty completion")
        self.cache.put(cache_key, text)
        return text

    async def _outline(self, request: NovelRequest) -> Dict[str, Any]:
        prompt = f"""Create a complete story bible and chapter architecture for an
original novel.

TITLE: {request.title}
PREMISE: {request.premise}
CHAPTER COUNT: {request.chapter_count}
TARGET TOTAL WORDS: {request.target_words}

Return one JSON object with: schema, title, logline, themes, setting, style,
characters, continuity_rules, and chapters. Chapters must contain exactly
{request.chapter_count} objects with number, title, objective, conflict, turn,
continuity_in, continuity_out, and image_motif. Build a closed ending. JSON only."""
        raw = await self._completion(
            project_id=request.project_id,
            title=f"{request.title}: outline",
            prompt=prompt,
            response_format={"type": "json_object"},
        )
        try:
            outline = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("creative outline was not valid JSON") from exc
        chapters = list(outline.get("chapters") or [])
        if len(chapters) != request.chapter_count:
            raise RuntimeError("creative outline chapter count did not match the request")
        if [int(item.get("number") or 0) for item in chapters] != list(
            range(1, request.chapter_count + 1)
        ):
            raise RuntimeError("creative outline chapter numbering was not canonical")
        outline.update({
            "schema": OUTLINE_SCHEMA,
            "title": request.title,
            "premise": request.premise,
        })
        outline["outline_root_hash72"] = hash72(OUTLINE_SCHEMA, outline)
        return outline

    @staticmethod
    def _story_bible(outline: Mapping[str, Any]) -> str:
        keys = (
            "title", "logline", "themes", "setting", "style", "characters",
            "continuity_rules", "chapters",
        )
        return json.dumps(
            {key: outline.get(key) for key in keys},
            ensure_ascii=False,
            separators=(",", ":"),
        )

    async def _chapter(
        self,
        request: NovelRequest,
        outline: Mapping[str, Any],
        chapter: Mapping[str, Any],
        semaphore: asyncio.Semaphore,
    ) -> Dict[str, Any]:
        number = int(chapter["number"])
        target = max(700, request.target_words // request.chapter_count)
        prompt = f"""Write Chapter {number} from this original novel contract.

STORY_BIBLE_JSON:
{self._story_bible(outline)}

CURRENT_CHAPTER_JSON:
{json.dumps(dict(chapter), ensure_ascii=False, separators=(",", ":"))}

CONTRACT:
Write approximately {target} words. Start with `## Chapter {number}: <title>`.
Dramatize objective, conflict, and turn. Preserve continuity. Do not summarize
future chapters or include planning notes. End in continuity_out. Prose only."""
        async with semaphore:
            text = await self._completion(
                project_id=request.project_id,
                title=f"{request.title}: chapter {number}",
                prompt=prompt,
            )
        if not text.startswith("## Chapter"):
            text = f"## Chapter {number}: {chapter.get('title') or 'Untitled'}\n\n{text}"
        return {
            "number": number,
            "title": str(chapter.get("title") or f"Chapter {number}"),
            "text": text.strip(),
            "word_count": _word_count(text),
            "chapter_root_hash72": hash72(
                "HHS_VM81_CREATIVE_NOVEL_CHAPTER_V1",
                {"number": number, "text": text},
            ),
        }

    @staticmethod
    def _assemble(
        request: NovelRequest,
        outline: Mapping[str, Any],
        chapters: Sequence[Mapping[str, Any]],
    ) -> str:
        front = (
            f"# {request.title}\n\n*A VM81-governed creative-writing novel artifact.*\n\n"
            f"**Premise:** {request.premise}\n\n---\n\n"
        )
        body = "\n\n---\n\n".join(str(item["text"]).strip() for item in chapters)
        provenance = (
            "\n\n---\n\n## Runtime provenance\n\n"
            f"- Generator: `{VERSION}`\n"
            f"- Outline root Hash72: `{outline.get('outline_root_hash72', '')}`\n"
            f"- Model request identity: `{outline.get('request_model_id', '')}`\n"
            "- External generation surface: `/api/runtime/creative/novel`\n"
            "- Direct model-to-filesystem mutation: `false`\n"
            "- Persistence path: HHS persistence guard egress\n"
        )
        return front + body + provenance

    async def generate(self, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        request = NovelRequest.from_mapping(payload, output_root=self.output_root)
        started = time.perf_counter()
        outline = await self._outline(request)
        outline["request_model_id"] = self.request_model_id
        semaphore = asyncio.Semaphore(request.max_concurrency)
        chapters = sorted(
            await asyncio.gather(*(
                self._chapter(request, outline, chapter, semaphore)
                for chapter in outline["chapters"]
            )),
            key=lambda item: item["number"],
        )
        manuscript = self._assemble(request, outline, chapters)
        novel_root = hash72("HHS_VM81_CREATIVE_NOVEL_MANUSCRIPT_V1", {
            "request": request.to_dict(),
            "outline_root_hash72": outline["outline_root_hash72"],
            "chapter_roots": [item["chapter_root_hash72"] for item in chapters],
            "manuscript": manuscript,
        })
        persistence = None
        artifact_path = None
        if request.persist:
            path = _safe_output_path(request.output_root, request.filename)
            persistence = self.exporter(
                path,
                manuscript,
                source="api.runtime.creative.novel.export",
            )
            artifact_path = str(path)
        elapsed = max(time.perf_counter() - started, 1e-9)
        result = {
            "schema": RESULT_SCHEMA,
            "version": VERSION,
            "ok": True,
            "status": "ADMIT_VM81_CREATIVE_NOVEL_ARTIFACT",
            "request": request.to_dict(),
            "request_model_id": self.request_model_id,
            "outline": outline,
            "chapters": [{key: item[key] for key in (
                "number", "title", "word_count", "chapter_root_hash72"
            )} for item in chapters],
            "manuscript": manuscript if not request.persist else None,
            "artifact_path": artifact_path,
            "persistence": persistence,
            "word_count": _word_count(manuscript),
            "elapsed_ms": int(elapsed * 1000),
            "words_per_second": round(_word_count(manuscript) / elapsed, 3),
            "performance": {
                "parallel_chapter_generation": True,
                "max_concurrency": request.max_concurrency,
                "single_turn_compacted_threads": True,
                "full_prior_chapter_replay": False,
                "bounded_prompt_cache": self.cache.status(),
                "engine_token_bound_encoded_in_model_id": True,
                "assistant_tool_schema_injection": False,
            },
            "novel_root_hash72": novel_root,
            "provider_output_is_canonical_without_runtime_admission": False,
            "direct_model_filesystem_mutation_allowed": False,
            "runtime_mutation_admitted": False,
            "artifact_persistence_admitted": bool(persistence),
            "authority": AUTHORITY,
        }
        result["result_root_hash72"] = hash72(RESULT_SCHEMA, result)
        return result

    def status(self) -> Dict[str, Any]:
        return {
            "schema": "HHS_VM81_CREATIVE_NOVEL_STATUS_V1",
            "version": VERSION,
            "ok": True,
            "request_model_id": self.request_model_id,
            "output_root": self.output_root,
            "performance": {
                "single_turn_compacted_threads": True,
                "parallel_chapter_generation": True,
                "bounded_prompt_cache": self.cache.status(),
                "engine_token_bound_encoded_in_model_id": True,
                "assistant_tool_schema_injection": False,
            },
            "external_surface": "/api/runtime/creative/novel",
            "direct_litert_lm_client_surface_exposed": False,
            "authority": AUTHORITY,
        }


DEFAULT_VM81_CREATIVE_NOVEL_GENERATOR = VM81CreativeNovelGenerator()
