from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_lane5_model_weight_hydration_v1 import (
    UnifiedModelWeightHydrator,
)
from hhs_runtime.hhs_pass220_lane5_unified_corpus_v1 import (
    ExtractedPage,
    Lane5UnifiedCorpus,
    SourceManifestEntry,
    UnifiedCorpusError,
    build_page_packet,
)


class FakeExtractor:
    def __init__(self, pages, *, fail_after=None):
        self.pages = list(pages)
        self.fail_after = fail_after
        self.start_pages = []
        self.page_count_calls = 0

    def page_count(self, path: Path) -> int:
        self.page_count_calls += 1
        return len(self.pages)

    def iter_pages(self, path: Path, *, start_page: int = 1):
        self.start_pages.append(start_page)
        for page in self.pages[start_page - 1 :]:
            yield page
            if self.fail_after == page.page_number:
                raise RuntimeError("SIMULATED_PAGE_INTERRUPT")


def _jpeg(seed: int) -> bytes:
    return b"\xff\xd8\xff\xe0" + bytes([seed]) * 64


def _fixture(tmp_path: Path):
    raw = b"%PDF-1.4\npass220 deterministic source bytes\n%%EOF\n"
    source = tmp_path / "fixture.pdf"
    source.write_bytes(raw)
    entry = {
        "source_id": "fixture",
        "filename": "fixture.pdf",
        "sha256": sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "pages": 2,
    }
    manifest = {
        "schema": "HHS_PASS220_LANE5_UNIFIED_CORPUS_SOURCE_MANIFEST_V1",
        "version": "test",
        "sources": [entry],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    pages = [
        ExtractedPage(
            1,
            "P^2 = pq + 1\nNarrative line carries semantic meaning across the graph.\n",
            _jpeg(1),
        ),
        ExtractedPage(
            2,
            "def hydrate(x):\n    return x\n{\"mode\":\"structured\"}\n",
            _jpeg(2),
        ),
    ]
    return source, manifest_path, pages, SourceManifestEntry.from_mapping(entry)


def test_parallel_perspective_packet_preserves_one_source_identity(tmp_path: Path) -> None:
    _, _, pages, entry = _fixture(tmp_path)
    packet = build_page_packet(entry, pages[0])
    assert packet["source_sha256"] == entry.sha256
    assert packet["all_perspectives_share_one_source_identity"] is True
    assert "P^2 = pq + 1" in packet["perspectives"]["FORMAL_ALGEBRA"]["text"]
    assert "Narrative line" in packet["perspectives"]["NARRATIVE_TEXT"]["text"]
    assert packet["perspectives"]["VISUAL_PAGE"]["present"] is True


def test_document_hydrates_binary_page_packet_and_visual_into_one_graph(tmp_path: Path) -> None:
    _, manifest_path, pages, _ = _fixture(tmp_path)
    state = tmp_path / "state"
    extractor = FakeExtractor(pages)
    corpus = Lane5UnifiedCorpus(state, extractor=extractor)
    receipt = corpus.run_manifest(manifest_path, tmp_path)

    assert receipt["source_count"] == 1
    assert receipt["declared_page_count"] == 2
    assert receipt["one_vector_store_knowledge_graph"] is True
    assert receipt["canonical_authority_widened"] is False
    assert receipt["pass165_status"]["ingestion_epoch"] == 5
    assert len(corpus.graph.nodes) >= 9
    assert extractor.start_pages == [1]

    recovered_extractor = FakeExtractor(pages)
    recovered = Lane5UnifiedCorpus(state, extractor=recovered_extractor)
    second = recovered.run_manifest(manifest_path, tmp_path)
    assert second["graph_root_hash216"] == receipt["graph_root_hash216"]
    assert recovered_extractor.page_count_calls == 0
    assert recovered_extractor.start_pages == []
    assert second["pass165_status"]["ingestion_epoch"] == 5


def test_restart_continues_from_first_incomplete_page(tmp_path: Path) -> None:
    _, manifest_path, pages, _ = _fixture(tmp_path)
    state = tmp_path / "state"
    interrupted = Lane5UnifiedCorpus(
        state,
        extractor=FakeExtractor(pages, fail_after=1),
    )
    with pytest.raises(RuntimeError, match="SIMULATED_PAGE_INTERRUPT"):
        interrupted.run_manifest(manifest_path, tmp_path)

    resume_extractor = FakeExtractor(pages)
    resumed = Lane5UnifiedCorpus(state, extractor=resume_extractor)
    receipt = resumed.run_manifest(manifest_path, tmp_path)
    assert resume_extractor.start_pages == [2]
    assert receipt["pass165_status"]["ingestion_epoch"] == 5


def test_source_hash_mismatch_fails_before_hydration(tmp_path: Path) -> None:
    source, manifest_path, pages, _ = _fixture(tmp_path)
    source.write_bytes(source.read_bytes() + b"tamper")
    corpus = Lane5UnifiedCorpus(tmp_path / "state", extractor=FakeExtractor(pages))
    with pytest.raises(UnifiedCorpusError, match="SOURCE_SIZE_MISMATCH|SOURCE_SHA256_MISMATCH"):
        corpus.run_manifest(manifest_path, tmp_path)
    assert corpus.service.status()["ingestion_epoch"] == 0


def test_model_weight_bytes_are_hydrated_candidate_only(tmp_path: Path) -> None:
    _, manifest_path, pages, _ = _fixture(tmp_path)
    corpus = Lane5UnifiedCorpus(tmp_path / "state", extractor=FakeExtractor(pages))
    corpus_receipt = corpus.run_manifest(manifest_path, tmp_path)
    before = corpus.service.status()["ingestion_epoch"]

    weight = tmp_path / "model.bin"
    weight.write_bytes(bytes(range(256)) * 8)
    node = UnifiedModelWeightHydrator(corpus).process_file(
        weight,
        model_id="fixture-model",
        source_kind="NATIVE_OPEN_MODEL",
        corpus_root=corpus_receipt["corpus_root_node"],
        provenance={"provider": "TEST"},
        expected_sha256=sha256(weight.read_bytes()).hexdigest(),
        expected_size_bytes=weight.stat().st_size,
    )
    after = corpus.service.status()["ingestion_epoch"]

    assert node in corpus.graph.nodes
    assert before == after
    assert any(
        json.loads(line)["record"].get("body", {}).get("extra", {}).get("model_id")
        == "fixture-model"
        for line in (tmp_path / "state/unified_graph/nodes.jsonl").read_text().splitlines()
    )


def test_safetensors_tensor_metadata_is_linked_without_loading_values(tmp_path: Path) -> None:
    _, manifest_path, pages, _ = _fixture(tmp_path)
    corpus = Lane5UnifiedCorpus(tmp_path / "state", extractor=FakeExtractor(pages))
    corpus_receipt = corpus.run_manifest(manifest_path, tmp_path)

    header = json.dumps(
        {
            "layer.weight": {
                "dtype": "F32",
                "shape": [2, 2],
                "data_offsets": [0, 16],
            },
            "__metadata__": {"format": "pt"},
        },
        separators=(",", ":"),
    ).encode()
    weight = tmp_path / "model.safetensors"
    weight.write_bytes(len(header).to_bytes(8, "little") + header + b"\x00" * 16)

    UnifiedModelWeightHydrator(corpus).process_file(
        weight,
        model_id="safe-model",
        source_kind="HUGGING_FACE_MODEL",
        corpus_root=corpus_receipt["corpus_root_node"],
        provenance={"revision": "0" * 40},
    )

    node_records = [
        json.loads(line)["record"]
        for line in (tmp_path / "state/unified_graph/nodes.jsonl").read_text().splitlines()
    ]
    tensors = [row for row in node_records if row.get("kind") == "MODEL_TENSOR_METADATA"]
    assert tensors
    assert tensors[0]["body"]["name"] == "layer.weight"
    assert tensors[0]["body"]["shape"] == [2, 2]
    assert tensors[0]["body"]["values_not_scalarized_by_metadata_parser"] is True
