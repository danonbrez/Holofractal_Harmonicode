# Browser-Level Runtime Verification — Pass 046

Pass 046 adds `hhs_gui/scripts/live-gui-e2e-source-verify.mjs`, a dependency-free browser bundle path verifier. It checks that:

- `RuntimeSocketManager` captures live kernel fields.
- `LiveRuntimeProjectionPanel` renders all four channels.
- `RuntimeShell` mounts the live projection panel.
- Vite proxies `/api` and `/ws` to FastAPI.
- The frontend source does not contain Node demo runtime authority.

Executed:

```bash
cd hhs_gui && node ./scripts/live-gui-e2e-source-verify.mjs
```

Result:

```text
live-gui-e2e-source-verify: PASS
```

A full Playwright/Chromium run was not executed in this container because the browser runner dependencies are not bundled in the repository ZIP.
