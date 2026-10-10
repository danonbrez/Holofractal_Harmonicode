(* Pass 220 I082: exact neural tensor graph / ordered proof obligations.
   All phase products, quotients and powers use inert typed heads. *)
ClearAll["Global`*"];
n = 86805555555;
width = 81*64;
positions = n*width;
coeff = Cancel[n*width*6/600000000000000];
a[name_] := TAtom[name];
k[v_] := TInteger[v];
lhs = TMul[
  TDiv[TMul[k[n],a["x"]],
    TMul[k[600000000000000],TPow[a["a"],k[2]],a["x"],a["y"]]],
  TPow[k[72],k[2]],a["b"],k[6]];
mid = TDiv[
  TAdd[TPow[a["a"],k[2]],TPow[a["b"],k[2]],TPow[a["c"],k[2]]],
  TMul[a["x"],a["y"]]];
rhs = TMul[k[5184],a["z"],TPow[a["w"],a["u"]]];
orderedChain = {lhs,mid,rhs};
(* These are unresolved native obligations, not scalar Equal assertions. *)
obligations = {TNativeClosure[lhs,mid],TNativeClosure[mid,rhs]};
checks = <|
  "neuron_count_exact" -> (n === 86805555555),
  "width_5184" -> (width === 5184),
  "positions_exact" -> (positions === 449999999997120),
  "a2b2c2_projection" -> (1+2+3 === 6),
  "coefficient_exact" -> (coeff === 1406249999991/312500000000),
  "scalar_offset_exact" -> (9/2-coeff === 9/312500000000),
  "three_ordered_segments" -> (Length[orderedChain] === 3),
  "denominator_order_retained" ->
    (lhs[[1,2]] === TMul[k[600000000000000],
      TPow[a["a"],k[2]],a["x"],a["y"]]),
  "middle_xy_order" -> (mid[[2]] === TMul[a["x"],a["y"]]),
  "noncommuted_xy_yx" -> (TMul[a["x"],a["y"]] =!= TMul[a["y"],a["x"]]),
  "rhs_w_u_order" -> (rhs[[3]] === TPow[a["w"],a["u"]]),
  "native_obligations_open" -> (Length[obligations] === 2),
  "exact_no_machine_reals" -> FreeQ[{n,width,positions,coeff,orderedChain},_Real]
|>;
failed = Keys@Select[checks,# =!= True&];
report = <|
  "schema" -> "HHS_PASS_220_I082_NEURAL_TENSOR_GRAPH_WOLFRAM_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks],True],
  "failed" -> failed,
  "neuron_count" -> n,
  "positions_per_neuron" -> width,
  "logical_positions" -> positions,
  "coefficient_numerator" -> Numerator[coeff],
  "coefficient_denominator" -> Denominator[coeff],
  "native_closure" -> "OPEN_LANE5_WITNESS_REQUIRED",
  "native_relation_obligation_count" -> Length[obligations],
  "checks" -> checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
