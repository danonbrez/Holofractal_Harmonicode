import HHS.Pass220.HNANPhase5184

/-!
# Universal 5184-address binary and balanced-trinary preservation

This is a generic, lossless *witnessed representation* theorem over every
possible indexed assignment, not merely 5184 sample states. Two complete
trinary lanes are retained independently, with an ordered difference witness.

It does NOT claim arbitrary 5184-bit inputs can be reduced to a standalone
Hash72 generator. A 72-symbol digest is not a universal inverse payload.
-/

namespace HHS.Pass220.HNANFullStateSpacePreservation

abbrev Address := Fin 5184
abbrev BinaryFrame := Address → Bool

inductive Trit where
  | negative
  | neutral
  | positive
deriving Repr, BEq, DecidableEq

abbrev TritFrame := Address → Trit
abbrev TritCode := Bool × Bool

/-- Canonical two-bit codes for all three trinary values; 11 is invalid. -/
def packTrit : Trit → TritCode
  | .negative => (false, false)
  | .neutral => (false, true)
  | .positive => (true, false)

/-- Admission-sensitive decoder: noncanonical 11 is rejected. -/
def unpackTrit : TritCode → Option Trit
  | (false, false) => some .negative
  | (false, true) => some .neutral
  | (true, false) => some .positive
  | (true, true) => none

theorem tritRoundTrip (t : Trit) :
    unpackTrit (packTrit t) = some t := by
  cases t <;> rfl

theorem invalidTritCodeRejected :
    unpackTrit (true, true) = none := by
  rfl

theorem tritCodeValid (t : Trit) :
    packTrit t ≠ (true, true) := by
  cases t <;> decide

/-- Total inverse only used after admission; invalid codes are separately
    rejected by unpackTrit before this path may be admitted. -/
def unpackAdmitted : TritCode → Trit
  | (false, false) => .negative
  | (false, true) => .neutral
  | (true, false) => .positive
  | (true, true) => .negative

theorem tritAdmittedRoundTrip (t : Trit) :
    unpackAdmitted (packTrit t) = t := by
  cases t <;> rfl

def packFrame (t : TritFrame) : Address → TritCode :=
  fun i => packTrit (t i)

def unpackFrame (t : Address → TritCode) : TritFrame :=
  fun i => unpackAdmitted (t i)

/-- Pointwise proof holds for every address and trit, without enumeration. -/
theorem allTritAddressesRoundTrip (t : TritFrame) :
    unpackFrame (packFrame t) = t := by
  funext i
  exact tritAdmittedRoundTrip (t i)

theorem allPackedTritFramesInjective :
    Function.Injective packFrame := by
  intro a b h
  have hd := congrArg unpackFrame h
  exact (allTritAddressesRoundTrip a).symm.trans
    (hd.trans (allTritAddressesRoundTrip b))

/-- Ordered phase difference of complete first and second trinary lanes.
    The HNAN x/y and z/w products remain typed elsewhere; this is an exact
    symbolic/role-difference witness, not host commutation authority. -/
def tritValue : Trit → Int
  | .negative => -1
  | .neutral => 0
  | .positive => 1

def relativePhase (left right : Trit) : Int :=
  tritValue left - tritValue right

theorem relativePhaseReconstructsLeft (left right : Trit) :
    tritValue right + relativePhase left right = tritValue left := by
  simp [relativePhase, sub_eq_add_neg,
    add_assoc, add_left_comm, add_comm]

structure FullState where
  binary : BinaryFrame
  xyLane : TritFrame
  zwLane : TritFrame

/-- Each encoded state retains exactly one source bit, and two two-bit
    trinary channels per fixed address, plus their relative-phase witness. -/
structure EncodedState where
  binary : BinaryFrame
  xyCode : Address → TritCode
  zwCode : Address → TritCode
  difference : Address → Int

def encodeState (state : FullState) : EncodedState :=
  {
    binary := state.binary
    xyCode := packFrame state.xyLane
    zwCode := packFrame state.zwLane
    difference := fun i => relativePhase (state.xyLane i) (state.zwLane i)
  }

