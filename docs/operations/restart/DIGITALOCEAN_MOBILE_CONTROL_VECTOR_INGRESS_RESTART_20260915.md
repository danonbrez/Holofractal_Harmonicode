# DigitalOcean Mobile Control + Vector Ingress Restart — 2026-09-15

## Restart identity

- Base exact main: `a8fc0646e21b2a67804468575f364fef1762ec6a`
- Branch: `agent/digitalocean-mobile-control-ingress-20260915`
- Pull request: `#466` — `Repair DigitalOcean mobile control, multimodal vector ingress, and SSH trust`
- Merge target: `main`
- Implementation checkpoint: `b24aa08bf03bd196b829917ebecdaa7126d5900e`
- First sealed restart head: `106687909d594edc3634befd4d2c301e55caf493`
- Production-root verifier repair: `5ff3751a29a96a2211324f78e3a4505f3bb188a2`

## Production environment observed

DigitalOcean account state:

- Droplet: `hhs-production-01`
- Droplet id: `598826630`
- Region: `nyc3`
- Public IPv4: `165.227.220.193`
- Size: `s-2vcpu-4gb-120gb-intel`
- State: active
- Created: `2026-09-08T19:11:12Z`
- Backups and monitoring enabled.

Previous production droplet resource `589036816` was destroyed earlier on `2026-09-08`. A stale pinned SSH host key from the previous host is therefore a plausible deployment failure mode.

Registered DigitalOcean SSH public keys:

- `hhs-github-actions-deploy` — id `59207482`, fingerprint `39:90:66:80:df:d1:82:f8:93:82:a0:c4:fb:be:e3:ef`
- `hhs-phone` — id `58136400`, fingerprint `91:64:cf:1c:46:35:24:62:7a:5b:bb:87:09:d8:03:44`

GitHub repository secrets are intentionally unreadable through the repository API, so this checkpoint does not claim that the deploy private key or pinned known-hosts secret is current. The deployment workflow now distinguishes those cases without weakening SSH verification.

## Changed files

1. `.github/workflows/digitalocean-production-main.yml`
2. `.github/workflows/digitalocean-mobile-control-ingress.yml`
3. `hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx`
4. `hhs_gui/runtime_os/workspace/HHSProductWorkspace.tsx`
5. `hhs_gui/runtime_os/workspace/WorkspaceCommandClient.ts`
6. `hhs_gui/scripts/live-gui-e2e-source-verify.mjs`
7. `hhs_gui/scripts/workspace-source-verify.mjs`
8. `docs/operations/restart/DIGITALOCEAN_MOBILE_CONTROL_VECTOR_INGRESS_RESTART_20260915.md`

## Implemented behavior

### Mobile application server surface

The public HHS Runtime OS defaults to a mobile-first `Control` surface while preserving `Visual Program`, `Workspace`, and `Authority` as click-through surfaces.

The control surface exposes runtime health, Pass 174 persistent-vector-store health, current project identity, multi-file selection, local file preview for text/source/code/JSON/YAML/CSV/PDF/image/audio/video, bounded binary ingress, governed Pass 174 ingestion, and persisted Hash216 vector readback when a continuation operation key is available.

Exact source bytes are read with `File.arrayBuffer()`, base64 encoded, and sent to `/api/v1/pass174/sdlc/run`. The inherited route continues through the established development lifecycle and Pass 174 `PersistentEncryptedVectorStore`. Readback uses `/api/v1/pass174/hash216/query`, not the lightweight workspace semantic-name search surface.

### Runtime error visibility

`WorkspaceCommandClient` no longer assumes every backend/proxy response is valid JSON. It preserves non-JSON response text and reports HTTP status, authority endpoint, and timeout classification so reverse-proxy/runtime disconnects do not collapse into opaque JSON parse failures.

### SSH deployment trust

The production workflow fallback host changed from retired `137.184.223.84` to active production `165.227.220.193`.

