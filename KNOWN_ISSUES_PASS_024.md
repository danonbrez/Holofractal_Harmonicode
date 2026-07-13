# Known Issues — Pass 024

- Capability plans are metadata-only and do not execute candidate functions.
- Function input/output schemas are inferred only at the argument-name level; dedicated semantic adapters must define authoritative schemas before live invocation.
- Risk flags are heuristic and intentionally conservative.
- GUI surfaces do not yet display the capability planner manifest.
- Full plugin execution remains blocked until adapter-specific closure-harness tests exist.
