# Visual IDE project-capability preservation — November 2026

## Observed existing behavior

`applications/holofractal_harmonizer/src/project-lifecycle.mjs` already implements conventional browser-based file/folder selection, source editing, build orchestration through the established backend, project manifest creation, and ZIP export. Its prior build path rejected projects having more than **64 files** or more than **24 MiB of source bytes**, before the backend was called. Those were frontend eligibility rules, not native VM81 or Lane 5 workload limits.

This patch removes those two synthetic eligibility gates, retaining the checks for a nonempty file set and requested compiler targets. It changes no VM81, signed admission, Hash72, Hash216, or backend implementation.

## Precise remaining boundaries

- The browser worktree currently stores complete files through in-memory JavaScript state and localStorage; this is **not yet** an unrestricted native file-workspace implementation.
- `addBrowserFiles` and `importFolder` currently call `file.arrayBuffer()`, making complete per-file copies in browser RAM; arbitrary-length native processing does not eliminate this frontend transport/materialization gap.
- The existing `project-zip.mjs` creates an in-memory **classic ZIP** archive and explicitly limits its entries to 65,535. It also serializes classic 32-bit sizes and offsets. To support larger archives, use ZIP64 or a conventional streamed archive facility, preserving byte-exact original files. These ZIP representation constraints are not project acceptance constraints and must not be used to justify reinstating 64/24 MiB gates.
- The project build invokes JSON/base64 ingress endpoints, which may be restricted by adapter-specific request buffering or backend limits until the Lane 5 streaming successor is integrated. See PR #914; do not describe that PR as merged or deployed without evidence.
- A successful source-level or Node test proves no synthetic *preflight* file-count/size rejection. It does **not** prove a 25 MiB end-to-end backend compile, full browser-memory behavior, arbitrary-size ZIP export, or signed VM81 admission.

## Further functional acceptance

Test real project creation, folder import, save/reopen, source encoding fidelity, build and compile, Ubuntu PTY, debugging, Git, native knowledge retrieval, agent sessions, and ZIP64/streaming egress against the **existing** Runtime OS. Reuse the existing HHSWorkspaceShell, Pass185 TerminalPanel, I043 Ubuntu guest PTY, agent services, and VM81 control plane before implementing a new UI subsystem.

The governing architectural contract is conventional IDE/application capability preservation with native constraints enforced at their real runtime boundaries.
