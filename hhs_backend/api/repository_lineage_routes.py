"""Repository pass-contract and commit-lineage projection for the production IDE.

This service is read-only. It derives pass coverage from the repository files shipped
with the application and derives commit lineage from local Git metadata when present,
falling back to the public GitHub API when Heroku omits ``.git`` from the slug.
"""
from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
import os
from pathlib import Path
import re
import subprocess
import threading
import time
from typing import Any, Iterable

from fastapi import APIRouter, HTTPException, Query
import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
REPOSITORY_FULL_NAME = os.environ.get("HHS_REPOSITORY_FULL_NAME", "danonbrez/Holofractal_Harmonicode")
GITHUB_COMMITS_URL = f"https://api.github.com/repos/{REPOSITORY_FULL_NAME}/commits"
MAX_HISTORY_PAGES = max(1, min(100, int(os.environ.get("HHS_REPOSITORY_HISTORY_MAX_PAGES", "30"))))
HISTORY_CACHE_SECONDS = max(60, int(os.environ.get("HHS_REPOSITORY_HISTORY_CACHE_SECONDS", "900")))
MAX_TEXT_BYTES = 2 * 1024 * 1024
TEXT_EXTENSIONS = {".md", ".json", ".jsonl", ".txt", ".py", ".c", ".h", ".js", ".mjs", ".ts", ".tsx", ".yml", ".yaml", ".toml"}
EXCLUDED_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "venv", "dist", "build", "training_specimens"}
FOUNDATION_FILES = ("README.md", "ARCHITECTURE.md", "AGENTS.md", "CHANGELOG.md")
PASS_PATTERN = re.compile(r"(?i)(?:HHS[\s_.-]*)?PASS[\s_.-]*0*(\d{1,3})")
CONSTRAINT_PATTERN = re.compile(
    r"(?i)\b(SHALL|MUST|REQUIRED|REQUIRES|PROHIBITED|FORBIDDEN|HARD INVARIANT|NORMATIVE|MAY NOT|MUST NOT|NO[_ -][A-Z0-9_ -]+)\b"
)

router = APIRouter(
    prefix="/api/runtime/repository-lineage",
    tags=["runtime", "repository", "pass-history", "contracts", "constraints", "lineage"],
)

_history_lock = threading.Lock()
_history_cache: dict[str, Any] = {"expires_at": 0.0, "payload": None}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pass_number(value: str) -> int | None:
    match = PASS_PATTERN.search(value or "")
    if not match:
        return None
    number = int(match.group(1))
    return number if 0 <= number <= 999 else None


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()


def _safe_repository_path(relative_path: str) -> Path:
    candidate = (ROOT_DIR / relative_path).resolve()
    root = ROOT_DIR.resolve()
    if candidate != root and root not in candidate.parents:
        raise HTTPException(status_code=422, detail={"classification": "REPOSITORY_PATH_TRAVERSAL_REJECTED"})
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail={"classification": "REPOSITORY_FILE_NOT_FOUND", "path": relative_path})
    return candidate


def _read_text(path: Path, *, limit: int = MAX_TEXT_BYTES) -> str:
    size = path.stat().st_size
    if size > limit:
        raise ValueError(f"REPOSITORY_TEXT_FILE_TOO_LARGE:{size}")
    return path.read_text(encoding="utf-8", errors="replace")


def _iter_pass_files() -> Iterable[Path]:
    for path in ROOT_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        relative_parts = path.relative_to(ROOT_DIR).parts
        if any(part in EXCLUDED_DIRS for part in relative_parts):
            continue
        if _pass_number(path.as_posix()) is None:
            continue
        yield path


def _category(relative_path: str) -> str:
    upper = relative_path.upper()
    if "CONTRACT" in upper:
        return "CONTRACT"
    if "SPEC" in upper:
        return "SPECIFICATION"
    if "RECEIPT" in upper:
        return "RECEIPT"
    if "EVIDENCE" in upper:
        return "EVIDENCE"
    if "REPORT" in upper:
        return "REPORT"
    if "MANIFEST" in upper:
        return "MANIFEST"
    if "/TEST" in upper or upper.startswith("TEST") or "_TEST" in upper:
        return "TEST"
    if Path(relative_path).suffix.lower() in {".py", ".c", ".h", ".js", ".mjs", ".ts", ".tsx"}:
        return "IMPLEMENTATION"
    return "PASS_ARTIFACT"


def _first_heading(text: str, fallback: str) -> str:
    for raw in text.splitlines()[:120]:
        line = raw.strip()
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            if title:
                return title[:300]
    return fallback


