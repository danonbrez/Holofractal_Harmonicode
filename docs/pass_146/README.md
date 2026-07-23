# HHS Pass 146

Pass 146 makes the security boundary part of the executable structure of every public HHS operation.

The implementation adds authenticated identities, capability grants, immutable boundary contracts, minimum-path construction, temporary capability activation, high-resolution pathway steps, explicit reversibility, signed peer envelopes, receiver-side boundary reconstruction, conflict negotiation, and deterministic replay. The root `hhs` and `hhs-android` launchers route inherited Pass 145 CLI operations through `RUN_CLI_COMMAND` boundaries. The combined loopback API routes inherited knowledge endpoints through the same mechanism.

## Primary modules

- `hhs_runtime/pass146/engine.py` — identity, grant, contract, path, propagation, negotiation, replay.
- `hhs_runtime/pass146/service.py` — Pass 145 service extension and capability status.
- `hhs_runtime/pass146/cli.py` — boundary-wrapped inherited CLI and security administration.
- `hhs_runtime/pass146/api.py` — authenticated combined loopback API.
- `hhs_runtime/pass145/database.py` — canonical transactional tables and database-root integration.

## External network evidence

Two separate database nodes exchange an Ed25519-signed propagation envelope over an authenticated loopback HTTP request. The receiver uses explicit peer trust and constructs a fresh `RECEIVE_PROPAGATION` boundary before admission. Remote-device binding is deliberately not exposed by this release because no authenticated remote transport, certificate lifecycle, Android APK, or real multi-device test is available in the execution environment.
