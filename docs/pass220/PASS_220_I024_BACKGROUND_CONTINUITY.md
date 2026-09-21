# Pass 220 I024 — T_COSMO-06 Exact Background Continuity

Date: 2026-09-21

## 1. Scope

I024 removes the free background-Hubble function from the HHS cosmological
transfer. The background contribution is generated from:

- one finite SHA-bound reference density state;
- one exact gravity-coupling constant;
- the exact curvature sign and c0;
- committed phase/Hash receipts;
- exact continuity exponents.

No B(z), rho(z), interpolation table, fit spline, host-time clock, or inverse
H(z)->state path is admitted.

## 2. Reference epoch

The density anchors belong to one selected reference epoch:

~~~text
rho_b,ref
rho_r,ref
rho_D,ref
a_ref = 1
~~~

The reference epoch is explicit and need not be the final/present endpoint of
the finite trajectory.

This distinction prevents a hidden boundary-value solve. If present-day density
anchors are later required to generate an earlier history, that reverse
projection must be separately proven rather than silently introduced.

## 3. Exact background carrier

Define the exact egress coupling

~~~text
gamma_G = 8*pi*G/3
~~~

as one finite SHA-bound constant. The canonical runtime does not numerically
evaluate pi; it consumes the already-authorized exact egress coefficient.

At transition n:

~~~text
B_n =
gamma_G (rho_b,n + rho_D,n + rho_r,n)
+ K_n
~~~

with reference curvature carrier

~~~text
K_ref = -k c0^2
~~~

because a_ref = 1.

The I023 Friedmann transfer then receives:

~~~text
H_n^2 = B_n + (lambda_n/(tau theta_n))^2
~~~

as an exact rational/symbolic receipt.

## 4. Baryon and radiation continuity

The source-free exact continuity laws are:

~~~text
rho_b,n+1 =
rho_b,n ExpSym(-3 Deltaell_n)

rho_r,n+1 =
rho_r,n ExpSym(-4 Deltaell_n)
~~~

where:

~~~text
Deltaell_n = H_n tau theta_n
~~~

is produced by the exact I023 committed-interval transfer.

These imply the standard invariant forms:

~~~text
rho_b a^3 = constant
rho_r a^4 = constant
~~~

within the selected projection.

## 5. Hash/dark sourced continuity

The HHS dark sector is not silently forced to be conserved CDM because the
proposed Hash72/Hash216 exhaust can grow with committed state history.

I024 therefore uses:

~~~text
rho_D,n+1 =
rho_D,n ExpSym(-3 Deltaell_n)
+ J_D,n
~~~

where J_D,n is:

- exact;
- nonnegative at this boundary;
- finite;
- bound to the committed phase/Hash receipt;
- not callable;
- not fitted from H(z).

For:

~~~text
J_D,n = 0
~~~

the law reduces exactly to pressureless conserved continuity:

~~~text
rho_D a^3 = constant
~~~

A nonzero J_D,n is therefore an explicit HHS payload-source prediction rather
than a hidden change in the density-evolution law.

## 6. Curvature continuity

The exact curvature H^2 carrier evolves as:

~~~text
K_n+1 =
K_n ExpSym(-2 Deltaell_n)
~~~

which is the a^-2 curvature scaling.

The curvature sign remains one of:

~~~text
-1, 0, +1
~~~

and c0 is an exact egress constant.

## 7. Forward deterministic recurrence

For each committed phase/Hash input, the full causal order is:

~~~text
reference/background state_n
+ committed phase/Hash receipt_n
-> B_n
-> I023 exact H_n
-> Deltaell_n
-> rho_b,n+1
-> rho_D,n+1
-> rho_r,n+1
-> K_n+1
-> continuity receipt_n
~~~

The next step binds the previous continuity-receipt SHA.

Thus:

~~~text
anchors + committed receipts
-> unique B_0, B_1, ..., B_N
~~~

without a free background function.

## 8. I023 integration

I024 extends the I023 transfer receipt so background_h2 may be an ExactExpr,
not only a Fraction.

The existing rational path remains unchanged. If B_n is rational, I023 retains
the historical rational representation. If B_n contains symbolic continuity
factors, I023 carries:

~~~text
total_h2_exact
~~~

as a deterministic symbolic expression and continues the same exact
square-root/exponential transfer.

No numerical solver is introduced.

## 9. Wolfram closure

Connected Wolfram Language returned:

~~~text
schema = HHS_PASS_220_I024_COSMO_BACKGROUND_CONTINUITY_WOLFRAM_20260921_V2
status = PASS
checks = 10/10
failed = []
~~~

Verified identities include:

~~~text
rho_b,n+1 / rho_b,n = Exp[-3 Deltaell]
rho_r,n+1 / rho_r,n = Exp[-4 Deltaell]
K_n+1 / K_n         = Exp[-2 Deltaell]

rho_D,n+1 =
rho_D,n Exp[-3 Deltaell] + J_D,n
~~~

and the J_D=0 dark branch closes to the exact a^-3 invariant.

The background expression contains no Wolfram Function or InterpolatingFunction.

Evidence:

~~~text
evidence/pass220/i024_background_continuity_wolfram_20260921_v2.wl
evidence/pass220/i024_background_continuity_wolfram_20260921_v2.output.json
~~~

The earlier v1 evidence is retained as pre-source-term development evidence;
v2 is authoritative for I024.

## 10. Receipt chain

Every background step emits:

1. a background-input receipt binding the current densities, previous
   continuity receipt, phase/Hash receipt, and B_n;
2. an I023 TransferReceipt whose source SHA is the background-input receipt;
3. a continuity receipt binding Deltaell_n and the next density state.

Therefore an observer cannot substitute a different density sequence without
breaking receipt identity.

## 11. Authority boundaries

I024 adds no:

- VM81 mutation authority;
- Delta admission authority;
- Hash72 mint authority;
- Hash216 persistence authority;
- G72 scalar-resolution authority;
- floating-point authority;
- host wall-clock authority;
- arbitrary B(z) function;
- arbitrary rho(z) function;
- inverse H(z)->state authority.

It is a read-only cosmological projection over already committed state history.

## 12. Remaining physical closures

I024 proves the deterministic background continuity mechanism, but it does not
by itself prove that Hash exhaust is the observed dark matter.

That identification still requires the same effective dark payload to reproduce:

- background expansion;
- structure growth;
- gravitational lensing;
- absence from the electromagnetic projection.

Likewise, observational comparison requires a declared reference epoch and
measured anchor receipt with uncertainties.

The next empirical boundary is therefore:

~~~text
T_COSMO-07:
verified I022-I024 trajectory
+ declared reference-epoch measurement receipt
-> numerical egress only
-> DESI / SN / CMB residuals
~~~

with no parameter refit after the reference receipt is sealed.
