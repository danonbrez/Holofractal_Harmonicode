# Next Pass 044 — Runtime Garbage Collection and Ledger Pruning Scheduler

Recommended next milestone: schedule automatic cleanup of expired expanded-state handles, compact old validated residues, and prune ledger views into rolling bounded checkpoints while preserving Hash72/u^72 reconstruction roots.

Focus areas:

1. background GC scheduler for expired expanded states,
2. rolling ledger checkpoint roots,
3. reconstruction-on-demand cache hydration,
4. performance budget enforcement in CI,
5. GUI status for metadata metabolism and decay events.
