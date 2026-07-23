from __future__ import annotations
import hashlib, json, os, tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "HHS_PASS151_V1"

def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_file(path: os.PathLike[str] | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def atomic_write(path: os.PathLike[str] | str, data: str) -> None:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=target.name + ".", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(data); fh.flush(); os.fsync(fh.fileno())
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def append_jsonl(path: os.PathLike[str] | str, record: dict[str, Any]) -> None:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    line = canonical_json(record) + "\n"
    with open(target, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(line); fh.flush(); os.fsync(fh.fileno())

def load_jsonl(path: os.PathLike[str] | str) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists(): return []
    out=[]
    for line in target.read_text(encoding="utf-8").splitlines():
        if line.strip(): out.append(json.loads(line))
    return out
