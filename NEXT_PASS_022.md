# Next Pass — 022

## Recommended Priority

Classify and integrate the highest-value orphan/plugin-ready modules into explicit categories.

## Candidate Work

1. Add an explicit module disposition registry:
   - integrate
   - plugin-ready
   - documented-only
   - deprecated
   - archived
2. Select the first high-value module cluster from `PLUGIN_READY`.
3. Wire that cluster through the guarded service registry/API/closure harness where appropriate.
4. Reduce orphan count without deleting architectural material.

## Rule

No source file should remain ambiguous. Every module must have a declared path into the runtime graph or an explicit reason for non-execution.
