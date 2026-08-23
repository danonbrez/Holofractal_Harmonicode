"""Repository pass-contract and commit-lineage projection for the production IDE.

This surface is read-only. It exposes repository-visible history to the visual IDE
without replacing the editor, compiler, VM81, registry, or lifecycle authorities.
"""
from __future__ import annotations

from functools import lru_cache
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(
    prefix="/api/runtime/repository",
    tags=["runtime", "repository", "pass-history", "commit-lineage", "visual-ide"],
)

ROOT_DIR = Path(__file__).resolve().parents[2]
REPOSITORY = "danonbrez/Holofractal_Harmonicode"
GITHUB_API = f"https://api.github.com/repos/{REPOSITORY}"
TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml",
    ".py", ".c", ".h", ".cc", ".cpp", ".js", ".mjs", ".ts", ".tsx",
    ".html", ".css", ".sh", ".ps1", ".xml", ".csv",
}
EXCLUDED_PARTS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "venv"}
PASS_PATTERN = re.compile(r"(?i)(?:^|[^a-z0-9])(?:hhs[_-]?)?pass[_\s.-]?0*(\d{1,3})(?:[^0-9]|$)")
CONTRACT_PATTERN = re.compile(r"(?i)\b(contract|specification|normative|requirements?)\b")
STATUS_PATTERN = re.compile(r"(?i)\b(verified|complete|completed|incomplete|blocked|partial|deprecated|superseded|implemented|pending)\b")
CONSTRAINT_PATTERN = re.compile(r"(?i)\b(must|shall|required|prohibited|constraint|invariant|inherit|authority|rejection|zero[-_ ]bypass)\b")


