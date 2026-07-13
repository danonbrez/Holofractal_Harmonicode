# Live Runtime Workflow — Pass 045

The live workflow runs in FastAPI startup and owns the live kernel event stream.

```text
startup
→ runtime emulator boot
→ graph substrate init
→ websocket router init
→ live FastAPI workflow start
→ background kernel tick loop
→ canonical runtime event emission
```

Health/status endpoints expose bounded summaries so live status does not rebuild the entire conformance graph on every poll.
