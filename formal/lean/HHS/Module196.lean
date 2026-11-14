/- Module 196: native proof boundary. Pure properties only; no VM81 authority.
   The signed VM81/Hash72/Hash216 receipt must be provided by the inherited path. -/
namespace HHS.Module196

structure DualLane (α : Type) where
  lhs : α
  rhs : α

def collapse {α : Type} (value : α) : DualLane α :=
  ⟨value, value⟩

theorem collapse_preserves_both {α : Type} (v : α) :
    (collapse v).lhs = v ∧ (collapse v).rhs = v := by
  constructor <;> rfl

theorem square_cell_partition : 18 + 63 = 81 := by decide
theorem hnan_child_positions : 25 * 81 = 2025 := by decide
theorem fractal_square : 243 * 243 = 59049 := by decide

/- Typed octic return equality: use an explicit ordered multiplication witness,
   not scalar cancellation or division. -/
structure OrderedReturn (α : Type) where
  forward : α
  reverse : α
  octic : α

def admitsOrderedReturn {α : Type} [Mul α] [Neg α] (r : OrderedReturn α) : Prop :=
  r.forward * r.reverse = -r.octic

theorem ordered_return_requires_witness {α : Type} [Mul α] [Neg α]
    (r : OrderedReturn α) (h : admitsOrderedReturn r) :
    r.forward * r.reverse = -r.octic := h

end HHS.Module196
