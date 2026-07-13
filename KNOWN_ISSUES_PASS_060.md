# Known Issues — Pass 060

- Recovery records are deterministic in-process Runtime objects; durable cross-process recovery journals remain a later storage integration concern.
- Exactly-once applies to canonical admission and effect identity under the witnessed idempotency contract; external non-idempotent side effects require provider-specific compensation contracts.
