# Pass 220 I067 — Agent Scope Boundary

## Objective

I067 turns agent scope into an executable boundary that preserves authorized work instead of treating safety as a reason to globally stop the workflow.

The governing distinction is between the **externally authorized live envelope** and an **audit-only minimum-required projection**. The projection may identify missing authority or unnecessary authority, but it does not silently shrink, widen, or reinterpret the live scope.

## Boundary invariants

For an agent-local transition from scope S to S':

~~~text
capabilities(S') = capabilities(S)
readable(S')     = readable(S)
writable(S')     = writable(S)
interfaces(S')   = interfaces(S)
semanticRoot(S') = semanticRoot(S)
steps(S')       <= steps(S)
retries(S')     <= retries(S)
~~~

Authority expansion is a separate typed operation and is accepted only from EXTERNAL_USER_GOVERNOR.

A denied request has the transition:

~~~text
DENY(request, S) -> S
~~~

It is terminal for that request, has no boundary-authorized mutation, and does **not** globally poison the workflow. A later independent request is evaluated against the unchanged S.

An admitted request does not have a generic REFUSE execution outcome. Runtime failures remain typed as success, bounded transient retry, or permanent failure.

## Avoiding overconstraint

The scope compiler computes the union of requirements for the whole declared workflow. It is used to prove that the external envelope covers the workflow; it does not replace that envelope with the current step's narrower requirement. This prevents a safety mechanism from deleting permissions that a later authorized step legitimately needs.

## Python validation

Dependency-scoped execution on 2026-10-02:

~~~text
7 passed in 0.06s
~~~

The runtime self-test additionally reported 10/10 PASS, covering workflow preservation, request-local denial, semantic-root preservation, bounded retry, agent self-grant rejection, and explicit external expansion.

## Wolfram verification

The connected Wolfram Language kernel evaluated ten symbolic/exhaustive checks:

~~~text
HHS_PASS_220_I067_AGENT_SCOPE_BOUNDARY_WOLFRAM_V1
PASS
10 / 10
failed = {}
~~~

The bounded scans cover retry budgets 0..2048 and nonincreasing agent budgets 0..64. Boolean proof obligations cover exact workflow-scope compilation, denial side effects, independent continuation after denial, self-grant rejection, and explicit external grants.

## Lean surface

formal/lean/HHS/Pass220/AgentScopeBoundary.lean proves the structural properties directly over the typed transition model: admitted work maps to execution; denial leaves scope unchanged; agent-local transitions preserve authority dimensions and the semantic root; step/retry budgets do not increase; and agent authority cannot self-grant or rewrite the semantic root.

Lean kernel validation is delegated to the branch workflow with lake build, leanchecker, and axiom audit, matching the repository's current native Lean CI pattern.
