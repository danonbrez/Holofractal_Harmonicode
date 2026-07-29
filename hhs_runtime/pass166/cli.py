"""Pass 166 shell control surface."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO

from .service import Word2VecError, Word2VecService

EXIT_BY_PREFIX = {
    "P166_MANIFEST": 2, "P166_UNSUPPORTED": 2, "P166_INVALID_EXPECTED": 2, "P166_TOP_K": 2, "P166_ANALOGY": 2,
    "P166_LICENSE": 3, "P166_UNREGISTERED": 3, "P166_NETWORK": 4, "P166_SOURCE_NOT": 4, "P166_REDIRECT": 4,
    "P166_BYTE": 5, "P166_DIGEST": 5, "P166_ARCHIVE": 5, "P166_DECOMPRESSION": 5, "P166_TRUNCATED": 5,
    "P166_MALFORMED_WORD2VEC": 6, "P166_MIXED_VECTOR": 6, "P166_INVALID_TOKEN": 6, "P166_DUPLICATE_TOKEN": 6,
    "P166_NONFINITE": 6, "P166_MODEL_GEOMETRY": 6, "P166_VOCABULARY": 6, "P166_NUMERIC": 7,
    "P166_NONDETERMINISTIC": 7, "P166_INDEX": 8, "P166_STALE_PASS165": 9, "P166_MODEL_NOT_INSTALLED": 9,
    "P166_RECEIPT": 10, "P166_REPLAY": 10, "P166_OFFLINE": 10, "P166_PACKAGE_SIZE": 11, "P166_REPAIR_REQUIRED": 12,
}


def _exit_for(classification: str) -> int:
    for prefix, code in EXIT_BY_PREFIX.items():
        if classification.startswith(prefix):
            return code
    return 2


def _normalize_argv(argv: Sequence[str]) -> list[str]:
    values = list(argv)
    global_options: list[str] = []
    command: list[str] = []
    index = 0
    while index < len(values):
        value = values[index]
        if value in ("--output", "--storage-root"):
            if index + 1 >= len(values):
                command.append(value)
                index += 1
                continue
            global_options.extend((value, values[index + 1]))
            index += 2
            continue
        command.append(value)
        index += 1
    if command[:5] == ["modality", "language", "model", "install", "word2vec"]:
        command = ["model", "word2vec", "install", *command[5:]]
    elif command[:3] == ["model", "install", "word2vec"]:
        command = ["model", "word2vec", "install", *command[3:]]
    return [*global_options, *command]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hhs")
    parser.add_argument("--storage-root", type=Path, default=None)
    parser.add_argument("--output", choices=("text", "json"), default="text")
    root = parser.add_subparsers(dest="root", required=True)
    model = root.add_parser("model")
    families = model.add_subparsers(dest="family", required=True)
    word2vec = families.add_parser("word2vec")
    actions = word2vec.add_subparsers(dest="action", required=True)
    actions.add_parser("list")
    inspect = actions.add_parser("inspect"); inspect.add_argument("model_id")
    register = actions.add_parser("register-manifest"); register.add_argument("manifest", type=Path)
    install = actions.add_parser("install")
    install.add_argument("model_id"); install.add_argument("--manifest", type=Path); install.add_argument("--license-accept", action="store_true")
    install.add_argument("--activate", action=argparse.BooleanOptionalAction, default=True)
    install.add_argument("--offline-ready", action=argparse.BooleanOptionalAction, default=True)
    install.add_argument("--replace-existing", action="store_true"); install.add_argument("--expected-pass165-frontier")
    for action in ("verify", "activate", "deactivate", "repair", "remove", "replay"):
        command = actions.add_parser(action); command.add_argument("model_id")
        if action == "activate": command.add_argument("--expected-pass165-frontier")
        if action == "remove": command.add_argument("--purge-package", action="store_true")
    receipt = actions.add_parser("receipt"); receipt.add_argument("operation_id")
    vector = actions.add_parser("vector"); vector.add_argument("token"); vector.add_argument("--model-id")
    similarity = actions.add_parser("similarity"); similarity.add_argument("left"); similarity.add_argument("right"); similarity.add_argument("--model-id")
    nearest = actions.add_parser("nearest"); nearest.add_argument("token"); nearest.add_argument("--model-id"); nearest.add_argument("--top-k", type=int, default=16)
    analogy = actions.add_parser("analogy"); analogy.add_argument("--positive", action="append", required=True); analogy.add_argument("--negative", action="append", default=[]); analogy.add_argument("--model-id"); analogy.add_argument("--top-k", type=int, default=16)
    project = actions.add_parser("project"); project.add_argument("token"); project.add_argument("--model-id")
    return parser


def _emit(stream: TextIO, output: str, value: Any) -> None:
    if output == "json":
        stream.write(json.dumps(value, sort_keys=True, ensure_ascii=False, default=str) + "\n")
    elif isinstance(value, (dict, list)):
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n")
    else:
        stream.write(str(value) + "\n")


def main(argv: Sequence[str] | None = None, *, service: Word2VecService | None = None, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    stdout, stderr = stdout or sys.stdout, stderr or sys.stderr
    args = _parser().parse_args(_normalize_argv(argv if argv is not None else sys.argv[1:]))
    service = service or Word2VecService(args.storage_root)
    try:
        if args.action == "list": result = {"models": service.list_models()}
        elif args.action == "inspect": result = service.inspect(args.model_id)
        elif args.action == "register-manifest": result = service.register_manifest(json.loads(args.manifest.read_text("utf-8")))
        elif args.action == "install":
            if args.manifest: service.register_manifest(json.loads(args.manifest.read_text("utf-8")))
            result = service.install(args.model_id, accept_license=args.license_accept, activate=args.activate, offline_ready=args.offline_ready, replace_existing=args.replace_existing, expected_pass165_frontier=args.expected_pass165_frontier)
        elif args.action == "verify": result = service.verify(args.model_id)
        elif args.action == "activate": result = service.activate(args.model_id, expected_pass165_frontier=args.expected_pass165_frontier)
        elif args.action == "deactivate": result = service.deactivate(args.model_id)
        elif args.action == "repair": result = service.repair(args.model_id)
        elif args.action == "remove": result = service.remove(args.model_id, purge_package=args.purge_package)
        elif args.action == "receipt": result = service.get_operation(args.operation_id)
        elif args.action == "replay": result = service.replay(args.model_id)
        elif args.action == "vector": result = service.vector(args.token, model_id=args.model_id)
        elif args.action == "similarity": result = service.similarity(args.left, args.right, model_id=args.model_id)
        elif args.action == "nearest": result = service.nearest(args.token, model_id=args.model_id, top_k=args.top_k)
        elif args.action == "analogy": result = service.analogy(args.positive, args.negative, model_id=args.model_id, top_k=args.top_k)
        elif args.action == "project": result = service.project(args.token, model_id=args.model_id)
        else: raise Word2VecError("P166_UNSUPPORTED_COMMAND")
        _emit(stdout, args.output, result); return 0
    except Word2VecError as exc:
        _emit(stderr, args.output, {"classification": exc.classification, "detail": exc.detail}); return _exit_for(exc.classification)


if __name__ == "__main__":
    raise SystemExit(main())
