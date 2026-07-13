# Browser Command E2E Verification — Pass 047

Pass 047 extends the source-level browser verification introduced in Pass 046.

Verified source path:

```text
RuntimeCommandPanel
  → RuntimeCommandClient
  → POST /api/runtime/gui/command
  → command authority result
  → WebSocket feedback is displayed by the existing live projection panel
```

The source verifier checks that:

- `RuntimeCommandPanel` is mounted by `RuntimeShell`.
- `RuntimeCommandClient` emits `HHS_LIVE_GUI_COMMAND_ENVELOPE_V1`.
- commands require admissibility.
- the command endpoint is `/api/runtime/gui/command`.
- the GUI command panel declares the request-only doctrine.
- Node/Vite remains a proxy and not a runtime event authority.

A dependency-free verifier is used because Playwright/Chromium dependencies are not bundled in the release ZIP.
