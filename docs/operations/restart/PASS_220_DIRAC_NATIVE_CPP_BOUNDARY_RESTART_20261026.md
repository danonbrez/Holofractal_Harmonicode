# Pass 220 — Native C++ Dirac eight-sector candidate restart (2026-10-26)

## Identity
Base: inherited Pass 220 source branch after `cd13bc765c4c831aa75c3ecae2ca642cc8c7ce3c`.
Branch: `pass220/standalone-adaptive-device-resolution-20261023`. Merge target: `main`.
Source commit: `55ecd7c602cc1b01236a0b81e0e06134ffd02286`.
Test commit: `e929e71a7d04143bfc8a2b5e016e6218fa992950`.

## Source changes
- `hhs_runtime/cpp/hhs_pass220_dirac_hnan_eight_sector_candidate_v1.hpp`: exact Gaussian integer Dirac reference K action, K^2 identity, ordered HNAN roles, eight-sector admission candidate. Native admission always false.
- `tests/pass220/test_dirac_hnan_native_candidate_v1.cpp`: constexpr involution tests, boundary/non-boundary cases, ordering failure, and fail-closed native flags.
- Unmodified original particle motion integrator, UI controls, and Hash72/Hash216 authority.

## Unverified
C++ compile and test execution have not run through the GitHub connector. No native link integration, VM81 transition, true group-to-HNAN phase witness, physics change, or hydrogen spectrum is certified.

## Commands remaining
```sh
c++ -std=c++17 -Wall -Wextra -Werror -I. tests/pass220/test_dirac_hnan_native_candidate_v1.cpp -o /tmp/hhs-dirac-test
/tmp/hhs-dirac-test
python -m unittest tests.pass220.test_dirac_hnan_boundary_candidate_v1
```

## Next action
1. Validate native compilation and negative tests.
2. Derive source-group HNAN correspondence from runtime identity and ordered source contracts, not index similarity.
3. Route validated eight-sector boundary decisions through existing Pass219 C++ cell wall with registered ABI and global conservation witnesses.
4. Preserve original motion engine and expose only admitted transition outcomes in `examples/ParticleSimulation.html`; obtain native receipts, replay, browser smoke evidence.
5. Commit, PR/merge, verify exact main, and perform production acceptance only after the native gate and tests pass.
