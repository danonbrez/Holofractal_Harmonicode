#!/usr/bin/env python3
"""Idempotently attach the standalone application-VM API to production nginx."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import subprocess
from typing import Iterable

DEFAULT_INCLUDE = "/etc/nginx/snippets/hhs-application-vm.conf"
BACKEND_MARKER = "proxy_pass http://127.0.0.1:8080"


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
    raise RuntimeError("HHS_APPLICATION_VM_NGINX_UNBALANCED_BRACES")


def _server_blocks(text: str) -> Iterable[tuple[int, int]]:
    for match in re.finditer(r"(?m)^\s*server\s*\{", text):
        open_index = text.find("{", match.start(), match.end())
        yield match.start(), _matching_brace(text, open_index)


def inject_application_vm_include(
    text: str,
    *,
    include_path: str = DEFAULT_INCLUDE,
) -> tuple[str, bool]:
    include_line = f"include {include_path};"
    for start, end in _server_blocks(text):
        block = text[start : end + 1]
        tls = re.search(
            r"(?m)^\s*listen\s+(?:\[[^\]]+\]:)?443\b[^;]*;",
            block,
        )
        owns_runtime = BACKEND_MARKER in block
        if not (tls and owns_runtime):
            continue
        if include_line in block:
            return text, False
        insertion = f"\n    {include_line}\n"
        return text[:end] + insertion + text[end:], True
    raise RuntimeError("HHS_APPLICATION_VM_TLS_RUNTIME_SERVER_NOT_FOUND")


def discover_site() -> Path:
    candidates: list[Path] = []
    for root in (Path("/etc/nginx/sites-enabled"), Path("/etc/nginx/conf.d")):
        if not root.is_dir():
            continue
        for path in sorted(root.iterdir()):
            if not path.is_file() and not path.is_symlink():
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if BACKEND_MARKER in content:
                candidates.append(path.resolve())
    unique = list(dict.fromkeys(candidates))
    if len(unique) != 1:
        raise RuntimeError(
            "HHS_APPLICATION_VM_NGINX_SITE_AMBIGUOUS:"
            + ",".join(str(path) for path in unique)
        )
    return unique[0]


def configure(
    *,
    site: Path,
    snippet_source: Path,
    snippet_destination: Path,
) -> dict[str, str | bool]:
    if not site.is_file():
        raise RuntimeError(f"HHS_APPLICATION_VM_NGINX_SITE_MISSING:{site}")
    if not snippet_source.is_file():
        raise RuntimeError(
            f"HHS_APPLICATION_VM_NGINX_SNIPPET_SOURCE_MISSING:{snippet_source}"
        )

    snippet_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(snippet_source, snippet_destination)
    snippet_destination.chmod(0o644)

    original = site.read_text(encoding="utf-8")
    updated, changed = inject_application_vm_include(
        original,
        include_path=str(snippet_destination),
    )

    backup: Path | None = None
    if changed:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = site.with_name(site.name + f".pre-hhs-application-vm-{stamp}")
        shutil.copy2(site, backup)
        site.write_text(updated, encoding="utf-8")

    try:
        subprocess.run(["nginx", "-t"], check=True)
    except Exception:
        if changed and backup is not None:
            shutil.copy2(backup, site)
            subprocess.run(["nginx", "-t"], check=False)
        raise

    subprocess.run(["systemctl", "reload", "nginx"], check=True)
    return {
        "site": str(site),
        "snippet": str(snippet_destination),
        "changed": changed,
        "backup": str(backup) if backup is not None else "",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site")
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--snippet-destination", default=DEFAULT_INCLUDE)
    args = parser.parse_args()

    site = Path(args.site).resolve() if args.site else discover_site()
    repository_root = Path(args.repository_root).resolve()
    snippet_source = (
        repository_root
        / "deployment/ubuntu/application_vm/nginx-hhs-application-vm.conf"
    )
    receipt = configure(
        site=site,
        snippet_source=snippet_source,
        snippet_destination=Path(args.snippet_destination),
    )
    for key, value in receipt.items():
        print(f"HHS_APPLICATION_VM_NGINX_{key.upper()}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
