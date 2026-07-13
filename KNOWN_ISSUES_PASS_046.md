# Known Issues — Pass 046

- Full Playwright/Chromium browser execution was not run in this container because the JS browser-runner dependencies are not bundled in the ZIP.
- The GUI projection panel is intentionally compact and diagnostic; richer graph/transport visualization can build on the same live store lanes.
- `tsc --noEmit` cannot run cleanly in this container without `node_modules` / React type packages installed; this is an environment dependency issue rather than a Pass 046 source-path failure.
