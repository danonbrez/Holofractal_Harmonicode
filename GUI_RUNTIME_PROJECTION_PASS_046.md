# GUI Runtime Projection — Pass 046

The GUI renders live kernel state through four explicit websocket channels.  It displays channel health, sequence id, kernel tick, receipt hash, runtime state hash, event hash, packet age, and payload keys.

A live GUI state is valid only when it is traceable to a FastAPI kernel packet with:

```text
event_type
channel
sequence_id
kernel_tick
event_hash72
receipt_hash72
runtime_state_hash72
authority
payload
```

Failure states are explicit:

```text
REJECT_GUI_SYNTHETIC_RUNTIME_PACKET
REJECT_GUI_STATE_WITHOUT_KERNEL_PACKET
REJECT_NODE_GENERATED_RUNTIME_EVENT
REJECT_WEBSOCKET_PACKET_WITHOUT_RECEIPT
REJECT_CHANNEL_SEQUENCE_DRIFT
REJECT_STALE_GUI_RUNTIME_STATE
```
