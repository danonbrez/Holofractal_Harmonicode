# KNOWN ISSUES — PASS 007

## Open containment work

- Websocket packets still need explicit gateway wrapping or a documented streaming receipt policy.
- Graph/replay/prediction routes still need gateway wrapping.
- Sandbox routes still need gateway wrapping.
- Filesystem import/export paths still need gateway wrapping.
- Semantic memory and multimodal embedding writes still need explicit validated vector-cache integration.
- GUI consumers may need adaptation to guarded response envelopes.

## Existing open items

- GUI TypeScript build still requires `npm install`; dependencies are not bundled in the ZIP.
- C runtime builds with existing warnings in demo/native initializer code.
- More modules need orphan-path classification: guarded service, gateway route, diagnostic, archived, or deprecated.
