(* Pass220 Wolfram PROJECTION: preserve exact original source as opaque InputForm text. *)
module29Source = "List(NcalcMatrixPower((I^List(List(List(List(1,x,2),List(w,z,y),List(4,z,3)),List(List(-x,1,-y),List(4,y,2),List(-w,3,-z))),List(List(List(4,3,3),List(2,z,4),List(1,1,2)),List(List(w,3,-z),List(2,w,4),List(-x,1,y))))/List(List(4,9,2),List(3,5,7),List(8,1,6))),(-1)),I^List(List(List(List(1,x,2),List(w,z,y),List(4,z,3)),List(List(-x,1,-y),List(4,y,2),List(-w,3,-z))),List(List(List(4,3,3),List(2,z,4),List(1,1,2)),List(List(w,3,-z),List(2,w,4),List(-x,1,y))))/List(List(4,9,2),List(3,5,7),List(8,1,6)))";
(* Only the two-sided inverse axiom is discharged here; no native HHS phase gate is evaluated. *)
ClearAll[phase, inverse, product, one];
forward = HoldComplete[product[inverse[phase], phase]];
backward = HoldComplete[product[phase, inverse[phase]]];
forwardRule = HoldPattern[product[inverse[t_], t_]] :> one;
backwardRule = HoldPattern[product[t_, inverse[t_]]] :> one;
forwardProof = ReleaseHold[forward /. forwardRule] === one;
backwardProof = ReleaseHold[backward /. backwardRule] === one;
(* Conventional exact matrix projection is separate from native ordered Q2. *)
matrix = {{1, 2}, {3, 7}};
projection = {Det[matrix] != 0, Inverse[matrix].matrix == IdentityMatrix[2], matrix.Inverse[matrix] == IdentityMatrix[2]};
<|"source" -> module29Source, "forwardInverseAxiom" -> forwardProof, "backwardInverseAxiom" -> backwardProof, "matrixProjection" -> projection, "nativePhaseOperatorEvaluated" -> False, "vm81ReceiptMinted" -> False|>
