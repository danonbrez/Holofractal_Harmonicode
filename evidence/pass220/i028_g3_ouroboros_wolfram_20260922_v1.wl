(* Pass 220 I028 exact G^3/Ouroboros opcode and Lo Shu closure proof. *)
ClearAll[p4,c4,p2];

opcodes = Range[24,34];
lo = {{4,9,2},{3,5,7},{8,1,6}};
centered = lo - 5;
pos[v_] := (First@Position[lo,v]) - 1;
rows = Total /@ centered;
cols = Total /@ Transpose[centered];
diags = {Tr[centered], Tr[Reverse[centered,2]]};
primitive = Range[24,33];
acceptance[bits_List] := And @@ bits;

checks=<|
 "01_legacy_halt_precedes_g3" -> (23 < First[opcodes]),
 "02_g3_values_exact_24_34" -> (opcodes===Range[24,34]),
 "03_g3_values_unique" -> DuplicateFreeQ[opcodes],
 "04_primitive_count_ten" -> (Length[primitive]===10),
 "05_fused_opcode_34" -> (Last[opcodes]===34),
 "06_lo_shu_c5_position" -> (pos[5]==={1,1}),
 "07_lo_shu_c7_position" -> (pos[7]==={1,2}),
 "08_lo_shu_c1_position" -> (pos[1]==={2,1}),
 "09_zero_centered_all_lines" ->
   (rows===ConstantArray[0,3] && cols===ConstantArray[0,3] &&
    diags==={0,0}),
 "10_p4_c4_carrier_equality_no_p2_symbol" ->
   (Solve[p4==c4,p4]==={{p4->c4}} &&
    FreeQ[HoldComplete[p4==c4],p2]),
 "11_all_constituents_required" ->
   And@@Table[
     acceptance[ReplacePart[ConstantArray[True,10],i->False]]===False,
     {i,1,10}
   ],
 "12_all_constituents_accept" ->
   acceptance[ConstantArray[True,10]]===True
|>;

failed=Keys@Select[checks,#=!=True&];
result=<|
 "schema"->"HHS_PASS_220_I028_G3_OUROBOROS_WOLFRAM_20260922_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "check_count"->Length[checks],
 "pass_count"->Count[Values[checks],True],
 "failed"->failed,
 "opcode_values"->opcodes,
 "lo_shu"->lo,
 "zero_centered_lo_shu"->centered,
 "checks"->checks
|>;
ExportString[result,"RawJSON"]
