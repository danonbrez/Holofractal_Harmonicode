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
7. Do NOT rerun the failed deploy-exact-main job while the release
   block is active. The existing installer enables and starts the
   guarded-update timer BEFORE native, HTTPS and Chromium admission,
   violating the release freeze. Use the separately audited I088
   acceptance-only operator collector after the real host repair.
   It verifies HTTPS, Runtime OS registry and actual Chromium against
   the pinned release WITHOUT redeployment or timer reactivation.
8. Lift release block and resume feature merges/updater **only after**
   real native, HTTPS and Chromium evidence verifies the same source
   and the operator explicitly authorizes release resumption.

## Restart state and audit

- Previous repair PR HEAD: `af1da0f05f8a8ad4cee1ff05e1bb48c6fc412372`; merge target `main`.
- Change list: rename/re-pin operator script; replace restart record
  with the production failure evidence and safer nonpromoting acceptance-only route.
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


## I087 — guarded remediation checkpoint (2026-10-11)

**RELEASE BLOCKED. PR #769 MUST REMAIN DRAFT AND UNMERGED.**

- Production main and promoted-but-unaccepted source: 579dbb58f7f9d99419e73cb4d686901e6d123212.
- Repair branch: agent/production-native-causal-repair-20261011.
- Previous draft head: ae0e1e9c906f80ca27bb240bb8b68f2ec97e0513.
- Completed repair-only commit 58f0eee02e1107c1a765ec22b4474eb93ac21533:
  after BOTH exclusive locks, recheck host HEAD, main branch and clean tree;
  verify authoritative last-success.json promotion receipt contains exact
  matching candidate SHA, Runtime OS bundle SHA, and PROMOTED outcome
  before any dependency installation. Accept only four generated answers
  with four distinct 64-character response hashes, positive integer
  serialized-block counts, no per-turn errors and no mutation admission.
- Offline test commit ae0e1e9c906f80ca27bb240bb8b68f2ec97e0513:
  adds tests/pass220/test_hhs_pass220_native_causal_host_repair_audit_v1.py
  and .github/workflows/pass220-native-causal-host-repair-audit.yml.
  Uses no secrets, SSH, remote host, service mutation or deployment.
  Static audit CI: https://github.com/danonbrez/Holofractal_Harmonicode/actions/runs/38157319118
  passed. Source integrity:
  https://github.com/danonbrez/Holofractal_Harmonicode/actions/runs/38157319084
  (recheck conclusion for the final PR head).
- GitHub main branch protection could not be read (403 forbidden by
  integration). Documented release freeze is not proof of branch protection.
- Host SSH, production venv provision/import, genuine native generation,
  public HTTPS and Chromium have NOT been run by this agent.
  No technical acceptance or release unfreeze is asserted.
- The repair script remains
  scripts/production-native-causal-host-repair-579dbb58.sh and must be
  reviewed by exact commit SHA, then executed by an authorized operator
  against deployed SHA 579dbb58f7f9d99419e73cb4d686901e6d123212.
- After the real native CLI succeeds on host, do NOT replay the
  deployment job: it automatically enables hhs-guarded-update.timer.
  Use I088 public acceptance-only collector and fail-closed verifier
  with the pinned SHA, native and promotion receipts, strict TLS HTTPS,
  and actual Chromium. The release remains blocked until review.

NEXT ACTION: authorized production SSH and dependency installation;
then isolated HTTPS/Chromium acceptance without any new promotion. Fail closed on any SHA drift,
lock conflict, untrusted model provenance or undistinct response.

## I088 — fail-closed acceptance-only repair (2026-10-11)

**SUPERSEDES I086/I087 instructions to rerun deploy-exact-main.**
The preexisting production installer enables and starts the updater timer
in deployment/digitalocean/guarded_auto_update/install.sh lines 415-416.
The old exact-main workflow requires that timer active at line 502,
BEFORE native, HTTPS and Chromium acceptance. Replaying failed deploy
job 114457801946 during freeze would therefore violate incident #768.
Do not rerun that job until production acceptance and release clearance.

Added a separate operator-only evidence path on the still-UNMERGED
draft branch:
- scripts/collect_production_native_causal_acceptance_579dbb58.sh
- scripts/verify_production_native_causal_acceptance_579dbb58.py
- tests/pass220/test_hhs_pass220_i088_acceptance_evidence_v1.py

After authorized host operator executes the native venv/model repair
script under SSH and produces actual JSONL CLI and PROMOTED receipts,
copy those two artifacts to an authorized operator machine. This host
transfer is NOT performed by any connected tool.

Run the collector from the immutable reviewed draft script with
an independent clean checkout of pinned main HEAD
579dbb58f7f9d99419e73cb4d686901e6d123212. Before running,
install pinned playwright@1.55.0 and Chromium locally on the
operator machine; these are not automatically installed or changed
by the collector. Supply environment variables:
  HHS_I088_OPERATOR_APPROVED=YES
  HHS_PRODUCTION_BASE_URL=https://<production HTTPS host>
  HHS_I088_RELEASE_ROOT=<path to clean exact-main checkout>
  HHS_I088_NATIVE_CLI_RECEIPT=<copied host native JSONL>
  HHS_I088_PROMOTION_RECEIPT=<copied host last-success.json>
  HHS_I088_EVIDENCE_DIR=<absolute operator evidence output directory>
Run: bash scripts/collect_production_native_causal_acceptance_579dbb58.sh

The collector performs certificate-validated HTTPS requests without
curl -k, refuses browser ignoreHTTPS errors, and checks public Runtime
OS source SHA. Then it invokes existing Chromium end-to-end browser
suite, which intentionally exercises live app workflows and therefore
requires explicit operator approval. The separate Python verifier
requires four distinct real native serialized-block responses,
matching SHA and PROMOTED host receipt, correct public service registry,
six browser execution gates, no browser errors, and a real PNG screenshot.
It writes an evidence-hash JSON receipt only on success and NEVER
clears the release block or re-enables the updater automatically.

Offline fixtures are SYNTHETIC, useful only to test rejection logic.
CI passes are not proof of production recovery or browser operation.
No authenticated SSH or remote execution is available from connected
DigitalOcean/GitHub tools. Main remains frozen and feature merges blocked.
