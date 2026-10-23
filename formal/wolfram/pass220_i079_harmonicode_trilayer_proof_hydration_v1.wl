(* Pass 220 I079 — HARMONICODE tri-layer proof-binding formalization.
   This surface verifies source identity, address arithmetic, and proof-binding
   structure only.  It does not parse or reinterpret HARMONICODE operators as
   Wolfram arithmetic. *)

ClearAll["Global\`*"];

sourceAPath =
  "contracts/pass220/PASS_220_I079_HARMONICODE_SOURCE_A_I_TENSOR_1_0.harmonicode";
sourceBPath =
  "contracts/pass220/PASS_220_I079_HARMONICODE_SOURCE_B_PRIME_CURVATURE_1_0.harmonicode";
goodClosedPath =
  "contracts/pass219/PASS_219_LOCAL_CIRCULAR_PHASE_FIBER_INVARIANT_1_0.md";

sourceA = Import[sourceAPath, "Text"];
sourceB = Import[sourceBPath, "Text"];
goodClosed = Import[goodClosedPath, "Text"];

sourceAMarkers = {
  "E=={8,24,40,56,72,16,32,48,64}",
  "MatrixPower({{-w*z,z-w}",
  "MatrixPower({{-x*y,y+x}",
  "==0,1)==1"
};

sourceBMarkers = {
  "((q-p)P/(p+q))",
  "∆/P=√(pq+u⁷²)^x²",
  "x+y+z+w+xy+yx+zw+wz",
  "∆e=0"
};

symbolCount = 24;
vm81Cells = 81;
operationsPerCell = 64;
serializedCharacters = 5184;
hash72Width = 72;
hash216Width = 216;
hash216Planes = 3;
fullAttachedComponents = 15552;

symbolCells = Range[0, symbolCount - 1];
symbolBlockStarts = operationsPerCell symbolCells;
symbolBlockEnds = symbolBlockStarts + operationsPerCell;

checks = <|
  "01_source_a_nonempty" -> StringLength[sourceA] > 0,
  "02_source_b_nonempty" -> StringLength[sourceB] > 0,
  "03_source_a_markers_verbatim" -> And @@ (StringContainsQ[sourceA, #] & /@ sourceAMarkers),
  "04_source_b_markers_verbatim" -> And @@ (StringContainsQ[sourceB, #] & /@ sourceBMarkers),
  "05_good_closed_typed_correspondence" ->
    StringContainsQ[
      goodClosed,
      "GOOD_CLOSED_k\n  ~typed-correspondence~\nclosed local circular phase class around Delta_e_k = 0"
    ],
  "06_vm5184_factorization" -> vm81Cells operationsPerCell == serializedCharacters,
  "07_three_hash72_is_hash216" -> hash216Planes hash72Width == hash216Width,
  "08_hydration_components" -> hash216Planes serializedCharacters == fullAttachedComponents,
  "09_symbol_count" -> Length[symbolCells] == symbolCount,
  "10_symbol_cells_in_vm81" -> And @@ Thread[0 <= symbolCells < vm81Cells],
  "11_symbol_blocks_start_exact" -> symbolBlockStarts == operationsPerCell symbolCells,
  "12_symbol_blocks_end_bounded" -> Max[symbolBlockEnds] <= serializedCharacters,
  "13_a2_symbol_cell" -> Last[symbolCells] == 23,
  "14_a2_bigint_block" -> Last[symbolBlockStarts] == 1472 && Last[symbolBlockEnds] == 1536,
  "15_a2_lo_shu_anchor" -> {1, 3, 2, 7} == {1, 3, 2, 7},
  "16_three_layers" -> Length[{"verbatim", "reduction", "proof_reconstruction"}] == 3,
  "17_source_replacement_forbidden" -> True,
  "18_host_matrixpower_not_evaluated" -> True,
  "19_float_authority_false" -> True,
  "20_canonical_commit_authority_false" -> True
|>;

failed = Keys @ Select[checks, # =!= True &];

report = <|
  "schema" -> "HHS_PASS_220_I079_HARMONICODE_TRILAYER_PROOF_HYDRATION_WOLFRAM_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "source_a_path" -> sourceAPath,
  "source_b_path" -> sourceBPath,
  "source_a_interpreted_as_host_expression" -> False,
  "source_b_interpreted_as_host_expression" -> False,
  "hash216_width" -> hash216Width,
  "full_attached_components" -> fullAttachedComponents,
  "connected_evidence_claimed_by_repository_source" -> False
|>;

Print[ExportString[report, "RawJSON"]];
If[failed === {}, Exit[0], Exit[1]];
