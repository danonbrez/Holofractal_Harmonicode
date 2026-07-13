# Known Issues — Pass 057

- Consensus is deterministic and repository-local; transport and clock synchronization remain outside this pass.
- Partition evidence uses sequence witnesses rather than wall-clock trust.
- Recovery preserves stale remote results as noncanonical evidence; automatic semantic merge is intentionally excluded.
