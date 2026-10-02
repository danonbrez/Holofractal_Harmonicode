from hhs_runtime.hhs_pass220_i067_agent_scope_boundary_v1 import (
    Decision,
    EXTERNAL_GRANT_AUTHORITY,
    Grant,
    Outcome,
    Request,
    Scope,
    apply_grant,
    audit_workflow,
    required_scope,
    run_agent_scope_boundary_self_test,
    transition,
)

SEM = "user-spec:test"


def base_scope() -> Scope:
    return Scope(
        capabilities=frozenset({"repo.read", "repo.write", "test.run"}),
        readable=frozenset({"repo", "workspace"}),
        writable=frozenset({"workspace"}),
        interfaces=frozenset({"test-runner"}),
        step_budget=6,
        retry_budget=2,
        semantic_root=SEM,
    )


def test_self_test_passes():
    result = run_agent_scope_boundary_self_test()
    assert result["ok"] is True
    assert result["status"] == "PASS"
    assert result["check_count"] == result["pass_count"] == 10


def test_denial_is_request_local_and_side_effect_free():
    scope = base_scope()
    denied = Request("root", "host.root.write", writes=frozenset({"/"}), semantic_root=SEM)
    result = transition(scope, denied, Outcome.SUCCESS)
    assert result.decision is Decision.DENY
    assert result.next_scope == scope
    assert result.request_terminal is True
    assert result.workflow_continues is True
    assert result.retry_allowed is False
    assert result.mutation_authorized is False

    later = Request("test", "test.run", reads=frozenset({"workspace"}), interfaces=frozenset({"test-runner"}), semantic_root=SEM)
    assert transition(result.next_scope, later, Outcome.SUCCESS).decision is Decision.EXECUTE


def test_authorized_workflow_is_not_under_scoped_or_implicitly_shrunk():
    scope = base_scope()
    workflow = (
        Request("read", "repo.read", reads=frozenset({"repo"}), semantic_root=SEM),
        Request("write", "repo.write", writes=frozenset({"workspace"}), semantic_root=SEM),
        Request("test", "test.run", reads=frozenset({"workspace"}), interfaces=frozenset({"test-runner"}), semantic_root=SEM),
    )
    required = required_scope(workflow, semantic_root=SEM)
    audit = audit_workflow(scope, workflow)
    assert required.capabilities == frozenset({"repo.read", "repo.write", "test.run"})
    assert audit["workflow_preserved"] is True
    assert audit["live_scope_was_shrunk"] is False
    assert audit["scope_projection_is_audit_only"] is True


def test_agent_cannot_self_grant_but_external_governor_can():
    scope = base_scope()
    grant = Grant(capabilities=frozenset({"deploy.publish"}), interfaces=frozenset({"deployment"}), step_budget_delta=1)
    rejected = apply_grant(scope, grant, authority="AGENT")
    assert rejected.accepted is False
    assert rejected.next_scope == scope

    accepted = apply_grant(scope, grant, authority=EXTERNAL_GRANT_AUTHORITY)
    assert accepted.accepted is True
    assert "deploy.publish" in accepted.next_scope.capabilities
    assert "deployment" in accepted.next_scope.interfaces
    assert accepted.next_scope.step_budget == scope.step_budget + 1


def test_semantic_root_cannot_drift_during_agent_transition():
    scope = base_scope()
    request = Request("semantic", "repo.write", writes=frozenset({"workspace"}), semantic_root="agent-root")
    result = transition(scope, request, Outcome.SUCCESS)
    assert result.decision is Decision.DENY
    assert "SEMANTIC_ROOT_DIVERGENCE" in result.reasons
    assert result.next_scope.semantic_root == SEM


def test_retry_budget_is_finite():
    scope = Scope(
        capabilities=frozenset({"test.run"}),
        readable=frozenset({"workspace"}),
        writable=frozenset(),
        interfaces=frozenset({"test-runner"}),
        step_budget=4,
        retry_budget=2,
        semantic_root=SEM,
    )
    request = Request("flaky", "test.run", reads=frozenset({"workspace"}), interfaces=frozenset({"test-runner"}), semantic_root=SEM)
    decisions = []
    for _ in range(3):
        result = transition(scope, request, Outcome.TRANSIENT_FAILURE)
        decisions.append(result.decision)
        scope = result.next_scope
    assert decisions == [Decision.RETRY, Decision.RETRY, Decision.FAIL]
    assert scope.retry_budget == 0


def test_admitted_success_preserves_authority_dimensions():
    scope = base_scope()
    request = Request("write", "repo.write", reads=frozenset({"repo"}), writes=frozenset({"workspace"}), semantic_root=SEM)
    result = transition(scope, request, Outcome.SUCCESS)
    assert result.decision is Decision.EXECUTE
    assert result.next_scope.capabilities == scope.capabilities
    assert result.next_scope.readable == scope.readable
    assert result.next_scope.writable == scope.writable
    assert result.next_scope.interfaces == scope.interfaces
    assert result.next_scope.semantic_root == scope.semantic_root
    assert result.next_scope.step_budget == scope.step_budget - 1
