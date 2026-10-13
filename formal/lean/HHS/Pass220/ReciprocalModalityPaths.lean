import Std

namespace HHS.Pass220.ReciprocalModalityPaths

/-- Ordered syntax: tensor multiplication and roots are not host scalar arithmetic. -/
inductive Expr where
  | atom : String → Expr
  | orderedMul : Expr → Expr → Expr
  | orderedNeg : Expr → Expr
  | orderedRoot : Expr → Expr
  | pow4 : Expr → Expr
deriving Repr, DecidableEq

open Expr

/-- The four terms are recorded without commutation or scalar cancellation. -/
def ab : Expr := orderedMul (atom "A") (atom "B")
def p4 : Expr := pow4 (atom "P")
def firstReciprocal : Expr :=
  orderedMul (orderedMul (atom "P_1") (atom "P_2"))
    (orderedRoot (orderedMul (atom "B") (atom "A")))
def secondReciprocal : Expr :=
  orderedNeg (orderedMul (orderedMul (atom "P_2") (atom "P_1"))
    (orderedRoot (orderedMul (atom "A") (atom "B"))))

theorem reciprocal_orders_distinct :
    orderedMul (atom "P_1") (atom "P_2") ≠
    orderedMul (atom "P_2") (atom "P_1") := by
  decide

/-- Native equality-chain obligation; not a scalar equality theorem. -/
def OrderedReciprocalClosure (R : Expr → Expr → Prop) : Prop :=
  R ab p4 ∧ R p4 firstReciprocal ∧ R firstReciprocal secondReciprocal

/-- Exact metadata modality node. P is index metadata, not a new free variable. -/
structure ModalityNode where
  pIndex : Int
  modality : String
deriving Repr, DecidableEq

/-- Certified directed bridge, including the proof of its reversible route.
    Native admission and phase ancestry remain prerequisites for instances. -/
structure ReversibleBridge (Admitted : ModalityNode → ModalityNode → Prop)
    (a b : ModalityNode) where
  forward : Admitted a b
  backward : Admitted b a

/-- A finite chain of certified directed transitions. -/
inductive Path (Admitted : ModalityNode → ModalityNode → Prop) :
    ModalityNode → ModalityNode → Prop where
  | refl (a) : Path Admitted a a
  | step {a b c} : Admitted a b → Path Admitted b c → Path Admitted a c

theorem path_trans {Admitted : ModalityNode → ModalityNode → Prop}
    {a b c : ModalityNode}
    (abPath : Path Admitted a b) (bcPath : Path Admitted b c) :
    Path Admitted a c := by
  induction abPath with
  | refl _ => exact bcPath
  | step edge _ ih => exact .step edge ih

theorem bridge_forward {Admitted : ModalityNode → ModalityNode → Prop}
    {a b : ModalityNode} (w : ReversibleBridge Admitted a b) :
    Path Admitted a b := by
  exact .step w.forward (.refl b)

theorem bridge_reverse {Admitted : ModalityNode → ModalityNode → Prop}
    {a b : ModalityNode} (w : ReversibleBridge Admitted a b) :
    Path Admitted b a := by
  exact .step w.backward (.refl a)

/-- This explicitly requires actual native admission for every pair of
    admitted modalities. It does NOT claim the obligation is already proved. -/
def UniversalReversibleCoverage
    (Admitted : ModalityNode → ModalityNode → Prop)
    (Membership : ModalityNode → Prop) : Prop :=
  ∀ a b, Membership a → Membership b →
    ∃ (pBridge : ModalityNode),
      Path Admitted a pBridge ∧ Path Admitted pBridge b ∧
      Path Admitted b pBridge ∧ Path Admitted pBridge a

theorem admitted_coverage_implies_bidirectional_paths
    {Admitted : ModalityNode → ModalityNode → Prop}
    {Membership : ModalityNode → Prop}
    (coverage : UniversalReversibleCoverage Admitted Membership)
    (a b : ModalityNode) (ha : Membership a) (hb : Membership b) :
    Path Admitted a b ∧ Path Admitted b a := by
  obtain ⟨bridge, ab, bb, ba, aa⟩ := coverage a b ha hb
  exact ⟨path_trans ab bb, path_trans ba aa⟩

/-- Ordered reciprocal closure is a separately carried global prerequisite. -/
structure GlobalPathCertificate
    (R : Expr → Expr → Prop)
    (Admitted : ModalityNode → ModalityNode → Prop)
    (Membership : ModalityNode → Prop) where
  reciprocal : OrderedReciprocalClosure R
  modalityCoverage : UniversalReversibleCoverage Admitted Membership

end HHS.Pass220.ReciprocalModalityPaths
