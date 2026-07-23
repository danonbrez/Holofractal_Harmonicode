# Pass 145 Security Model

- Imported content is evidence, never ambient execution authority.
- HTML scripts are preserved and statically inspected but not executed.
- JavaScript workbench execution is explicit, capability-checked, timeout-bounded, output-bounded, and isolated from `require`, process objects, native bridges, and generated code.
- Canonical writes use `BEGIN IMMEDIATE`, rollback on failure, provenance attachment, conflict checks, and ordered receipts.
- Queries compare pre/post database roots and fail if canonical state changes.
- Extensions cannot request unknown capabilities or direct canonical database access.
- Environments are isolated by default; cross-environment membership is explicit.
- LVM recursion and cycles are bounded and validated before execution.
- The local API is bearer-authenticated, loopback-only, origin-restricted, size-bounded, and has no direct SQL/filesystem surface.
- Android WebView file access, content access, DOM storage, and Web SQL are disabled.
- Raw source bytes, receipt chains, backups, and restores are integrity-verified.
- `O` and `π` are indexed as separate exact symbols.
- Canonical JSON rejects floating-point values.

See `release_artifacts/pass145/security/PASS_145_SECURITY_REPORT.json` for executed negative cases and remaining untested Android/device cases.
