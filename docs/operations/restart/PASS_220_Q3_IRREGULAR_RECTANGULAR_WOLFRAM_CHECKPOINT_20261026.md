# Pass 220 Q³ — General Irregular Rectangular Matrix Wolfram Checkpoint
Date: 2026-10-26
Status: **bounded Wolfram diagnostics; generalized native HNAN theorem not yet proven**
Scope: candidate/read-only; no VM81 mutation, Hash72/Hash216 mint, compiler/runtime or production authority.

## Goal
Prove or falsify the proposed generalized irregular-matrix operation **through** the pre-existing 81-cell Lo Shu/HNAN mediator; the 81-cell qudit is not an input dimension cap. Preserve ordered native AB, BA, and P⁴/P⁸ phase semantics and original address provenance. User-specified direct reciprocal factor normalization is unity; transpose-oriented factors must recover original distinct cell values. The 8×8→9×9 difference of 17 positions is a calibration example, not the theorem's full scope.

## Existing authoritative repository surfaces inspected
- `hhs_runtime/pass219/hnan_4x4_recursive_gate_v1.py`: HNAN ordered AST gate, xy != yx; typed epsilon residual. It does not authorize host arithmetic simplification.
- `hhs_runtime/hhs_pass220_i065_lossless_emergent_compression_hydration_v1.py`: Hash72 generator expands to 72×72 = 5184 address vertices; roundtrip exact for fixed admitted generator family.
- `hhs_runtime/hhs_pass220_hnan_phase5184_lossless_bridge_v1.py`: independently retains raw 5184-bit source; explicitly does not claim arbitrary 5184 bits invertible from Hash72 alone.
- `hhs_runtime/hhs_pass220_i075_native_rectangular_tensor_power_hydration_v1.py`: held ordered 4×2 native rectangular tensor-power AST, candidate-only, no host MatrixPower evaluation. Its _validate_matrix currently fixes two inherited 4×2 source nodes; it is not yet a general-shape multiplication operator.
No changes to these files.

## Exact Wolfram Language evaluation 1
```wl
ClearAll["Global`*"];
pairs=Table[{i,i+2,1/(i+2),(i+2)*(1/(i+2))},{i,1,17}];
recover=And@@(#[[2]]==1/#[[3]]&/@pairs);
m={{2,3},{5,7}}; r={1/2,-1/3}; c={1/2,-1/3}; h=1;
full=ArrayFlatten[{{m,List/@r},{{c},{{h}}}}];
f=full.Transpose[full]; g=Transpose[full].full;
<|"boundary_8_to_9"->9^2-8^2,
  "unit_17"->And@@(#[[4]]==1&/@pairs),
  "recover_17"->recover,
  "unique_17"->Length[DeleteDuplicates[pairs[[All,2]]]],
  "transpose_twice"->(Transpose[Transpose[full]]==full),
  "forward_reverse_same"->(f==g),
  "counterexample_difference"->(f-g)|>
```
Observed: boundary=17; unit_17=True; recover_17=True; unique_17=17; transpose_twice=True; forward_reverse_same=False; difference={{-16,-10,2/3},{-10,16,1},{2/3,1,0}}. These 17 reciprocal *factor tests* are not a full 9×9 HNAN native closure experiment.

## Exact Wolfram Language evaluation 2
```wl
ClearAll["Global`*"];
a={{1,2,3},{4,5,6}}; b=Transpose[a];
left=a.b; right=b.a;
<|"rectA"->Dimensions[a],"rectB"->Dimensions[b],
  "AB"->Dimensions[left],"BA"->Dimensions[right],
  "ABtrace"->Tr[left],"BAtrace"->Tr[right],
  "traceEqual"->(Tr[left]==Tr[right]),
  "ABentries"->left,"BAentries"->right|>
```
Observed: input 2×3, reciprocal 3×2; AB is 2×2 {{14,32},{32,77}}, BA is 3×3 {{17,22,27},{22,29,36},{27,36,45}}, and both traces are exactly 91. Distinct squares have common aggregate trace; their cells and dimensions differ. Trace equality is standard rectangular cyclicity when products are defined, not a proof of native HNAN octic closure or existence for arbitrary nonconformable inner dimensions.

## Current proof obligations
1. Define exact native typed completion operator for arbitrary m×n and r×s shapes using signed ±1 reciprocal transpose without overwriting source cells. Specify the position of the shared overlap and missing margins when dimensions differ.
2. Define *transposed product* explicitly: bare host matrix transpose plus ordinary multiplication need not reconstruct original per-cell values. Keep source factors, addresses, and operator order.
3. Show direct reciprocal unity and transpose recovery for **every admitted source cell**, not just 17 sample scalar pairs; validate the 17 boundary cells within a complete 9×9 construction.
4. Formalize HNAN resolution of unequal square outputs into common Q³/P⁴/P⁸ tensor state, preserving AB=-BA as **typed phase law**, not equality of ordinary rational/real-valued matrix products.
5. Prove exact output, closure, shape admissibility and partition/traversal independence for arbitrary dimensions; identify counterexamples or domain restrictions as needed.
6. Reuse I065 native Hash72 vertex addressing and Pass219 HNAN gate, not a new digest translation layer. Track contract/gap/error IDs before any runtime implementation.
7. Attach Lean and Wolfram exact proof identities to guarded service contracts before production admission.

No universal theorem, compiler integration, main merge, or runtime/production validation is claimed here.
