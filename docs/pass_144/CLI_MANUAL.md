# Command-Line Manual

This manual indexes the inherited Pass 135–143 command-line surfaces. Run commands from the repository root with a Python environment capable of importing `hhs_runtime`.

## Pass 135 — GfE logarithm constraints

```bash
python -m hhs_runtime.hhs_gfe_log_constraint_v1 --g 5/4
```

Purpose: exact reciprocal-state and symbolic-log constraint witnesses.

## Pass 137 — Native proof lifecycle

```bash
python -m hhs_runtime.hhs_native_proof_lifecycle_v1 \
  formal/coq/HHS_GFE_Field_Quotient.v \
  formal/lean/HHS_GFE_Field_Quotient.lean \
  formal/certificates/gfe_state_5_4_grobner.json \
  --store proof_cas \
  --egress proof_egress \
  --output proof_lifecycle_receipt.json
```

Purpose: ingress, validation, compression, storage, reversal, revalidation, and egress of proof artifacts.

## Pass 138 — General Algebraic Reasoning Unit

```bash
python -m hhs_runtime.harmonicode_general_algebraic_reasoning_unit_v1 \
  examples/pass_138/gfe_5_4_request.json \
  --output reports/pass_138/PASS_138_EXECUTION_RECEIPT.json
```

Purpose: proof-carrying exact algebraic reasoning for agent requests.

## Pass 139 — THE ARCHITECT

```bash
python -m hhs_runtime.harmonicode_architect_ouroboros_v1 \
  examples/pass_139/architect_gfe_optimization_request.json \
  --output reports/pass_139/PASS_139_EXECUTION_RECEIPT.json
```

Purpose: bounded propose–execute–measure–commit/rollback optimization.

## Pass 141 — Entropic phase equilibrium and cache

```bash
scripts/hhs-pass141 \
  --cache-root ./cache-primary \
  --cache-root ./cache-mirror \
  optimize examples/pass_141/architect_epe_request.json
```

Purpose: ethical optimization, exact entropic scoring, phase placement, and revalidated replicated cache use.

## Pass 142 — Multimodal snapshot offsets

```bash
scripts/hhs-pass142 encode \
  examples/pass_142/multimodal_snapshot_request.json \
  --output reports/pass_142/PASS_142_ENCODING_RECEIPT.json
```

Purpose: symbolic global-state compression, redundant offset embedding, reconstruction, and graph indexing.

## Pass 143 — Conflict-gradient simulation

```bash
scripts/hhs-pass143 examples/pass_143/conflict_gradient_request.json
```

Purpose: exact parallel priority-conflict smoothing with monotonic energy admission and typed quantum/audio/visual projections.

## Exit and failure discipline

A nonzero process exit, malformed receipt, failed receipt validation, unproved goal, or unrecoverable state is not a successful execution. Shell wrappers do not confer proof authority beyond the receipts and validators they invoke.
