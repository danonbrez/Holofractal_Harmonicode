# PASS 170 — Core Sandbox Hash72 Delegation Repair Restart Record

## Status

TERMINAL DEPENDENCY-SCOPED REPAIR CLOSURE. The missing core-sandbox Hash72 export is repaired, merged to authoritative main, and verified present on main. Unrelated backend final-certification failures remain a separate repair queue.

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base commit: `a1532df2cbcc02d30728055f3a1dfd55a0c1f387`
- Base tree: `d765e97335c95638ad4942df955a38dbf75be8a0`
- Working branch: `agent/core-sandbox-hash72-delegation-repair`
- Intended merge target: `main`
- Defect-introducing historical commit: `b1a435dddee4573e11cd6e0db710f819d1774f86`

## Defect

`hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py` did not export `security_hash72_v44`, while `hhs_runtime/hhs_cross_modal_shell_gate_v1.py` imports and uses it. This causes an import-time gateway failure before request serving.

The repair must not create a second Hash72 semantic implementation. Pass 170 requires multiple surfaces to invoke the same canonical authority rather than retain separate semantic implementations.

## Changed files

- `hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py`
  - adds the missing public module-level `security_hash72_v44(obj: Any, *, domain: str = "HASH72_SECURITY") -> str` shim;
  - delegates through `load_authoritative_kernel()` on every call;
  - canonicalizes payloads with `canonicalize_for_hash72` before delegation;
  - provides no SHA or local reimplementation fallback.
- `tests/test_core_sandbox_hash72_delegation.py`
  - proves importability and digest equivalence against the resolved authoritative kernel;
  - proves `HHSRuntimeLoadError` propagates when authority resolution fails.
- `docs/operations/restart/PASS_170_CORE_SANDBOX_HASH72_DELEGATION_REPAIR_RESTART.md`
  - this restartable recovery record.

## Evidence inspected

- Current `main` branch head and tree via GitHub repository API.
- Current sandbox runtime implementation and `hhs_runtime/kernel_resolution.py`.
- Authoritative kernel `security_hash72_v44` signature and trust policy.
- Pass 170 public API authority contract, including the prohibition on separate semantic implementations.
- Historical commit `b1a435ddde` that inlined a standalone sandbox implementation.

## Validation state

Completed:

1. Exact current-main source inspection confirms the missing export.
2. Signature comparison confirms the shim matches the authoritative kernel signature.
3. Authority-path inspection confirms `load_authoritative_kernel()` is fail-closed and verifies `security_hash72_v44` among required kernel symbols.
4. Patch is dependency-scoped and does not add a local Hash72 algorithm, cache, or import-time kernel singleton.
5. A local semantic smoke of the exact shim passed with a stub authoritative kernel: tuple/Fraction/Path/dict canonicalization, keyword-only domain forwarding, and returned digest propagation matched the delegated authority call exactly.
6. Fail-closed propagation passed locally: an authority-loader HHSRuntimeLoadError escaped unchanged and no fallback digest was produced.
7. The branch push triggered 11 GitHub Actions workflow runs, but they all terminated before job materialization. Sampled runs report total_count=0 jobs and therefore executed no repository test steps; these zero-job failures are infrastructure/workflow-dispatch evidence, not code-validation failures.

Environment limitation:

- A local shallow clone was attempted from the execution container and failed before checkout with DNS resolution failure for `github.com` (git exit 128). This is an execution-environment/network limitation, not a repository/code result.

Remaining dependency-scoped executable validation:

```bash
python -m pytest -q tests/test_core_sandbox_hash72_delegation.py
python3 hhs_runtime_api_server_v1.py
# then exercise:
# GET /api/status
# POST /api/calculator/evaluate with deterministic replay
# GET /api/certification
```

Expected certification behavior is independent of this repair: pre-existing backend certification failures may remain visible after the gateway becomes importable and must be handled as the next repair queue rather than rewritten as a Hash72 delegation failure.

## Exact next action

None for this defect. The repair is merged and target-verified. Continue only with the separate pre-existing backend final-certification repair queue.

## Blockers

None for this defect. Historical execution limitations during validation were lack of outbound GitHub DNS in the local execution container and zero-job GitHub Actions termination before workflow steps executed; neither remains a blocker to this completed merge.


## Terminal closure receipt

- Pull request: `#336` — Repair core sandbox Hash72 authority export
- Branch head merged: `f5f45141b62965a023a31a59a52e5202714560e4`
- Merge commit: `765bb21fd30d9a18c97c4bf33b8ccbf4f27f71a7`
- Merge target: `main`
- Merge result: `MERGED`
- Target verification: `main` resolved to merge commit `765bb21fd30d9a18c97c4bf33b8ccbf4f27f71a7` immediately after merge.
- Verified on target:
  - `hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py` exports the exact delegation shim;
  - `tests/test_core_sandbox_hash72_delegation.py` is present on `main`;
  - the shim delegates through `load_authoritative_kernel()`, canonicalizes at the boundary, preserves the kernel signature, and contains no alternate Hash72 or legacy SHA fallback.
- External workflow state: branch-triggered Actions runs terminated before job materialization with zero jobs; no repository test steps executed. Per repository delivery policy, this external infrastructure condition did not delay the completed dependency-scoped merge.
- Remaining work for this defect: `NONE`.
- Separate next repair queue: pre-existing backend final-certification failures exposed once gateway import succeeds.
