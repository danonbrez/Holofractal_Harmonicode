#!/usr/bin/env python3
"""Cut production transport over from host Python to the exact-SHA Ubuntu guest.

The host remains presentation/network/hypervisor infrastructure only:
* static Runtime OS bytes may still be served directly by nginx;
* dynamic Runtime OS/IDE requests go to the guest IDE on loopback :18080;
* /vm-api goes to the guest application-VM control plane on loopback :18720.

No HHS computation or canonical persistence is performed by this module.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Iterable
from urllib.request import urlopen

LEGACY_BACKEND = "proxy_pass http://127.0.0.1:8080"
GUEST_BACKEND = "proxy_pass http://127.0.0.1:18080"
DEFAULT_SNIPPET = "/etc/nginx/snippets/hhs-application-vm.conf"


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
    raise RuntimeError("HHS_I047_NGINX_UNBALANCED_BRACES")


def _server_blocks(text: str) -> Iterable[tuple[int, int]]:
    for match in re.finditer(r"(?m)^\s*server\s*\{", text):
        open_index = text.find("{", match.start(), match.end())
        yield match.start(), _matching_brace(text, open_index)


def _tls_runtime_block(text: str) -> tuple[int, int]:
    matches: list[tuple[int, int]] = []
    for start, end in _server_blocks(text):
        block = text[start : end + 1]
        if not re.search(r"(?m)^\s*listen\s+(?:\[[^\]]+\]:)?443\b[^;]*;", block):
            continue
        if LEGACY_BACKEND in block or GUEST_BACKEND in block:
            matches.append((start, end))
    if len(matches) != 1:
        raise RuntimeError(f"HHS_I047_TLS_RUNTIME_BLOCK_COUNT_INVALID:{len(matches)}")
    return matches[0]


def patch_runtime_backend(text: str, *, target: str = "guest") -> tuple[str, bool]:
    start, end = _tls_runtime_block(text)
    block = text[start : end + 1]
    if target not in {"guest", "host"}:
        raise RuntimeError(f"HHS_I047_PROXY_TARGET_INVALID:{target}")
    if LEGACY_BACKEND in block and GUEST_BACKEND in block:
        raise RuntimeError("HHS_I047_MIXED_HOST_GUEST_BACKENDS")
    desired = GUEST_BACKEND if target == "guest" else LEGACY_BACKEND
    current = GUEST_BACKEND if GUEST_BACKEND in block else LEGACY_BACKEND
    if current == desired:
        return text, False
    if block.count(current) != 1:
        raise RuntimeError(
            f"HHS_I047_BACKEND_COUNT_INVALID:{current}:{block.count(current)}"
        )
    patched = block.replace(current, desired, 1)
    marker = "    # HHS_PASS_220_I047_UNIFIED_GUEST_DYNAMIC_BACKEND\n"
    patched = patched.replace(marker, "")
    if target == "guest":
        location = re.search(r"(?m)^\s*location\s+/\s*\{", patched)
        if location is not None:
            patched = patched[: location.start()] + marker + patched[location.start() :]
    return text[:start] + patched + text[end + 1 :], True


def discover_site() -> Path:
    matches: list[Path] = []
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
            if (LEGACY_BACKEND in content or GUEST_BACKEND in content) and re.search(
                r"(?m)^\s*listen\s+(?:\[[^\]]+\]:)?443\b[^;]*;", content
            ):
                matches.append(path.resolve())
    unique = list(dict.fromkeys(matches))
    if len(unique) != 1:
        raise RuntimeError(
            "HHS_I047_NGINX_SITE_AMBIGUOUS:" + ",".join(str(p) for p in unique)
        )
    return unique[0]


def _json_health(url: str) -> dict[str, object]:
    with urlopen(url, timeout=10) as response:  # noqa: S310 - loopback constants only
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"HHS_I047_HEALTH_NOT_OBJECT:{url}")
    return payload


def verify_guest_transport() -> dict[str, object]:
    ide = _json_health("http://127.0.0.1:18080/api/health")
    vm = _json_health("http://127.0.0.1:18720/health")
    if ide.get("runtime_ready") is not True:
        raise RuntimeError("HHS_I047_GUEST_IDE_NOT_READY")
    if ide.get("frontend_runtime_authority") is not False:
        raise RuntimeError("HHS_I047_GUEST_IDE_CLAIMS_FRONTEND_AUTHORITY")
    if vm.get("ok") is not True:
        raise RuntimeError("HHS_I047_GUEST_VM_API_NOT_READY")
    if vm.get("new_vm81_authority") is not False:
        raise RuntimeError("HHS_I047_GUEST_VM_CREATED_SECOND_VM81_AUTHORITY")
    return {"ide": ide, "application_vm": vm}


def configure(
    *,
    site: Path,
    snippet_source: Path,
    snippet_destination: Path,
    reload_nginx: bool = True,
    target: str = "guest",
) -> dict[str, object]:
    if not site.is_file():
        raise RuntimeError(f"HHS_I047_NGINX_SITE_MISSING:{site}")
    if not snippet_source.is_file():
        raise RuntimeError(f"HHS_I047_NGINX_SNIPPET_MISSING:{snippet_source}")

    health = verify_guest_transport() if target == "guest" else {}
    original_site = site.read_text(encoding="utf-8")
    updated_site, changed = patch_runtime_backend(original_site, target=target)

    original_snippet = (
        snippet_destination.read_text(encoding="utf-8")
        if snippet_destination.exists()
        else None
    )
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    site_backup = site.with_name(site.name + f".pre-hhs-i047-{stamp}")
    shutil.copy2(site, site_backup)

    snippet_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(snippet_source, snippet_destination)
    snippet_destination.chmod(0o644)

    if changed:
        temporary = site.with_name(site.name + ".i047.tmp")
        temporary.write_text(updated_site, encoding="utf-8")
        temporary.replace(site)

    try:
        if reload_nginx:
            subprocess.run(["nginx", "-t"], check=True)
            subprocess.run(["systemctl", "reload", "nginx"], check=True)
            subprocess.run(["systemctl", "is-active", "--quiet", "nginx"], check=True)
    except Exception:
        shutil.copy2(site_backup, site)
        if original_snippet is None:
            snippet_destination.unlink(missing_ok=True)
        else:
            snippet_destination.write_text(original_snippet, encoding="utf-8")
        subprocess.run(["nginx", "-t"], check=False)
        raise

    return {
        "schema": "HHS_PASS_220_I047_UNIFIED_GUEST_PROXY_RECEIPT_V1",
        "site": str(site),
        "site_backup": str(site_backup),
        "snippet": str(snippet_destination),
        "changed": changed,
        "target": target,
        "dynamic_backend": "127.0.0.1:18080" if target == "guest" else "127.0.0.1:8080",
        "application_vm_backend": "127.0.0.1:18720" if target == "guest" else "127.0.0.1:8720",
        "host_application_compute_authority": target == "host",
        "canonical_state_authority": False,
        "guest_health_verified": bool(health),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site")
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--snippet-destination", default=DEFAULT_SNIPPET)
    parser.add_argument("--no-reload", action="store_true")
    parser.add_argument("--target", choices=("guest", "host"), default="guest")
    args = parser.parse_args()

    repository_root = Path(args.repository_root).resolve()
    site = Path(args.site).resolve() if args.site else discover_site()
    snippet_source = (
        repository_root / "deployment/ubuntu/guest_runtime/nginx-hhs-unified-guest-vm.conf"
        if args.target == "guest"
        else repository_root / "deployment/ubuntu/application_vm/nginx-hhs-application-vm.conf"
    )
    receipt = configure(
        site=site,
        snippet_source=snippet_source,
        snippet_destination=Path(args.snippet_destination),
        reload_nginx=not args.no_reload,
        target=args.target,
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
