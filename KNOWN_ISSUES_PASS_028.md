# Known Issues — Pass 028

1. Pass 028 intentionally does not permit arbitrary plugin function execution.
2. `SELF_TEST_DELEGATE` is reserved for the Pass 027 controlled live executor and is not enabled in the read-only adapter yet.
3. The adapter does not yet expose a backend API route or GUI bridge method; this is recommended for Pass 029.
4. Full-suite pytest can be slow in this environment due to repeated ledger/manifest generation; targeted pass verification passed.
