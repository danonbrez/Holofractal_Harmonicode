# Pass 220 I003.1 pre-repair checkpoint — cold x86_64 raw-byte calibration isolation

Status: **RESTARTABLE PRE-REPAIR CHECKPOINT**

## Trigger

The I003 max-hardware calibration must not execute HARMONICODE services, HHS kernel/runtime logic, the native exact ABI, Lane 5, Hash72/Hash216 services, Python runtime ranking, or compiled project code inside the hardware-calibration workload.

The calibration workload is instead:

- cold GitHub-hosted x86_64 Linux runner;
- ordinary raw byte files only;
- shell + standard Linux/coreutils commands only;
- adaptive doubling with no configured workload-size ceiling;
- bounded only by the cold runner's actual resources and the declared time membrane;
- four repeated phase-labelled calibration cohorts;
- three A/B/C raw byte paths;
- no HHS semantic interpretation of the raw phase labels.

## Frozen predecessor

- branch: `pass220-lo-shu-normalization-checkpoint-1`
- I003 checkpoint: `86832d8cfb26c22b45de8f780d15e9f8d3c35a76`
- merge target: `main`
- draft PR: `#491`

I001/I002 logic remains frozen. The I003 Lane 5 bridge remains useful as post-calibration integration code, but it is no longer part of the hardware-calibration workload.

## Repair target

1. Add a pure Bash/coreutils cold-runner benchmark executed immediately after checkout and before package installation, build, Python, make, or any HHS command.
2. Use one raw byte source for each adaptive size and the three raw arms:
   - A: `cat FILE >/dev/null`
   - B: `dd if=FILE of=/dev/null bs=1M status=none`
   - C: `sha256sum FILE >/dev/null`
3. Rotate `ABC/BCA/CAB` order.
4. Repeat across labels `xy/yx/zw/wz`; these labels are inert cohort labels only in the raw calibration.
5. Begin at a small byte count and double without a static max until:
   - an arm exceeds the per-leg time membrane;
   - the global time membrane is reached; or
   - the next source size would violate actual runner free-space reserve / source generation fails.
6. Record the largest all-arm closed byte count per cohort and their minimum as the cold-runner raw-byte capacity witness.
7. Keep integer nanoseconds and byte counts as the primary evidence.
8. Move HHS/Lane 5 builds/tests/query comparison after this cold calibration and classify them as post-calibration integration, not hardware calibration.
9. Remove the inherited HHS raw-runner A:B:C preflight from the cold calibration path because it exercises project ABI/services.
10. Seal a repair checkpoint before waiting for CI.

## Next action

Implement the raw Bash benchmark, rewrite the I003 workflow ordering and documentation, run static/source checks where available, and checkpoint.
