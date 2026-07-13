# Node Proxy Runtime Boundary — Pass 046

Node/Vite remains GUI/proxy only.

```text
/api → http://127.0.0.1:8000
/ws  → ws://127.0.0.1:8000
```

Node may serve the UI and proxy connections. It may not generate runtime events, runtime ticks, receipts, graph projections, or transport state.
