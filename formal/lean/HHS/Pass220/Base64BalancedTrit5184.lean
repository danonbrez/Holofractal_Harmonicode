import HHS.Pass220.HNANPhase5184

/-!
# Pass 220: exact radix correspondence for full 5184-bit VM81 frames

Three binary bits have eight outer tensor addresses, encoded by two balanced
trits in the supplied 3x3 HNAN Lo Shu tensor. The ninth, central (0,0) pair
is HNAN itself, not a spare or invalid state. Two such three-bit groups
form one Base64 sextet (64 binary states), represented by four trits.

This is a source-preserving ingress radix theorem; it neither rewrites
ordered HNAN products nor claims digest-only Hash72 inversion.
-/

namespace HHS.Pass220.Base64BalancedTrit5184

inductive Trit where
  | negative | neutral | positive
deriving Repr, BEq, DecidableEq

abbrev BinaryTriple := Bool × Bool × Bool
abbrev TritPair := Trit × Trit

/-- 3x3 tensor pair coordinates: -1/0/+1 in each dimension.
    The central (.neutral,.neutral) is the existing HNAN gate. -/
def encodeBits : BinaryTriple → TritPair
  | (false, false, false) => (.negative, .negative) -- xy
  | (false, false, true)  => (.negative, .neutral)  -- x+y
  | (false, true, false)  => (.negative, .positive) -- yx
  | (false, true, true)   => (.neutral, .negative) -- xy-zw
  | (true, false, false)  => (.neutral, .positive) -- wz-yx
  | (true, false, true)   => (.positive, .negative) -- wz
  | (true, true, false)   => (.positive, .neutral)  -- z+w
  | (true, true, true)    => (.positive, .positive) -- zw

/-- A genuine nine-state typed tensor address; the center is HNAN. -/
inductive TensorAddress where
  | binary (bits : BinaryTriple)
  | hnan
deriving Repr, BEq, DecidableEq

def decodeCell : TritPair → TensorAddress
  | (.negative, .negative) => .binary (false, false, false)
  | (.negative, .neutral)  => .binary (false, false, true)
  | (.negative, .positive) => .binary (false, true, false)
  | (.neutral, .negative)  => .binary (false, true, true)
  | (.neutral, .neutral)   => .hnan
  | (.neutral, .positive) => .binary (true, false, false)
  | (.positive, .negative) => .binary (true, false, true)
  | (.positive, .neutral)  => .binary (true, true, false)
  | (.positive, .positive) => .binary (true, true, true)

def encodeCell : TensorAddress → TritPair
  | .binary bits => encodeBits bits
  | .hnan => (.neutral, .neutral)

/-- Binary-only interpretation is undefined for HNAN; tensor decode is total. -/
def decodePair (pair : TritPair) : Option BinaryTriple :=
  match decodeCell pair with
  | .binary bits => some bits
  | .hnan => none

theorem hnanCenterDecoded :
    decodeCell (.neutral, .neutral) = .hnan := by
  rfl

theorem hnanCenterIsNotBinary :
    decodePair (.neutral, .neutral) = none := by
  rfl

theorem allNineTensorStatesRoundTrip :
    ∀ cell : TensorAddress, decodeCell (encodeCell cell) = cell := by
  intro cell
  cases cell with
  | hnan => rfl
  | binary bits =>
    cases bits with
    | mk a bc =>
      cases bc with
      | mk b c =>
        cases a <;> cases b <;> cases c <;> rfl

theorem allNineTritPairsRoundTrip :
    ∀ pair : TritPair, encodeCell (decodeCell pair) = pair := by
  intro pair
  cases pair with
  | mk a b =>
    cases a <;> cases b <;> rfl

/-- The ordered x/y/z/w phase source is retained, not rearranged. -/
def hnanTensorSource : List (List String) :=
  [["xy", "x+y", "yx"],
   ["xy-zw", "x+y-z-w+xy+yx-zw-wz", "wz-yx"],
   ["wz", "z+w", "zw"]]

def binaryAddressGrid : List (List String) :=
  [["000", "001", "010"],
   ["011", "HNAN", "100"],
   ["101", "110", "111"]]

def loShuPositions : List (List Nat) :=
  [[4, 9, 2], [3, 5, 7], [8, 1, 6]]

theorem nativeHNANTensorOrder :
    hnanTensorSource =
      [["xy", "x+y", "yx"],
       ["xy-zw", "x+y-z-w+xy+yx-zw-wz", "wz-yx"],
       ["wz", "z+w", "zw"]] := by
  rfl

