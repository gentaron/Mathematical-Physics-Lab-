import Mathlib

namespace MathPhysicsLab

/-- Group the two terms that carry the X13 pole, for nonzero rational channels. -/
theorem fivePointGrouping (a b c d e : ℚ)
    (ha : a ≠ 0) (hb : b ≠ 0) (hc : c ≠ 0) (hd : d ≠ 0) (he : e ≠ 0) :
    1 / (a * b) + 1 / (a * e) + 1 / (b * c) + 1 / (c * d) + 1 / (d * e) =
    (1 / a) * (1 / b + 1 / e) + 1 / (b * c) + 1 / (c * d) + 1 / (d * e) := by
  field_simp [ha, hb, hc, hd, he] <;> ring

/-- The algebraic coefficient of the pole can be written over a common denominator. -/
theorem poleCoefficient (b e : ℚ) (hb : b ≠ 0) (he : e ≠ 0) :
    1 / b + 1 / e = (b + e) / (b * e) := by
  field_simp [hb, he] <;> ring

end MathPhysicsLab

#print axioms MathPhysicsLab.fivePointGrouping
#print axioms MathPhysicsLab.poleCoefficient
