# Pass 209 Restart Record

## Scope

Install and route the production HHS language hierarchy as:

1. Kimi K3 API primary agentic-swarm assistant;
2. LiteRT-LM Gemma 4 E2B local CPU fallback;
3. repository-native HHS AGI backend learning and optimization observer.

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base branch: `main`
- Base commit: `13025bbeccb0cd45ebfcf7151fa2bca9cfbb61ea`
- Working branch: `agent/pass209-kimi-k3-native-llm`
- Merge target: `main`
- Contract: `HHS-P209-KIMI-K3-AGENTIC-SWARM-LITERT-LM-GEMMA4-NATIVE-AGI-OPTIMIZER-DIGITALOCEAN`

## Implemented state

- Added a Kimi K3 OpenAI-compatible transport using `kimi-k3`.
- Added complete Kimi `reasoning_content`, assistant tool-call, and tool-result
  history preservation.
- Added bounded parallel HHS API tool execution with deterministic result order.
- Added Kimi-first and Gemma-fallback continuation over one shared witnessed
  conversation thread.
- Removed the repository-native provider from the user-facing fallback chain.
- Added a durable SQLite observation queue for the repository-native AGI.
- Added asynchronous noncanonical optimization proposal production.
- Repointed `/api/assistant` to the Pass 209 hierarchy.
- Added `/api/runtime/llm-orchestrator/*` status and evidence surfaces.
- Added a pinned LiteRT-LM 0.14.0 DigitalOcean installation.
- Added the pinned Gemma 4 E2B artifact and SHA-256 verification.
- Added systemd services for Gemma and the native optimization worker.
- Added an `hhs.service` preflight and guarded-update integration.

## Authority boundaries

- Kimi K3 and Gemma are capability providers only.
- The native AGI is an observer and proposal producer only.
- No provider may directly mutate VM81.
- No provider may directly commit Hash72 or Hash216.
- No provider may directly modify the repository.
- Optimization proposals require separate admission.
- If Kimi and Gemma are both unavailable, the turn closes without a synthetic
  native-provider answer.

## Required host inputs

- Existing DigitalOcean HHS deployment at `/opt/hhs/app`.
- Existing Python environment at `/opt/hhs/venv`.
- Existing `hhs` service account.
- Valid `MOONSHOT_API_KEY`.
- Outbound access to Moonshot and Hugging Face during installation.
- Sufficient disk for the 2.6 GB Gemma artifact and installation overhead.

## Validation planned

- Parse the Pass 209 contract JSON.
- Run shell syntax checks on all deployment scripts.
- Compile all new and modified Python files.
- Run Kimi multi-tool history preservation tests.
- Run Kimi-to-Gemma witnessed failover tests.
- Run native optimizer persistence and proposal tests.
- Run deployment contract tests.
- Import the production FastAPI app and verify route registration.
- Run selected inherited assistant regression tests.

## Physical deployment claim boundary

Repository implementation and CI validation do not configure a real Moonshot
secret, download the multi-gigabyte Gemma artifact, or mutate the DigitalOcean
host. Physical closure requires running:

```bash
cd /opt/hhs/app
git pull --ff-only origin main
read -rsp 'Moonshot API key: ' MOONSHOT_API_KEY
printf '\n'
sudo --preserve-env=MOONSHOT_API_KEY \
  bash deployment/digitalocean/llm/install.sh
unset MOONSHOT_API_KEY
```

Then retain:

- `/var/lib/hhs/pass209/PASS209_LLM_PREFLIGHT_RECEIPT.json`;
- `/api/assistant/health` output;
- `/api/runtime/llm-orchestrator/status` output;
- one Kimi-primary functional turn receipt;
- one bounded Gemma-fallback test receipt;
- one completed native optimization proposal witness.

## Next action

Run repository CI, repair any syntax or integration failures, merge only after
all dependency-scoped validation succeeds, then execute the installer on the
DigitalOcean host with the Moonshot secret supplied interactively.
