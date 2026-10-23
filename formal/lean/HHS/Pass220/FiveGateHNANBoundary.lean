import HHS.Pass220.HNANPhase5184
import HHS.Pass219.QGUHNANTransport
import HHS.Alignment.ReciprocalTensor

namespace HHS.Pass220.FiveGateHNANBoundary

/-- A rank-one circuit retains the two ordered roles and its source position. -/
structure Rank1Circuit where
  periodicity : String
  quantization : String
  sourceOffset : Nat
  predecessor : Nat
deriving Repr, BEq, DecidableEq

/-- A candidate HNAN bypass does not mint canonical proof authority. -/
structure PhaseSnapshot where
  curvature : String
  phase : String
  writes : Nat
deriving Repr, BEq, DecidableEq

def hnanBypass (state : PhaseSnapshot) : PhaseSnapshot := state

theorem hnan_gain_one_no_phase_write (s : PhaseSnapshot) :
    (hnanBypass s).curvature = s.curvature ∧
    (hnanBypass s).phase = s.phase ∧
    (hnanBypass s).writes = s.writes := by
  exact ⟨rfl, rfl, rfl⟩


/-- A declared zero is a candidate, not a trusted witness. The ordered
    boundary always preserves the original frame until native admission. -/
structure CandidateBoundary where
  prior : PhaseSnapshot
  declaredZero : Bool
  candidateOnly : Bool
  authorizedCommit : Bool
deriving Repr, BEq, DecidableEq

def inspectBoundary (s : PhaseSnapshot) (declaredZero : Bool) :
    CandidateBoundary :=
  { prior := hnanBypass s, declaredZero := declaredZero,
    candidateOnly := true, authorizedCommit := false }

theorem bypass_no_write_even_on_zero_declaration
    (s : PhaseSnapshot) :
    (inspectBoundary s true).prior.writes = s.writes := by
  rfl

theorem boundary_never_mints_from_boolean
    (s : PhaseSnapshot) (declaredZero : Bool) :
    (inspectBoundary s declaredZero).authorizedCommit = false ∧
    (inspectBoundary s declaredZero).candidateOnly = true := by
  exact ⟨rfl, rfl⟩

/-- Proofs inherit ordered roles; they cannot exchange xy with yx. -/
theorem phase_order_inherited :
    HHS.Pass220.HNANPhase5184.PhaseCell.xy ≠
      HHS.Pass220.HNANPhase5184.PhaseCell.yx :=
  HHS.Pass220.HNANPhase5184.forwardReverseDistinct.1

theorem transport_epsilon_inherited (q c d : Nat) :
    (HHS.Pass219.QGUHNANTransport.transportHNAN q c d).base =
      .xyPlusEpsilon :=
  HHS.Pass219.QGUHNANTransport.qgu_hnan_preserves_epsilon_terminal q c d

/-- These are source addresses, not proofs of gate truth. -/
def fiveGateOffsets : List Nat := [54, 139, 223, 229, 276]
theorem fiveGateOffsetsDistinct : fiveGateOffsets.Nodup := by
  decide

theorem fiveGateOffsetStrictOrder :
    54 < 139 ∧ 139 < 223 ∧ 223 < 229 ∧ 229 < 276 := by
  decide

/-- Preserve the parser-derived nesting geometry of all five native gates. -/
def fiveGateDepths : List Nat := [3, 3, 1, 0, 1]

theorem fiveGateDepthsExact :
    fiveGateDepths = [3, 3, 1, 0, 1] := by
  rfl

theorem fiveGateLayoutLengths :
    fiveGateOffsets.length = fiveGateDepths.length ∧
    fiveGateOffsets.length = 5 := by
  decide

theorem fiveGateOffsetsExact :
    fiveGateOffsets = [54, 139, 223, 229, 276] := by
  rfl


/-- This cursor checks source-address sequence only, not algebraic closure.
    A gate at a later source address cannot be consumed early. -/
def nextGateOffset (cursor : Nat) : Option Nat :=
  fiveGateOffsets[cursor]?

def advanceGateCursor (cursor offset : Nat) : Option Nat :=
  if nextGateOffset cursor == some offset then some (cursor + 1) else none

theorem rejects_second_gate_first : advanceGateCursor 0 139 = none := by
  decide

theorem rejects_skipped_third_gate : advanceGateCursor 1 223 = none := by
  decide

theorem ordered_five_gate_cursor :
    (do
      let a ← advanceGateCursor 0 54
      let b ← advanceGateCursor a 139
      let c ← advanceGateCursor b 223
      let d ← advanceGateCursor c 229
      advanceGateCursor d 276) = some 5 := by
  decide

theorem rejects_sixth_gate : advanceGateCursor 5 276 = none := by
  decide


/-- Source cursor is separate from gate truth: a failed gate cannot advance. -/
def advanceVerifiedGate (cursor offset : Nat) (nativeGateClosed : Bool) : Option Nat :=
  if nativeGateClosed then advanceGateCursor cursor offset else none

theorem rejected_gate_does_not_advance (cursor offset : Nat) :
    advanceVerifiedGate cursor offset false = none := by
  rfl

theorem wrong_offset_does_not_advance (cursor : Nat) (offset : Nat)
    (h : advanceGateCursor cursor offset = none) :
    advanceVerifiedGate cursor offset true = none := by
  simp [advanceVerifiedGate, h]

theorem all_five_require_closed_gate_flags :
    (do
      let a ← advanceVerifiedGate 0 54 true
      let b ← advanceVerifiedGate a 139 true
      let c ← advanceVerifiedGate b 223 true
      let d ← advanceVerifiedGate c 229 true
      advanceVerifiedGate d 276 true) = some 5 := by
  decide

theorem failed_third_gate_blocks_terminal :
    (do
      let a ← advanceVerifiedGate 0 54 true
      let b ← advanceVerifiedGate a 139 true
      let c ← advanceVerifiedGate b 223 false
      let d ← advanceVerifiedGate c 229 true
      advanceVerifiedGate d 276 true) = none := by
  decide

def newVM81Authority : Bool := false
def newHashMintAuthority : Bool := false
theorem local_formalization_fail_closed :
    newVM81Authority = false ∧ newHashMintAuthority = false := by
  exact ⟨rfl, rfl⟩

end HHS.Pass220.FiveGateHNANBoundary
