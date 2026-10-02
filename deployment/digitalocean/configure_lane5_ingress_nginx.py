#!/usr/bin/env python3
"""Move the production TLS proxy behind the Lane 5 host ingress membrane."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
from typing import Iterable

DIRECT_BACKEND_MARKER = "proxy_pass http://127.0.0.1:8080"
LANE5_GATEWAY_MARKER = "proxy_pass http://127.0.0.1:8715"


def _matching_brace(text: str, open_index: int) -> int:
    depth = 0
    quote: str | None = None
    escaped = False
    comment = False
    for index in range(open_index, len(text)):
        ch = text[index]
        if comment:
            if ch == "\n":
                comment = False
            continue
        if quote is not None:
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == quote:
                quote = None
            continue
        if ch == "#":
            comment = True
            continue
        if ch in {'"', "'"}:
            quote = ch
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return index
    raise RuntimeError("HHS_LANE5_INGRESS_NGINX_UNBALANCED_BRACES")


def _server_blocks(text: str) -> Iterable[tuple[int, int]]:
    for match in re.finditer(r"(?m)^\s*server\s*\{", text):
        open_index = text.find("{", match.start(), match.end())
        yield match.start(), _matching_brace(text, open_index)


def _tls_runtime_blocks(text: str) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for start, end in _server_blocks(text):
        block = text[start : end + 1]
        tls = re.search(
            r"(?m)^\s*listen\s+(?:\[[^\]]+\]:)?443\b[^;]*;",
            block,
        )
        runtime = DIRECT_BACKEND_MARKER in block or LANE5_GATEWAY_MARKER in block
        if tls and runtime:
            result.append((start, end))
    return result


def patch_nginx_text(text: str) -> tuple[str, bool]:
    blocks = _tls_runtime_blocks(text)
    if len(blocks) != 1:
        raise RuntimeError(
            f"HHS_LANE5_INGRESS_TLS_RUNTIME_SERVER_COUNT_INVALID:{len(blocks)}"
        )
    start, end = blocks[0]
    block = text[start : end + 1]
    migrated = block.replace(DIRECT_BACKEND_MARKER, LANE5_GATEWAY_MARKER)
    if DIRECT_BACKEND_MARKER in migrated:
        raise RuntimeError("HHS_LANE5_INGRESS_DIRECT_BACKEND_BYPASS_REMAINS")
    if LANE5_GATEWAY_MARKER not in migrated:
        raise RuntimeError("HHS_LANE5_INGRESS_GATEWAY_PROXY_MISSING")
    changed = migrated != block
    return text[:start] + migrated + text[end + 1 :], changed


def discover_site(search_roots: Iterable[Path]) -> Path:
    matches: list[Path] = []
    seen: set[Path] = set()
    for root in search_roots:
        if not root.exists():
            continue
        for candidate in sorted(root.rglob("*")):
            if not candidate.is_file() and not candidate.is_symlink():
                continue
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            try:
                text = resolved.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if not _tls_runtime_blocks(text):
                continue
            matches.append(resolved)
            seen.add(resolved)
    if len(matches) != 1:
        raise RuntimeError(
            "HHS_LANE5_INGRESS_NGINX_SITE_COUNT_INVALID:"
            + str(len(matches))
            + ":"
            + ",".join(str(path) for path in matches)
        )
    return matches[0]


def configure(site: Path, *, reload_nginx: bool = True) -> dict[str, str | bool]:
    original = site.read_text(encoding="utf-8")
    updated, changed = patch_nginx_text(original)
    backup: Path | None = None
    if changed:
        backup = site.with_name(site.name + ".pre-hhs-lane5-ingress")
        if not backup.exists():
            shutil.copy2(site, backup)
        temporary = site.with_name(site.name + ".lane5.tmp")
        temporary.write_text(updated, encoding="utf-8")
        temporary.replace(site)
    if reload_nginx:
        try:
            subprocess.run(["nginx", "-t"], check=True)
            subprocess.run(["systemctl", "reload", "nginx"], check=True)
            subprocess.run(["systemctl", "is-active", "--quiet", "nginx"], check=True)
        except Exception:
            if changed and backup is not None:
                shutil.copy2(backup, site)
                subprocess.run(["nginx", "-t"], check=False)
                subprocess.run(["systemctl", "reload", "nginx"], check=False)
            raise
    final = site.read_text(encoding="utf-8")
    if DIRECT_BACKEND_MARKER in final:
        raise RuntimeError("HHS_LANE5_INGRESS_DIRECT_BACKEND_BYPASS_REMAINS")
    return {
        "site": str(site),
        "changed": changed,
        "backup": str(backup) if backup is not None else "",
        "gateway": LANE5_GATEWAY_MARKER,
        "direct_backend_bypass": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site")
    parser.add_argument("--no-reload", action="store_true")
    args = parser.parse_args()
    site = (
        Path(args.site).resolve()
        if args.site
        else discover_site((Path("/etc/nginx/sites-enabled"), Path("/etc/nginx/conf.d")))
    )
    receipt = configure(site, reload_nginx=not args.no_reload)
    for key, value in receipt.items():
        print(f"HHS_LANE5_INGRESS_NGINX_{key.upper()}={value}")
    print("HHS_LANE5_INGRESS_ZERO_BYPASS=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
