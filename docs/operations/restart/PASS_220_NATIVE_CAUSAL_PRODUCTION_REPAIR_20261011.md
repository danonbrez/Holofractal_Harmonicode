# I086 — blocked production causal-model remediation (2026-10-11)

**Release state: BLOCKED. Do not merge or promote delivery changes.**
Issue: https://github.com/danonbrez/Holofractal_Harmonicode/issues/768

## Source lineage

- Authoritative failed production promotion: `6c452d4abe80eff0c77f58a12b43f2902020b5b1`.
- Deployment run: https://github.com/danonbrez/Holofractal_Harmonicode/actions/runs/38131417478
- Job `114446578371`: deployed bundle promoted; CLI native causal acceptance failed; HTTPS and Chromium steps skipped.
- Repair base main when repair branch created:
  `579dbb58f7f9d99419e73cb4d686901e6d123212`.
- Branch and merge target:
  `agent/production-native-causal-repair-20261011` => `main`
  **DRAFT PR ONLY; NO MERGE AUTHORIZED until blocker resolved.**
- Changed file:
  `scripts/production-native-causal-host-repair-6c452d4a.sh`.
- This record:
  `docs/operations/restart/PASS_220_NATIVE_CAUSAL_PRODUCTION_REPAIR_20261011.md`.

## Verified observations

1. DigitalOcean reports active `hhs-production-04` droplet ID `603583798`,
   IP `159.65.178.254`; this is the SSH host configured by the
   production workflow.
2. The failed job's CLI generated four identical responses:
   `generation_path=EXACT_SEMANTIC_FALLBACK`,
   `response_block_count=null`, `distinct_response_count=1`,
   `NativeCausalLMNotReady: transformers is unavailable`.
3. The core `requirements.txt` does **not** pin transformers or Torch.
   `requirements-native-causal-lm.txt` pins `transformers==4.57.6`
   and the existing pinned provisioner separately requires CPU-only
   `torch==2.14.1+cpu` from PyTorch CPU index. The provisioner also
   verifies exact model weight SHA-256, tokenizer, config, and hhs access.
4. The previous workflow's `origin/main == TARGET_SHA` comparison
   means rerunning the historical 6c452d4a deployment job is presently
   fail-closed as **stale** because remote main advanced. Never force
   `main` backward or dilute normal current-main promotion checks.

## Executed work

- Fetched original exact-main GitHub Actions evidence and source scripts.
- Inspected the active production DigitalOcean droplet with control-plane
  APIs only; **no remote SSH/console execution is available through the
  connected DigitalOcean actions.**
- Opened release-blocking issue #768.
- Created unmerged, auditable repair script on separate branch.
- Read static script content and confirmed pin, venv, version checks,
  native acceptance, locks and fail-closed timer behavior.
- **NOT executed:** host pip/provisioner, service-user import, model load,
  native generation, exact historical deployment rerun, HTTPS, Chromium.

## Operator next action (under the pinned SSH authority)

1. Review `scripts/production-native-causal-host-repair-6c452d4a.sh`
   before using it on `hhs-production-04`. It requires current
   **deployed** `/opt/hhs/app` HEAD be exactly `6c452d4a`;
   if host HEAD is different, STOP rather than checking out or modifying
   a different revision.
2. Run it as root under real host SSH, with no competing production
   workflow. The script stops the unattended updater timer and keeps it
   stopped after installation; obtains both production mutation and
   guarded updater locks; provisions pinned CPU-only causal model through
   existing canonical installer; checks interpreter and hhs-user imports;
   and requires four distinct real serialized-block generations.
3. Record the receipt emitted under
   `/var/lib/hhs/runtime-bootstrap/native-causal-6c452d4a-recovery.jsonl`.
   Never treat green imports alone as generation success.
4. Design an **audited historical-SHA acceptance replay** that targets
   the already-promoted 6c452d4a bundle, keeps current main and its
   normal promotion guard intact, then runs public HTTPS and actual
   Chromium tests with pinned SHA and service registry. The old
   exact-current-main workflow is unsuitable for a historical pin.
5. Do not resume delivery or re-enable updater timer until all of
   generation, HTTPS, Chromium and SHA/receipt checks pass.

## Blocking conditions

- No authenticated remote-command tool among connected DigitalOcean
  controls; requires operator execution with existing pinned SSH secrets.
- Prior deployed host is missing `transformers`; no current import proof.
- Later GitHub main moved beyond the target SHA; ordinary rerun is stale.
- No current browser screenshot, HTTPS response, or distinct native
  serialized generation receipt.

## Acceptance conditions

`/opt/hhs/venv` exact package versions and CPU-only Torch,
pinned local native model load, real four distinct serialized-block
outputs (no fallback or runtime mutation), successful public HTTPS and
Chromium capability verification at the exact pinned bundle, intact
VM81/Hash72/Hash216 admission and provenance.
