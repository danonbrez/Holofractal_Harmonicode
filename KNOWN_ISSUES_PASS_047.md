# Known Issues — Pass 047

- The command authority loop is implemented in receipt-only mode by default. Authorized command execution can be widened later per operation.
- The browser E2E verifier is dependency-free source verification. A full Playwright/Chromium run remains pending until browser-runner dependencies are bundled or installed.
- Some aggregate make targets can exceed container timeout limits because they invoke prior live runtime, GUI, reachability, and conformance checks sequentially.
- Command history is bounded in memory; durable command-history persistence should remain compact-residue only if added later.
