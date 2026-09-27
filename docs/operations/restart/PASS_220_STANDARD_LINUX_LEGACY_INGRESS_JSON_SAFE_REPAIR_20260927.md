# Pass 220 Linux legacy ingress JSON-safe repair — 2026-09-27

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Repair branch: `agent/linux-ingress-json-safe-repair-20260927`
- Merge target: `main`
- Parent delivery: PR #612, merged as `182806dab03d067b045ae64d7942a7a996db821f`
- Triggering workflow: Standard Frontend Ingress Compatibility run `36336455797`
- Triggering job: `108668116632`

## Failure

The PR #612 dependency-scoped workflow compiled every changed ingress surface successfully and then reported:

```text
1 failed, 22 passed
PydanticSerializationError:
Error serializing to JSON: invalid utf-8 sequence of 1 bytes from index 2
```

The failing case was:

`test_raw_octet_stream_redirects_to_workspace_ingress`

## Root cause

The compatibility HTTP router correctly forwarded raw bytes to the canonical workspace operation. The workspace ingress implementation correctly converted those bytes to the reversible Base64 source envelope before canonical object registration.

However, `WorkspaceAuthorityLoop.submit()` constructed and witnessed the workspace command envelope **before** the operation-specific ingress conversion. Therefore the authority decision returned through FastAPI still contained the original Python `bytes` value at:

```text
authority_decision.command.payload.source_payload
```

FastAPI/Pydantic then attempted to serialize those bytes as UTF-8 and failed.

The native ingress result itself was already reversible and correct. The defect was an egress/command-envelope serialization ordering deviation.

## Repair

### Idempotent binary source normalization

`normalize_legacy_payload()` now recognizes an existing
`HHS_REVERSIBLE_BINARY_SOURCE_V1` Base64 envelope, validates the Base64 and declared byte length, and preserves it without double encoding.

Commit:

`23f5c7bd8fb806528557f91d184c09b9e32749d0`

### Normalize before command witnessing

`WorkspaceAuthorityLoop.submit()` now pre-normalizes binary
`ingress.register` payloads before `build_workspace_command()`.

This makes the witnessed command envelope JSON-safe while preserving exact source bytes through the reversible Base64 representation.

The pre-normalization records:

- `compatibility_source_transport_encoding`
- `compatibility_source_size_bytes`

Those values continue into canonical ingress provenance as compatibility metadata.

Commit:

`ed933ccdaef8732b99ce850708f60379a8d66b35`

### Regression coverage

The raw-octet regression now proves that:

1. the returned command envelope contains `HHS_REVERSIBLE_BINARY_SOURCE_V1`, not raw Python bytes;
2. the encoding is Base64;
3. canonical modality remains `BINARY`;
4. packet transport encoding remains `BASE64_REVERSIBLE`;
5. original source byte length is retained in compatibility metadata;
6. source preservation remains true.

An additional regression proves normalization is idempotent: normalizing an already-normalized reversible source does not change its payload or byte length.

Commit:

`86b8cb2ab7f0ecddf96a928dae12a759a90ddb4c`

## Preserved invariants

This repair does not revert or narrow PR #612:

- known legacy types still translate;
- unknown/vendor types still fall back to reversible `BINARY`;
- malformed parser-specific payloads still preserve source rather than fail merely because of external representation;
- canonical low-level undeclared adapters remain fail-closed;
- frontend/compatibility layers do not gain VM81, Hash72, Hash216, receipt, or persistence authority;
- compatibility aliases still converge on `workspace.ingress.register`;
- Pass 187 Linux filesystem/process/Unix-socket/HTTP compatibility bindings remain unchanged.

## Dependency-scoped validation

The existing `.github/workflows/standard-frontend-ingress.yml` is already path-scoped to the modified runtime and test files. It executes the standard frontend and Linux/legacy ingress test suites together.

Expected terminal condition:

```text
tests/test_hhs_standard_frontend_ingress_v1.py
tests/test_hhs_linux_legacy_ingress_compat_v1.py
=> all passing
```

## Next action

Open the repair-forward PR, inspect the dependency-scoped workflow, repair any new concrete failure, merge when restartable/mergeable, verify exact main, and allow the exact-main production path to deploy normally.
