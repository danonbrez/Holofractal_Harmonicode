import Std

namespace HHS.Pass220.AgentScopeBoundary

/-- Admission has only an executable state or a typed denial. -/
inductive Decision
  | execute
  | deny
deriving Repr, BEq, DecidableEq

/-- The externally authorized envelope carried by an agent workflow. -/
structure Scope where
  capabilities : List String
  readable : List String
  writable : List String
  interfaces : List String
  steps : Nat
  retries : Nat
  semanticRoot : String
deriving Repr, BEq, DecidableEq

/-- Per-request facts computed by the executable boundary. -/
structure Admission where
  withinAuthority : Bool
  semanticsMatch : Bool
deriving Repr, BEq, DecidableEq

/-- A request is admitted only when authority and semantics match and work remains. -/
def admitted (s : Scope) (a : Admission) : Bool :=
  a.withinAuthority && a.semanticsMatch && !(s.steps == 0)

/-- Admission never has a third, untyped soft-refusal outcome. -/
def decision (s : Scope) (a : Admission) : Decision :=
  if admitted s a then .execute else .deny

/-- Agent-local execution may consume a step but cannot rewrite authority fields. -/
def agentNext (s : Scope) (a : Admission) : Scope :=
  if admitted s a then { s with steps := s.steps - 1 } else s

theorem admitted_executes (s : Scope) (a : Admission)
    (h : admitted s a = true) :
    decision s a = .execute := by
  simp [decision, h]

theorem denied_state_unchanged (s : Scope) (a : Admission)
    (h : admitted s a = false) :
    agentNext s a = s := by
  simp [agentNext, h]

theorem agent_preserves_capabilities (s : Scope) (a : Admission) :
    (agentNext s a).capabilities = s.capabilities := by
  unfold agentNext
  split <;> rfl

theorem agent_preserves_readable (s : Scope) (a : Admission) :
    (agentNext s a).readable = s.readable := by
  unfold agentNext
  split <;> rfl

theorem agent_preserves_writable (s : Scope) (a : Admission) :
    (agentNext s a).writable = s.writable := by
  unfold agentNext
  split <;> rfl

theorem agent_preserves_interfaces (s : Scope) (a : Admission) :
    (agentNext s a).interfaces = s.interfaces := by
  unfold agentNext
  split <;> rfl

theorem agent_preserves_semantic_root (s : Scope) (a : Admission) :
    (agentNext s a).semanticRoot = s.semanticRoot := by
  unfold agentNext
  split <;> rfl

theorem agent_steps_nonincreasing (s : Scope) (a : Admission) :
    (agentNext s a).steps ≤ s.steps := by
  unfold agentNext
  split
  · exact Nat.sub_le _ _
  · exact Nat.le_refl _

/-- Retry is a consumable budget rather than a self-renewing loop. -/
def retryNext (n : Nat) : Nat := n - 1

theorem retry_budget_nonincreasing (n : Nat) :
    retryNext n ≤ n := by
  exact Nat.sub_le _ _

theorem positive_retry_consumes_one (n : Nat) :
    retryNext (n + 1) = n := by
  simp [retryNext]

/-- An in-band agent grant attempt is an identity operation on authority. -/
def agentGrantAttempt
    (current requested : List String) : List String :=
  current

theorem agent_cannot_self_grant
    (current requested : List String) :
    agentGrantAttempt current requested = current := by
  rfl

/-- User semantics cannot be replaced by an agent-local rewrite attempt. -/
def agentSemanticRewriteAttempt
    (current replacement : String) : String :=
  current

theorem agent_cannot_rewrite_user_semantics
    (current replacement : String) :
    agentSemanticRewriteAttempt current replacement = current := by
  rfl

/-- A denial is local to the request: it does not poison the workflow scope. -/
def denyRequest (s : Scope) : Scope := s

theorem denial_is_request_local (s : Scope) :
    denyRequest s = s := by
  rfl

end HHS.Pass220.AgentScopeBoundary
