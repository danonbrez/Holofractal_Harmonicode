# Stateless-Resumable Agentic Delivery Policy

## 1. Normative rule

```text
EVERY AGENTIC TASK MUST BE RESTARTABLE
FROM REPOSITORY-VISIBLE STATE ALONE.
```

Conversation memory, private scratch state, an open process, an active shell, or an indefinitely retained agent thread MUST NOT be required to recover, continue, validate, merge, deploy, or close project work.

## 2. Mandatory checkpoint state

Before any long-running, failure-prone, externally dependent, installation, benchmark, build, deployment, or migration step, the agent MUST externalize repository-visible state containing:

- exact repository and authoritative base commit;
- active branch and intended merge target;
- files changed;
- commands already executed;
- captured validation results and remaining checks;
- deployment, installation, and environment state;
- concrete next action;
- exact blocker details when blocked;
- timeout, fallback, and replay instructions for commands that can hang;
- checksums, logs, and idempotent restart commands for external downloads or installations.

Repository-visible state MAY be stored in committed receipts, branch-local checkpoint files, pull-request descriptions, issues, workflow artifacts, or other durable repository records, provided the record is sufficient for an independent agent to resume without conversation context.

## 3. Bounded closure sequence

Near completion, the required closure sequence is:

```text
IMPLEMENT
→ DEPENDENCY-SCOPED VALIDATION
→ COMMIT
→ MERGE OR OPEN READY PR
→ VERIFY MAIN
→ RETURN COMPLETION RESPONSE
```

Work is not delivered merely because it exists in a local workspace, temporary branch, detached process, upload, or unmerged commit.

## 4. Forbidden indefinite states

An agent MUST NOT remain indefinitely in any of the following states:

- waiting after tests have completed;
- holding uncommitted changes in a private workspace;
- waiting for an internal subprocess without a timeout;
- retaining the only recovery instructions in thread context;
- repeatedly polling an unchanged condition;
- stopping after push without merge, ready pull request, blocked receipt, or user-facing response;
- treating conversation memory as required execution state;
- leaving a deployment without a terminal success, failure, or blocked classification.

## 5. Command and external-operation requirements

Every command that can hang MUST have:

1. a bounded timeout;
2. captured stdout and stderr;
3. a recorded exit status;
4. a defined fallback;
5. an exact resumable next command.

Every external installation or download MUST use resumable transfer where supported, checksum verification, durable logs, and idempotent scripts.

Every deployment operation MUST terminate in exactly one classification:

```text
SUCCESS | FAILURE | BLOCKED
```

## 6. Recovery receipt schema

A task that cannot continue MUST still close with a repository-visible recovery receipt containing at least:

```text
status: BLOCKED
repository: <owner/repository>
base_commit: <sha>
branch: <branch>
latest_commit: <sha>
worktree_clean: true|false
completed_scope: [...]
remaining_scope: [...]
files_changed: [...]
commands_executed: [...]
validation_results: [...]
remaining_checks: [...]
deployment_state: <state>
last_command: <command>
last_exit_status: <status>
blocker: <specific cause>
next_command: <exact resumable action>
merge_target: <branch>
merge_status: <main|PR|unmerged>
```

Additional fields SHOULD record source identities, checksums, artifacts, workflow runs, pull requests, environment constraints, and cleanup actions.

## 7. Branch and pull-request closure

- Use the authoritative main branch directly when safe.
- Otherwise use a short-lived task branch with an explicit merge target.
- After dependency-scoped validation, merge immediately or open a ready-to-merge pull request.
- A branch may remain unmerged only when the task is explicitly classified `BLOCKED` and a complete recovery receipt identifies the exact resumable action.
- Temporary execution-carrier branches and pull requests MUST be closed, reset, or otherwise made non-authoritative after their evidence has been externalized.

## 8. Delivery model

The HHS repository is governed as stateless-resumable corporate delivery:

```text
AGENT LOSS MUST NOT STRAND
IMPLEMENTATION,
EVIDENCE,
DEPLOYMENT KNOWLEDGE,
OR THE NEXT REQUIRED ACTION.
```
