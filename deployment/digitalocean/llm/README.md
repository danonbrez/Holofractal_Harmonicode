# Pass 210 DigitalOcean Production LLM Hierarchy

Pass 210 makes the existing `/api/assistant` surface use one cumulative,
governed provider hierarchy:

1. **Kimi K3 API** — primary agentic-swarm language and tool-planning provider.
2. **LiteRT-LM Gemma 4 E2B** — local CPU fallback served only on
   `127.0.0.1:9379`.
3. **Repository-native HHS AGI** — durable backend learning and optimization
   observer. It does not replace either user-facing provider.

No language provider owns VM81, Hash72, Hash216, repository mutation, deployment,
or canonical state. Provider output passes through the existing proposal,
capability-policy, invocation-receipt, and result-ingress path.

## Resource requirements

The pinned Gemma fallback artifact is approximately 2.6 GB. Allow additional
space for the dedicated LiteRT-LM virtual environment, model registry, temporary
download, runtime cache, and logs. A production host should have at least:

- 4 CPU cores;
- 16 GB RAM;
- 12 GB free disk before installation;
- outbound HTTPS access to the Moonshot API and Hugging Face during install;
- an existing `/opt/hhs/app` checkout and `/opt/hhs/venv`;
- the `hhs` service account;
- a valid Moonshot API key.

The Gemma fallback deliberately uses the CPU backend during ordinary development.
The temporary Pass 208 GPU is still reserved for the final hydration-training
and calibration stage.

## Installation

Update the repository first:

```bash
cd /opt/hhs/app
git fetch origin main
git checkout main
git pull --ff-only origin main
```

Run the installer without writing the secret into shell history where possible:

```bash
read -rsp 'Moonshot API key: ' MOONSHOT_API_KEY
printf '\n'
sudo --preserve-env=MOONSHOT_API_KEY \
  bash deployment/digitalocean/llm/install.sh
unset MOONSHOT_API_KEY
```

The installer performs all of the following:

- validates Pass 210 Python and shell sources;
- creates `/opt/hhs/litert-lm` as a dedicated virtual environment;
- installs `litert-lm==0.14.0`;
- imports `gemma-4-E2B-it.litertlm` as `gemma-4-E2B-it`;
- verifies SHA-256
  `181938105e0eefd105961417e8da75903eacda102c4fce9ce90f50b97139a63c`;
- installs the local LiteRT-LM systemd service;
- installs the native-AGI optimization worker;
- writes `/etc/hhs/pass210-llm.env` as `root:hhs` mode `0640`;
- adds an `hhs.service` drop-in requiring the local fallback preflight;
- validates that the configured Kimi model is registered;
- restarts the complete hierarchy and verifies the hosted assistant health.

The Moonshot key is stored only in the root-owned host environment file. It is
never added to the repository, receipts, status payloads, or logs.

## Services

```text
hhs-litert-lm-gemma4.service
        │
        ▼
hhs.service  →  /api/assistant
        │
        ▼
hhs-native-agi-optimizer.service
```

The local fallback starts before HHS. The optimizer starts after HHS and consumes
only the durable post-turn observation queue.

## Verification

```bash
sudo systemctl status \
  hhs-litert-lm-gemma4.service \
  hhs.service \
  hhs-native-agi-optimizer.service \
  --no-pager --full

curl -fsS http://127.0.0.1:9379/v1/models | python3 -m json.tool
curl -fsS http://127.0.0.1:8080/api/assistant/health | python3 -m json.tool
curl -fsS http://127.0.0.1:8080/api/runtime/llm-orchestrator/status | python3 -m json.tool
curl -fsS http://127.0.0.1:8080/api/runtime/llm-orchestrator/optimizer/status | python3 -m json.tool

sudo cat /var/lib/hhs/pass210/PASS210_LLM_PREFLIGHT_RECEIPT.json
```

A healthy Kimi-first response contains:

```text
effective_mode = KIMI_K3_AGENTIC_SWARM_API
fallback_used = false
native_agi_is_user_facing_provider = false
native_agi_observation_root_hash72 = <72-character witness>
```

During a Kimi outage, a healthy local fallback response contains:

```text
effective_mode = GEMMA4_LITERT_LM_FALLBACK
fallback_used = true
native_agi_is_user_facing_provider = false
```

## Functional smoke test

```bash
thread_id=$(
  curl -fsS -X POST http://127.0.0.1:8080/api/assistant/threads \
    -H 'content-type: application/json' \
    -d '{"project_id":"project:production-smoke","title":"Pass 210 smoke"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["thread"]["thread_id"])'
)

curl -fsS -X POST \
  "http://127.0.0.1:8080/api/assistant/threads/${thread_id}/messages" \
  -H 'content-type: application/json' \
  -d '{"content":"Inspect the current HHS runtime state and report only witnessed evidence."}' \
  | python3 -m json.tool
```

## Failover test

Do not delete the key. Temporarily block the primary only for a bounded test:

```bash
sudo cp /etc/hhs/pass210-llm.env /etc/hhs/pass210-llm.env.test-backup
sudo sed -i 's#^HHS_KIMI_K3_BASE_URL=.*#HHS_KIMI_K3_BASE_URL=http://127.0.0.1:9/v1#' \
  /etc/hhs/pass210-llm.env
sudo systemctl restart hhs.service

curl -fsS http://127.0.0.1:8080/api/assistant/health | python3 -m json.tool
```

Restore immediately:

```bash
sudo mv /etc/hhs/pass210-llm.env.test-backup /etc/hhs/pass210-llm.env
sudo chown root:hhs /etc/hhs/pass210-llm.env
sudo chmod 0640 /etc/hhs/pass210-llm.env
sudo systemctl restart hhs.service
```

## Native optimization evidence

The observer stores bounded turn evidence and hashes provider reasoning instead
of duplicating raw reasoning into the optimization database. Its proposals are
noncanonical and require separate admission.

```bash
curl -fsS \
  'http://127.0.0.1:8080/api/runtime/llm-orchestrator/optimizer/observations?limit=10' \
  | python3 -m json.tool

curl -fsS \
  'http://127.0.0.1:8080/api/runtime/llm-orchestrator/optimizer/proposals?limit=10' \
  | python3 -m json.tool
```

The optimizer is intentionally not a third conversational fallback. If both
Kimi K3 and Gemma 4 are unavailable, the assistant closes the turn with an
explicit provider-unavailable result rather than fabricating a response.

## Guarded updates

When the guarded DigitalOcean updater is installed, the Pass 210 installer
changes its ordered units to:

```text
hhs-litert-lm-gemma4.service hhs.service hhs-native-agi-optimizer.service
```

Candidate promotion must preserve the Gemma registry, Pass 210 preflight,
assistant health, and native optimizer importability. The model file remains in
`/var/lib/hhs/litert-lm` and is not redownloaded for ordinary source updates.

## Recovery

```bash
sudo journalctl \
  -u hhs-litert-lm-gemma4.service \
  -u hhs.service \
  -u hhs-native-agi-optimizer.service \
  -n 400 --no-pager

sudo systemctl restart hhs-litert-lm-gemma4.service
sudo /usr/local/lib/hhs-llm/hhs-llm-preflight.sh
sudo systemctl restart hhs.service hhs-native-agi-optimizer.service
```

If Kimi is unavailable but Gemma is healthy, HHS remains usable in explicit
fallback mode. If Gemma is unavailable, repair the local model service before
claiming installation closure.
