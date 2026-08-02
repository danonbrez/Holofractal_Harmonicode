# Pass 189 Iteration 2 restart record

- Authoritative base: `main @ 992b4e92a54d4656d66af4edfab7e03922addca6`
- Parent implementation merge: `a1a55a4f621ff3678f5af81119439e9558cf9db4`
- Branch: `agent/pass189-iteration2-calibration-causal`
- Merge target: `main`
- Scope: persistent exact calibration ledger, bounded output admission, joint causal batches, checkpoint/recovery, API/UI, DigitalOcean durable state
- Vercel: excluded from scope and acceptance
- Validation command: `make validate` from `native_projects/hhs_pass189_hqlh_runtime`
- Local Iteration 2 validation: 11 unit tests and Iteration 2 surface smoke test passed
- External DigitalOcean mutation: not performed from the implementation environment
- Real hardware calibration: not present and not claimed
- Next action after repository merge: run `deployment/digitalocean/install.sh` on the authoritative host and record real device-specific calibration in a later iteration
