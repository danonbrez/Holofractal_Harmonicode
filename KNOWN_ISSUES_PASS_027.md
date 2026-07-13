# Known Issues — Pass 027

- Controlled live execution is intentionally limited to allow-listed self-test functions.
- Full repository pytest remains expensive in this environment because ledger/manifest generation accumulates large runtime artifacts.
- Future passes should add closure-harness coverage before expanding controlled live execution beyond self-tests.
