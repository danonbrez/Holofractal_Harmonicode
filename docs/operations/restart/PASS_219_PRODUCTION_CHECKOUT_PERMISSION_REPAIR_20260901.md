# Pass 219 Production Checkout Permission Repair — Restart Checkpoint

## Base and branch

- Base/main: `a5c0da9df9bef4c848c186d74e2ba5f897f93687`
- Branch: `agent/pass219-production-checkout-permission-repair-20260901`
- Merge target: `main`
- Prior repaired H36 / exact 25/3 merge: PR #342 / `a5c0da9df9bef4c848c186d74e2ba5f897f93687`

## Workflow evidence

Original requested merge `7d9c6234970783b5086c8b2d2a86125004ccdd9e`:

- `33540477980` Pass 217 Current Main Integration: green.
- `33540477979` Pass 219 Global Canonical Defaults: original dependency-integration failure repaired by PR #342; current-main replacement `33546053209` is green.
- `33540478070` Pass 219 Multimodal Optimization Generalization: original coverage declaration failure repaired by PR #342; current-main replacement `33546053219` is green.
- `33540477970` DigitalOcean Production Exact Main: substantive production failure after successful runner startup, build, bundle transfer, and guarded admission.
- Current-main DigitalOcean rerun `33546053234`: reproduced the production blocker after a clean build, bundle seal, SSH transfer, host-drift check, and recovery admission.

## First real production defects

1. Mandatory production language authority is not configured on the host. `tools/install_production_language_assets.py --install-if-configured --require-assistant` correctly fails closed until either a reachable LiteRT-LM Gemma provider or an authoritative Pass 166 Word2Vec manifest is configured. This requirement is preserved and is not bypassed by this repair.
2. Rollback health independently fails because `hhs.service` runs as `User=hhs` / `Group=hhs` while the guarded updater runs as root with `umask 027`; tracked files in `/opt/hhs/app` can therefore become unreadable to the service. Observed failure: `PermissionError: [Errno 13] Permission denied: '/opt/hhs/app/hhs_backend/visual_server.py'`.

## Repair implemented

- `tools/install_production_language_assets.py`
  - adds `_normalize_production_checkout_readability()`;
  - root-only and enabled by default;
  - resolves the configured production service group, default `hhs`;
  - enumerates only Git-tracked files with `git ls-files -z`;
  - grants the service group read access to tracked files and read/traverse access to their parent directories;
  - does not normalize untracked host state or secrets;
  - runs before the existing fail-closed production language authority gate, so rollback can restore service readability even when the external language asset remains unavailable.
- `tests/test_hhs_production_checkout_readability_repair_v1.py`
  - locks tracked-only normalization, service-group alignment, call ordering, and preservation of `--require-assistant` / fixture-substitution rejection.

## Preserved invariants

- H36 authority unchanged.
- Global exact `25/3` latency authority unchanged.
- VM81 / Hash72 / Hash216 singleton authority separation unchanged.
- Production language provider requirement remains fail closed.
- No fixture substitution, no semantic bypass, no timing authority changes.

## Validation state

- GitHub compare against base: branch is ahead by the repair commits only; no base drift at checkpoint creation.
- Dependency-scoped contract tests are committed and should be executed by PR/main CI.
- Local clone/test execution was unavailable in the automation environment because direct network/DNS access to GitHub is blocked; connected GitHub API operations succeeded.

## Remaining closure

1. Open/validate the repair PR against `main`.
2. Merge when dependency-relevant checks are green; do not wait on zero-job/external startup noise.
3. Rerun/observe DigitalOcean exact-main deployment.
4. The checkout permission defect should no longer break rollback health.
5. Production promotion remains legitimately blocked until a reachable LiteRT-LM Gemma model or authoritative Pass 166 Word2Vec manifest is configured on the host.
6. Do not weaken H36, exact `25/3`, or production assistant authority to obtain a green workflow.
