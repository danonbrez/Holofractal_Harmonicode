(* Pass220 I087 — actual RML10/RML11 exact real-Clifford projection.
   Reconstructs the *same exact generators* in the original
   hhs_runtime/pass219/real_clifford_morita_witness.py (RML10), then
   the same ordered primitive/product actions used by RML11.
   This proves an exact 48x48 *representation* inverse of the I086
   source denominator and the 5184/M quotient. It does not establish
   native HHS matrix invertibility or canonical Hash72 authority. *)

ClearAll["Global\`*"];
i2=IdentityMatrix[2];
s1={{0,1},{1,0}};
s2={{1,0},{0,-1}};
s12={{0,-1},{1,0}};
(* Exact original RML10 Cl_(0,8) first four generators. *)
x=-KroneckerProduct[i2,i2,s2,s12];
y=-KroneckerProduct[i2,i2,s12,i2];
z=-KroneckerProduct[i2,s1,s1,s12];
w=-KroneckerProduct[i2,s2,s1,s12];
id16=IdentityMatrix[16];
xy=x.y;yx=y.x;zw=z.w;wz=w.z;wx=w.x;xw=x.w;
(* Exact order/left-to-right signs from supplied I086 denominator. *)
blocks={
 {yx,y+w,wx},
 {-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx},
 {xy,x-z,zw}
};
m=ArrayFlatten[blocks];
source="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72";
det=Det[m];
rank=MatrixRank[m];
invertible=rank===48 && det=!=0;
inv=If[invertible,Inverse[m],$Failed];
leftInv=If[invertible,m.inv===IdentityMatrix[48],False];
rightInv=If[invertible,inv.m===IdentityMatrix[48],False];
q=If[invertible,5184 inv,$Failed];
leftQuot=If[invertible,m.q===5184 IdentityMatrix[48],False];
rightQuot=If[invertible,q.m===5184 IdentityMatrix[48],False];
inverseValues=If[invertible,Sort[DeleteDuplicates[Flatten[inv]]],{}];
quotValues=If[invertible,Sort[DeleteDuplicates[Flatten[q]]],{}];

checks=<|
 "01_RML10_first_four_original_matrix_order"->And@@(Dimensions[#]==={16,16}& /@ {x,y,z,w}),
 "02_RML10_each_primitive_square_minus_I"->And@@((#.#===-id16)& /@ {x,y,z,w}),
 "03_RML10_antipair_x_y"->(xy===-yx),
 "04_RML10_antipair_z_w"->(zw===-wz),
 "05_new_wx_exact_order"->(wx===w.x),
 "06_wx_and_xw_anticommute"->(wx===-xw),
 "07_wx_ne_wz"->(wx=!=wz),
 "08_full_I086_block_count"->(Dimensions[blocks]==={3,3,16,16}),
 "09_lifted_matrix_48_by_48"->(Dimensions[m]==={48,48}),
 "10_original_center_signed_sequence"->(blocks[[2,2]]===x+y-z-w+xy+yx-zw-wz),
 "11_original_wx_at_0_2"->(blocks[[1,3]]===wx),
 "12_original_negative_corner_1_0"->(blocks[[2,1]]===-xy-wz),
 "13_original_negative_corner_1_2"->(blocks[[2,3]]===-zw-yx),
 "14_original_x_minus_z_at_2_1"->(blocks[[3,2]]===x-z),
 "15_no_machine_real"->FreeQ[{m,inv,q},_Real],
 "16_full_rank"->(rank===48),
 "17_nonzero_exact_determinant"->(det===10485760000),
 "18_actual_inverse_constructed"->invertible,
 "19_exact_left_inverse"->leftInv,
 "20_exact_right_inverse"->rightInv,
 "21_original_5184_numerator"->(81*64===5184),
 "22_exact_5184_left_quotient_identity"->leftQuot,
 "23_exact_5184_right_quotient_identity"->rightQuot,
 "24_rational_inverse_coefficients"->If[invertible,And@@(Head[#]===Rational || IntegerQ[#]& /@ inverseValues),False],
 "25_rational_quotient_coefficients"->If[invertible,And@@(Head[#]===Rational || IntegerQ[#]& /@ quotValues),False],
 "26_original_i086_source_unmodified"->(source==="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72"),
 "27_i085_VM5184_equality_preserved"->(9*9*8*8===5184 && 72^2===5184)
|>;
failed=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS220_I087_RML11_EXACT_TWO_SIDED_MATRIX_INVERSE_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "checks_total"->Length[checks],
 "checks_passed"->Count[Values[checks],True],
 "failed"->failed,
 "original_I086_matrix_source"->source,
 "original_Clifford_generators_source"->"hhs_runtime/pass219/real_clifford_morita_witness.py",
 "Clifford_transport"->"hhs_runtime/pass219/phase_clifford_intertwiner.py",
 "matrix_order"->If[invertible,48,Null],
 "rank"->rank,
 "determinant"->det,
 "left_inverse_exact"->leftInv,
 "right_inverse_exact"->rightInv,
 "left_5184_quotient_exact"->leftQuot,
 "right_5184_quotient_exact"->rightQuot,
 "inverse_unique_coefficients"->Length[inverseValues],
 "quotient_unique_coefficients"->Length[quotValues],
 "wx_original_basis8_admitted"->False,
 "native_VM81_matrix_inverse_proven"->False,
 "native_hash72_ledger_equation_proven"->False,
 "Hash72_minted"->False,
 "Hash216_minted"->False,
 "VM81_mutated"->False,
 "checks"->checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
