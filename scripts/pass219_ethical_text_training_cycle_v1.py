#!/usr/bin/env python3
"""Run the bounded Pass 219 ethical text training-cycle compiler.

The command requires the repository WordNet CSV set and a ready Pass 166
Word2Vec installation.  It emits a candidate-only JSON artifact; it does not
perform VM81 commit, model fine-tuning, or irreversible pruning.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hhs_runtime.hhs_pass219_ethical_text_training_v1 import (  # noqa: E402
    EthicalTextTrainingError,
    compile_repository_training_cycle,
)
from hhs_runtime.pass166.service import Word2VecService  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository-root",
        default=str(REPOSITORY_ROOT),
        help="repository root containing hhs_runtime WordNet assets",
    )
    parser.add_argument(
        "--dataset",
        default="data/pass219/ethical_alignment_prompt_response_v1.jsonl",
        help="prompt/response JSONL path, relative to repository root unless absolute",
    )
    parser.add_argument(
        "--word2vec-storage-root",
        default=None,
        help="optional Pass 166 storage root; defaults to HHS_PASS166_STORAGE_DIR/.hhs/pass166",
    )
    parser.add_argument(
        "--model-id",
        default=None,
        help="explicit installed Pass 166 model id; otherwise the active model is used",
    )
    parser.add_argument(
        "--output",
        default=".hhs/pass219/ethical_text_training/cycle_v1.json",
        help="candidate-cycle output path",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repository_root = Path(args.repository_root).resolve()
    dataset_path = Path(args.dataset)
    if not dataset_path.is_absolute():
        dataset_path = repository_root / dataset_path
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = repository_root / output_path

    service = Word2VecService(root_path=args.word2vec_storage_root)
    status = service.status()
    model_id = args.model_id or status.get("active_model_id")
    if not model_id:
        raise EthicalTextTrainingError("P219_ETT_ACTIVE_WORD2VEC_MODEL_REQUIRED")
    service.inspect(str(model_id))

    cycle = compile_repository_training_cycle(
        repository_root,
        dataset_path,
        word2vec_service=service,
        model_id=str(model_id),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(cycle, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output_path)

    summary = {
        "classification": (
            "P219_ETHICAL_TEXT_TRAINING_CYCLE_READY_FOR_LANE5_REVIEW"
            if cycle["admitted_training_candidates"] and not cycle["rejected_training_candidates"]
            else "P219_ETHICAL_TEXT_TRAINING_CYCLE_HOLD"
        ),
        "dataset_hash72": cycle["dataset_hash72"],
        "final_hash216_root": cycle["final_hash216_root"],
        "record_count": cycle["record_count"],
        "admitted": len(cycle["admitted_training_candidates"]),
        "held": len(cycle["held_training_candidates"]),
        "rejected": len(cycle["rejected_training_candidates"]),
        "word2vec_model_id": model_id,
        "output": str(output_path),
        "candidate_only": True,
        "vm81_commit_invoked": False,
    }
    print(json.dumps(summary, sort_keys=True, indent=2))
    return 0 if not cycle["rejected_training_candidates"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
