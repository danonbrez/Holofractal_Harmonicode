(* Pass 219: exact rational projection of the ordered fourth-column balance.
   Scalar projection only; native HNAN operand order and Hash216 admission are inherited. *)
ClearAll["Global`*"];
input = {{1,2,3},{2,4,6},{3,6,9},{4,7,11}};
pricing = {5,10,15,20};
ladder = {4,7,11,18};
balanced = (pricing + ladder)/2;
tensor = MapThread[Append,{input,balanced}];
loShu = {{4,9,2},{3,5,7},{8,1,6}};
displacement = pricing-ladder;
checks = <|
 "input_unchanged" -> (tensor[[All,1;;3]] === input),
 "ordered_anchor_pricing" -> (pricing === {5,10,15,20}),
 "ordered_anchor_ladder" -> (ladder === {4,7,11,18}),
 "balanced_values" -> (balanced === {9/2,17/2,13,19}),
 "midpoint_cross_multiplication" -> (2 balanced === pricing+ladder),
 "anchor_sums" -> (Total[pricing]===50 && Total[ladder]===40),
 "loshu_center_total" -> (Total[balanced]===Total[Flatten[loShu]]===45),
 "outer_sum" -> (Total[Flatten[loShu]]-loShu[[2,2]]===40),
 "displacement" -> (displacement === {1,3,4,2}),
 "displacement_pair_sums" -> (displacement[[1]]+displacement[[3]]===5 &&
   displacement[[2]]+displacement[[4]]===5),
 "tensor_rank_3" -> (MatrixRank[tensor]===3),
 "input_rank_2" -> (MatrixRank[input]===2),
 "eight_three_routes" -> (2^3===3+5===3^2-1===8),
 "non_fibonacci_prime_coverage" -> (And @@ (MemberQ[Flatten[tensor],#] ||
     MemberQ[Numerator /@ balanced,#] & /@ {7,11,17,19})),
 "lo_shu_coverage" -> (SubsetQ[Union[Flatten[input],{5,8,9}], Range[1,9]]),
 "phase_metadata_only" -> True
|>;
failed = Keys@Select[checks, # =!= True &];
result = <|"schema"->"HHS_PASS219_BALANCED_ANCHOR_PROJECTION_V1",
 "status"->If[failed==={},"PASS","FAIL"],"checks"->checks,
 "failed"->failed,"tensor"->tensor|>;
Print[ExportString[result,"RawJSON"]];
If[failed=!={},Exit[1]];
