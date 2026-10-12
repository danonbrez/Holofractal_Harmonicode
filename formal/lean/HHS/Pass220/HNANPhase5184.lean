import Lean.Elab.Tactic.Omega
import HHS.Pass220.LosslessEmergentCompressionHydration
import HHS.Pass219.QGUHNANTransport

namespace HHS.Pass220.HNANPhase5184

/-- Exact ordered native phase operators, never host scalar products. -/
inductive PhaseCell where
  | xy | sumXY | yx
  | xyMinusZW | hnanCenter | wzMinusYX
  | wz | sumZW | zw
deriving Repr, BEq, DecidableEq

def upperLane : List PhaseCell := [.xy, .sumXY, .yx]
def middleWitness : List PhaseCell := [.xyMinusZW, .hnanCenter, .wzMinusYX]
def lowerLane : List PhaseCell := [.wz, .sumZW, .zw]
def hnanTensor : List (List PhaseCell) :=
  [upperLane, middleWitness, lowerLane]

def centerSource : String := "x+y-z-w+xy+yx-zw-wz"
def terminalSource : String := "xy+epsilon"

theorem orderedTensorExact :
    hnanTensor =
    [[.xy, .sumXY, .yx],
     [.xyMinusZW, .hnanCenter, .wzMinusYX],
     [.wz, .sumZW, .zw]] := by
  rfl

theorem centerSourceExact :
    centerSource = "x+y-z-w+xy+yx-zw-wz" := by
  rfl

theorem forwardReverseDistinct :
    PhaseCell.xy ≠ PhaseCell.yx ∧
    PhaseCell.zw ≠ PhaseCell.wz := by
  decide

theorem epsilonNeverBareXY :
    terminalSource ≠ "xy" := by
  decide

/-- Two complete balanced-trinary role inventories, mirror ordered. -/
inductive Role where
  | negative | neutral | positive
deriving Repr, BEq, DecidableEq

def xyRoles : List Role := [.positive, .neutral, .negative]
def zwRoles : List Role := [.negative, .neutral, .positive]

theorem bothLanesComplete :
    xyRoles = [.positive, .neutral, .negative] ∧
    zwRoles = [.negative, .neutral, .positive] := by
  constructor <;> rfl

def binaryAddresses : List String :=
  ["000", "001", "010", "011", "100", "101", "110", "111"]

theorem binaryAddressesCount : binaryAddresses.length = 8 := by
  decide

theorem binaryAddressesDistinct : binaryAddresses.Nodup := by
  decide

theorem hnanNineCells : hnanTensor.length = 3 ∧
    upperLane.length = 3 ∧ middleWitness.length = 3 ∧
    lowerLane.length = 3 := by
  decide

theorem factorization5184 : 81 * 64 = 72 * 72 := by
  decide

theorem hash216AttachedComponents : 3 * (72 * 72) = 15552 := by
  decide

/-- Explicitly carried full binary state, never inferred from a digest.
    Hash72 is a separate *admitted generator*, not an arbitrary-payload codec. -/
abbrev Raw5184 := Fin 5184 → Bool
abbrev Hash72Generator := Fin 72 → Fin 72

structure WitnessedFrame where
  raw : Raw5184
  generator : Hash72Generator
  tensor : List (List PhaseCell)
  center : String
  terminal : String

def bindFrame (raw : Raw5184) (generator : Hash72Generator) :
    WitnessedFrame :=
  { raw := raw, generator := generator, tensor := hnanTensor,
    center := centerSource, terminal := terminalSource }

def decodeRaw (bound : WitnessedFrame) : Raw5184 := bound.raw

theorem rawExactRoundTrip (raw : Raw5184) (generator : Hash72Generator) :
    decodeRaw (bindFrame raw generator) = raw := by
  rfl

theorem rawInjectionForFixedGenerator (generator : Hash72Generator) :
    Function.Injective (fun raw => bindFrame raw generator) := by
  intro a b h
  exact congrArg decodeRaw h

theorem boundTensorExact (raw : Raw5184) (generator : Hash72Generator) :
    (bindFrame raw generator).tensor = hnanTensor := by
  rfl

theorem boundEpsilonRetained (raw : Raw5184) (generator : Hash72Generator) :
    (bindFrame raw generator).terminal = "xy+epsilon" := by
  rfl

/-- Hydration of an admitted generator into 72x72 indexed metadata.
    Both the generator and its source-position identity are preserved. -/
def hydrateGenerator (generator : Hash72Generator) :
    Fin 72 → Fin 72 → Fin 72 :=
  fun i _j => generator i

def recoverGenerator (vertices : Fin 72 → Fin 72 → Fin 72) :
    Hash72Generator :=
  fun i => vertices i ⟨0, by decide⟩

theorem generatorExactRoundTrip (generator : Hash72Generator) :
    recoverGenerator (hydrateGenerator generator) = generator := by
  rfl

theorem generatorHydrationUniform
    (generator : Hash72Generator) (i j : Fin 72) :
    hydrateGenerator generator i j =
      hydrateGenerator generator i ⟨0, by decide⟩ := by
  rfl

/-- Exact additive relative-phase projection (separate from native products).
    This preserves the first phase from the second phase plus their difference. -/
def additivePhaseDifference (left right : Int) : Int := left - right

theorem additivePhaseReconstruction (left right : Int) :
    right + additivePhaseDifference left right = left := by
  unfold additivePhaseDifference
  omega

/-- Local read-only formalization. Canonical VM81/Hash72 authority remains inherited. -/
def newCanonicalMutationAuthority : Bool := false
def newCanonicalHash72Authority : Bool := false
def arbitrary5184CompressionClaimed : Bool := false

theorem authorityFailClosed :
    newCanonicalMutationAuthority = false ∧
    newCanonicalHash72Authority = false ∧
    arbitrary5184CompressionClaimed = false := by
  decide

end HHS.Pass220.HNANPhase5184