/-- Decoder's domain is restricted to canonical encoded values. The
    standalone unpackTrit rejects invalid pairs; no unrestricted arbitrary
    encoded input is admitted on this total proof projection. -/
def decodeState (encoded : EncodedState) : FullState :=
  {
    binary := encoded.binary
    xyLane := unpackFrame encoded.xyCode
    zwLane := unpackFrame encoded.zwCode
  }

theorem fullStateRoundTrip (state : FullState) :
    decodeState (encodeState state) = state := by
  cases state with
  | mk binary xyLane zwLane =>
    change
      FullState.mk binary (unpackFrame (packFrame xyLane))
        (unpackFrame (packFrame zwLane)) =
      FullState.mk binary xyLane zwLane
    rw [allTritAddressesRoundTrip, allTritAddressesRoundTrip]

theorem fullStateEncodingInjective :
    Function.Injective encodeState := by
  intro a b h
  have hd := congrArg decodeState h
  exact (fullStateRoundTrip a).symm.trans
    (hd.trans (fullStateRoundTrip b))

theorem allBinaryBitsRetained (state : FullState) (i : Address) :
    (decodeState (encodeState state)).binary i = state.binary i := by
  rw [fullStateRoundTrip]

theorem allXYTritsRetained (state : FullState) (i : Address) :
    (decodeState (encodeState state)).xyLane i = state.xyLane i := by
  rw [fullStateRoundTrip]

theorem allZWTritsRetained (state : FullState) (i : Address) :
    (decodeState (encodeState state)).zwLane i = state.zwLane i := by
  rw [fullStateRoundTrip]

theorem allRelativePhaseWitnessesRetained (state : FullState) (i : Address) :
    (encodeState state).difference i =
      tritValue (state.xyLane i) - tritValue (state.zwLane i) := by
  rfl

theorem allXYCodesAdmitted (state : FullState) (i : Address) :
    unpackTrit ((encodeState state).xyCode i) =
      some (state.xyLane i) := by
  exact tritRoundTrip (state.xyLane i)

theorem allZWCodesAdmitted (state : FullState) (i : Address) :
    unpackTrit ((encodeState state).zwCode i) =
      some (state.zwLane i) := by
  exact tritRoundTrip (state.zwLane i)

/-- Exact alternate VM81 and Hash72 coordinate address reconstructions. -/
def vmCoordinates (i : Address) : Nat × Nat := (i.val / 64, i.val % 64)
def hashCoordinates (i : Address) : Nat × Nat := (i.val / 72, i.val % 72)

theorem vm81CoordinatesPreserveAddress (i : Address) :
    (vmCoordinates i).1 * 64 + (vmCoordinates i).2 = i.val := by
  simpa [vmCoordinates, Nat.mul_comm, Nat.add_comm] using
    (Nat.mod_add_div i.val 64)

theorem hash72CoordinatesPreserveAddress (i : Address) :
    (hashCoordinates i).1 * 72 + (hashCoordinates i).2 = i.val := by
  simpa [hashCoordinates, Nat.mul_comm, Nat.add_comm] using
    (Nat.mod_add_div i.val 72)

theorem vm81AndHash72SharePosition (i : Address) :
    (vmCoordinates i).1 * 64 + (vmCoordinates i).2 =
    (hashCoordinates i).1 * 72 + (hashCoordinates i).2 := by
  rw [vm81CoordinatesPreserveAddress, hash72CoordinatesPreserveAddress]

/-- This proof is universal over all assigned frames but explicitly
    requires the additional trinary witness storage. -/
def fullStateSpaceCovered : Bool := true
def arbitraryRawCompressionIntoHash72Claimed : Bool := false
def newCanonicalAuthority : Bool := false

theorem scopeAndAuthority :
    fullStateSpaceCovered = true ∧
    arbitraryRawCompressionIntoHash72Claimed = false ∧
    newCanonicalAuthority = false := by
  decide

end HHS.Pass220.HNANFullStateSpacePreservation
