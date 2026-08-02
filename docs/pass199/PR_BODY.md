# Pass 199 publication summary

Implements durable distributed execution of Pass 198 calibration trees through the verified Pass 190 Iteration 7 worker fabric.

Key properties:

- two durable branch jobs per parameter state;
- immutable exact candidate computation outside the authority lock;
- claim, capability, worker, lease, and candidate-Hash72 validation on completion;
- canonical ordinal serialization;
- one singleton `calibration.commit_tree` operation;
- cancellation, retry, stale-worker recovery, and process restart support;
- complete independent replay;
- Pass 198 proof-carrying simplification integration;
- no automatic compiler or runtime promotion.

The exact workflow is authoritative for validation. No DigitalOcean or Vercel mutation is included.