theorem nativeBinaryAddressGrid :
    binaryAddressGrid =
      [["000", "001", "010"],
       ["011", "HNAN", "100"],
       ["101", "110", "111"]] := by
  rfl

theorem nativeLoShuOrder :
    loShuPositions =
      [[4, 9, 2], [3, 5, 7], [8, 1, 6]] := by
  rfl

/-- Eight exact local inputs, verified by kernel-evaluable finite cases. -/
theorem allThreeBitTriplesRoundTrip :
    ∀ bits : BinaryTriple, decodePair (encodeBits bits) = some bits := by
  decide

theorem centerNotEmittedAsBinary :
    ∀ bits : BinaryTriple,
      encodeBits bits ≠ (.neutral, .neutral) := by
  intro bits
  rcases bits with ⟨a, b, c⟩
  cases a <;> cases b <;> cases c <;> decide

/-- A total decoder is used only after the admitted-pair proof. -/
def decodeAdmitted (pair : TritPair) : BinaryTriple :=
  (decodePair pair).getD (false, false, false)

theorem admittedLocalRoundTrip :
    ∀ bits : BinaryTriple, decodeAdmitted (encodeBits bits) = bits := by
  intro bits
  rcases bits with ⟨a, b, c⟩
  cases a <;> cases b <;> cases c <;> decide

/-- Every 5184-bit frame is represented by 1728 ordered triples.
    This theorem quantifies over all possible such frames, not samples. -/
abbrev Binary5184 := Fin 1728 → BinaryTriple
abbrev BalancedTrit3456 := Fin 1728 → TritPair

def encodeFrame (raw : Binary5184) : BalancedTrit3456 :=
  fun index => encodeBits (raw index)

def decodeFrame (carrier : BalancedTrit3456) : Binary5184 :=
  fun index => decodeAdmitted (carrier index)

theorem full5184RadixRoundTrip (raw : Binary5184) :
    decodeFrame (encodeFrame raw) = raw := by
  funext index
  exact admittedLocalRoundTrip (raw index)

theorem full5184RadixInjective :
    Function.Injective encodeFrame := by
  intro a b h
  have decoded := congrArg decodeFrame h
  exact (full5184RadixRoundTrip a).symm.trans
    (decoded.trans (full5184RadixRoundTrip b))

theorem fullFrameCodesAdmitted (raw : Binary5184) (index : Fin 1728) :
    decodePair ((encodeFrame raw) index) = some (raw index) := by
  exact allThreeBitTriplesRoundTrip (raw index)

/-- Base64: pair of 3-bit octets = one of 64 six-bit input states. -/
abbrev BinarySextet := BinaryTriple × BinaryTriple
abbrev EncodedSextet := TritPair × TritPair

def encodeSextet (value : BinarySextet) : EncodedSextet :=
  (encodeBits value.1, encodeBits value.2)

def decodeSextet (value : EncodedSextet) : Option BinarySextet := do
  let left ← decodePair value.1
  let right ← decodePair value.2
  pure (left, right)

theorem allBase64SextetsRoundTrip :
    ∀ bits : BinarySextet,
      decodeSextet (encodeSextet bits) = some bits := by
  intro bits
  rcases bits with ⟨⟨a, b, c⟩, ⟨d, e, f⟩⟩
  cases a <;> cases b <;> cases c <;>
    cases d <;> cases e <;> cases f <;> decide

/-- Whole-frame six-bit groups: 864 sextets, each with 4 output trits. -/
abbrev Base64Frame864 := Fin 864 → BinarySextet

def encodeBase64Frame (raw : Base64Frame864) :
    Fin 864 → EncodedSextet :=
  fun index => encodeSextet (raw index)

theorem base64FrameRoundTrip (raw : Base64Frame864) :
    ∀ index : Fin 864,
      decodeSextet ((encodeBase64Frame raw) index) =
        some (raw index) := by
  intro index
  exact allBase64SextetsRoundTrip (raw index)

theorem base64DomainCardinality :
    2 ^ 6 = 64 ∧ 8 * 8 = 64 ∧ 3 ^ 4 = 81 := by
  decide

theorem fixed5184Factorization :
    1728 * 3 = 5184 ∧ 1728 * 2 = 3456 ∧
    864 * 6 = 5184 ∧ 864 * 4 = 3456 ∧
    81 * 64 = 72 * 72 := by
  decide

def hnanGateReplacementAuthority : Bool := false
def standaloneHash72PayloadInversionClaimed : Bool := false

theorem noNewNativeAuthority :
    hnanGateReplacementAuthority = false ∧
    standaloneHash72PayloadInversionClaimed = false := by
  decide

end HHS.Pass220.Base64BalancedTrit5184
