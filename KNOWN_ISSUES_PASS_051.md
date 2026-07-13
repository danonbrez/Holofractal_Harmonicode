# Known Issues Pass 051

- Providers are local deterministic stand-ins in this pass; real OCR/ASR/vision/model/device integrations are intentionally deferred.
- Provider invocation is wired as a receipt-producing fabric, not as unbounded external execution.
- Browser Playwright/Chromium automation remains dependency-deferred; source-level GUI verifier is used.