The workflow still requires pinned `HHS_DIGITALOCEAN_KNOWN_HOSTS`, `StrictHostKeyChecking=yes`, the repository deploy private key, and no runtime `ssh-keyscan` or trust-on-first-use bypass.

The SSH preflight classifies stale/mismatched host key, rejected deploy-key authorization, unreachable SSH endpoint/firewall/sshd, and other SSH failures.

## Validation completed

- PR `#466` is open, non-draft, and mergeable against exact main `a8fc0646e21b2a67804468575f364fef1762ec6a`.
- Exact main remained unchanged when the verifier repair was inspected.
- `DigitalOcean Production Exact Main` run `35038108002` completed successfully on restart head `106687909d594edc3634befd4d2c301e55caf493`.
- `DigitalOcean Mobile Control and Vector Ingress` run `35038107957` completed successfully on restart head `106687909d594edc3634befd4d2c301e55caf493`.
- The first current-head `Validate HHS Runtime OS Production Root` run `35038107926` reached the Runtime OS source/build stage after successfully installing production requirements and compiling the native runtime. It failed only because `hhs_gui/scripts/workspace-source-verify.mjs` still asserted the retired default `useState<ProductSurface>("program")`.
- Repair commit `5ff3751a29a96a2211324f78e3a4505f3bb188a2` updates that inherited gate to require the canonical `control` default and explicitly retain `Control`, `Visual Program`, `Workspace`, and `Authority` composition.
- Before the stale assertion stopped run `35038107926`, `npm run typecheck`, calculator tests, and `npm run test:e2e:source` all passed.
- Current-head post-repair runs were started: dedicated mobile-control run `35038412701`, production-root run `35038412626`, and deployment-contract run `35038412849`.
- A local repository clone was unavailable because the execution container could not resolve `github.com`; this is an environment limitation, not a repository test result.

Per repository policy, queued or slow external CI does not block a restartable checkpoint after the dependency-scoped implementation is committed. The stale source assertion was repaired forward rather than reverting the requested mobile landing surface.

## Validation remaining

1. Merge PR `#466` once mergeability remains true; current-head external runs may finish independently.
2. Verify the resulting exact main SHA.
3. Inspect the exact-main `DigitalOcean Production Exact Main` deployment triggered by the merge.
4. Classify SSH preflight result:
   - stale host key: replace `HHS_DIGITALOCEAN_KNOWN_HOSTS` with an independently audited current host-key entry for `165.227.220.193`;
   - deploy credential rejected: restore/rotate the public key corresponding to `HHS_DIGITALOCEAN_SSH_PRIVATE_KEY` in the production authorization path;
   - do not disable `StrictHostKeyChecking` and do not substitute `ssh-keyscan` discovery for audited trust.
5. After successful promotion verify public production:
   - `/api/system/status`
   - `/api/interface/status`
   - `/`
   - `/health`
   - `/api/v1/pass174/status`
   - one real file ingress through `/api/v1/pass174/sdlc/run`
   - persisted vector readback through `/api/v1/pass174/hash216/query` when an operation key is returned.

## Environment state

No DigitalOcean droplet mutation, reboot, key deletion, trust bypass, or direct production filesystem mutation has been performed. The active production droplet remains intact. Repository changes remain isolated to PR `#466` until merge/deployment.

## Exact next action

```text
1. Re-read PR #466 head and mergeability.
2. Merge #466 to main using the exact expected head SHA.
3. Verify main advanced to the returned merge SHA.
4. Inspect the resulting DigitalOcean Production Exact Main run.
5. Use the strict SSH preflight classification to repair only the stale trust/credential component if necessary.
6. Verify public Runtime OS plus real file -> Pass174 persistent vector store -> readback behavior.
```

Do not replace the Pass 174 persistent vector store with the lightweight `memory.search` projection, and do not weaken VM81/Hash72/Hash216 authority boundaries merely to make the UI appear connected.
