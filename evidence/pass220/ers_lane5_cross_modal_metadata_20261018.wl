(* Pass 220: source-locked ERS relations and exact arithmetic projections.
   Receipt is a candidate Wolfram evaluation record, NOT minted Hash216. *)
ClearAll[rawGates, rawPrompts, checks, receipt];
rawGates = <|
  "forward" -> "AB=P^4",
  "reverse" -> "BA=-P^4",
  "composite" -> "P^4=c^4=(Aa+Ab)(Ba+Bb)",
  "quadrature" -> "(Aa/Ba:Bb/Ab=Ab/Aa:Bb/Ba)^4/Delta=Delta",
  "h144" -> "144=36*4=(6+6)^2=((a^2+b^2+c^2)+(a^2*b^2*c^2))^((pxy+qzw)/P)=b^8*c^4",
  "periodic" -> "3/4:2/5",
  "token" -> "one -> 1=Delta"
|>;
rawPrompts = {
  "Do not deduplicate locally asymmetric phase states.",
  "Recognize native payload-contextual token relationships.",
  "Native reconstruction follows ordered state transitions, not copy substitution.",
  "Retain VM81 mutation and Hash72/Hash216 mint authority."
};
checks = <|
  "genesis_base_12" -> (1+2+3+1*2*3 == 12),
  "genesis_144" -> ((1+2+3+1*2*3)^2 == 144),
  "register_144" -> (2^4*3^2 == 144),
  "h36_quad_144" -> (36*4 == 144),
  "vm81_5184" -> (81*64 == 72^2),
  "polyrhythm_repetition_horizon" -> (LCM[4,5] == 20),
  "reciprocal_horizon" -> (1/LCM[4,5] == 1/20)
|>;
receipt = <|
 "schema" -> "HHS_PASS220_ERS_LANE5_EXACT_METADATA_V1",
 "status" -> If[And@@Values[checks], "PASS", "FAIL"],
 "sourceGates" -> rawGates,
 "promptConstraints" -> rawPrompts,
 "exactProjectionChecks" -> checks,
 "nativeGateClosure" -> "NOT EVALUATED: requires inherited VM81 typed gates",
 "hash216Mint" -> "NONE: use canonical VM81 authority"
|>;
Print[ExportString[receipt, "RawJSON", "Compact" -> True]];
If[receipt["status"] =!= "PASS", Exit[1]];
