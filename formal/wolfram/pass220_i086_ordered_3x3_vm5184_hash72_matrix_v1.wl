(* I086: source-ordered 3x3 denominator of VM81 5184 / Matrix = hash72.
   The HHS native quotient is HELD. This script never inverts,
   divides by, takes a determinant of, or scalarizes that tensor. *)

ClearAll["Global\`*"];
sourceEquation =
 "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72";
sourceMatrix = {
 {"yx","y+w","wx"},
 {"-xy-wz","x+y-z-w+xy+yx-zw-wz","-zw-yx"},
 {"xy","x-z","zw"}
};
sourceCenter = "x+y-z-w+xy+yx-zw-wz";
sourceMatrixString =
 "((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))";

(* NonCommutativeMultiply is a deliberately inert native ordered-term
   visual source. The real HHS runtime resolves phase products. *)
heldNativeQuotient = HoldComplete[
  Equal[
   Divide[Times[81,64], {
     {NonCommutativeMultiply[y,x], Plus[y,w],
      NonCommutativeMultiply[w,x]},
     {Plus[Times[-1,NonCommutativeMultiply[x,y]],
           Times[-1,NonCommutativeMultiply[w,z]]],
      Plus[x,y,-z,-w,
           NonCommutativeMultiply[x,y],
           NonCommutativeMultiply[y,x],
           Times[-1,NonCommutativeMultiply[z,w]],
           Times[-1,NonCommutativeMultiply[w,z]]],
      Plus[Times[-1,NonCommutativeMultiply[z,w]],
           Times[-1,NonCommutativeMultiply[y,x]]]},
     {NonCommutativeMultiply[x,y],Plus[x,-z],
      NonCommutativeMultiply[z,w]}
   }],hash72]
];

(* Every signed lexeme is stored at its original matrix position.
   No commutation or sign normalization of underlying native objects. *)
orderedCellLexemes = {
 {{"yx"},{"y","+w"},{"wx"}},
 {{"-xy","-wz"},
  {"x","+y","-z","-w","+xy","+yx","-zw","-wz"},
  {"-zw","-yx"}},
 {{"xy"},{"x","-z"},{"zw"}}
};
reconstructed = Map[StringJoin,orderedCellLexemes,{2}];

(* Exactly inherited Pass220 I071:
   9 VM81 nuclei * 9 local Lo Shu source cells * 8 operation classes
   * 8 ordered basis channels = 5184 positions.
   Each VM81 cell=(nucleus*9 + local cell); operation64=8*class+basis.
 *)
positions = Range[0,5183];
vmCell = Quotient[positions,64];
operation64 = Mod[positions,64];
nucleus9 = Quotient[vmCell,9];
matrixCell = Mod[vmCell,9];
class8 = Quotient[operation64,8];
basis8 = Mod[operation64,8];
inheritedPhaseSlot = 9 basis8 + matrixCell;
nativeInverse = 64(9 nucleus9 + matrixCell) + 8 class8 + basis8;
hashRow72 = Quotient[positions,72];
hashCol72 = Mod[positions,72];
hashInverse = 72 hashRow72 + hashCol72;
q144Lane36 = Quotient[positions,144];
q144 = Mod[positions,144];
q144Inverse = 144 q144Lane36 + q144;
loShu = {{4,9,2},{3,5,7},{8,1,6}};
nativeValueIndex = Map[loShu[[Quotient[#,3]+1, Mod[#,3]+1]]&, matrixCell];

checks = <|
 "01_verbatim_matrix_source" ->
  (sourceEquation==="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72"),
 "02_source_three_rows" -> (Length[sourceMatrix]===3),
 "03_source_nine_cells" -> (And@@(Length[#]===3& /@ sourceMatrix)),
 "04_denominator_source_parentheses" ->
  (StringContainsQ[sourceEquation,sourceMatrixString]),
 "05_reconstituted_ordered_signed_lexemes" -> (reconstructed===sourceMatrix),
 "06_original_hnan_center_unchanged" -> (sourceMatrix[[2,2]]===sourceCenter),
 "07_center_eight_signed_terms" -> (Length[orderedCellLexemes[[2,2]]]===8),
 "08_original_wx_outer_noncommutative" -> (sourceMatrix[[1,3]]==="wx"),
 "09_wx_distinct_from_wz" -> (sourceMatrix[[1,3]]=!="wz"),
 "10_xy_distinct_from_yx_source" -> (sourceMatrix[[3,1]]=!=sourceMatrix[[1,1]]),
 "11_neg_xy_minus_wz_unchanged" -> (sourceMatrix[[2,1]]==="-xy-wz"),
 "12_neg_zw_minus_yx_unchanged" -> (sourceMatrix[[2,3]]==="-zw-yx"),
 "13_native_matrix_quotient_held" -> (Head[heldNativeQuotient]===HoldComplete),
 "14_vm81_matrix_crosswalk_length" -> (Length[positions]===5184),
 "15_nine_nuclei" -> (Union[nucleus9]===Range[0,8]),
 "16_nine_matrix_cells_per_nucleus" -> (Union[matrixCell]===Range[0,8]),
 "17_eight_operation_classes" -> (Union[class8]===Range[0,7]),
 "18_eight_inherited_ordered_basis_channels" -> (Union[basis8]===Range[0,7]),
 "19_all_72_inherited_phase_slots" -> (Union[inheritedPhaseSlot]===Range[0,71]),
 "20_vm81_inverse_5184" -> (nativeInverse===positions),
 "21_hash72_grid_inverse_5184" -> (hashInverse===positions),
 "22_original_pass186_q144_inverse" -> (q144Inverse===positions),
 "23_9_times_72_times_8_5184" -> (9*72*8===5184),
 "24_81_times_64_5184" -> (81*64===5184),
 "25_72_times_72_5184" -> (72*72===5184),
 "26_original_lo_shu_cell_values_complete" ->
  (Sort[Union[nativeValueIndex]]===Range[9]),
 "27_exact_position_no_float" ->
  FreeQ[{positions,vmCell,matrixCell,basis8,hashInverse,q144Inverse},_Real]
|>;
failed=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS220_I086_SOURCE_ORDERED_MATRIX_HASH72_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "checks_total"->Length[checks],
 "checks_passed"->Count[Values[checks],True],
 "failed"->failed,
 "verbatim_matrix_source"->sourceEquation,
 "nine_matrix_expressions"->sourceMatrix,
 "matrix_center_original_HNAN"->sourceCenter,
 "native_division_by_noncommutative_matrix_proven"->False,
 "wx_native_extension_admitted"->False,
 "source_5184_hydration_addresses_proven"->(Length[positions]===5184),
 "hash72_candidate_cryptographic_ledger_admitted"->False,
 "native_matrix_inverse_computed"->False,
 "native_vm81_hash216_state_mutated"->False,
 "checks"->checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
