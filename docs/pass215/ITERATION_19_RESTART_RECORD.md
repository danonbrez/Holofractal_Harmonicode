# Pass 215 Iteration 19 Restart Record

## Base authority

- parent closure head: `d89919b1010df0dda46e18cb43b4a6ef913a5615`
- parent closure tree: `2a74f697278e754b44998df4d5a3598750643a4a`
- branch: `agent/pass215-transformer-ingestion-benchmark`
- merge target: `main`
- draft PR: `#172`

## Implemented scope

Iteration 19 introduces a self-contained content-addressed checkpoint representation for the exact Iteration 18 resume state. It losslessly interns repeated symbolic strings, serializes large components deterministically, chunks at 1 MiB, compresses with zlib level 9, addresses uncompressed chunks by SHA-256, Hash216-binds the content-store manifest, reconstructs the original Iteration 18 checkpoint root, and resumes through the validated `TerminalHeadSymbolicDAG` path without forward replay.

The source workflow must establish the measured compact canonical size, compaction ratio, compact-checkpoint Hash216, content-store Hash216, compaction Hash216, suite/evidence roots, Hash72 receipt, cross-process equality, and exact inherited Iteration 18 semantic roots.

## Validation sequence

1. `bash scripts/run_pass215_iteration19_validation.sh`
2. verify authenticated `stories15M-q4_0.gguf` SHA-256
3. process A: four certified tokens → compact checkpoint → reconstruct Iteration 18 checkpoint → zero-replay restore → remaining three certified tokens
4. process B: independent identical execution
5. compare compact checkpoint, content store, compaction, suite, evidence, and receipt roots
6. bind source-run identities into the implementation record and this restart record
7. create one freeze commit
8. exact-head replay that frozen commit
9. do not create a post-validation commit

## Current state

Source execution pending. Any source failure must be repaired forward with its failed head/run retained in the implementation record rather than rewritten away.