def _extract_field(text: str, labels: tuple[str, ...]) -> str | None:
    joined = "|".join(re.escape(label) for label in labels)
    patterns = (
        re.compile(rf"(?im)^\s*(?:[-*]\s*)?(?:{joined})\s*[:|]\s*`?([^`\n|]+)"),
        re.compile(rf"(?im)^\s*\|\s*(?:{joined})\s*\|\s*`?([^`\n|]+)"),
    )
    for pattern in patterns:
        match = pattern.search(text[:200_000])
        if match:
            return match.group(1).strip().strip("`*")[:500]
    return None


def _metadata(text: str, path: str, pass_number: int | None) -> dict[str, Any]:
    return {
        "pass_number": pass_number,
        "title": _first_heading(text, Path(path).name),
        "contract_identifier": _extract_field(text, ("Contract identifier", "Contract ID", "Identifier")),
        "canonical_name": _extract_field(text, ("Canonical pass name", "Canonical name", "Pass name")),
        "status": _extract_field(text, ("Status", "Implementation status", "Contract status", "Classification")),
        "baseline": _extract_field(text, ("Authoritative baseline", "Baseline", "Repository baseline")),
        "inheritance_parent": _extract_field(text, ("Immediate inheritance parent", "Inheritance parent", "Parent pass")),
        "binding_ancestry": _extract_field(text, ("Binding ancestry", "Ancestry", "Inherited history")),
    }


