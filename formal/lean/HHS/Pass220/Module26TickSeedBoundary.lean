import HHS.Pass220.Module25ProofInheritance

namespace HHS.Pass220.Module26

inductive OperationIntent where
  | readonlyEgress
  | inheritedProofReuse
  | canonicalTick
  deriving DecidableEq

def requiresAdmission : OperationIntent → Bool
  | .canonicalTick => true
  | .readonlyEgress => false
  | .inheritedProofReuse => false

theorem readonlyNoNewAdmission :
    requiresAdmission .readonlyEgress = false := by decide

theorem reuseNoNewAdmission :
    requiresAdmission .inheritedProofReuse = false := by decide

theorem tickRequiresAdmission :
    requiresAdmission .canonicalTick = true := by decide

theorem hash216WitnessCardinality : 3 * 72 = 216 := by decide

end HHS.Pass220.Module26