def _safe_relative(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def _pass_number(path: str, text: str = "") -> int | None:
    match = PASS_PATTERN.search(path)
    if not match and text:
        match = PASS_PATTERN.search(text[:8192])
    return int(match.group(1)) if match else None


def _kind(path: str, text: str) -> str:
    lowered = path.lower()
    if "receipt" in lowered:
        return "RECEIPT"
    if "evidence" in lowered or "validation" in lowered:
        return "EVIDENCE"
    if "report" in lowered:
        return "REPORT"
    if "test" in lowered or "/tests/" in f"/{lowered}":
        return "TEST"
    if "workflow" in lowered or "/.github/" in f"/{lowered}":
        return "WORKFLOW"
    if "contract" in lowered or "spec" in lowered or CONTRACT_PATTERN.search(text[:16384]):
        return "CONTRACT"
    return "IMPLEMENTATION"


def _title(path: str, text: str) -> str:
    for raw in text.splitlines()[:80]:
        line = raw.strip().lstrip("#").strip()
        if not line:
            continue
        if len(line) > 180:
            line = line[:177] + "…"
        if raw.lstrip().startswith("#") or "PASS" in line.upper():
            return line
    return Path(path).name


def _status_terms(text: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for match in STATUS_PATTERN.finditer(text[:65536]):
        value = match.group(1).upper()
        if value not in seen:
            seen.add(value)
            values.append(value)
        if len(values) == 8:
            break
    return values


def _constraint_excerpt(text: str) -> list[str]:
    excerpts: list[str] = []
    for raw in text.splitlines()[:900]:
        line = " ".join(raw.strip().split())
        if not line or len(line) < 8 or not CONSTRAINT_PATTERN.search(line):
            continue
        excerpts.append(line[:240])
        if len(excerpts) == 12:
            break
    return excerpts


def _read_text(path: Path, limit: int = 262_144) -> str:
    try:
        with path.open("rb") as handle:
            raw = handle.read(limit + 1)
    except OSError:
        return ""
    if len(raw) > limit:
        raw = raw[:limit]
    return raw.decode("utf-8", errors="replace")


@lru_cache(maxsize=1)
def _catalog() -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for path in ROOT_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = _safe_relative(path)
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        number_from_path = _pass_number(relative)
        name_upper = path.name.upper()
        if number_from_path is None and "PASS" not in name_upper:
            continue
        text = _read_text(path)
        number = number_from_path if number_from_path is not None else _pass_number(relative, text)
        if number is None:
            continue
        constraints = _constraint_excerpt(text)
        entries.append({
            "pass_number": number,
            "path": relative,
            "name": path.name,
            "title": _title(relative, text),
            "kind": _kind(relative, text),
            "size_bytes": path.stat().st_size,
            "status_terms": _status_terms(text),
            "constraint_count_sampled": len(constraints),
            "constraint_excerpts": constraints,
            "github_url": f"https://github.com/{REPOSITORY}/blob/main/{relative}",
        })

    entries.sort(key=lambda item: (item["pass_number"], item["kind"], item["path"]))
    grouped: dict[int, dict[str, Any]] = {}
    for entry in entries:
        group = grouped.setdefault(entry["pass_number"], {
            "pass_number": entry["pass_number"],
            "files": [],
            "kinds": set(),
            "status_terms": set(),
            "constraint_count_sampled": 0,
        })
        group["files"].append(entry)
        group["kinds"].add(entry["kind"])
        group["status_terms"].update(entry["status_terms"])
        group["constraint_count_sampled"] += entry["constraint_count_sampled"]

    passes = []
    for number in sorted(grouped):
        group = grouped[number]
        files = group["files"]
        contract = next((item for item in files if item["kind"] == "CONTRACT"), files[0])
        passes.append({
            "pass_number": number,
            "title": contract["title"],
            "primary_path": contract["path"],
            "file_count": len(files),
            "kinds": sorted(group["kinds"]),
            "status_terms": sorted(group["status_terms"]),
            "constraint_count_sampled": group["constraint_count_sampled"],
            "files": files,
        })

    return {
        "schema": "HHS_REPOSITORY_PASS_CONSTRAINT_CATALOG_V1",
        "ok": True,
        "repository": REPOSITORY,
        "pass_count": len(passes),
        "file_count": len(entries),
        "earliest_pass": passes[0]["pass_number"] if passes else None,
        "latest_pass": passes[-1]["pass_number"] if passes else None,
        "passes": passes,
        "frontend_is_authority": False,
        "catalog_source": "DEPLOYED_REPOSITORY_FILESYSTEM",
    }


def _local_commits(page: int, limit: int) -> tuple[list[dict[str, Any]], bool] | None:
    offset = (page - 1) * limit
    command = [
        "git", "log", f"--skip={offset}", f"-n{limit + 1}",
        "--date=iso-strict", "--format=%H%x1f%P%x1f%aI%x1f%an%x1f%s",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT_DIR,
            check=True,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    rows = [line for line in completed.stdout.splitlines() if line.strip()]
    has_more = len(rows) > limit
    commits = []
    for row in rows[:limit]:
        sha, parents, authored_at, author, subject = (row.split("\x1f", 4) + ["", "", "", "", ""])[:5]
        commits.append({
            "sha": sha,
            "short_sha": sha[:12],
            "parents": [value for value in parents.split() if value],
            "authored_at": authored_at,
            "author": author,
            "message": subject,
            "url": f"https://github.com/{REPOSITORY}/commit/{sha}",
        })
    return commits, has_more


def _github_commits(page: int, limit: int) -> tuple[list[dict[str, Any]], bool]:
    query = urlencode({"sha": "main", "per_page": limit, "page": page})
    request = Request(
        f"{GITHUB_API}/commits?{query}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "HHS-Repository-Lineage-Surface/1.0",
            **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.environ.get("GITHUB_TOKEN") else {}),
        },
    )
    try:
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=503, detail={
            "classification": "HHS_REPOSITORY_COMMIT_HISTORY_UNAVAILABLE",
            "error": f"{type(exc).__name__}: {exc}",
        }) from exc
    commits = []
    for item in payload:
        commit = item.get("commit") or {}
        author = commit.get("author") or {}
        commits.append({
            "sha": item.get("sha"),
            "short_sha": str(item.get("sha") or "")[:12],
            "parents": [parent.get("sha") for parent in item.get("parents") or [] if parent.get("sha")],
            "authored_at": author.get("date"),
            "author": author.get("name"),
            "message": str(commit.get("message") or "").splitlines()[0],
            "url": item.get("html_url"),
        })
    return commits, len(commits) == limit


