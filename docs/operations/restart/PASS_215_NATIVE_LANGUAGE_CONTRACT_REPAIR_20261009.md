# Pass 215 inherited language contract — 2026-10-09 repair checkpoint

## Scope and authority

This cycle repairs production native-causal generation reliability without
redefining the frozen Pass 214/215 contract. It does **not** claim that Pass 215
has become an arbitrary-prompt HHS-native exact transformer runtime.

Binding inputs:
- `contracts/pass214/PASS_214_CONTRACT.json`: native open-transformer exact
  quantized reproduction, Pass 213 ROM compilation, generator/transition
  comparison with dense references, and full inherited-stack benchmark.
- `contracts/pass215/PASS_215_BENCHMARK_PROFILE.json`: full-stack, cache,
  continuation/delta, native dispatch and fixed inherited profile; post-hoc
  benchmark redefinition prohibited.
- `contracts/pass215/PASS_215_ITERATION_20_CONTRACT.json`: certified bounded
  seven-token fixture. This is a parent witness, **not** an operational
  general-generation completion certificate.
- `docs/pass220/PASS_220_UNIFIED_CHATBOT_MODEL_FABRIC_LANE5.md`: one assistant
  conversation service and inherited VM81/Hash72/Hash216 admission.

## Repository-visible restart state

- Base `main`: `7fefacde360e6a5bb537cb01e94415c96430915b`
- Branch: `repair/native-causal-retrieval-contract-20261009`
- Merge target: `main`
- First implementation commit: `5f4767045f916af1e882f848432074ce850fc181`
- Test implementation commit: `00897635314b9b08400724c9c049854760d6e3f7`
- Source: `hhs_backend/runtime/hhs_native_litert_lm_provider_v1.py`
- Test: `tests/pass220/test_hhs_pass220_i009_native_causal_rag_generation.py`
- Restart record: this file
- Source authority changed: **none**. No canonical mutation, tensor reordering,
  unauthorized numeric projection, Hash72 minting, or Hash216 state promotion.

## Implemented

1. Separate bounded optional Pass 166/219 retrieval timeout from the model's
   causal generation budget (new `HHS_NATIVE_LANGUAGE_RETRIEVAL_TIMEOUT_SECONDS`,
   default 2.0 seconds).
2. When candidate retrieval fails/times out, preserve a typed diagnostic
   (including failure type), use no candidate context, and continue with the
   real causal generator on the same user turn.
3. Read `HHS_NATIVE_CAUSAL_LM_REQUIRED` explicitly in the provider and require
   model configuration for admission. Preserve lazy loading: `configured` is
   necessary to admit a call, but `loaded_and_ready` remains a separately
   reported fact.
4. If required generation fails, raise `HHSNativeLanguageProviderNotReady`
   instead of manufacturing a semantic fallback completion.
5. Add four focused regressions for optional retrieval failure, timeout,
   unconfigured required model, and failed required model.

## Validation performed

- Read authoritative original Pass 214, Pass 215 benchmark, Pass 215 I20,
  native provider, causal adapter, existing integration tests and the active
  production service configuration at base main.
- Generated exact-once source replacements against the original provider file;
  all six source edit anchors matched exactly once.
- Committed only the changed provider and existing Pass 220 test file.
- Local Python/pytest and live production validation have **not** run in this
  chat environment (GitHub-hosted repository is not locally reachable).

## Required validation (pending)

1. PR exact-head GitHub Actions: existing
   `pass220-i003-four-phase-abc-max-hardware.yml` runs the modified I009
   test suite. Inspect result before describing tests as green.
2. `python -m pytest -q tests/pass220/test_hhs_pass220_i009_native_causal_rag_generation.py`
   under the repository's supported Python environment.
3. Regress current production native CLI strict four-prompt acceptance with
   a genuinely loaded on-host causal model.
4. Verify `HHS_NATIVE_CAUSAL_LM_REQUIRED=1` produces a real, evidenced
   generation path or a visible failed admission, never semantic fallback.
5. Exact-main deploy and public/browser acceptance only after evidence.

## Unclosed inherited contract obligations

- Pass 215 exact transformer callable path wired into the unified assistant,
  not merely the conventional Transformers/PyTorch egress adapter.
- Pass 213 ROM compilation/equivalent admission of the actual quantized
  network with exact inbound/outbound type and ordered tensor semantics.
- Arbitrary supported prompt/tokenizer and generation limits beyond the
  seven-token immutable benchmark, with exact certification/equality evidence.
- Pass 166 Word2Vec, WordNet phase semantics, Pass 219/RNA prototype context,
  Hash216 vector hydration and VM81 governed ingress/egress through one
  service, with negative bypass tests.
- Real on-host test fixture and dependency-scoped replay proving these
  surfaces compose, not just separately load or respond.

## Next action

Complete focused PR checks, repair any dependency-scoped failure, merge only
after validated checks or leave a clearly labeled ready-for-validation PR.
Continue the remaining Pass 215 compiler/inference bridge from the original
frozen contract; do not recertify the seven-token parent fixture unnecessarily.

## Environment and blockers

- Repository edits used GitHub connector actions, not a checked-out local tree.
- No local model downloads, model weights, secrets, production environment
  mutations, or VM81 canonical state changes.
- GitHub-hosted CI results and live host readiness must be checked separately.
