# GUI Command Authority Loop — Pass 047

Pass 047 closes the live runtime loop without giving the frontend authority over the runtime.

## Authority boundary

```text
Browser / GUI: request-only
FastAPI: command intake and policy enforcement
Kernel/composition stack: admissibility authority
WebSocket bridge: feedback projection
GUI store/panels: display only
```

## Command lifecycle

```text
HHS_LIVE_GUI_COMMAND_ENVELOPE_V1
  → HHS_LIVE_GUI_COMMAND_CONTRACT_V1
  → zero-bypass interposition token
  → kernel-derived composition preflight
  → runtime constraint enforcement decision
  → command decision hash72
  → live kernel feedback event
  → GUI projection update
```

## Explicit non-authority rule

The GUI must not update runtime truth optimistically after a button press. Runtime panels update from received kernel/WebSocket packets only.
