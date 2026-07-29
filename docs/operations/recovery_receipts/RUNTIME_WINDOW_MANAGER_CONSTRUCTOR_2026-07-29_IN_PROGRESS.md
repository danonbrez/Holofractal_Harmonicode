# RuntimeWindowManager Constructor Repair Checkpoint

```text
status: IN_PROGRESS
repository: danonbrez/Holofractal_Harmonicode
authoritative_base_commit: d41f0190f75f534434970664fa94ad227fecc792
branch: main
merge_target: main
worktree_clean: true
reported_browser_error: TypeError: ap is not a constructor
mapped_source: RuntimeOS constructor -> new RuntimeWindowManager()
root_cause: hhs_gui/runtime_os/core contained both RuntimeWindowManager.ts and RuntimeWindowManager.tsx; Vite resolved .tsx before .ts, selecting a React function instead of the constructible state class
completed_scope:
  - removed conflicting RuntimeWindowManager.tsx
  - changed Vite extension resolution to .ts before .tsx
  - added source validation rejecting the duplicate stem and asserting constructible class usage
remaining_scope:
  - run native/backend/frontend release gate
  - verify generated bundle instantiates the class implementation
  - publish regenerated dist to main
  - close validation-only PR
next_action: open validation-only PR from agent/validate-window-manager-constructor and run Build HHS Canonical Visual Runtime OS
```
