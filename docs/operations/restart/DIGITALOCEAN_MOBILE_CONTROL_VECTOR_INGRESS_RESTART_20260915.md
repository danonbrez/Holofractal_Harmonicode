# DigitalOcean Mobile Control + Vector Ingress Restart — 2026-09-15

## Restart identity

- Base exact main: `a8fc0646e21b2a67804468575f364fef1762ec6a`
- Branch: `agent/digitalocean-mobile-control-ingress-20260915`
- Pull request: `#466` — `Repair DigitalOcean mobile control, multimodal vector ingress, and SSH trust`
- Implementation checkpoint before this restart record: `b24aa08bf03bd196b829917ebecdaa7126d5900e`
- Merge target: `main`

## Production environment observed

DigitalOcean account state at this checkpoint:

- Droplet: `hhs-production-01`
- Droplet id: `598826630`
- Region: `nyc3`
- Public IPv4: `165.227.220.193`
- Size: `s-2vcpu-4gb-120gb-intel`
- State: active
- Created: `2026-09-08T19:11:12Z`
- Backups and monitoring are enabled.

The previous production droplet resource `589036816` was destroyed earlier on `2026-09-08`. This makes a stale pinned SSH host key from the previous host a plausible deployment failure mode.

Registered DigitalOcean SSH public keys:

- `hhs-github-actions-deploy` — id `59207482`, fingerprint `39:90:66:80:df:d1:82:f8:93:82:a0:c4:fb:be:e3:ef`
- `hhs-phone` — id `58136400`, fingerprint `91:64:cf:1c:46:35:24:62:7a:5b:bb:87:09:d8:03:44`

GitHub repository secrets are intentionally not readable through the repository API, so this checkpoint does not claim that the private deploy key or pinned known-hosts secret is current. The deployment workflow now distinguishes those cases without weakening SSH verification.

## Changed files

1. `.github/workflows/digitalocean-production-main.yml`
2. `.github/workflows/digitalocean-mobile-control-ingress.yml`
3. `hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx`
4. `hhs_gui/runtime_os/workspace/HHSProductWorkspace.tsx`
5. `hhs_gui/runtime_os/workspace/WorkspaceCommandClient.ts`
6. `hhs_gui/scripts/live-gui-e2e-source-verify.mjs`
7. `docs/operations/restart/DIGITALOCEAN_MOBILE_CONTROL_VECTOR_INGRESS_RESTART_20260915.md`

## Implemented behavior

### Mobile application server surface

The public HHS Runtime OS now defaults to a mobile-first `Control` surface while preserving `Visual Program`, `Workspace`, and `Authority` as click-through surfaces.

The control surface exposes:

- runtime health;
- persistent Pass 174 vector-store health;
- current project identity;
- real multi-file selection;
- local file reader/preview for text/source/code/JSON/YAML/CSV, PDF, image, audio, and video;
- bounded binary ingress for non-previewed files;
- direct governed ingress to the existing Pass 174 SDLC/vector-store path;
- persisted Hash216 vector readback when the continuation exposes its operation key.

The ingress request preserves exact source bytes by reading `File.arrayBuffer()`, base64 encoding those bytes, and sending them to `/api/v1/pass174/sdlc/run`. The inherited route continues through the established development lifecycle and Pass 174 `PersistentEncryptedVectorStore`. Readback is performed through `/api/v1/pass174/hash216/query` rather than through the lightweight workspace semantic-name search surface.

### Runtime error visibility

`WorkspaceCommandClient` no longer assumes every backend/proxy response is valid JSON. It now preserves non-JSON response text and reports the HTTP status, authority endpoint, and timeout classification so reverse-proxy/runtime disconnects do not collapse into opaque JSON parse failures.

### SSH deployment trust

The production workflow fallback host was changed from retired `137.184.223.84` to active production `165.227.220.193`.

The workflow still requires:

- pinned `HHS_DIGITALOCEAN_KNOWN_HOSTS`;
- `StrictHostKeyChecking=yes`;
- the repository deploy private key;
- no runtime `ssh-keyscan` or trust-on-first-use bypass.

A dedicated SSH preflight now classifies:

- stale/mismatched host key;
- rejected deploy private-key authorization;
- unreachable SSH endpoint/firewall/sshd;
- other SSH preflight failures.

## Validation completed

- PR `#466` was observed as open, non-draft, and mergeable against exact base main.
- `DigitalOcean Production Exact Main` run `35037973220` on implementation head `5e137070d83f56d0e442523567b06c42ce5bfe13` completed its `validate-deployment-contract` job successfully. The deploy job correctly skipped on pull-request context.
- The dependency-scoped workflow `.github/workflows/digitalocean-mobile-control-ingress.yml` was added at implementation checkpoint `b24aa08bf03bd196b829917ebecdaa7126d5900e` to run:
  - `npm run test:e2e:source`
  - `npm run typecheck`
  - `npm run build`
  - production-bundle assertions for the Pass 174 ingress/readback endpoints and the SSH target/trust contract.
- Dedicated run `35038015874` was queued at checkpoint creation.
- Exact-head `DigitalOcean Production Exact Main` run `35038015810` was queued.
- Exact-head `Validate Full Application IDE` run `35038015772` was pending.
- Exact-head `Validate HHS Runtime OS Production Root` run `35038015823` was pending.
- A local repository clone was not available in the execution container because outbound DNS could not resolve `github.com`; this is an environment limitation rather than a repository test result.

Per repository policy, queued external CI does not block a restartable implementation checkpoint.

## Validation remaining

Only dependency-scoped/external completion and production promotion remain:

1. Inspect `DigitalOcean Mobile Control and Vector Ingress` run `35038015874` for source gate, TypeScript, and build results.
2. Repair forward only if that run finds an implementation defect.
3. Merge PR `#466` when the implementation remains green/mergeable.
4. Inspect the exact-main production deployment created by the merge.
5. Classify the SSH preflight result:
   - if stale host key: replace `HHS_DIGITALOCEAN_KNOWN_HOSTS` with an independently audited current host-key entry for `165.227.220.193`;
   - if deploy credential rejected: restore/rotate the public key corresponding to `HHS_DIGITALOCEAN_SSH_PRIVATE_KEY` in the production account/server authorization path;
   - do not disable `StrictHostKeyChecking` and do not substitute `ssh-keyscan` discovery for audited trust.
6. After successful promotion verify public production:
   - `/api/system/status`
   - `/api/interface/status`
   - `/`
   - `/health`
   - `/api/v1/pass174/status`
   - one real file ingress through `/api/v1/pass174/sdlc/run`
   - persisted vector readback through `/api/v1/pass174/hash216/query` when an operation key is returned.

## Environment state

No DigitalOcean droplet mutation, reboot, key deletion, trust bypass, or direct production filesystem mutation was performed in this cycle. The active production droplet remains intact. Changes are isolated to PR `#466` until merge/deployment.

## Exact next action

From repository-visible state:

```text
1. Open PR #466 at its current head.
2. Inspect run 35038015874.
3. If green, merge #466 to main.
4. Inspect the resulting DigitalOcean Production Exact Main run.
5. Use the new SSH preflight classification to repair only the stale trust/credential component if necessary.
6. Verify the public Runtime OS and real multimodal file -> persistent vector-store -> readback path.
```

Do not replace the Pass 174 persistent vector store with the lightweight `memory.search` projection, and do not weaken the existing VM81/Hash72/Hash216 authority boundaries merely to make the UI appear connected.
