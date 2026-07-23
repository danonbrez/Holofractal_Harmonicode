# Pass 105.4 — Production-Path Negative Attack Closure

Pass 105.4 replaces the synthetic Pass 101–105 negative-case records with 77 malformed workloads executed through their owning production implementations.

- Pass 101: 14/14
- Pass 102: 14/14
- Pass 103: 14/14
- Pass 104: 16/16
- Pass 105: 19/19
- Parallel test computations: 0
- Mock components: 0
- Failed attacks: 0

The test layer invokes the production attack entrypoints and checks observed typed rejections. It does not calculate replacement results.
