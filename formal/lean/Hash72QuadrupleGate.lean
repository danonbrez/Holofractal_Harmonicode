-- Module 29 exact field-level theorem; no HNAN admission claim.
namespace HHS.Hash72QuadrupleGate
theorem polynomial_equivalence (x y z w : ℚ) (hy : y ≠ 0) (hz : z ≠ 0) (hw : w ≠ 0) :
    x^4/(z*w) = (-(y*z*w)^2/y^3)^(-2) ↔ x^4*(z*w)^3 = y^2 := by
  field_simp
  ring
theorem genesis_example :
    (1:ℚ)^4/(2*(1/2)) = (-(((-1:ℚ)*2*(1/2))^2)/(-1:ℚ)^3)^(-2) := by norm_num
theorem factorization_5184 : 16*18*18 = 81*64 := by decide
theorem seed_factor : 179971 = 11*16361 := by decide
theorem seed_ratio : (179971179971:ℚ)/1000000 = 179971*(1000001/1000000) := by norm_num
end HHS.Hash72QuadrupleGate
