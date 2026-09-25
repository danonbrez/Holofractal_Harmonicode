ClearAll[theta, phi, delta, delta1, delta2, r, Rxy, Rzw, Rk, rho, n, rot2, J2, rot4, J4, pair, tests, report];

rot2[d_] := {{Cos[d], -Sin[d]}, {Sin[d], Cos[d]}};
J2 = {{0, 1}, {-1, 0}};
rot4[d1_, d2_] := ArrayFlatten[{{rot2[d1], ConstantArray[0, {2, 2}]}, {ConstantArray[0, {2, 2}], rot2[d2]}}];
J4 = ArrayFlatten[{{J2, ConstantArray[0, {2, 2}]}, {ConstantArray[0, {2, 2}], J2}}];
pair[R_, t_] := {R Cos[t], R Sin[t]};

tests = {
 VerificationTest[FullSimplify[Cos[theta]^2 + Sin[theta]^2, Element[theta, Reals]], 1, TestID -> "unit-circle-squared-radius"],
 VerificationTest[FullSimplify[(r Sin[phi] Cos[theta])^2 + (r Sin[phi] Sin[theta])^2, Element[{r, phi, theta}, Reals]], r^2 Sin[phi]^2, TestID -> "three-dimensional-latitude-circle"],
 VerificationTest[FullSimplify[(Rxy Cos[theta])^2 + (Rxy Sin[theta])^2, Element[{Rxy, theta}, Reals]], Rxy^2, TestID -> "four-dimensional-xy-circle"],
 VerificationTest[FullSimplify[(Rzw Cos[phi])^2 + (Rzw Sin[phi])^2, Element[{Rzw, phi}, Reals]], Rzw^2, TestID -> "four-dimensional-zw-circle"],
 VerificationTest[FullSimplify[Total[{(Rxy Cos[theta])^2, (Rxy Sin[theta])^2, (Rzw Cos[phi])^2, (Rzw Sin[phi])^2}], Element[{Rxy, Rzw, theta, phi}, Reals]], Rxy^2 + Rzw^2, TestID -> "four-dimensional-product-of-circles"],
 VerificationTest[FullSimplify[pair[Rk, theta].pair[Rk, theta], Element[{Rk, theta}, Reals]], Rk^2, TestID -> "scale-parametric-circular-fiber"],
 VerificationTest[FullSimplify[Transpose[rot2[delta]].rot2[delta], Element[delta, Reals]], IdentityMatrix[2], TestID -> "planar-rotation-orthogonal"],
 VerificationTest[FullSimplify[Transpose[rot2[delta]].J2.rot2[delta], Element[delta, Reals]], J2, TestID -> "planar-rotation-symplectic"],
 VerificationTest[FullSimplify[Transpose[rot4[delta1, delta2]].J4.rot4[delta1, delta2], Element[{delta1, delta2}, Reals]], J4, TestID -> "four-dimensional-pair-rotation-symplectic"],
 VerificationTest[FullSimplify[rot2[delta].pair[Rk, theta], Element[{delta, Rk, theta}, Reals]], pair[Rk, delta + theta], TestID -> "phase-step-stays-on-same-circle"],
 VerificationTest[FullSimplify[(rho rot2[delta].pair[Rk, theta]).(rho rot2[delta].pair[Rk, theta]), Element[{rho, delta, Rk, theta}, Reals]], rho^2 Rk^2, TestID -> "cross-scale-circle-to-circle"],
 VerificationTest[FullSimplify[Transpose[rho rot2[delta]].J2.(rho rot2[delta]), Element[{rho, delta}, Reals]], rho^2 J2, TestID -> "cross-scale-conformal-symplectic-form"],
 VerificationTest[FullSimplify[Mod[n + 72, 72] == Mod[n, 72], Element[n, Integers]], True, TestID -> "phase-address-period-72"]
};

report = TestReport[tests];
Print @ ExportString[
 <|
  "Schema" -> "HHS_PASS219_LOCAL_CIRCULAR_PHASE_FIBER_WOLFRAM_PROOF_V1",
  "TestsRun" -> Length[tests],
  "TestsSucceeded" -> report["TestsSucceededCount"],
  "TestsFailed" -> report["TestsFailedCount"],
  "AllSucceeded" -> (report["TestsFailedCount"] === 0 && report["TestsSucceededCount"] === Length[tests])
 |>,
 "RawJSON"
];
If[report["TestsFailedCount"] =!= 0, Exit[1]];
