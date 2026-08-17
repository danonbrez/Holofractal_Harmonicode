# Pass 218 Full Implementation — Iteration 1 Restart Record

**Pass:** HHS Pass 218 — Relational Curriculum Corpus Hydration  
**Iteration:** 1  
**Base commit:** `b0656a92ab29507f81eae760e070f74e49db83f4`  
**Branch:** `agent/pass218-full-iteration1-genesis-curriculum`  
**Merge target:** `main`  
**Status:** implementation checkpoint; **not** Pass 218 closure.

## Implemented in this iteration

1. Added a dedicated cumulative `hhs_runtime.pass218` package instead of treating the earlier reference crawler as the pass.
2. Implemented a versioned Stage-0 Genesis asset manifest binding the inherited English word list, grammar corpus, and all eight WordNet CSV authorities by exact SHA-256 and Hash72 identity.
3. Implemented bounded Genesis relational compilation: WordNet typed revisable priors; no retained WordNet definitions/examples; provisional unknown objects; exact integer form neighborhoods; symbolic/analogical type separation; exact integer/rational relation state.
4. Added an exact adapter over inherited Pass 166 Word2Vec `nearest()` results, preserving cosine sign and exact squared-rational similarity without creating a second vector engine.
5. Implemented deterministic curriculum manifests binding Genesis identity, stage, ordered source checksums, and compiler version.
6. Implemented an exact restartable cursor that refuses out-of-order authoritative promotion and resumes from the last closed source boundary.
7. Added repository-native evidence generation and dependency-scoped tests.

## Acceptance matrix progress

This iteration establishes foundations for P218-T01, T02, T04, T05, T06, T07, T13, T14, T16, T17, T18, T29, and T40. These are partial pass-level acceptance contributions, not a claim that the complete acceptance tests are satisfied.

## Deliberately incomplete after Iteration 1

- grammar examples are reduced to nonverbatim category priors; exact compositional rule compilation remains required;
- full WordNet sense disambiguation remains required;
- Pass 166 Word2Vec is integrated as a callable exact provider, but a production model must be installed/activated and exercised in the full Pass 218 training path;
- contextual open-weight model hydration remains required;
- narrative-beat extraction, perspective hydration, and nonverbatim relational memory promotion remain required;
- document/ZIP/folder/repository/official-site production ingress adapters remain required;
- authoritative Hash216/vector-store promotion, VM5184 projection, candidate-commit/purge/quarantine transaction semantics, ablations, and full replay remain required;
- the existing `pass218_native_corpus_crawler.py` remains bounded reference evidence and is not promoted to production authority by this iteration;
- preparatory PR #208 remains separate scaffolding and is not Pass 218 completion evidence.

## Changed files

- `hhs_runtime/pass218/__init__.py`
- `hhs_runtime/pass218/genesis.py`
- `hhs_runtime/pass218/curriculum.py`
- `tests/pass218/test_pass218_iteration1_genesis_curriculum.py`
- `tools/pass218_iteration1_evidence.py`
- `.github/workflows/pass218-full-iteration1.yml`
- `docs/pass218/PASS_218_ITERATION_1_RESTART.md`

## Required validation

```text
python -m py_compile hhs_runtime/pass218/*.py tools/pass218_iteration1_evidence.py
pytest -q tests/pass218/test_pass218_iteration1_genesis_curriculum.py
pytest -q tests/pass218/test_repository_native_creative_writing_crawler.py
python tools/pass218_iteration1_evidence.py
AST no-float-literal check over hhs_runtime/pass218/*.py
```

## Next deterministic action

Iteration 2 should compile the grammar/reference layer into explicit exact relation/rule objects and connect the Stage-0 seed plus Pass 166 exact distributional evidence to the first nonverbatim narrative-beat hydration object and Hash216 candidate transition, without yet enabling unrestricted production crawling.
