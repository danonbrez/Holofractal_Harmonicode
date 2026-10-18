import Std
namespace HHS.Pass220.PrimeResidue64
def primes : Array Nat := #[2,3,5,7,11,13,17,19]
def ringLoShu : Array Nat := #[4,9,2,7,6,1,8,3]
def ringHNANAddress : Array String := #["000","001","010","100","111","110","101","011"]
def hubHNANAddress : String := "HNAN"
def hub : Nat := 5
def signedSpins : Array Int := #[-4,-3,-2,-1,1,2,3,4]
def residue (p : Nat) : Nat := p % 8
def classPlusOne : Array Nat := #[17]
def classPlusThree : Array Nat := #[3,11,19]
def classMinusThree : Array Nat := #[5,13]
def classMinusOne : Array Nat := #[7]
def evenAnchor : Nat := 2
/-- Address indexes the eight primes; the center is an axis, not a ninth ring slot. -/
structure Slot where
  primeIndex : Fin 8
  spinIndex : Fin 8
deriving Repr, DecidableEq
def linearAddress (s : Slot) : Nat := s.primeIndex.val * 8 + s.spinIndex.val
theorem sixtyFour : 8 * 4 * 2 = (64 : Nat) := by decide
theorem primeSpinSixtyFour : 8 * 8 = (64 : Nat) := by decide
theorem census : primes.size = 8 := by decide
theorem spinNoZero : !(signedSpins.contains 0) = true := by decide
theorem ringCenterDistinct : !(ringLoShu.contains hub) = true := by decide
theorem oddResidueCensus :
    (primes.toList.map residue) = [2,3,5,7,3,5,1,3] := by decide
theorem classCounts :
    classPlusOne.size + classPlusThree.size + classMinusThree.size +
      classMinusOne.size + 1 = 8 := by decide
theorem allAddressesInRange (s : Slot) : linearAddress s < 64 := by
  unfold linearAddress
  omega
end HHS.Pass220.PrimeResidue64
