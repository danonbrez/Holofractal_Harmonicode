import HHS.Alignment.ReciprocalTensor

namespace HHS.Pass219.QGUHNANTransport

/-- Canonical QGU phase ring. -/
def phaseRing : Nat := 72

/-- Exact additive QGU transport excess: (c*q^2 + d*q^4) mod 72. -/
def qguDelta (q c d : Nat) : Nat :=
  (c * q ^ 2 + d * q ^ 4) % phaseRing

/-- Add the QGU excess to an already-addressed phase. -/
def transportPhase (phase q c d : Nat) : Nat :=
  (phase + qguDelta q c d) % phaseRing

theorem phaseRing_pos : 0 < phaseRing := by
  decide

theorem qguDelta_lt_phaseRing (q c d : Nat) :
    qguDelta q c d < phaseRing := by
  exact Nat.mod_lt _ phaseRing_pos

theorem transportPhase_lt_phaseRing (phase q c d : Nat) :
    transportPhase phase q c d < phaseRing := by
  exact Nat.mod_lt _ phaseRing_pos

theorem qguDelta_zero_coefficients (q : Nat) :
    qguDelta q 0 0 = 0 := by
  simp [qguDelta]

/-- Ordered product channels remain typed and non-interchangeable. -/
inductive OrderedProduct
  | xy
  | yx
  | zw
  | wz
deriving Repr, BEq, DecidableEq

structure TransportedProduct where
  base : OrderedProduct
  delta : Nat
deriving Repr, BEq, DecidableEq

def transportProduct (base : OrderedProduct) (q c d : Nat) :
    TransportedProduct :=
  { base := base, delta := qguDelta q c d }

theorem qgu_transport_preserves_xy_yx_distinction (q c d : Nat) :
    (transportProduct .xy q c d).base ≠
      (transportProduct .yx q c d).base := by
  simp [transportProduct]

theorem qgu_transport_preserves_zw_wz_distinction (q c d : Nat) :
    (transportProduct .zw q c d).base ≠
      (transportProduct .wz q c d).base := by
  simp [transportProduct]

/--
The symbolic QGU ratio is retained as an ordered provenance object.
The executable transport is qguDelta; this structure forbids silently
identifying the ratio AST with the additive phase projection.
-/
structure QGUKernelAST where
  numerator : List String
  denominator : List String
deriving Repr, BEq, DecidableEq

def canonicalKernel : QGUKernelAST :=
  {
    numerator := ["xy", "cq^2", "dq^4"]
    denominator := ["xy", "cq^2"]
  }

theorem canonical_kernel_numerator_exact :
    canonicalKernel.numerator = ["xy", "cq^2", "dq^4"] := by
  rfl

theorem canonical_kernel_denominator_exact :
    canonicalKernel.denominator = ["xy", "cq^2"] := by
  rfl

theorem canonical_kernel_views_are_not_identical :
    canonicalKernel.numerator ≠ canonicalKernel.denominator := by
  decide

/-- HNAN terminal identity: QGU transports xy+epsilon, never bare xy. -/
inductive HNANTerminal
  | xyPlusEpsilon
  | bareXY
deriving Repr, BEq, DecidableEq

structure TransportedHNAN where
  base : HNANTerminal
  delta : Nat
deriving Repr, BEq, DecidableEq

def transportHNAN (q c d : Nat) : TransportedHNAN :=
  { base := .xyPlusEpsilon, delta := qguDelta q c d }

theorem qgu_hnan_preserves_epsilon_terminal (q c d : Nat) :
    (transportHNAN q c d).base = .xyPlusEpsilon := by
  rfl

theorem qgu_hnan_rejects_bare_xy_terminal (q c d : Nat) :
    (transportHNAN q c d).base ≠ .bareXY := by
  simp [transportHNAN]

structure QGUHNANReceipt where
  phaseRing72 : Bool
  ratioKernelRetained : Bool
  orderedProductsPreserved : Bool
  epsilonTerminalPreserved : Bool
  hostFloatAuthority : Bool
  scalarCancellationAuthorized : Bool
deriving Repr, BEq, DecidableEq

def QGUHNANReceipt.admitted (r : QGUHNANReceipt) : Prop :=
  r.phaseRing72 = true ∧
  r.ratioKernelRetained = true ∧
  r.orderedProductsPreserved = true ∧
  r.epsilonTerminalPreserved = true ∧
  r.hostFloatAuthority = false ∧
  r.scalarCancellationAuthorized = false

theorem admitted_forbids_host_float
    (r : QGUHNANReceipt)
    (h : r.admitted) :
    r.hostFloatAuthority = false :=
  h.2.2.2.2.1

theorem admitted_forbids_scalar_cancellation
    (r : QGUHNANReceipt)
    (h : r.admitted) :
    r.scalarCancellationAuthorized = false :=
  h.2.2.2.2.2

end HHS.Pass219.QGUHNANTransport
