# NEXT PASS — 023

## Recommended Priority

Guarded legacy adapter registry.

## Goal

Convert selected `PLUGIN_READY` module groups into adapter descriptors that can be reached through the service registry without executing arbitrary legacy code directly.

## Candidate Groups

1. semantic/database/NLP modules
2. runtime AI/agent/governor modules
3. backend runtime projection modules
4. mobile GUI runtime console bridge
5. developer tools/plugin SDK candidates

## Required Rule

No plugin-ready module may become executable until it has:

```text
canonical adapter descriptor
→ runtime contract
→ Hash72/u⁷² witness
→ foundational conformance
→ guarded service/API/GUI entrypoint
```
