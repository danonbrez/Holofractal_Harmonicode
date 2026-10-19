(* Pass220 M19 source-faithful conventional symbolic projection audit.
   Does not evaluate native ordered / or == gates and cannot mint Hash216. *)
ClearAll[x,y,lam,s,l,n,m,adj,expected,checks,result];
s={{-4,-3,-2},{-1,0,1},{2,3,4}};
l={{4,9,2},{3,5,7},{8,1,6}};
n=Expand[x*s+l+y*(-s)];
m=n/(x*y);
adj={
{-3*x^2+6*x*y-2*x-3*y^2+2*y+23,6*x^2-12*x*y-14*x+6*y^2+14*y-52,-3*x^2+6*x*y-2*x-3*y^2+2*y+53},
{6*x^2-12*x*y+16*x+6*y^2-16*y+38,-12*x^2+24*x*y+4*x-12*y^2-4*y+8,6*x^2-12*x*y+16*x+6*y^2-16*y-22},
{-3*x^2+6*x*y-2*x-3*y^2+2*y-37,6*x^2-12*x*y-14*x+6*y^2+14*y+68,-3*x^2+6*x*y-2*x-3*y^2+2*y-7}};
expected=lam^3*x^3*y^3-15*lam^2*x^2*y^2+
  (-18*x^3*y+36*x^2*y^2-18*x*y^3+24*x*y)*lam-360;
checks=<|
 "source_ordered_numerator"->(n===Expand[x*s+l+y*(-s)]),
 "det_n_360"->TrueQ[FullSimplify[Det[n]==360]],
 "all_9_inverse_entries"->TrueQ[And@@Flatten[MapThread[
   (FullSimplify[#1==#2])&, {Inverse[m],x*y*adj/360},2]]],
 "two_sided_cofactor_identity"->TrueQ[And@@Flatten[
   Thread[Flatten[Expand[n.adj]]==Flatten[360*IdentityMatrix[3]]]]],
 "characteristic_polynomial"->TrueQ[FullSimplify[
   Expand[Det[lam*x*y*IdentityMatrix[3]-n]-expected]==0]],
 "trace_15"->TrueQ[FullSimplify[Tr[n]==15]]
|>;
result=<|"schema"->"HHS_PASS220_M19_SPIN_LOSHU_EXACT_PROJECTION_V1",
 "checks"->checks,"status"->If[And@@Values[checks],"PASS","FAIL"],
 "nativeGateAdmission"->False,"hash216Mint"->False|>;
Print[ExportString[result,"RawJSON","Compact"->True]];
If[result["status"]!="PASS",Exit[1]];
