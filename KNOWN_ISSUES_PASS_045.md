# Known Issues — Pass 045

- Live runtime loop is intentionally conservative and emits one kernel tick per interval.
- WebSocket client integration should be exercised in a browser session in the next pass.
- Full end-to-end GUI assertions are not yet automated.
- The FastAPI server is authoritative, but deployment scripts may still need environment-specific tuning.
