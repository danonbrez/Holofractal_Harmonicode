# Pass 219 Exact-Main Production Closure — 2026-09-08

## Status

**CLOSED**

Exact production target:

`73652c122ffff6a8b9bde9de00020610964d704c`

Production host:

`165.227.220.193`

## Closure evidence

The exact-main recovery completed successfully for `73652c122ffff6a8b9bde9de00020610964d704c`.

Verified closure surfaces:

- writable persistent runtime state;
- healthy `hhs.service` and guarded-update service/timer surfaces;
- production checkout at `/opt/hhs/app` clean and on `main` with exact deployed `HEAD` matching the required main payload;
- public HTTPS Runtime OS reachable and serving the production Runtime OS surface;
- a real production assistant turn completed successfully with sealed receipts;
- the prior SQLite/fresh-host startup blocker is closed.

The replacement production host remains the authority surface recorded by the fresh-host bootstrap record. The previous floating IP `137.184.223.84` remains reserved/unattached and is not the live production target.

The trusted SSH host-key evidence remains the audited Ed25519 fingerprint already recorded in the repository bootstrap receipt. Runtime host-key discovery remains forbidden.

The exact successful closure Actions run identifier was not recovered into this record; no run identifier is invented here. The production-state facts above are the accepted closure evidence for this checkpoint and should be augmented with the exact run identifier if it is later recovered from GitHub Actions history.

## Production-hardening cleanup

The recovery branch has been converted from a one-shot exact-SHA recovery vehicle into mergeable production hardening:

- removed the temporary recovery-branch push trigger;
- restored normal production authority to `TARGET_SHA=${{ github.sha }}`;
- removed the temporary SSH reachability diagnostic workflow;
- retained fail-closed `HHS_DIGITALOCEAN_KNOWN_HOSTS` authority;
- retained `StrictHostKeyChecking=yes`;
- retained explicit `UserKnownHostsFile`;
- retained `UpdateHostKeys no`;
- retained explicit verification that the pinned known-hosts file contains the configured production host;
- retained exact checkout and guarded promotion semantics.

No runtime `ssh-keyscan` trust discovery is permitted by the hardened workflow.

## Repository restart surface

Base exact main at production closure:

`73652c122ffff6a8b9bde9de00020610964d704c`

Recovery/hardening branch:

`agent/pass219-exact-main-73652c12-ssh-pinning-recovery-20260908`

Pull request:

`#411`

Branch state immediately before this closure record was created:

`77d43eb20417da17169e7019d48b25dc464fe0a2`

The branch contains the permanent pinned-host-trust production hardening and this closure receipt. Historical failure/recovery documents remain unchanged as evidence of the earlier blocked states.

## Validation and merge gate

At the pre-record branch head, GitHub reported 14 check runs and no failing or in-progress check run was observed in the bounded inspection. Some event-inapplicable jobs were correctly skipped. Repository branch-protection status checks could not be enumerated through the installed GitHub integration because the branch-protection endpoint returned `403 Resource not accessible by integration`; repository rulesets were empty.

Therefore the merge gate remains:

1. validate this closure-record head after the documentation commit;
2. require no failed or still-running required/triggered checks on the current PR head;
3. mark PR #411 ready for review;
4. merge production hardening to `main`;
5. verify `main` contains pinned-host-trust hardening and no temporary recovery routing/diagnostic workflow;
6. only then advance PR #412 integration work.

## Next action

After PR #411 is merged and verified on `main`, refresh PR #412 against the new main head. Restore the immutable exact-v1.1 source blob or introduce a separately versioned ABI successor, repair the portable Pass 168 exact arithmetic path without a required `__int128` dependency or float fallback, and rerun the cumulative validation suite.
