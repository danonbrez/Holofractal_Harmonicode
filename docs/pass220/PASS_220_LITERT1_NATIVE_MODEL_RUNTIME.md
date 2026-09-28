# Pass 220 LiteRT1 — Native Model Runtime and Dependency Inversion

## Status

`IMPLEMENTED — RESTARTABLE VALIDATION CHECKPOINT`

Branch:

`pass220-litert1-native-model-runtime`

## Objective

Replace LiteRT-LM as a mandatory internal dependency without breaking the
existing LiteRT/Gemma deployment contract.

LiteRT1 separates two responsibilities that were previously coupled:

```text
external compatibility / import / serve
                !=
native HHS model identity / tensor topology / assistant runtime
```

The official `litert-lm==0.14.0` package remains available through
`requirements-litert-lm.txt`, but it is no longer pulled into the default
repository dependency closure.

## Default runtime

The default launcher mode is now:

`HHS_LITERT_LM_PROVIDER_MODE=native`

In that mode HHS does not bootstrap or probe an external LiteRT-LM server
before using the repository-native provider.

The following compatibility modes remain explicit and supported:

- `local` — supervise the official local LiteRT-LM CLI/server;
- `external` — use a separately managed OpenAI-compatible LiteRT endpoint;
- `auto` — legacy discovery/local bootstrap behavior;
- `disabled`.

The existing stdlib HTTP transport remains unchanged as the external
compatibility membrane.

## Native C11 model/tensor registry

Project:

`native_projects/hhs_pass220_litert_native_model_runtime`

The native registry owns model topology metadata:

- model generation;
- execution-backend identity;
- context/output-token bounds;
- source SHA-256;
- 216-character model identity;
- ordered input/output tensor records;
- dtype;
- rank/dimensions;
- tensor-name SHA-256;
- deterministic registration fingerprint.

It has no model inference authority beyond this registration layer and no
canonical VM81/Hash72/Hash216 state authority.

Floating dtype identifiers in this registry are **type metadata**, not
permission to use floating-point arithmetic as canonical HHS computation.

## Python2 RNA class binding

Every registered model uses the same native runtime class identity:

`hhs.litert.LiteRTModelRuntime`

with the seven RNA members:

1. `__init__`
2. `model_identity`
3. `input_tensors`
4. `output_tensors`
5. `invoke`
6. `list_models`
7. `chat_completion`

Together with the class anchor this exactly fills the inherited eight-domain
Pass 219 RNA 1.11 class-registration nucleus.

Different model artifacts/generations therefore receive different model
Hash216 identities while sharing the same registered runtime class identity.

This is also the future Mojo class boundary. Mojo does not get a separate
model object registry.

## Pass 153 preserved

Pass 153 already defines the critical authority split:

- model output is advisory;
- VM81 is semantic/state-commit authority;
- Hash72 receipts witness governed operations;
- Hash216 identifies model/runtime objects.

Its existing `LiteRTModelAdapter` is retained as an external tensor-runtime
compatibility path. LiteRT1 does not delete it.

## Dependency closure

Before LiteRT1:

```text
requirements.txt
    -> requirements-litert-lm.txt
       -> litert-lm==0.14.0
```

After LiteRT1:

```text
requirements.txt
    -> HHS native provider/runtime

requirements-litert-lm.txt
    -> optional explicit compatibility installation
       -> litert-lm==0.14.0
```

Deployments that intentionally use Google's CLI can still install:

```bash
python -m pip install -r requirements-litert-lm.txt
HHS_LITERT_LM_PROVIDER_MODE=local bash start.sh
```

or point `external` mode at a managed endpoint.

## Validation

LiteRT1 validation covers:

- strict C11 model registry build;
- C++17 native registration wrapper;
- deterministic model registration replay;
- tensor topology rejection;
- Python bridge to the native registry;
- Python2 RNA runtime-class registration;
- same RNA class identity across distinct model generations;
- external LiteRT tensor metadata ingestion;
- root dependency closure excluding `litert-lm`;
- optional compatibility pin retained;
- launcher native default;
- shell syntax;
- authority flags.

## Numerical execution boundary

LiteRT1 does **not** implement a second tensor arithmetic engine.

LiteRT2 must lower admitted tensor buffers/operators into the already merged
NumPy1 HARMONICODE engine:

```text
LiteRT tensor metadata
        ↓
native LiteRT execution graph
        ↓
NumPy1 shape/broadcast/index membrane
        ↓
exact symbolic / BigInt HARMONICODE arithmetic
        ↓
dtype-required IEEE ingress/egress
```

This preserves NumPy-compatible observable tensor behavior without restoring
host floating-point arithmetic as canonical authority.

## Next checkpoint

LiteRT2:

1. native tensor-buffer objects;
2. operator graph registration;
3. first exact operator subset over NumPy1;
4. external LiteRT interpreter differential oracle;
5. tokenizer/model-import normalization;
6. generation pipeline connection to the existing native causal LM service;
7. Mojo acceleration bindings using the same RNA class and model identities.
