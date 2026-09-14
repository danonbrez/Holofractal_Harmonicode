# Pass 219 External + Environmental Authority Reconciliation v1 — Continuation Checkpoint

Date: 2026-09-12

## Restart coordinates

```text
canonical main at reconciliation:
  d09c81aa97f1064f054795d778cf6ad947be0dae
canonical main tree:
  94e0a4412e1ac03fbfd52ead8527799ca3347543
working branch:
  agent/pass219-external-runtime-authority-closure-v1-20260912
merge target:
  main
continuation PR:
  #436
```

The main commit above is the successful PR #426 production-repair merge and is qualified by DigitalOcean Production Exact Main #309 / run `34697074466` according to the production closure record supplied for this continuation.

## Main reconciliation

The authority branch was eight commits behind the new canonical main, with merge base:

```text
e157ef775f5da94281573a2d428e2ddb811c385e
```

The eight main-side commits touched only the production deployment repair / Pass202 validation surfaces and did not overlap the 29 authority-closure files.

Repository-visible sync PR:

```text
PR: #438
head: main @ d09c81aa97f1064f054795d778cf6ad947be0dae
base: agent/pass219-external-runtime-authority-closure-v1-20260912
merge commit on authority branch:
  a4dc8fc22da390bca94f4be89ed8eb2cc59e0252
```

PR #436 became mergeable again after this ancestry reconciliation.

## Preserved authority lineage

The original two-parent security reconciliation remains intact:

```text
0c67f389c6044638731791ca6da8d8976ed4ad42
  external-authority parent:
    3bf5ed3d6fb4ee48ee4d0d1ce5397d376e7c786c
  environmental/PQC parent:
    015f1e29eb2e9032d70991c1a5b7712929398cab
```

The current production authority order remains:

```text
Pass 220+ candidate
  -> RNA C++ cell wall
  -> parent Hash216 proof
  -> 1.32 Genesis/environment witness
  -> PQ-signed environmental witness
  -> hidden 1.31 ML-DSA/SLH-DSA boundary
  -> hidden 1.30 provenance/HMAC membrane
  -> hidden RNA/VM81 canonical admission
  -> child Hash216 proof
  -> singleton VM81 commit + canonical receipt
```

Sole intended public post-219 mutation ABI:

```text
hhs_exact_pass219_vm81_environment_admit_signed
```

## Dedicated validation evidence inherited from head 18c13778

Dedicated run:

```text
34695584239
```

`system-provider` completed PASS through all dependency-scoped stages:

```text
exact ABI build
sole dynamic mutation-authority audit
strict firewall/reference test
strict signed environmental boundary compile
system-provider fail-closed/security-halt verification
environmental recovery test
post-219 candidate-development regression
static no-self-vouching audit
```

The only dedicated failure was job `openssl-35-positive`, and it failed in its OpenSSL-build/provider setup step before any HARMONICODE ML-DSA, SLH-DSA, environmental-boundary, recovery, or export-audit test executed.

## Repair-forward: OpenSSL 3.5 positive lane

The OpenSSL 3.5 workflow installs a private shared build under:

```text
/tmp/openssl35
```

The build step previously invoked `/tmp/openssl35/bin/openssl` immediately after `make install_sw` without first binding the private library directory into the dynamic loader path. All later HARMONICODE 3.5 steps already used `LD_LIBRARY_PATH=/tmp/openssl35/lib`.

Repair commit:

```text
63b80dba6f1350adcb959bdffeb4302919547a30
```

Repair scope:

```text
.github/workflows/pass219-vm81-pqc-signature-boundary-v1.yml
```

Changes are CI-only:

```text
add curl retry for the OpenSSL source archive
export LD_LIBRARY_PATH=/tmp/openssl35/lib before first local openssl execution
prepend /tmp/openssl35/bin to PATH
preserve all runtime/PQC/environmental implementation code unchanged
```

## Current dedicated validation

Repair-forward dedicated run:

```text
run: 34697863978
head at launch: 63b80dba6f1350adcb959bdffeb4302919547a30
workflow: Pass 219 VM81 PQC + Environmental Authority Boundary v1
state at checkpoint: queued
```

A large inherited PR workflow matrix is also queued on this head. Per the standing forward-progress policy, runner queue latency is not a reason to withhold a repository-visible checkpoint.

## Validation still required

Dependency-scoped closure remains:

1. Read run `34697863978`.
2. Require `system-provider` to stay green after the exact-main sync.
3. Require the OpenSSL 3.5 lane to reach HARMONICODE execution and prove:
   - ML-DSA positive canonical path;
   - SLH-DSA positive canonical path;
   - canonical constraint rejection remains non-security rejection;
   - verified environmental recovery + anti-rollback behavior;
   - sole public mutation export remains 1.32.
4. Repair only the exact failing stage if the dedicated run is red.
5. Once the dedicated authority workflow is green, merge PR #436 with its then-current head SHA.
6. Verify exact `main` contains the singleton 1.32 public mutation boundary and still contains the PR #426 production-repair ancestry.

Unrelated legacy workflow-startup failures are not authority-closure acceptance evidence unless they execute a dependency used by this change.

## Next action

Continue from this branch. Inspect dedicated run `34697863978`; if it is green, merge PR #436 and verify exact main. If it exposes a functional PQC/environmental defect, repair forward on this same lineage, rerun only the affected dedicated gate, and preserve the production-main ancestry above.