def _clean_constraint_line(raw: str) -> str:
    line = raw.strip().strip("|")
    line = re.sub(r"^[-*+>\d.)\s]+", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def _constraints(text: str, *, limit: int | None) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        clean = _clean_constraint_line(raw)
        if len(clean) < 12 or len(clean) > 800 or not CONSTRAINT_PATTERN.search(clean):
            continue
        key = clean.casefold()
        if key in seen:
            continue
        seen.add(key)
        found.append(clean)
        if limit is not None and len(found) >= limit:
            break
    return found


def _file_record(path: Path, *, full_constraints: bool = False) -> dict[str, Any]:
    relative_path = _relative(path)
    raw = path.read_bytes()
    text = raw[:MAX_TEXT_BYTES].decode("utf-8", errors="replace")
    pass_number = _pass_number(relative_path) or _pass_number(text[:50_000])
    constraints = _constraints(text, limit=None if full_constraints else 12)
    return {
        "path": relative_path,
        "pass_number": pass_number,
        "category": _category(relative_path),
        "size_bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
        "metadata": _metadata(text, relative_path, pass_number),
        "constraint_count": len(_constraints(text, limit=None)),
        "constraint_preview": constraints if not full_constraints else constraints[:24],
        **({"constraints": constraints} if full_constraints else {}),
    }


@lru_cache(maxsize=1)
def build_pass_catalog() -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in sorted(_iter_pass_files(), key=lambda item: _relative(item).casefold()):
        try:
            files.append(_file_record(path))
        except (OSError, ValueError):
            continue

    grouped: dict[int, list[dict[str, Any]]] = {}
    for record in files:
        number = record.get("pass_number")
        if isinstance(number, int):
            grouped.setdefault(number, []).append(record)

    passes = []
    for number in sorted(grouped):
        records = grouped[number]
        categories: dict[str, int] = {}
        for record in records:
            categories[record["category"]] = categories.get(record["category"], 0) + 1
        contracts = [record for record in records if record["category"] in {"CONTRACT", "SPECIFICATION"}]
        statuses = sorted({str(record["metadata"].get("status")) for record in records if record["metadata"].get("status")})
        passes.append({
            "pass_number": number,
            "artifact_count": len(records),
            "contract_count": len(contracts),
            "constraint_count": sum(int(record["constraint_count"]) for record in records),
            "categories": categories,
            "statuses": statuses,
            "titles": [record["metadata"]["title"] for record in contracts[:6]],
            "contract_paths": [record["path"] for record in contracts],
        })

    present = sorted(grouped)
    minimum = present[0] if present else None
    maximum = present[-1] if present else None
    missing = [number for number in range(minimum or 0, (maximum or -1) + 1) if number not in grouped] if present else []
    foundations = []
    for name in FOUNDATION_FILES:
        path = ROOT_DIR / name
        if path.is_file():
            foundations.append({"path": name, "size_bytes": path.stat().st_size, "sha256": sha256(path.read_bytes()).hexdigest()})

    return {
        "schema": "HHS_REPOSITORY_PASS_CONTRACT_CATALOG_V1",
        "ok": True,
        "repository": REPOSITORY_FULL_NAME,
        "generated_at": _utc_now(),
        "root": str(ROOT_DIR),
        "pass_range": {"minimum": minimum, "maximum": maximum, "present_count": len(present), "missing": missing},
        "summary": {
            "pass_artifact_count": len(files),
            "contract_specification_count": sum(1 for item in files if item["category"] in {"CONTRACT", "SPECIFICATION"}),
            "constraint_line_count": sum(int(item["constraint_count"]) for item in files),
            "foundation_file_count": len(foundations),
        },
        "foundations": foundations,
        "passes": passes,
        "files": files,
        "source": "DEPLOYED_REPOSITORY_FILESYSTEM",
        "frontend_is_authority": False,
    }


def _commit_record(sha: str, parents: list[str], committed_at: str, author: str, message: str, url: str | None) -> dict[str, Any]:
    number = _pass_number(message)
    return {
        "sha": sha,
        "short_sha": sha[:12],
        "parents": parents,
        "committed_at": committed_at,
        "author": author,
        "message": message,
        "pass_number": number,
        "url": url,
    }


def _local_git_history() -> list[dict[str, Any]]:
    if not (ROOT_DIR / ".git").exists():
        return []
    command = [
        "git", "-C", str(ROOT_DIR), "log", "--all", "--date=iso-strict",
        "--pretty=format:%H%x1f%P%x1f%aI%x1f%an%x1f%s",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
    if completed.returncode != 0:
        return []
    records = []
    for line in completed.stdout.splitlines():
        parts = line.split("\x1f")
        if len(parts) != 5:
            continue
        sha, parents, committed_at, author, message = parts
        records.append(_commit_record(sha, parents.split(), committed_at, author, message, f"https://github.com/{REPOSITORY_FULL_NAME}/commit/{sha}"))
    return records


def _github_history() -> tuple[list[dict[str, Any]], bool, dict[str, Any]]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "HHS-Repository-Lineage-V1"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    records: list[dict[str, Any]] = []
    complete = False
    rate: dict[str, Any] = {}
    for page in range(1, MAX_HISTORY_PAGES + 1):
        response = requests.get(GITHUB_COMMITS_URL, params={"per_page": 100, "page": page}, headers=headers, timeout=8)
        rate = {
            "limit": response.headers.get("X-RateLimit-Limit"),
            "remaining": response.headers.get("X-RateLimit-Remaining"),
            "reset": response.headers.get("X-RateLimit-Reset"),
        }
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise RuntimeError("GITHUB_COMMIT_HISTORY_RESPONSE_INVALID")
        for item in payload:
            commit = item.get("commit") or {}
            author = item.get("author") or {}
            commit_author = commit.get("author") or {}
            message = str(commit.get("message") or "").splitlines()[0]
            records.append(_commit_record(
                str(item.get("sha") or ""),
                [str(parent.get("sha") or "") for parent in item.get("parents") or []],
                str(commit_author.get("date") or ""),
                str(author.get("login") or commit_author.get("name") or "unknown"),
                message,
                item.get("html_url"),
            ))
        if len(payload) < 100:
            complete = True
            break
    return records, complete, rate


def _classify_history(records: list[dict[str, Any]], *, source: str, complete: bool, rate: dict[str, Any] | None = None) -> dict[str, Any]:
    dated = [item for item in records if item.get("committed_at")]
    numbered_dates = sorted(item["committed_at"] for item in dated if item.get("pass_number") is not None)
    earliest_numbered = numbered_dates[0] if numbered_dates else None
    for item in records:
        item["legacy_pre_pass"] = bool(earliest_numbered and item.get("committed_at") and item["committed_at"] < earliest_numbered)
        item["history_class"] = (
            "LEGACY_PRE_PASS" if item["legacy_pre_pass"]
            else "NUMBERED_PASS" if item.get("pass_number") is not None
            else "UNNUMBERED_POST_PASS"
        )
    return {
        "schema": "HHS_REPOSITORY_COMMIT_LINEAGE_V1",
        "ok": bool(records),
        "repository": REPOSITORY_FULL_NAME,
        "generated_at": _utc_now(),
        "source": source,
        "history_complete": complete,
        "max_pages": MAX_HISTORY_PAGES,
        "commit_count": len(records),
        "legacy_pre_pass_count": sum(1 for item in records if item["legacy_pre_pass"]),
        "numbered_pass_commit_count": sum(1 for item in records if item.get("pass_number") is not None),
        "unnumbered_post_pass_count": sum(1 for item in records if item["history_class"] == "UNNUMBERED_POST_PASS"),
        "earliest_numbered_pass_commit_at": earliest_numbered,
        "rate_limit": rate or {},
        "commits": records,
        "frontend_is_authority": False,
    }


def build_commit_history(*, refresh: bool = False) -> dict[str, Any]:
    now = time.time()
    with _history_lock:
        cached = _history_cache.get("payload")
        if not refresh and cached and now < float(_history_cache.get("expires_at") or 0):
            return {**cached, "cache_hit": True}

        local = _local_git_history()
        if local:
            payload = _classify_history(local, source="LOCAL_GIT_HISTORY", complete=True)
        else:
            try:
                remote, complete, rate = _github_history()
                payload = _classify_history(remote, source="GITHUB_COMMITS_API", complete=complete, rate=rate)
            except Exception as exc:
                if cached:
                    return {**cached, "cache_hit": True, "stale": True, "refresh_error": f"{type(exc).__name__}: {exc}"}
                payload = {
                    "schema": "HHS_REPOSITORY_COMMIT_LINEAGE_V1",
                    "ok": False,
                    "repository": REPOSITORY_FULL_NAME,
                    "generated_at": _utc_now(),
                    "source": "UNAVAILABLE",
                    "history_complete": False,
                    "commit_count": 0,
                    "legacy_pre_pass_count": 0,
                    "numbered_pass_commit_count": 0,
                    "unnumbered_post_pass_count": 0,
                    "commits": [],
                    "error": f"{type(exc).__name__}: {exc}",
                    "frontend_is_authority": False,
                }
        _history_cache["payload"] = payload
        _history_cache["expires_at"] = now + HISTORY_CACHE_SECONDS
        return {**payload, "cache_hit": False}


@router.get("/status")
def repository_lineage_status() -> dict[str, Any]:
    catalog = build_pass_catalog()
    return {
        "schema": "HHS_REPOSITORY_LINEAGE_STATUS_V1",
        "ok": True,
        "status": "REPOSITORY_LINEAGE_INDEXED",
        "catalog": catalog["summary"],
        "pass_range": catalog["pass_range"],
        "history_sources": {
            "local_git_present": (ROOT_DIR / ".git").exists(),
            "github_api_fallback": GITHUB_COMMITS_URL,
            "cache_seconds": HISTORY_CACHE_SECONDS,
        },
        "catalog_api": "/api/runtime/repository-lineage/catalog",
        "history_api": "/api/runtime/repository-lineage/history",
        "frontend_is_authority": False,
    }


@router.get("/catalog")
def repository_pass_catalog() -> dict[str, Any]:
    return build_pass_catalog()


@router.get("/pass/{pass_number}")
def repository_pass_detail(pass_number: int) -> dict[str, Any]:
    catalog = build_pass_catalog()
    records = [record for record in catalog["files"] if record.get("pass_number") == pass_number]
    if not records:
        raise HTTPException(status_code=404, detail={"classification": "REPOSITORY_PASS_NOT_FOUND", "pass_number": pass_number})
    details = []
    for record in records:
        path = _safe_repository_path(record["path"])
        details.append(_file_record(path, full_constraints=True))
    return {
        "schema": "HHS_REPOSITORY_PASS_DETAIL_V1",
        "ok": True,
        "pass_number": pass_number,
        "artifact_count": len(details),
        "constraint_count": sum(len(item.get("constraints") or []) for item in details),
        "artifacts": details,
        "frontend_is_authority": False,
    }


@router.get("/file")
def repository_lineage_file(path: str = Query(min_length=1, max_length=2048)) -> dict[str, Any]:
    resolved = _safe_repository_path(path)
    try:
        text = _read_text(resolved)
    except ValueError as exc:
        raise HTTPException(status_code=413, detail={"classification": str(exc), "path": path}) from exc
    pass_number = _pass_number(path) or _pass_number(text[:50_000])
    return {
        "schema": "HHS_REPOSITORY_LINEAGE_FILE_V1",
        "ok": True,
        "path": _relative(resolved),
        "pass_number": pass_number,
        "category": _category(path),
        "sha256": sha256(resolved.read_bytes()).hexdigest(),
        "size_bytes": resolved.stat().st_size,
        "metadata": _metadata(text, path, pass_number),
        "constraints": _constraints(text, limit=None),
        "content": text,
        "read_only": True,
        "frontend_is_authority": False,
    }


@router.get("/history")
def repository_commit_history(refresh: bool = False) -> dict[str, Any]:
    return build_commit_history(refresh=refresh)
