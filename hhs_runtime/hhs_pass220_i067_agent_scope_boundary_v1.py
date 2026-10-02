"""Pass 220 I067 — Agent scope boundary and workflow-preservation kernel.

The boundary is intentionally request-local:
- admitted work executes inside the externally authorized envelope;
- denied work cannot mutate that envelope and terminates only that request;
- independent later authorized steps remain admissible;
- agent-local transitions cannot add capabilities/resources/interfaces or rewrite
  the user semantic root;
- only an explicit external-user-governor grant may expand authority;
- transient retry is finite and budgeted.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import Enum
from typing import Iterable, Sequence

SCHEMA = "HHS_PASS_220_I067_AGENT_SCOPE_BOUNDARY_V1"
VERSION = "1.0.0"


class Decision(str, Enum):
    EXECUTE = "EXECUTE"
    DENY = "DENY"
    RETRY = "RETRY"
    FAIL = "FAIL"


class Outcome(str, Enum):
    SUCCESS = "SUCCESS"
    TRANSIENT_FAILURE = "TRANSIENT_FAILURE"
    PERMANENT_FAILURE = "PERMANENT_FAILURE"


@dataclass(frozen=True)
class Scope:
    capabilities: frozenset[str]
    readable: frozenset[str]
    writable: frozenset[str]
    interfaces: frozenset[str]
    step_budget: int
    retry_budget: int
    semantic_root: str

    def __post_init__(self) -> None:
        if self.step_budget < 0 or self.retry_budget < 0:
            raise ValueError("scope budgets must be non-negative")
        if not self.semantic_root:
            raise ValueError("semantic_root must be non-empty")


@dataclass(frozen=True)
class Request:
    request_id: str
    capability: str
    reads: frozenset[str] = frozenset()
    writes: frozenset[str] = frozenset()
    interfaces: frozenset[str] = frozenset()
    semantic_root: str = ""

    def __post_init__(self) -> None:
        if not self.request_id or not self.capability or not self.semantic_root:
            raise ValueError("request_id, capability, and semantic_root are required")


@dataclass(frozen=True)
class Transition:
    request_id: str
    decision: Decision
    next_scope: Scope
    reasons: tuple[str, ...]
    request_terminal: bool
    workflow_continues: bool
    retry_allowed: bool
    mutation_authorized: bool

    def to_dict(self) -> dict:
        out = asdict(self)
        out["decision"] = self.decision.value
        out["next_scope"] = scope_to_dict(self.next_scope)
        return out


def scope_to_dict(scope: Scope) -> dict:
    return {
        "capabilities": sorted(scope.capabilities),
        "readable": sorted(scope.readable),
        "writable": sorted(scope.writable),
        "interfaces": sorted(scope.interfaces),
        "step_budget": scope.step_budget,
        "retry_budget": scope.retry_budget,
        "semantic_root": scope.semantic_root,
    }


def required_scope(
    workflow: Iterable[Request],
    *,
    semantic_root: str,
    retry_budget: int = 0,
) -> Scope:
    """Compute the exact declared workflow requirement as an audit projection.

    This function does not mutate or shrink a live externally authorized scope.
    """
    requests = tuple(workflow)
    for request in requests:
        if request.semantic_root != semantic_root:
            raise ValueError("workflow request semantic root diverges from declared root")
    return Scope(
        capabilities=frozenset(r.capability for r in requests),
        readable=frozenset().union(*(r.reads for r in requests)),
        writable=frozenset().union(*(r.writes for r in requests)),
        interfaces=frozenset().union(*(r.interfaces for r in requests)),
        step_budget=len(requests),
        retry_budget=retry_budget,
        semantic_root=semantic_root,
    )


def missing_requirements(scope: Scope, request: Request) -> tuple[str, ...]:
    reasons: list[str] = []
    if request.capability not in scope.capabilities:
        reasons.append("CAPABILITY_OUTSIDE_SCOPE")
    if not request.reads <= scope.readable:
        reasons.append("READ_OUTSIDE_SCOPE")
    if not request.writes <= scope.writable:
        reasons.append("WRITE_OUTSIDE_SCOPE")
    if not request.interfaces <= scope.interfaces:
        reasons.append("INTERFACE_OUTSIDE_SCOPE")
    if request.semantic_root != scope.semantic_root:
        reasons.append("SEMANTIC_ROOT_DIVERGENCE")
    if scope.step_budget <= 0:
        reasons.append("STEP_BUDGET_EXHAUSTED")
    return tuple(reasons)


def request_admitted(scope: Scope, request: Request) -> bool:
    return not missing_requirements(scope, request)


def decide_request(scope: Scope, request: Request) -> Decision:
    return Decision.EXECUTE if request_admitted(scope, request) else Decision.DENY


def transition(scope: Scope, request: Request, outcome: Outcome) -> Transition:
    reasons = missing_requirements(scope, request)
    if reasons:
        return Transition(
            request_id=request.request_id,
            decision=Decision.DENY,
            next_scope=scope,
            reasons=reasons,
            request_terminal=True,
            workflow_continues=True,
            retry_allowed=False,
            mutation_authorized=False,
        )

    consumed = replace(scope, step_budget=scope.step_budget - 1)
    if outcome is Outcome.SUCCESS:
        return Transition(
            request_id=request.request_id,
            decision=Decision.EXECUTE,
            next_scope=consumed,
            reasons=(),
            request_terminal=True,
            workflow_continues=True,
            retry_allowed=False,
            mutation_authorized=True,
        )

    if outcome is Outcome.TRANSIENT_FAILURE and scope.retry_budget > 0:
        return Transition(
            request_id=request.request_id,
            decision=Decision.RETRY,
            next_scope=replace(consumed, retry_budget=scope.retry_budget - 1),
            reasons=("TRANSIENT_FAILURE",),
            request_terminal=False,
            workflow_continues=True,
            retry_allowed=True,
            mutation_authorized=True,
        )

    reason = "RETRY_BUDGET_EXHAUSTED" if outcome is Outcome.TRANSIENT_FAILURE else "PERMANENT_FAILURE"
    return Transition(
        request_id=request.request_id,
        decision=Decision.FAIL,
        next_scope=consumed,
        reasons=(reason,),
        request_terminal=True,
        workflow_continues=True,
        retry_allowed=False,
        mutation_authorized=True,
    )


def scope_covers_scope(authorized: Scope, required: Scope) -> bool:
    return (
        required.capabilities <= authorized.capabilities
        and required.readable <= authorized.readable
        and required.writable <= authorized.writable
        and required.interfaces <= authorized.interfaces
        and required.step_budget <= authorized.step_budget
        and required.retry_budget <= authorized.retry_budget
        and required.semantic_root == authorized.semantic_root
    )


def audit_workflow(authorized_scope: Scope, workflow: Sequence[Request]) -> dict:
    required = required_scope(
        workflow,
        semantic_root=authorized_scope.semantic_root,
        retry_budget=0,
    )
    per_request = [request_admitted(authorized_scope, request) for request in workflow]
    workflow_preserved = scope_covers_scope(authorized_scope, required) and all(per_request)
    return {
        "schema": "HHS_PASS_220_I067_AGENT_SCOPE_WORKFLOW_AUDIT_V1",
        "workflow_preserved": workflow_preserved,
        "required_scope": scope_to_dict(required),
        "authorized_scope": scope_to_dict(authorized_scope),
        "all_requests_individually_admitted": all(per_request),
        "live_scope_was_shrunk": False,
        "scope_projection_is_audit_only": True,
    }


def _coding_workflow(semantic_root: str) -> tuple[Request, ...]:
    return (
        Request("inspect", "repo.read", reads=frozenset({"repo"}), semantic_root=semantic_root),
        Request("patch", "repo.write", reads=frozenset({"repo"}), writes=frozenset({"workspace"}), semantic_root=semantic_root),
        Request("test", "test.run", reads=frozenset({"repo", "workspace"}), interfaces=frozenset({"test-runner"}), semantic_root=semantic_root),
        Request("commit", "repo.commit", reads=frozenset({"workspace"}), interfaces=frozenset({"git"}), semantic_root=semantic_root),
    )


def run_agent_scope_boundary_self_test() -> dict:
    semantic_root = "user-spec:pass220-i067"
    workflow = _coding_workflow(semantic_root)
    authorized = Scope(
        capabilities=frozenset({"repo.read", "repo.write", "test.run", "repo.commit"}),
        readable=frozenset({"repo", "workspace"}),
        writable=frozenset({"workspace"}),
        interfaces=frozenset({"test-runner", "git"}),
        step_budget=8,
        retry_budget=2,
        semantic_root=semantic_root,
    )
    audit = audit_workflow(authorized, workflow)

    denied = Request(
        "root-write",
        "host.root.write",
        writes=frozenset({"/"}),
        semantic_root=semantic_root,
    )
    denied_transition = transition(authorized, denied, Outcome.SUCCESS)
    later_authorized = transition(denied_transition.next_scope, workflow[2], Outcome.SUCCESS)


    semantic_drift = transition(
        authorized,
        Request("rewrite-user-semantics", "repo.write", writes=frozenset({"workspace"}), semantic_root="agent-reinterpreted-root"),
        Outcome.SUCCESS,
    )

    retry_scope = Scope(
        capabilities=frozenset({"test.run"}),
        readable=frozenset({"workspace"}),
        writable=frozenset(),
        interfaces=frozenset({"test-runner"}),
        step_budget=4,
        retry_budget=2,
        semantic_root=semantic_root,
    )
    retry_request = Request(
        "flaky-test",
        "test.run",
        reads=frozenset({"workspace"}),
        interfaces=frozenset({"test-runner"}),
        semantic_root=semantic_root,
    )
    retry_trace: list[str] = []
    current = retry_scope
    for _ in range(3):
        result = transition(current, retry_request, Outcome.TRANSIENT_FAILURE)
        retry_trace.append(result.decision.value)
        current = result.next_scope

    checks = {
        "declared_workflow_preserved": audit["workflow_preserved"],
        "audit_does_not_shrink_live_scope": not audit["live_scope_was_shrunk"],
        "denied_request_has_no_scope_side_effect": denied_transition.next_scope == authorized,
        "denied_request_is_terminal": denied_transition.request_terminal and not denied_transition.retry_allowed,
        "denial_does_not_poison_workflow": later_authorized.decision is Decision.EXECUTE,
        "agent_transition_preserves_capabilities": later_authorized.next_scope.capabilities == authorized.capabilities,
        "no_in_band_grant_api": "apply_grant" not in globals(),
        "semantic_drift_rejected": semantic_drift.decision is Decision.DENY and semantic_drift.next_scope == authorized,
        "retry_is_finite": retry_trace == ["RETRY", "RETRY", "FAIL"],
        "no_generic_soft_refusal_outcome": "REFUSE" not in {d.value for d in Decision},
    }
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "ok": all(checks.values()),
        "check_count": len(checks),
        "pass_count": sum(bool(v) for v in checks.values()),
        "checks": checks,
        "workflow_audit": audit,
        "denied_transition": denied_transition.to_dict(),
        "later_authorized_transition": later_authorized.to_dict(),
        "retry_trace": retry_trace,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_agent_scope_boundary_self_test(), indent=2, sort_keys=True))
