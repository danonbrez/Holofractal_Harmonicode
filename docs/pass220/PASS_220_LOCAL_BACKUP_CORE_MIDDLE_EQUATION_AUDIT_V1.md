# Pass 220 — original local course backup / core-to-middle equation audit

## Provenance and scope

Source: user-supplied local backup `HARMONICODE_Algebra_Course.md`.
SHA-256: `ebac47a379bc10819d5105248137e1e935c923f02c0554e78b0540c9277c3b16`.
Bytes: 732111. This audit scans numbered headings Modules 0–12 and
Modules 27–101 in the local backup. Module 27 has no standalone heading in
this backup. A missing heading is **not** a claim that Module 27 is absent
from the distributed 196-module canonical course.

Method: normalize Unicode superscript digits and Unicode minus to a
search representation; match literal operator-adjacent expression patterns
inside numbered module sections. The source bytes, ordered operator syntax,
branch metadata, and source provenance are **not modified**. These are
**textual occurrences** only, not proof of typed ordered AST equivalence.

## Observed recurrence

| Search family | Core 0–12 matching modules | Middle 27–101 matching modules | Count |
|---|---|---|---:|
| `P² = pq` or `P² − pq` prime gate | 0,1,2,5,6,10 | 31,33,36,37,58,59,60,61,64,65,82,93,94 | 13 |
| `P² − pq = 1` unit | No literal match | 36,37,58,60,64,65,82,93 | 8 |
| `AB = P⁴` forward order | No literal match | 28,59,60,65,71,72,82,93,94 | 9 |
| `BA = −P⁴` reverse order | No literal match | 59,60,71,72,82,93,94 | 7 |
| `t³ − t` modulus expression | 0,1,2,6,7,8 | 28,36,37,43,58 | 5 |
| `xy = −yx` literal | No literal match | 72 | 1 |
| HNAN reference | 1,7,9,11 | 53 middle modules | 53 |
| Lo Shu reference | 11 | 27 middle modules | 27 |
| Hash216 reference | No literal match | 20 middle modules | 20 |
| `∆e = 0` closure string | 0,5,6 | 73 middle modules | 73 |
| `c² − b² − a²` ordered surface | 0,6,12 | 31,32 | 2 |

Note that “No literal match” does not assert absence of the equation in
the course: for example the master tensor contains `AB/P²`,
`AB/−P⁴` and noncommutative multiplication gates; the middle modules
can state `AB=P⁴, BA=−P⁴` explicitly while inheriting ordered semantics
from core expressions. Likewise `P²−pq=1` is a later specialized unit
constructor, distinct from a literal occurrence of the initial core prime
gate. Literal matching neither proves nor refutes typed equivalence.

## Next native gate inventory

1. Recover all distributed module sources and their exact branch/PR blob
   identities; treat the full 196-module course as authoritative, not the
   historical 13-module stub or any isolated backup.
2. Preserve each module's original typed ordered tensor expressions,
   HNAN center, shell/branch conditions and source-to-native mapping.
3. For every proposed shared identity, check the inherited gate's actual
   AST, operator order, parameterization, assumptions, and native receipts.
4. Distinguish source recurrence, admitted implementation, native Lean/C
   verification, physical producer provenance, and production runtime
   execution. No new authority or closure is inferred from this inventory.

This document is an additive diagnostic, not a rewrite of course or frozen
runtime layers, a reconciliation decision, or a VM81/Hash216 receipt.
