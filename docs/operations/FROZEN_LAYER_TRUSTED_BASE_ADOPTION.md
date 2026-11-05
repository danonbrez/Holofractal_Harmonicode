# Frozen-layer trusted-base gate — adoption and verification

This is an operational runbook, not evidence that GitHub repository rules have already been changed.

## Dependency order

1. Review and merge PR #864 (contract).
2. Validate and merge PR #866 (initial scoped guard).
3. Validate and merge PR #867 (manifest).
4. Review and merge PR #868 (trusted-base workflow); only then can the base-owned workflow apply reliably to subsequent main-targeting PRs.

## Required GitHub repository rule

Require status check **frozen-layer-trusted-base** from the workflow **HHS frozen-layer trusted-base guard** on protected main; prohibit bypass except separately controlled administrative emergency recovery; disallow force pushes and uncontrolled rule edits. Record actual rule configuration and a successful check ID before claiming enforcement.

## Negative test matrix on a disposable PR after activation

- Edit a registered native path: **reject**.
- Delete or weaken the frozen registry: **reject**.
- Modify either guard script or either guard workflow: **reject**.
- Introduce an additive higher-order file without touching protected paths: source-level check may **pass**, but computational admission remains separate.
- Remove/rename a protected file: **reject**.
- Attempt to bypass via proposed-branch edits to its own policy: **reject using base-owned policy**.

Use the base-commit workflow and base-commit scripts. Never execute a fork/PR candidate's scripts or dependencies in a privileged `pull_request_target` job. Before declaring closure, review logs for these adversarial tests and inspect the actual protected-branch rule.

## Limits

Current registry includes exactly two native paths and does not independently attest their mathematical closure. This policy is not the entire frozen service inventory. An approved foundational defect repair must use a separate explicitly authorized and evidenced process; the present gate has no automatic bypass for it.

The acceptance relation `inherited invariants preserved ∧ new composition admitted ∧ frozen implementation unchanged` is not proven merely by this Git diff check. Lane 5, VM81, Hash72, Hash216, Lean/proof and production validation remain separate requirements.
