# Pass 215 Iteration 20 Restart Record

## Restart authority

Resume only from the exact successful Iteration 19 closure:

```text
branch: agent/pass215-iteration20-terminal-closure
pre_iteration20_main_head: 42de97bdc1ddb8cfaed4fcbd7ff41d10d1641d3f
parent_head: 04745e6592f2d3bb8f227cc2dec61e25a66145d8
parent_tree: 4fb5ead812c564b423f7a13155988e5384c53d0e
parent_run: 31288268305
parent_job: 93180913426
parent_artifact: 9030733029
parent_artifact_sha256: 867159f45a4e22922b858a5ada13bbab25c1a8b400598ebabe5cd6bfcd4106f8
pre_iteration20_merge: faba6bc40745a04c8d5937254d228e56348d2cc0
merge_target: main
```

Do not modify or recreate Iteration 19 while completing this restart state. Its implementation, documentation, roots, run, and retained artifact are frozen inputs.

## Required Iteration 20 state

The restart-state commit must contain only the new Iteration 20 runtime, tool, tests, cumulative validation entrypoint, contract, implementation record, documentation, and workflow. The authenticated source execution must freeze:

- both sequential Iteration 18 checkpoint roots and canonical sizes;
- both checkpoint-manifest roots;
- the shared content-store and bundle roots;
- reused chunk count and compressed bytes;
- later incremental compressed blob bytes;
- separate-store bytes, union-store bytes, and exact savings;
- sequential reuse, Pass 215 completion, suite, evidence, and receipt identities;
- the unchanged seven-token true-greedy chain;
- zero restore replays at both checkpoints;
- `pass216_status=RESERVED_NUMBER_NO_PASS` and `next_implemented_pass=217`.

The authenticated two-process source execution is frozen with 240 cumulative controls, 36 reused unique chunks, 28,375,966 reused compressed bytes, 125,510,422 later incremental compressed bytes, shared-store root `b7a9eb1678f263f20c5b61c0d9d3f01b76b152e2786b7e887ecb8265cbe454da`, Pass 215 completion root `3dfb034753309c5f45f56f9bec5bf2178b1eb74974264cc306e46c8d6551f76a`, evidence root `5a8a17e10b1dc10db2912bc2df40aa67306fc520439716eab47596dc1e8aac1e`, and receipt `rimw6Mf!E(*xCD5DK1/WGTK)*WRAl<RWjBQyi!qSI+rXW>H0L9AtWuu/3Cs5HKZ!B)JCwUTM`.

## Closure procedure

1. Run the cumulative dependency-scoped validation through Iteration 20.
2. Execute the pinned model locally and freeze its exact integer/hash identities in the Iteration 20 contract and implementation record.
3. Re-run the cumulative validation after freezing the record.
4. Publish the restart-state commit to `agent/pass215-iteration20-terminal-closure` and open the terminal-closure PR against `main`.
5. Require the Iteration 20 workflow to check out exactly the published head, reproduce the frozen identities in two independent processes, and upload its artifact.
6. If exact-head validation succeeds, do not create another commit. Merge the terminal-closure PR and verify the merged main state contains the validated tree.

Pass 216 has no restart state because the number is reserved. After merge, continue with Pass 217 and then Pass 219.

## Failure policy

Fail closed on any changed parent identity, checkpoint-root mismatch, absent reused content, incorrect incremental-byte accounting, blob-address mismatch, reconstruction mismatch, restore replay, changed token/root chain, output-projection pruning, float canonicalization, broader authority claim, or attempted Pass 216 dependency.