@router.get("/status")
def repository_history_status() -> dict[str, Any]:
    """Return constant-time repository-surface liveness without indexing files."""
    return {
        "schema": "HHS_REPOSITORY_HISTORY_STATUS_V1",
        "ok": True,
        "repository": REPOSITORY,
        "catalog_state": "DEFERRED_UNTIL_EXPLICIT_PASS_CATALOG_REQUEST",
        "pass_count": None,
        "pass_file_count": None,
        "earliest_pass": None,
        "latest_pass": None,
        "deployed_commit": os.environ.get("SOURCE_VERSION") or os.environ.get("HEROKU_SLUG_COMMIT"),
        "pass_catalog_api": "/api/runtime/repository/passes",
        "commit_history_api": "/api/runtime/repository/commits",
        "file_read_api": "/api/runtime/repository/file",
        "ide_default_surface": "FULL_INTEGRATED_DEVELOPMENT_ENVIRONMENT",
        "history_is_supporting_surface": True,
        "history_hydration": "USER_INITIATED",
        "status_read_is_bounded": True,
        "frontend_is_authority": False,
    }


@router.get("/passes")
def repository_pass_catalog(
    query: str = Query(default="", max_length=200),
    pass_number: int | None = Query(default=None, ge=0, le=999),
) -> dict[str, Any]:
    catalog = _catalog()
    passes = catalog["passes"]
    if pass_number is not None:
        passes = [item for item in passes if item["pass_number"] == pass_number]
    if query.strip():
        needle = query.casefold().strip()
        passes = [item for item in passes if needle in json.dumps(item, ensure_ascii=False).casefold()]
    return {**catalog, "passes": passes, "filtered_pass_count": len(passes), "query": query, "pass_number": pass_number}


@router.get("/commits")
def repository_commit_history(
    page: int = Query(default=1, ge=1, le=100_000),
    limit: int = Query(default=50, ge=1, le=100),
) -> dict[str, Any]:
    local = _local_commits(page, limit)
    if local is None:
        commits, has_more = _github_commits(page, limit)
        source = "GITHUB_MAIN_HISTORY"
    else:
        commits, has_more = local
        source = "LOCAL_GIT_HISTORY"
    return {
        "schema": "HHS_REPOSITORY_COMMIT_LINEAGE_PAGE_V1",
        "ok": True,
        "repository": REPOSITORY,
        "branch": "main",
        "page": page,
        "limit": limit,
        "has_more": has_more,
        "source": source,
        "commits": commits,
        "deployed_commit": os.environ.get("SOURCE_VERSION") or os.environ.get("HEROKU_SLUG_COMMIT"),
        "frontend_is_authority": False,
    }


@router.get("/file")
def repository_text_file(path: str = Query(min_length=1, max_length=1024)) -> dict[str, Any]:
    candidate = (ROOT_DIR / path).resolve()
    try:
        candidate.relative_to(ROOT_DIR.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=403, detail={"classification": "HHS_REPOSITORY_PATH_ESCAPE_REJECTED"}) from exc
    if not candidate.is_file() or candidate.suffix.lower() not in TEXT_SUFFIXES:
        raise HTTPException(status_code=404, detail={"classification": "HHS_REPOSITORY_TEXT_FILE_NOT_FOUND"})
    text = _read_text(candidate)
    return {
        "schema": "HHS_REPOSITORY_TEXT_FILE_V1",
        "ok": True,
        "path": _safe_relative(candidate),
        "size_bytes": candidate.stat().st_size,
        "truncated": candidate.stat().st_size > len(text.encode("utf-8")),
        "content": text,
        "read_only": True,
        "frontend_is_authority": False,
    }
