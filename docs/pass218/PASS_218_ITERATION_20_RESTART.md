# Pass 218 Iteration 20 — Governed Pass 166 Model Activation

Status: **IN DEVELOPMENT / VALIDATION PENDING**

## Frozen parent and branch

- Frozen I19 parent: `53b495b90abd0a9296571ed6804506ba12165916`
- I20 branch: `agent/pass218-full-iteration20-governed-pass166-model-activation`
- Merge target: `main`
- I19 must remain immutable. Do not extend or rewrite the I19 branch.

## Boundary

Iteration 19 ends with successful maintenance execution terminally closed and its external effect independently verified:

```text
I17 external operation
  -> I18 terminal closure
  -> I19 action-specific distributed postcondition verification
  -> EFFECT VERIFIED
```

Iteration 20 is a separate cognition/model lifecycle boundary. It binds one exact already-installed Pass 166 Word2Vec model to the existing Pass 218 relational-cognition candidate provider under current Pass 218 writer authority:

```text
I19 EFFECT VERIFIED / no pending successful-maintenance verification
  + current Pass 218 writer/fence
  + exact installed Pass 166 model identity
  + exact Pass 166 VM81 activation receipt
  + exact Pass 166 compatibility-verification receipt
        |
        v
 durable I20 model binding
        |
        v
 existing I1 Pass166Word2VecAdapter
        |
        v
 revisable exact relational candidates
```

The I20 binding is not truth promotion, an action grant, a canonical-learning commit, or a Pass 165 source-retaining learning commit.

## Governed activation semantics

I20 requires:

1. current Pass 218 lifecycle `authority_ready`;
2. if the distributed I19 postcondition membrane is configured, zero successful closures pending effect verification;
3. an exact configured Pass 166 `model_id`, `canonical_model_root`, and `index_root`;
4. no different active Pass 166 model;
5. explicit host configuration before I20 may call the inherited Pass 166 activation operation;
6. exact inherited Pass 166 `ACTIVATION` and `COMPATIBILITY_VALIDATION` receipts;
7. a durable Hash72-sealed binding record;
8. restart validation of those exact stored receipts without reactivation or re-verification receipt emission.

A durable I20 binding never silently reactivates a later-inactive model. Model replacement, identity change, or binding replacement requires a new explicitly governed iteration.

The original writer/fence that created the binding remains immutable provenance. A later legitimate writer fence may restart and validate the same binding, but it cannot rewrite that provenance.

## RuntimeOS surface

Production RuntimeOS installs I20 after I19.

Browser-visible I20 surface:

- `GET/HEAD /api/runtime/pass218/cognition/pass166-model/status`

There is deliberately no browser model activation, model switch, model replacement, truth-promotion, or action-authority route.

Host configuration:

- `HHS_PASS218_P166_MODEL_ID`
- `HHS_PASS218_P166_MODEL_ROOT`
- `HHS_PASS218_P166_INDEX_ROOT`
- `HHS_PASS218_P166_ACTIVATE`
- inherited Pass 166 store: `HHS_PASS166_STORAGE_DIR`

If the three exact model-identity variables are all absent, I20 remains safely unconfigured. Partial identity is fail-closed.

## Implementation delta

Current I20 files:

- `hhs_runtime/pass218/model_activation_i20.py`
- `hhs_backend/runtime_os_pass218_model_i20.py`
- `hhs_backend/runtime_os_application_server.py`
- `tests/pass218/test_pass218_iteration20_pass166_model_activation.py`
- `scripts/pass218_iteration20_model_activation_validation.py`
- `docs/pass218/PASS_218_ITERATION_20_RESTART.md`
- `.github/workflows/pass218-full-iteration20.yml` (to be added before validation)

## Required validation before freeze

- compile I20 runtime/backend/evidence harness;
- global Pass 218 no-authoritative-float literal gate plus I20 backend gate;
- focused I20 activation/binding tests;
- Pass 166 Word2Vec regression;
- evidence harness proving exact activation, exact verification, exact restart receipt reuse, newer legitimate writer-fence restart, no redispatch, and no new verification receipt;
- RuntimeOS production-root acceptance;
- inherited real-etcd Pass 218 distributed membrane regression;
- exact final-head CI after any validation-record update.

## Exclusions preserved

- canonical authority minted: false
- canonical mutation permitted by I20: false
- canonical learning commit invoked: false
- truth promotion: false
- action authority minted: false
- maintenance execution authority minted: false
- retry authority minted: false
- model activation via browser: false
- model replacement via browser: false
- Pass 165 source-retaining learning commit invoked: false
- verbatim corpus source retained by Pass 218: false
- authoritative float weights created: false

## Restart instruction

Until a terminal validation update freezes I20, resume from the current remote head of `agent/pass218-full-iteration20-governed-pass166-model-activation` and inspect CI before making further changes. Never resume by modifying frozen I19 in place.
