# Exact-Main Post-Promotion SIGPIPE Repair Restart — 2026-10-05

## Restart identity

- repository: `danonbrez/Holofractal_Harmonicode`
- base/current main at repair start: `16d521b4db1ab701331ec4c6e550816df513db51`
- branch: `repair/exact-main-post-promotion-pipefail-20261005`
- merge target: `main`
- originating Exact-Main run: `37324980478`
- originating deploy job: `111813963795`

## Proven production state before this repair

The Exact-Main run for `16d521b4...` successfully completed the guarded updater
promotion itself. The host emitted a valid promotion receipt:

- candidate SHA: `16d521b4db1ab701331ec4c6e550816df513db51`
- previous SHA: `a908e987335983451371a1d61df8438a5b9bbe54`
- runtime bundle SHA: `16d521b4db1ab701331ec4c6e550816df513db51`
- outcome: `PROMOTED`
- detail: candidate and exact Runtime OS bundle activated and health-verified

The workflow then emitted `HHS_PRODUCTION_SERVICE_PERMISSIONS_VERIFIED=1` and
exited with code `141` before the local service-registry/public HTTPS/live
browser gates could execute.

Therefore this incident is not a failed promotion, rollback, lock collision, or
runtime-health failure. The current production source was promoted, but
post-promotion CI verification remained incomplete.

## Root cause

The remote Exact-Main shell uses `set -Eeuo pipefail`. Post-promotion assertions
used pipelines such as:

`systemctl cat hhs.service | grep -Fq ...`

and:

`systemctl show ... | grep -Fq ...`

When `grep -q` finds its match it can close the pipe before `systemctl` has
finished writing. The producer can then exit on SIGPIPE (`128 + SIGPIPE = 141`),
which `pipefail` promotes to a false workflow failure even though the assertion
matched.

## Repair

The workflow now captures complete `systemctl` output before matching it:

- `hhs_service_unit="$(systemctl cat hhs.service)"`
- `hhs_service_exec_start="$(systemctl show hhs.service -p ExecStart --value)"`
- `lane5_service_exec_start="$(systemctl show hhs-lane5-ingress.service -p ExecStart --value)"`

All `grep -Fq` checks consume shell here-strings instead of live producer
pipelines. This preserves strict `pipefail` while removing SIGPIPE
misclassification.

A regression in `tests/test_hhs_guarded_auto_update_contract_v1.py` forbids the
three unsafe `systemctl ... | grep -Fq` forms and requires the captured-output
forms.

## Branch commits

- `355597b065aa36a57d77b82cac63e70ad6d3c75f` — avoid post-promotion SIGPIPE false failures
- `695b340214e44f08bee7da0d606df70e7688085d` — prevent exact-main SIGPIPE assertion regression

## Validation done

- exact failure boundary located from completed deploy-job log;
- valid `PROMOTED` receipt confirmed before exit 141;
- failure occurs immediately after service-permission marker;
- all unsafe targeted pipelines absent from repaired branch source;
- all captured-output assertion forms present;
- prior PR #716 Exact-Main deployment-contract rerun `37324837601` was SUCCESS;
- source/browser acceptance code from PR #716 remains unchanged by this repair.

## Validation remaining

1. open repair PR;
2. require Exact-Main deployment-contract validation;
3. merge repair;
4. follow only the new current-main Exact-Main deployment;
5. require post-promotion local/public service registry verification;
6. require live Chromium capability gate;
7. require browser JSON/PNG evidence;
8. follow serialized Hash216 successor if one is generated;
9. require final current-main Exact-Main convergence.

## Next action

Open and validate the repair PR. Do not roll back the already promoted
`16d521b4...` production state merely because the post-promotion assertion was
misclassified.
