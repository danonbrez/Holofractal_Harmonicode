# Next Pass 048 — Authorized GUI Command Expansion and Live Mutation Receipts

Pass 047 established the request-only GUI command loop. Pass 048 should selectively promote safe commands from receipt-only mode into authorized execution mode.

Candidate work:

- define explicit authorized GUI command allowlist;
- bind each command to a kernel-derived composition plan;
- produce mutation receipts for commands that alter runtime state;
- distinguish preview, receipt-only, and authorized execution modes in the GUI;
- add rollback/undo visibility for authorized GUI commands;
- verify command result packets round-trip through WebSocket projection.
