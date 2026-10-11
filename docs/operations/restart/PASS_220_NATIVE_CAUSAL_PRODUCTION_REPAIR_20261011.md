# I086 production causal venv repair — restart record (2026-10-11)

**Release: BLOCKED. Draft PR #769. Do not merge into main, deploy a new SHA, reenable updater, or claim acceptance.**

## Authoritative source and execution scope

- GitHub main and latest production-promoted source: `579dbb58f7f9d99419e73cb4d686901e6d123212`.
- Latest exact-main failure: https://github.com/danonbrez/Holofractal_Harmonicode/actions/runs/38135224316
  (deploy job `114457801946`). Source promotion occurred, but four general-chat
  prompts produced the same `EXACT_SEMANTIC_FALLBACK` answer because
  `transformers` was unavailable. `response_block_count=null`,
  `distinct_response_count=1`; HTTPS and Chromium steps **skipped**.
- Earlier failed baseline `6c452d4abe80eff0c77f58a12b43f2902020b5b1`
  is historical only; it must not be force-restored to current production.
- DigitalOcean active droplet `hhs-production-04` ID `603583798`
  (`159.65.178.254`). Control plane reports active status but cannot prove
  live host checkout HEAD or invoke SSH.
- PR branch `agent/production-native-causal-repair-20261011` => main, **UNMERGED / DRAFT / operator-only**.
- Audited script: `scripts/production-native-causal-host-repair-579dbb58.sh`.
  Obtain this script only from the reviewed immutable repair commit; verify
  content before copying to the host. Do not fetch arbitrary branch tip.
- This patch removes the obsolete 6c452d4a repair script. Source
  files on production remain untouched by the repair script.

## Exact execution instructions for the authorized host operator

1. Freeze delivery merges and production promotions at the latest
   `579dbb58f7f9d99419e73cb4d686901e6d123212`. Confirm no concurrent exact-main workflow job. A GitHub
   issue saying "release blocked" is not technical branch protection.
2. Via authenticated production SSH, inspect `/opt/hhs/app` HEAD,
   which **must** equal the literal SHA `579dbb58f7f9d99419e73cb4d686901e6d123212` on clean `main`.
   The repair script checks this before installing anything. Never
   `reset`, `checkout`, `pull`, or bypass the guard to fit the script.
3. As root, run the reviewed script. It holds the exclusive production
   mutation lock, stops `hhs-guarded-update.timer` without reenabling it,
   rejects a running guarded update, and takes the guarded-update lock.
   Missing venv, changed HEAD, or lock collision fails closed.
4. Under `/opt/hhs/venv/bin/python`, invoke the existing canonical
   `tools/provision_native_causal_model.py --install`. Verify
   `transformers==4.57.6`, CPU-only `torch==2.14.1+cpu`,
   pinned SmolLM2-360M-Instruct model weight SHA-256, tokenizer/config,
   and imports as root and `hhs` service account.
5. Execute `tools/hhs_native_chat_cli.py --acceptance --strict-generation
   --json` as `hhs` using the live service's whitelisted native
   model/cache environment. Require exactly four distinct serialized-block
   replies with `generation_path=NATIVE_CAUSAL_LM_SERIALIZED_BLOCK_STREAM`,
   `response_block_count>0`, no fallback/failure, and
   `runtime_mutation_admitted=false`. Import-only success is insufficient.
6. Preserve the JSONL receipt emitted to
   `/var/lib/hhs/runtime-bootstrap/native-causal-579dbb58-recovery.jsonl`.
   **Do not lift release block here.**
7. With GitHub main still frozen at `579dbb58f7f9d99419e73cb4d686901e6d123212`, rerun ONLY the
   failed `deploy-exact-main` job `114457801946` for that exact SHA.
   Normal `origin/main==TARGET_SHA` checks remain intact: no
   historical-SHA workaround is necessary when main stays frozen.
   Require all native CLI, public HTTPS Runtime OS, service registry and
   real Chromium frontend steps to PASS (not skip), with exact SHA
   and production receipts. This rerun must not promote a *different* SHA.
8. Lift release block and resume feature merges/updater **only after**
   real native, HTTPS and Chromium evidence verifies the same source
   and the operator explicitly authorizes release resumption.

## Restart state and audit

- Previous repair PR HEAD: `af1da0f05f8a8ad4cee1ff05e1bb48c6fc412372`; merge target `main`.
- Change list: rename/re-pin operator script; replace restart record
  with latest deploy/acceptance evidence and valid exact-main rerun route.
- Already verified: GitHub source HEAD, failed job's four canned replies,
  active droplet via control-plane inspection.
- **NOT executed:** SSH, host provisioning, service import, model load,
  four real serialized generations, HTTPS, Chromium, exact-main rerun.
  The connected infrastructure actions cannot execute authenticated host
  commands, and GitHub connector lacks workflow dispatch. An authorized
  operator must run the audited script and collect those receipts.
- Failures during operator execution leave the release blocked and updater
  stopped; record exact failed command, pinned host HEAD and partial receipt
  before repair-forward.
