#!/usr/bin/env python3
"""Install a Lane-5-mediated Runtime OS first-paint projection in nginx.

Root, assets, APIs, and WebSockets all remain behind the host Lane 5 ingress
gateway.  The first-paint locations retain their cache policy but never serve
directly from the filesystem, so public environmental ingress cannot bypass the
same exact byte/provenance membrane used by dynamic requests.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
from typing import Iterable

BACKEND_MARKER = "proxy_pass http://127.0.0.1:8715"
START_MARKER = "# HHS_RUNTIME_OS_STATIC_FIRST_V1_BEGIN"
END_MARKER = "# HHS_RUNTIME_OS_STATIC_FIRST_V1_END"


def _server_blocks(text: str) -> Iterable[tuple[int, int]]:
    for match in re.finditer(r"(?m)^\s*server\s*\{", text):
        start = match.start()
        depth = 0
        in_quote: str | None = None
        escaped = False
        for index in range(match.end() - 1, len(text)):
            ch = text[index]
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if in_quote:
                if ch == in_quote:
                    in_quote = None
                continue
            if ch in {"'", '"'}:
                in_quote = ch
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    yield start, index
                    break


def _find_tls_runtime_block(text: str) -> tuple[int, int]:
    candidates: list[tuple[int, int]] = []
    for start, end in _server_blocks(text):
        block = text[start : end + 1]
        if not re.search(r"(?m)^\s*listen\s+(?:\[[^\]]+\]:)?443\b[^;]*;", block):
            continue
        if BACKEND_MARKER not in block:
            continue
        candidates.append((start, end))
    if len(candidates) != 1:
        raise RuntimeError(
            f"HHS_RUNTIME_OS_TLS_PROXY_BLOCK_COUNT_INVALID:{len(candidates)}"
        )
    return candidates[0]


def _snippet(runtime_root: Path) -> str:
    _ = runtime_root
    return f"""
    {START_MARKER}
    # Presentation cache policy only. All bytes still traverse Lane 5 on :8715.
    location = / {{
        proxy_pass http://127.0.0.1:8715;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        add_header Cache-Control "no-cache" always;
    }}

    location ^~ /assets/ {{
        proxy_pass http://127.0.0.1:8715;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        expires 1y;
        add_header Cache-Control "public, immutable" always;
    }}
    {END_MARKER}
"""


def patch_nginx_text(text: str, runtime_root: Path) -> str:
    start, end = _find_tls_runtime_block(text)
    block = text[start : end + 1]
    existing = re.compile(
        rf"(?ms)^\s*{re.escape(START_MARKER)}.*?^\s*{re.escape(END_MARKER)}\s*"
    )
    block = existing.sub("", block)

    generic = re.search(r"(?m)^\s*location\s+/\s*\{", block)
    if generic is None:
        raise RuntimeError("HHS_RUNTIME_OS_GENERIC_LOCATION_MISSING")

    patched_block = block[: generic.start()] + _snippet(runtime_root) + block[generic.start() :]
    return text[:start] + patched_block + text[end + 1 :]


def discover_site(search_roots: Iterable[Path]) -> Path:
    matches: list[Path] = []
    seen: set[Path] = set()
    for root in search_roots:
        if not root.exists():
            continue
        for candidate in sorted(root.rglob("*")):
            if not candidate.is_file():
                continue
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            try:
                text = resolved.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if BACKEND_MARKER in text and re.search(
                r"(?m)^\s*listen\s+(?:\[[^\]]+\]:)?443\b[^;]*;", text
            ):
                matches.append(resolved)
                seen.add(resolved)
    if len(matches) != 1:
        raise RuntimeError(
            "HHS_RUNTIME_OS_NGINX_SITE_COUNT_INVALID:"
            + str(len(matches))
            + ":"
            + ",".join(str(path) for path in matches)
        )
    return matches[0]


def install(site: Path, runtime_root: Path, *, reload_nginx: bool = True) -> Path:
    index = runtime_root / "index.html"
    assets = runtime_root / "assets"
    if not index.is_file():
        raise RuntimeError(f"HHS_RUNTIME_OS_INDEX_MISSING:{index}")
    if not assets.is_dir():
        raise RuntimeError(f"HHS_RUNTIME_OS_ASSETS_MISSING:{assets}")

    original = site.read_text(encoding="utf-8")
    patched = patch_nginx_text(original, runtime_root)
    if patched != original:
        backup = site.with_name(site.name + ".pre-hhs-static-first")
        if not backup.exists():
            shutil.copy2(site, backup)
        temporary = site.with_name(site.name + ".tmp")
        temporary.write_text(patched, encoding="utf-8")
        temporary.replace(site)

    if reload_nginx:
        subprocess.run(["nginx", "-t"], check=True)
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
        subprocess.run(["systemctl", "is-active", "--quiet", "nginx"], check=True)
    return site


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site")
    parser.add_argument(
        "--runtime-os-root",
        default="/var/lib/hhs/runtime-os/current",
    )
    parser.add_argument("--no-reload", action="store_true")
    args = parser.parse_args()

    runtime_root = Path(args.runtime_os_root).resolve()
    site = (
        Path(args.site).resolve()
        if args.site
        else discover_site(
            (
                Path("/etc/nginx/sites-enabled"),
                Path("/etc/nginx/conf.d"),
            )
        )
    )
    install(site, runtime_root, reload_nginx=not args.no_reload)
    print(f"HHS_RUNTIME_OS_STATIC_FIRST_INSTALLED={site}")
    print(f"HHS_RUNTIME_OS_STATIC_FIRST_ROOT={runtime_root}")
    print("HHS_RUNTIME_OS_STATIC_FIRST_CANONICAL_AUTHORITY=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
