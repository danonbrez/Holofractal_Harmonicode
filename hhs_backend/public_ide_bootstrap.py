"""Serve the canonical IDE document with one non-blocking module authority."""
from __future__ import annotations

from pathlib import Path
import re

from fastapi.responses import HTMLResponse


LEGACY_PUBLIC_MODULES = (
    "production-startup-coordinator.mjs",
    "browser.mjs",
    "ux-default.mjs",
    "production-integration.mjs",
    "visual-ide.mjs",
)

INLINE_PUBLIC_BOOT = """\
<script data-hhs-inline-public-boot>
(() => {
  const moduleUrl = new URL('./src/production-startup-coordinator.mjs', window.location.href).href;
  const startedAt = performance.now();
  window.HHSInlinePublicBoot = Object.freeze({
    schema: 'HHS_INLINE_PUBLIC_BOOT_V2',
    module_url: moduleUrl,
    started_at_ms: Math.round(startedAt),
    legacy_parser_module_entries_disabled: true,
    frontend_is_authority: false,
  });
  import(moduleUrl).catch((error) => {
    const detail = {
      schema: 'HHS_INLINE_PUBLIC_BOOT_FAILURE_V1',
      module_url: moduleUrl,
      error: `${error?.name || 'Error'}: ${error?.message || String(error)}`,
      frontend_is_authority: false,
    };
    window.dispatchEvent(new CustomEvent('hhs:inline-public-boot:error', { detail }));
    console.error('HHS_INLINE_PUBLIC_BOOT_FAILED', detail);
  });
})();
</script>
"""


def _disable_legacy_module_entries(html: str) -> tuple[str, tuple[str, ...]]:
    """Remove duplicate parser-owned entries while preserving visible lineage."""
    disabled: list[str] = []
    for module_name in LEGACY_PUBLIC_MODULES:
        source_pattern = rf"(?:\./)?src/{re.escape(module_name)}"
        pattern = re.compile(
            rf"<script\b(?=[^>]*\btype\s*=\s*['\"]module['\"])(?=[^>]*\bsrc\s*=\s*['\"]{source_pattern}['\"])[^>]*>\s*</script>",
            flags=re.IGNORECASE,
        )
        replacement = f"<!-- data-hhs-legacy-module-disabled src=./src/{module_name} -->"
        html, count = pattern.subn(replacement, html)
        if count:
            disabled.extend([module_name] * count)
    return html, tuple(disabled)


def render_public_ide_index(asset_root: Path) -> HTMLResponse:
    """Return the IDE shell with exactly one repository-owned boot authority."""
    index_path = asset_root / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html, disabled = _disable_legacy_module_entries(html)
    missing = tuple(module for module in LEGACY_PUBLIC_MODULES if module not in disabled)
    if missing:
        raise RuntimeError(
            "public IDE legacy module entry contract changed; missing: " + ", ".join(missing)
        )

    if "data-hhs-inline-public-boot" not in html:
        marker = "</body>"
        if marker not in html:
            raise RuntimeError(f"public IDE index has no closing body marker: {index_path}")
        html = html.replace(marker, f"{INLINE_PUBLIC_BOOT}{marker}", 1)

    return HTMLResponse(
        html,
        headers={
            "Cache-Control": "no-store",
            "X-HHS-Public-Boot": "HHS_INLINE_PUBLIC_BOOT_V2",
            "X-HHS-Legacy-Module-Entries": "disabled",
        },
    )
