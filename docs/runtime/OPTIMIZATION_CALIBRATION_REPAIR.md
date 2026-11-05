# Exact optimization calibration repair

## Scope

This repair restores repository-visible calibrated defaults for the Hash216
continuation retrieval, Pass 207 vector/buffer cache, and Pass 208 bounded branch
manifold without rewriting any frozen Pass 215 evidence or changing VM81,
Hash72, or Hash216 admission semantics.

The calibration source is the previously validated deterministic multimodal
calibration branch and its promoted Pass 205 continuation evidence. The
validated retrieval profile used `top_k = 32`; the extended benchmark used
2,048 vector objects and 512 queries; continuation calibration used 360 ticks
for 13 deterministic seeds. The deployed Pass 208 profile used 256 branches
and a Pass 207 cache of 536,870,912 bytes / 512 entries.

## Root cause

The calibrated deployment profile survived in the DigitalOcean Pass 208
environment and installer, and Pass 205 retained `top_k = 32`. The direct
`Pass207VM81GPURuntime` constructor, however, still had the older fallback
values of 256 MiB / 256 entries. Code paths that instantiate Pass 207 directly
therefore bypassed the calibrated cache profile even though Pass 208 used the
larger validated defaults.

This was configuration drift, not loss of the exact algorithms.

## Repair

`hhs_backend/runtime/hhs_optimization_calibration_v1.py` is now the shared,
integer-only source for:

- Pass 205 retrieval shortlist: `32`
- Pass 207 cache bytes: `536870912`
- Pass 207 cache entries: `512`
- Pass 208 maximum branches: `256`
- calibration vector-object count: `2048`
- calibration query count: `512`
- continuation ticks: `360`
- deterministic calibration seed set

Pass 207 now resolves its direct-construction cache defaults from this profile
and honors exact positive-integer environment overrides. Pass 208 resolves its
branch and cache defaults from the same profile. Status payloads expose the
profile for deployment inspection.

## Authority boundary

No floating-point value is introduced into the authoritative optimization
profile, vector ranking, branch ranking, cache sizing, or admission path.
Pass 207 remains candidate-only and CPU-exact-verified. Pass 208 remains
candidate-only until the selected branch is recomputed and committed through
the singleton Pass 205 / VM81 admission path.

The historical receipt vector index, Python receipt vector cache, and
predictive sandbox remain legacy advisory surfaces. They are not imported by
the Pass 205/207/208 authoritative optimization path.

## Regression guard

`tests/test_hhs_optimization_calibration_v1.py` fails if:

- the recovered calibrated integers drift;
- direct Pass 207 construction stops using 512 MiB / 512 entries;
- Pass 208 diverges from the same cache/branch profile;
- Pass 205 retrieval ceases to default to `top_k = 32`;
- DigitalOcean deployment defaults diverge from the runtime profile;
- a floating-point literal enters the shared optimization authority modules; or
- a legacy float-based vector/predictive module is imported into those modules.

The repair is additive with respect to frozen higher-pass evidence: it changes
runtime configuration wiring and tests only.
