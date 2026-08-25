# Pass 219 I130 / inherited Pass 196 repair membrane — restart record

Status: `CENSUS COMPLETE — REPAIR AND MEMBRANE IMPLEMENTATION PENDING`

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass219-iteration130-pass196-repair-membrane`
- Intended target: `main`
- Frozen predecessor I129: `40e6e07d5f4a401541a6255339223e853846e713`
- Current authoritative main at branch creation: `634db40aaf57ec087b7353d6d9205d896622adb4`
- Historical Pass 196 implementation PR: `#128`
- Historical Pass 196 implementation head: `0142d9a6199f8acf9f23e287f471e6d80b9acd2a`
- Accepted Pass 196 implementation merge: `37687d479f2a9f1d996d225a4ba3556d9db72a86`
- Historical DigitalOcean topology repair PR: `#130`
- Accepted topology-repair merge: `959729c9070399fcdf0015702cd8777079e05dcc`
- Merge authorization: NOT GRANTED

## Classification

`INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE`

Historical PR #128 contains ten review findings. Current main independently repaired the service-state provisioning finding through `StateDirectory=hhs`; nine substantive findings remain reproducible in current source and require repair-forward treatment before Pass 196 can be exposed through the I130 C/C++ membrane.

## Historical review findings

- `3699626177` — direct runtime vector persistence can occur without validated VM81/Hash72 admission.
- `3699626180` — restart loses the persisted predecessor/object lineage and may create a second genesis branch.
- `3699626182` — test/evidence paths can satisfy executable-role classification and falsely mark a pass integrated.
- `3699626186` — browser registry projection is register-once and remains stale after later scan state changes.
- `3699626190` — canonical manifest identity contains host-specific repository root and worker count.
- `3699626194` — file bytes are hashed and then separately reread for classification, permitting race-incoherent evidence.
- `3699626196` — service state directory ownership/provisioning. CURRENT MAIN REPAIRED via `StateDirectory=hhs`.
- `3699626198` — tool `persist_vector` uses Python truthiness coercion instead of strict boolean validation.
- `3699626201` — failed rescan leaves prior closed manifest visible as current OK evidence.
- `3699626204` — tool invocation maps fewer scan failure classes than the direct `/scan` endpoint.

## Current-main observations

- `hhs_backend/runtime/hhs_pass196_integrated_environment_v1.py` retains historical blob `d2cff008db58a29bf27be20cb3547b9e0018f5e1`; the runtime review defects above remain present.
- `hhs_backend/api/pass196_integration_routes.py` retains historical blob `39bb09975bb0b23d5a5d7352b2cd578855fd6b7d`; boolean coercion and inconsistent scan-error mapping remain present.
- `applications/holofractal_harmonizer/src/pass196-integration.mjs` still registers the runtime object only when absent and does not update it after a scan.
- `deploy/digitalocean/hhs-pass196-integrated-environment.service` now contains `StateDirectory=hhs`, `/opt/hhs/app`, `127.0.0.1:8080`, and `/var/lib/hhs/pass196`; the provisioning/topology boundary is preserved.
- Open PR #141 contains later production-hardening work but is unmerged and is not treated as canonical inherited authority for I130.

## Required repair boundary

1. require exact validated Hash72 receipt input before any persistent vector admission;
2. restore persisted vector/predecessor lineage before appending after restart;
3. require non-test/non-evidence executable artifacts for `INTEGRATED` pass classification;
4. refresh the registered browser object after each scan/status change without granting browser mutation authority;
5. remove host-specific diagnostics from the canonical manifest identity while retaining them outside the hashed body;
6. observe/classify the exact same file bytes, failing or retrying if a live file changes during observation;
7. preserve the already-repaired systemd state-directory and DigitalOcean topology;
8. enforce strict boolean tool ingress for `persist_vector`;
9. quarantine current status on scan failure while retaining last-good evidence only as historical;
10. map equivalent scan failures consistently for direct and tool invocation routes.

## Authority boundary

I130 may expose repaired Pass 196 behavior but must not create candidate authority, canonical mutation authority, persistence authority outside inherited Pass 196 vector admission, a new Hash72 clock, C++ mutation authority, or VM81 mutation authority. Singleton VM81 admission remains inherited. Encrypted vector storage remains evidence/persistence and not source or mutation authority.

## Validation plan

- focused nine-finding repair regressions plus one service-state preservation regression;
- historical Pass 196 lifecycle regression;
- deterministic host-independent manifest replay;
- restart lineage continuation and failure quarantine;
- strict tool ingress/error parity;
- browser projection refresh syntax/behavior gate;
- exact C/C++ I130 membrane conformance;
- Pass043-derived membrane preflight;
- preserved I129/Pass197 successor membrane;
- exact and synthetic hosted seal against current main.

## Environment state

No local/private worktree is required for recovery. Repository-visible Git objects and GitHub Actions are the authoritative execution environment.

## Next action

Implement the nine remaining repairs on this branch, add focused regressions, then expose the repaired Pass 196 surface through the additive Pass 219 I130 C/C++/Python membrane. Commit bounded checkpoints, open a draft PR, and run dependency-scoped exact/synthetic validation. Do not merge without explicit authorization.

## Blockers

None known at census completion.
