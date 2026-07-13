# Changelog — Pass 045

- Added live kernel event bridge from real emulator ticks to canonical runtime event envelopes.
- Added FastAPI live workflow lifecycle.
- Mounted canonical websocket router on the main backend server.
- Added `/api/runtime/live/status` and `/api/runtime/live/tick`.
- Deprecated the standalone websocket stub and replaced it with a FastAPI compatibility launcher.
- Added bounded live status summaries to avoid repeated full conformance rebuilds.
- Added tests for live kernel events, websocket channel requirements, and Node proxy-only role.
