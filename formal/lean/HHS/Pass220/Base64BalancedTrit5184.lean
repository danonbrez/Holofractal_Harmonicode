import HHS.Pass220.HNANPhase5184

/-!
# Pass 220: exact radix correspondence for full 5184-bit VM81 frames

3 binary bits have eight states and encode as two balanced trits (nine
possible codes), with the final code reserved. Two such octets constitute
one six-bit Base64 sextet (64 states), represented by four trits.

This is a source-preserving ingress radix theorem; it neither rewrites
ordered HNAN products nor claims digest-only Hash72 inversion.
-/

namespace HHS.Pass220.Base64BalancedTrit5184

inductive Trit where
  | negative | neutral | positive
deriving Repr, BEq, DecidableEq

abbrev BinaryTriple := Bool × Bool × Bool
abbrev TritPair := Trit × Trit

def encodeBits : BinaryTriple → TritPair
  | (false, false, false) => (.negative, .negative)
  | (false, false, true)  => (.negative, .neutral)
  | (false, true, false)  => (.negative, .positive)
  | (false, true, true)   => (.neutral, .negative)
  | (true, false, false)  => (.neutral, .neutral)
  | (true, false, true)   => (.neutral, .positive)
  | (true, true, false)   => (.positive, .negative)
  | (true, true, true)    => (.positive, .neutral)

def decodePair : TritPair → Option BinaryTriple
  | (.negative, .negative) => some (false, false, false)
  | (.negative, .neutral)  => some (false, false, true)
  | (.negative, .positive) => some (false, true, false)
  | (.neutral, .negative)  => some (false, true, true)
  | (.neutral, .neutral)   => some (true, false, false)
  | (.neutral, .positive)  => some (true, false, true)
  | (.positive, .negative) => some (true, true, false)
  | (.positive, .neutral)  => some (true, true, true)
  | (.positive, .positive) => none

/-- Eight exact local inputs, verified by kernel-evaluable finite cases. -/
theorem allThreeBitTriplesRoundTrip :
    ∀ bits : BinaryTriple, decodePair (encodeBits bits) = some bits := by
  decide

theorem reservedNinthRejected :
    decodePair (.positive, .positive) = none := by
  rfl

theorem reservedNinthNeverEmitted :
    ∀ bits : BinaryTriple,
      encodeBits bits ≠ (.positive, .positive) := by
  decide

/-- A total decoder is used only after the admitted-pair proof. -/
def decodeAdmitted (pair : TritPair) : BinaryTriple :=
  (decodePair pair).getD (false, false, false)

theorem admittedLocalRoundTrip :
    ∀ bits : BinaryTriple, decodeAdmitted (encodeBits bits) = bits := by
  decide

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
  decide

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
