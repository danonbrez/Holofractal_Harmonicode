# HHS Pass 174 native harmonic runtime ABI

This strict C11 project additively wraps the inherited Pass 163 VMRC frame ABI. It does not establish a second commit authority.

Implemented callable surfaces:

- `hhs_p174_phase_at` — exact 64:72:81 and 5184 phase coordinates;
- `hhs_p174_build_candidate_frame` — immutable-source, authority-token-gated construction of a complete 648-byte candidate frame;
- `hhs_p174_hash216_join` — ordered predecessor/current/successor 72-character lane concatenation;
- `hhs_p174_hash216_indexes` — 216 domain-separated chained SHA-256 positional indexes and aggregate root;
- `hhs_p174_select_execution_path` — exact integer comparison of direct and retrieval virtual cost units.

The candidate-frame call never mutates the source. Authoritative commit remains governed by the singleton VM81 runtime and its Hash72 receipt path.

## Build and test

```sh
make -C native_projects/hhs_pass174_harmonic_runtime test
```

For filesystems mounted with `noexec`, build and execute through a temporary directory:

```sh
make -C native_projects/hhs_pass174_harmonic_runtime test-tmp
```

Expected terminal line:

```text
HHS_PASS_174_NATIVE_PHASE_HASH216_WHOLE_FRAME_ABI_VERIFIED
```
