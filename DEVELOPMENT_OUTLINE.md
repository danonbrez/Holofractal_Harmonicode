# Development Outline

## Current Phase

The repository is in v1 release integration. Development is no longer open-ended feature exploration. Each pass should improve integration, verification, packaging, documentation, and usability while preserving the proprietary HHS authority model.

## Deterministic Pass Loop

1. Start from latest clean release ZIP.
2. Inspect current blockers and stale interfaces.
3. Patch only release-relevant issues.
4. Run available verification commands.
5. Update state/docs/schema requirements.
6. Package a clean ZIP and patch artifact.
7. Use architectural feedback only when implementation intent is genuinely ambiguous.

## Architectural Spine

```text
Universal Input Layer
  → type detection / normalization / schema validation
  → HHS kernel authority and invariant routing
  → C runtime + Python bridge execution
  → ML / NLP / semantic search / storage service layers
  → backend API + websocket projection
  → GUI runtime OS / IDE / assistant / tools
```

## Release Priority Order

1. Runtime boot and verification path.
2. Python ↔ C ABI bridge stability.
3. Backend app and websocket endpoint contract.
4. GUI runtime projection compatibility.
5. Semantic memory / database integration surface.
6. Packaging, installer, CI/CD, and release candidate docs.

## Engineering Rules

- Preserve kernel authority.
- Treat GUI state as projection only.
- Do not create new functions unless needed to connect or stabilize existing functionality.
- Prefer compatibility adapters over destructive rewrites during release consolidation.
- Every pass must leave an audit trail.
