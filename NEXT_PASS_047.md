# Next Pass 047 — Live Runtime Action Dispatch from GUI

Pass 047 should add guarded GUI-originated runtime actions:

```text
GUI action request
→ FastAPI action endpoint
→ zero-bypass interposer
→ runtime constraint enforcement
→ kernel-derived composition cache
→ authorized execution / tick / service dispatch
→ receipt
→ live websocket projection back to GUI
```

The GUI should be able to request a kernel tick, service self-test, replay query, and graph refresh without becoming runtime authority.
