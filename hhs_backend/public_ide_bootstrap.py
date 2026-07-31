"""Serve the canonical IDE document with a non-blocking inline module launcher."""
from __future__ import annotations

from pathlib import Path

from fastapi.responses import HTMLResponse


INLINE_PUBLIC_BOOT = """\
<script data-hhs-inline-public-boot>
(() => {
  const moduleUrl = new URL('./src/production-startup-coordinator.mjs', window.location.href).href;
  const startedAt = performance.now();
  window.HHSInlinePublicBoot = Object.freeze({
    schema: 'HHS_INLINE_PUBLIC_BOOT_V1',
    module_url: moduleUrl,
    started_at_ms: Math.round(startedAt),
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


def render_public_ide_index(asset_root: Path) -> HTMLResponse:
    """Return the unchanged IDE shell plus one parsing-time boot launcher."""
    index_path = asset_root / "index.html"
    html = index_path.read_text(encoding="utf-8")
    if "data-hhs-inline-public-boot" not in html:
        marker = "</body>"
        if marker not in html:
            raise RuntimeError(f"public IDE index has no closing body marker: {index_path}")
        html = html.replace(marker, f"{INLINE_PUBLIC_BOOT}{marker}", 1)
    return HTMLResponse(
        html,
        headers={
            "Cache-Control": "no-store",
            "X-HHS-Public-Boot": "HHS_INLINE_PUBLIC_BOOT_V1",
        },
    )
