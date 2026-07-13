# Runtime Surface Interposition Map — Pass 036

- `io.ingress` — all external/raw input entering the HHS runtime boundary
- `service_registry.dispatch` — all service handler dispatch attempts
- `plugin_adapter.invocation` — all guarded, dry-run, readonly, or authorized plugin adapter invocations
- `authorized_execution.call` — all allow-listed pure-function execution calls
- `srcg.selfsolve` — SRCG primitive execution and closure attempts
- `semantic_memory.write` — semantic memory commit/write operations
- `vector_cache.write` — receipt-backed vector cache mutation operations
- `persistence.write` — filesystem/export/persistence write operations
- `api.egress` — API response egress envelopes
- `websocket.broadcast` — websocket/runtime event egress broadcasts
