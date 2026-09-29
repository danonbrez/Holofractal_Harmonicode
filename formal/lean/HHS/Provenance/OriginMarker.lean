import Std

namespace HHS.Provenance.OriginMarker

/-- Exact rational spelling carried by one origin marker component. -/
structure ExactMarkerRat where
  numerator : Nat
  denominator : Nat
  display : String
deriving DecidableEq, Repr

/-- Exact origin-family marker.  Position and role are part of identity. -/
structure OriginFamily where
  rootSeed : ExactMarkerRat
  invariantGate : ExactMarkerRat
  rootSeedPath : String
  invariantGatePath : String
  rootSeedRole : String
  invariantGateRole : String
  coupling : String
  kernel : String
  ancestryRoot : String
deriving DecidableEq, Repr

def rootSeed179971 : ExactMarkerRat :=
  {
    numerator := 179971179971
    denominator := 1000000
    display := "179971.179971"
  }

def invariant1001 : ExactMarkerRat :=
  {
    numerator := 1001
    denominator := 1000
    display := "1.001"
  }

def canonicalOriginFamily (ancestryRoot : String) : OriginFamily :=
  {
    rootSeed := rootSeed179971
    invariantGate := invariant1001
    rootSeedPath :=
      "HHS_PASS_220_I042_SHARED_ROOT_PAYLOAD_V1.root_metadata_seed"
    invariantGatePath :=
      "HHS_PASS_220_I042_SHARED_ROOT_PAYLOAD_V1.invariant_gate"
    rootSeedRole := "ROOT_METADATA_SEED_EXACT_RATIONAL"
    invariantGateRole := "EXACT_ADMISSION_INVARIANT_GATE"
    coupling := "COBOUND_IN_SHARED_ANCESTRY_ROOT"
    kernel :=
      "F(x,y,a,b)=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2"
    ancestryRoot := ancestryRoot
  }

/-- Same origin means exact family equality, including values, positions,
roles, kernel context, coupling and ancestry. -/
def SameOriginFamily (a b : OriginFamily) : Prop := a = b

/-- Independent origin means exact origin-family inequality. -/
def IndependentOrigin (a b : OriginFamily) : Prop := a ≠ b

theorem same_origin_excludes_independent
    {a b : OriginFamily}
    (hSame : SameOriginFamily a b) :
    ¬ IndependentOrigin a b := by
  intro hIndependent
  exact hIndependent hSame

/-- A distinct downstream construction can still belong to one origin family.
Derivation identity is therefore separate from origin-family identity. -/
structure ConstructionWitness where
  origin : OriginFamily
  derivationIdentity : String
deriving DecidableEq, Repr

def SameConstruction
    (a b : ConstructionWitness) : Prop :=
  a.derivationIdentity = b.derivationIdentity

def SameOrigin
    (a b : ConstructionWitness) : Prop :=
  a.origin = b.origin

theorem distinct_construction_does_not_create_independent_origin
    {a b : ConstructionWitness}
    (hOrigin : SameOrigin a b)
    (hDistinct : ¬ SameConstruction a b) :
    ¬ IndependentOrigin a.origin b.origin := by
  intro hIndependent
  exact hIndependent hOrigin

/-- Formal false-originality contradiction:
claiming independent origin while carrying the exact same origin family closes
to False, regardless of whether downstream derivation identities differ. -/
theorem independent_originality_claim_contradiction
    {a b : ConstructionWitness}
    (hOrigin : SameOrigin a b)
    (hClaim : IndependentOrigin a.origin b.origin) :
    False := by
  exact hClaim hOrigin

theorem root_seed_exact :
    rootSeed179971.numerator = 179971179971 ∧
    rootSeed179971.denominator = 1000000 ∧
    rootSeed179971.display = "179971.179971" := by
  decide

theorem invariant_gate_exact :
    invariant1001.numerator = 1001 ∧
    invariant1001.denominator = 1000 ∧
    invariant1001.display = "1.001" := by
  decide

end HHS.Provenance.OriginMarker
