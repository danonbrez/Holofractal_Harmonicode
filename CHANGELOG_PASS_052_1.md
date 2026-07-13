# Changelog — Pass 052.1

- Repaired the Pass 052 reporting boundary without altering document-perception semantics.
- Added a committed reachability manifest and committed conformance snapshot as the sole canonical report inputs.
- Added typed metrics with `AVAILABLE` / `UNAVAILABLE` state.
- Made JSON authoritative and Markdown a deterministic projection of the same report object.
- Removed zero-default behavior for unknown derived metrics.
