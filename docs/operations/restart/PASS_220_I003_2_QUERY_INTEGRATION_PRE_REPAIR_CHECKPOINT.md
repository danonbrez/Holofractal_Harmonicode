# Pass 220 I003.2 pre-repair checkpoint — query integration truthfulness

Status: **RESTARTABLE PRE-REPAIR CHECKPOINT**

## Predecessor

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- predecessor head: `537baa87fbdef21d5cc3aa7c238a8280e9b947f0`
- PR: #491
- dedicated cold calibration run: `35300451657`
- artifact: `10530216407`
- artifact SHA-256: `aa99ee4446c703e62d9b4277e059f8cbe94a9a20afafaa152faca3f641eaf64b`

## Frozen cold-runner measurement

The cold x86_64 raw-byte calibration itself succeeded independently of HHS runtime services.

Measured largest all-arm closed workload:

- xy: 33,554,432 bytes
- yx: 33,554,432 bytes
- zw: 33,554,432 bytes
- wz: 33,554,432 bytes
- global all-cohort minimum: 33,554,432 bytes

The cold measurement remains observational and is not rewritten by this repair.

## Post-calibration integration defect

The same workflow log exposed one failed dependency-scoped integration test:

`test_small_real_lane5_abc_integration`

Failure:

`ValueError: duplicate Hash216 candidate`

Root causes visible in the branch implementation:

1. `_counts(max_candidates)` retained the complete inherited 8..2048 ladder even when `max_candidates=8`.
2. Synthetic `_hash216(seed)` had only a 72-value rotation period, so larger candidate sets eventually produced duplicate Hash216 values forbidden by the inherited Lane 5 optimizer.
3. The workflow piped pytest through `tee` without `pipefail`, masking pytest's nonzero exit status and allowing the job to report success.
4. The post-calibration dimensional report divided bytes by 5184 while labeling the result a 5184-state equivalent; the raw 5184-bit ABI state width is 648 bytes, so the descriptive complete-state count must divide by 648.

## Authorized repair

- make the synthetic Hash216 generator injective over the benchmark's bounded seed domain;
- make `_counts` obey the requested maximum exactly;
- add regression tests for both behaviors;
- make pytest failure propagate through `tee`;
- correct the 5184-bit raw-state equivalent divisor to 648 bytes;
- preserve the already-measured cold raw evidence unchanged;
- then proceed to I004 zero-sum global Lo Shu closure halt implementation.

No canonical VM81, Hash72, or Hash216 authority is widened by this repair.
