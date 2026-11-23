(* Pass 220 — source-preserving 72-shell ordered-closure Wolfram audit.
   This is a diagnostic typed-projection fixture, NOT a VM81 admission proof.
   Native equality gates remain opaque until lowered by authoritative runtime. *)
ClearAll["Global`*"];
source = "(x^4/(Mod(72^72,Factorial(72))/(Mod(Factorial(72),72^72)))^(-0.2752680919)==(x^2+1)^2/x^3==b==1/b^3)^2/(c^2-a^2)==a^4/b^2";
rootSeed = "179971.179971";
invariantN = "1.001";
exponent = 2752680919/10000000000;
residueNumerator = Mod[72^72, Factorial[72]];
residueDenominator = Mod[Factorial[72], 72^72];
residue = residueNumerator/residueDenominator;
(* Never parse source == with Wolfram Equal; four operands in fixed order. *)
orderedOperands = {
  HoldComplete[x^4/Power[r72, -k72]],
  HoldComplete[(x^2+1)^2/x^3],
  HoldComplete[b],
  HoldComplete[1/b^3]
};
nativeChain = HoldComplete[HHSOrderedChain[gate1,gate2,gate3,gate4]];
nativeOuter = HoldComplete[HHSEqual[
  HHSDivide[HHSSquare[HHSOrderedChain[gate1,gate2,gate3,gate4]],
  HHSDifference[cSquared,aSquared]],
  HHSDivide[aFourth,bSquared]]];
sourceHash = IntegerString[Hash[source, "SHA256"], 16, 64];
gateOffsets = (First[#] - 1) & /@ StringPosition[source, "=="];
expectedOffsets = {74, 89, 92, 112};
sourceMutation = StringReplace[source, "b==1/b^3" -> "b==1/b^2"];
canonicalProjection = FullSimplify[
  eSquared/(3-1) == 1/2
];
checks = <|
 "ResidueDenominatorIsFactorial" -> TrueQ[residueDenominator == Factorial[72]],
 "ResiduePositive" -> TrueQ[0 < residue < 1],
 "ExponentExact" -> TrueQ[Denominator[exponent] == 10000000000],
 "OrderedOperandCount" -> TrueQ[Length[orderedOperands] == 4],
 "OuterProjectionUnit" -> TrueQ[canonicalProjection === (eSquared == 1)],
 "SourceByteCount" -> TrueQ[Length[ToCharacterCode[source, "UTF-8"]] == 121],
 "SourceSHA256Pinned" -> TrueQ[sourceHash == "cd6309c3a6ad1d71a08258322b95df127e6aab7428904a5ff903449864859bb2"],
 "SourceMutationRejected" -> TrueQ[IntegerString[Hash[sourceMutation, "SHA256"], 16, 64] != sourceHash],
 "GateOffsetsExact" -> TrueQ[gateOffsets === expectedOffsets],
 "FourSourceGates" -> TrueQ[Length[gateOffsets] == 4],
 "NativeGatesEvaluated" -> False,
 "VM81Admitted" -> False
|>;
report = <|
 "source" -> source,
 "sourceSHA256" -> sourceHash,
 "gateOffsetsZeroBased" -> gateOffsets,
 "rootMetadataSeed" -> rootSeed,
 "invariantN" -> invariantN,
 "residueExact" -> ToString[residue, InputForm],
 "exponentExact" -> ToString[exponent, InputForm],
 "nativeChain" -> ToString[nativeChain, InputForm],
 "nativeOuter" -> ToString[nativeOuter, InputForm],
 "canonicalProjection" -> ToString[canonicalProjection, InputForm],
 "checks" -> checks,
 "disposition" -> "PROJECTION_VERIFIED_NATIVE_RESIDUAL_UNRESOLVED"
|>;
report
