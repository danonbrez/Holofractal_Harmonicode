# HHS Legacy Service Validation Closure V1

## Status

This contract defines the repair-forward CI lifecycle for legacy linear service validation beneath the integrated Lane 5 system.

Source failure head: `f9aaa2d20a8f2269a5141828852b7953b787fafc`.

Closure branch: `pass220/legacy-service-closure-repair-20260926`.

## Invariant

A service validation that has passed on an accepted pull request is frozen as closed evidence until a later commit changes that service's declared dependency surface.

```
validated(service, closure_commit)
AND unchanged(dependency_surface(service), new_commit)
=> validation_status(service, new_commit) = INHERITED_CLOSED
```

A change that intersects the declared dependency surface reopens only the affected validation obligation:

```
touches(new_commit, dependency_surface(service))
=> REOPEN(service)
=> dependency_scoped_validation(service)
=> CLOSED | REPAIR_FORWARD
```

Validation obligations are never abandoned because they are historical. A failing inherited service is repaired forward or explicitly superseded by a declared upgrade/replacement path.

## Backward compatibility

For every non-superseded historical contract, the current integrated path must accept the legacy input semantics and reproduce the canonical prior result. Where the implementation redirects through Lane 5, compatibility remains exact at the authoritative egress/hash boundary.

A newer implementation may replace old machinery, but it must retain a direct path or adapter capable of processing the same admitted data and reproducing the prior canonical Hash72/Hash216 witness when that legacy contract remains authoritative.

## Lifecycle separation

Installation and compilation establish service capability, native linkage, compatibility adapters, exact replay, and closure receipts.

Startup is not installation or compilation. Startup loads the integrated downstream Lane 5 state and verifies current integrity/readiness; it does not linearly replay every historical service validation.

CI therefore proves legacy services in the closure pull request and subsequently reruns a service only when its workflow-declared dependency surface is touched.

## Queue policy

Legacy service workflows must:

- use dependency-scoped `pull_request.paths`;
- use dependency-scoped `push.paths` for `main` when exact-main replay is required;
- retain `workflow_dispatch` where manual replay is appropriate;
- cancel superseded runs on the same ref;
- avoid runner-only contexts before runner assignment;
- retain all existing substantive tests and exact compatibility/hash obligations.

The special Pass 166 validation relay remains branch-scoped because it writes evidence back to its dedicated relay branch; the Pass 165/166 dependency-scoped validation workflows provide the pull-request closure proof.

## Closure acceptance

This repair is closed only after the pull request executes the affected service workflows successfully. After merge, unchanged service dependency surfaces inherit that evidence rather than replaying on unrelated commits.

The central closure audit validates the workflow structure and emits a machine-readable receipt. It does not replace the substantive service workflows.
