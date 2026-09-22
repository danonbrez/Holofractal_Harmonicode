#!/usr/bin/env python3
"""Execute restartable Pass 220 unified corpus and model-weight hydration."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import canonical_bytes, hash216
from hhs_runtime.hhs_pass219_approved_projector_execution_v1 import SentenceTransformersRuntime
from hhs_runtime.hhs_pass220_lane5_model_weight_hydration_v1 import UnifiedModelWeightHydrator
from hhs_runtime.hhs_pass220_lane5_unified_corpus_v1 import (
    Lane5UnifiedCorpus,
    PopplerPDFExtractor,
    UnifiedCorpusError,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_MANIFEST = ROOT / "data/pass220/lane5_unified_corpus/source_manifest_v1.json"
DEFAULT_WEIGHT_MANIFEST = ROOT / "data/pass220/lane5_unified_corpus/model_weight_manifest_v1.json"


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_bytes(canonical_bytes(value) + b"\n")
    os.replace(temp, path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Hydrate the unified Pass 220 document/model knowledge graph"
    )
    parser.add_argument(
        "--source-root",
        required=True,
        help="directory containing the ten source PDFs under their manifest filenames",
    )
    parser.add_argument(
        "--state-dir",
        default=".hhs/pass220/lane5_unified_corpus",
        help="durable restart/checkpoint/vector graph directory",
    )
    parser.add_argument("--source-manifest", default=str(DEFAULT_SOURCE_MANIFEST))
    parser.add_argument("--weight-manifest", default=str(DEFAULT_WEIGHT_MANIFEST))
    parser.add_argument("--native-model-path", default=None)
    parser.add_argument("--hf-cache-dir", default=None)
    parser.add_argument("--dpi", type=int, default=96)
    parser.add_argument("--no-render-images", action="store_true")
    parser.add_argument("--no-language-projector", action="store_true")
    parser.add_argument("--skip-weights", action="store_true")
    parser.add_argument("--no-hf-download", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        projector = None if args.no_language_projector else SentenceTransformersRuntime()
        corpus = Lane5UnifiedCorpus(
            Path(args.state_dir),
            extractor=PopplerPDFExtractor(
                render_images=not args.no_render_images,
                dpi=args.dpi,
            ),
            external_projector_runtime=projector,
        )
        corpus_receipt = corpus.run_manifest(
            Path(args.source_manifest),
            Path(args.source_root),
        )

        weight_receipt = None
        if not args.skip_weights:
            weights = UnifiedModelWeightHydrator(corpus)
            weight_receipt = weights.run_manifest(
                Path(args.weight_manifest),
                corpus_root=corpus_receipt["corpus_root_node"],
                hf_cache_dir=Path(args.hf_cache_dir) if args.hf_cache_dir else None,
                native_model_path=Path(args.native_model_path) if args.native_model_path else None,
                download_hf=not args.no_hf_download,
            )

        closure = {
            "schema": "HHS_PASS220_LANE5_UNIFIED_CORPUS_MODEL_CLOSURE_V1",
            "corpus_receipt_hash216": corpus_receipt["receipt_hash216"],
            "weight_receipt_hash216": (
                weight_receipt["receipt_hash216"] if weight_receipt is not None else None
            ),
            "graph_root_hash216": corpus.graph.root_hash216(),
            "graph_nodes": len(corpus.graph.nodes),
            "graph_edges": len(corpus.graph.edges),
            "completed_units": len(corpus.graph.completed),
            "pass165_status": corpus.service.status(),
            "language_projector_enabled": projector is not None,
            "weights_included": weight_receipt is not None,
            "one_vector_store_knowledge_graph": True,
            "model_weights_candidate_only": True,
            "external_model_vectors_candidate_only": True,
            "canonical_authority_widened": False,
        }
        closure["receipt_hash216"] = hash216(
            "pass220-unified-corpus-model-closure",
            canonical_bytes(closure),
        )
        _write_json(Path(args.state_dir) / "unified.closure.receipt.json", closure)
        print(json.dumps(closure, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        error = {
            "schema": "HHS_PASS220_LANE5_UNIFIED_CORPUS_ERROR_V1",
            "classification": str(exc) or type(exc).__name__,
            "fail_closed": True,
        }
        print(json.dumps(error, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
