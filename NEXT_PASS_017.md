# Next Pass — 017

Recommended priority: runtime event/dataflow + persistence kernel witness unification.

Objectives:

1. Replace remaining high-risk surface-level `hash72_digest` usage in runtime dataflow/event/persistence guards with kernel-backed helpers.
2. Add full kernel witnesses to event, websocket/broadcast, and persistence contract records.
3. Add a migration audit listing all remaining direct `hash72_digest` imports and classify them as:
   - kernel authority surface,
   - legacy internal projection,
   - safe non-authority helper,
   - must migrate.
4. Keep all changes additive and compatibility-preserving.
