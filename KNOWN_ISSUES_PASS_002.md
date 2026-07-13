# Known Issues — Pass 002

## GUI

- Full GUI typecheck/build remains pending until Node dependencies are installed.
- Some older workspace abstraction files still exist and may be deprecated by the current `RuntimeWindowManager` path.
- Optional GUI applications may still contain stale assumptions that will surface only after TypeScript build verification.

## Backend

- The canonical backend app entry should be standardized in documentation. Current candidates include:
  - `hhs_backend.server:app`
  - `hhs_backend.runtime.runtime_server:app`
- `hhs_backend.api.runtime_server` is not present and should not be referenced as a launch target.

## C Runtime

- `make verify-c` passes but emits warnings. Future hardening should clean initializer warnings and unused static symbols where safe.

## Packaging

- Release ZIP should avoid generated caches, local build outputs, and dependency folders.
