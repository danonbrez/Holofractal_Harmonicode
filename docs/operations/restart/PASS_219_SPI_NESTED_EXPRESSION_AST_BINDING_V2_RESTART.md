# Pass 219 SPI Nested-Expression AST Binding v2 — Restart Checkpoint

## Status

Validated additive syntax/provenance successor for the HARMONICODE scalar-projection proof layer.

This checkpoint does **not** create canonical transition authority. VM81 remains the only canonical mutation/admission authority. The nested-expression parser, AST binding layer, and reconciliation layers are projection/provenance surfaces only.

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Merge target: `main`
- Authoritative base main: `2def7910b99046821f34e1446bcec33ca4fd4090`
- Working branch: `agent/pass219-spi-scalar-projection-registry-v1-20260910`
- Previous restart checkpoint: `ac452f0b1506eaea2ac07b0726a5162e47b60161`
- Validated v2 semantic head: `8714ea86a938433575e01cda1c4b81290c4814b0`
- Restart checkpoint lineage begins at: `b6caa79adbf9443b45618b74bb854b45feeaec9a`
- Pull request: `#427`
- Validated branch relation: ahead of `main`, with `main` still at the authoritative base above.

## Frozen predecessor evidence

The v2 layer is additive. It does not rewrite or replace the frozen predecessor evidence.

- Raw executable HARMONICODE corpus: 6 paths / 5 unique source bodies.
- Raw scalar candidate census: 472 candidates.
  - `PROVEN = 389`
  - `SYMBOLIC = 27`
  - `MISSING_PROJECTION = 56`
  - `UNSUPPORTED_DOMAIN = 0`
- Raw corpus manifest SHA-256: `fc421b2f84d7186693ba02e40515d7dcf471efe4fd6ade3b3a3ab662e36ef5a7`
- Reconciliation v1 census: `PROVEN = 429`, `SYMBOLIC = 43`, `MISSING_PROJECTION = 0`, `UNSUPPORTED_DOMAIN = 0`
- Reconciliation v1 manifest SHA-256: `d726356e1651df8e43ad56a47885b2d4aacbb4b5c56a106476cf48519dc50b4f`
- `classification_complete = true`
- `scalar_value_complete = false`

## Implemented v2 files

- `native_projects/hhs_harmonicode_language/hhs_harmonicode_nested_expression_ast_v2.py`
- `native_projects/hhs_harmonicode_language/hhs_harmonicode_nested_expression_ast_tests_v2.py`
- `hhs_spi_scalar_projection_corpus_ast_binding_v2.py`
- `hhs_spi_scalar_projection_corpus_ast_binding_tests_v2.py`
- `hhs_spi_scalar_projection_corpus_reconciliation_v2.py`
- `hhs_spi_scalar_projection_corpus_reconciliation_tests_v2.py`
- `.github/workflows/pass219-spi-scalar-projection-registry.yml` updated additively to validate v1 and v2 surfaces.

## Nested-expression AST contract

Parser version: `HHS_HARMONICODE_NESTED_EXPRESSION_AST_PASS_219_V2`.

The Pass 075 statement parser remains frozen. The v2 membrane records its predecessor parser version, predecessor AST root, original source SHA, source length, and predecessor statement nodes.

The additive AST recognizes `SuperscriptPower`, `PowerSurface`, `PowerChain`, and `RadicalPowerSurface` syntax surfaces without scalar evaluation.

The source `c^b^4` is preserved as a `PowerChain` with ordered operands `[c, b, 4]`, `associativity = UNRESOLVED_SOURCE_CHAIN`, `algebraic_associativity_selected = false`, `scalar_value = null`, and `canonical_admission = false`. It is not rewritten into `(c^b)^4` or `c^(b^4)`.

The source `√(pq+u⁷²)^x²` is preserved as a `RadicalPowerSurface` with ordered operands `[(pq+u⁷²), x²]`. The contained `u⁷²` and `x²` superscript surfaces retain explicit `SuperscriptPower` nodes; no scalar value is inferred.

Python's Unicode alphanumeric classification initially caused superscript digits to be consumed by the identifier scanner. The repaired v2 lexer explicitly excludes `⁰¹²³⁴⁵⁶⁷⁸⁹` from identifier characters. This is a lexical repair, not an algebraic interpretation.

## Parser-limit migration

Reconciliation v1 contained exactly two parser-limit expression families / five total occurrences:

- `(pq+u⁷²)^x` — 2 occurrences, lexical prefix of `√(pq+u⁷²)^x²`
- `c^b` — 3 occurrences, lexical prefix of `c^b^4`

v2 binds those five predecessor spans to exact enclosing nested AST nodes while retaining each original span as provenance.

Result: target families 2; parser-limit occurrences before 5; after 0; AST-bound symbolic occurrences 5; syntax binding complete true; scalar value complete false; canonical admission authority false.

Nested AST binding manifest SHA-256: `874e4b15850cece6996bf461d2f6d87d16ad455bfd117c2c3dd684051a2604ef`.

## Reconciliation v2 result

Reconciliation v2 replaces only the two `PARSER-LIMIT-WITNESS-v1` profiles with AST-backed `NESTED-AST-SYNTAX-WITNESS-v2` provenance. It does not change the scalar classification census.

Final reconciled candidate counts remain `PROVEN = 429`, `SYMBOLIC = 43`, `MISSING_PROJECTION = 0`, `UNSUPPORTED_DOMAIN = 0`. Migrated resolution families = 2; migrated occurrences = 5; parser-limit profile occurrences = 0; syntax provenance complete for migrated profiles = true; scalar value complete = false; canonical admission authority = false.

Reconciliation v2 manifest SHA-256: `481c0bb0264ad0771344ae068624dcfd7c9c5ba853a8c7963ad9a22971389aee`.

## Validation

Dedicated workflow run `34574371362`, job `103183383669`, conclusion `SUCCESS`, validated semantic head `8714ea86a938433575e01cda1c4b81290c4814b0`, PR merge-test checkout `9fec10ce15477b11bc8a59ec610f6386eb8cfeac`, Python 3.12.14.

Passing dependency-scoped suites:

- SPI registry v1: 22 passed / 0 failed
- raw corpus v1: 17 passed / 0 failed
- reconciliation v1: 13 passed / 0 failed
- nested-expression AST v2: 8 passed / 0 failed
- nested AST corpus binding v2: 8 passed / 0 failed
- reconciliation v2: 8 passed / 0 failed

Raw corpus strict-completion remains intentionally false at the frozen v1 raw-census layer. Reconciliation v1 and v2 scalar-value completion both return the expected fail-closed condition; v2 retains 43 open symbolic occurrences and 0 parser-limit profile occurrences.

## Workflow artifacts

- `10189019717` — scalar projection manifest — ZIP SHA-256 `f20a252c57d20742ec7a654702e466872e234c34b931d6497d048981a4972ec8`
- `10189020319` — repository corpus coverage — ZIP SHA-256 `e9b7403ac3cc2428745437e40cbabd6b6780fb773bb6acd0dc157953c4d53bdd`
- `10189020875` — corpus reconciled v1 — ZIP SHA-256 `af374d735e962d07d7bceecbaa76871d0e93b53bc546ff683715606a16b269ec`
- `10189021456` — nested AST binding v2 — ZIP SHA-256 `223db7650a15470eb2918b4f8646776a6960941d1c545f1c622458a52bc7a30a`
- `10189021997` — corpus reconciled v2 — ZIP SHA-256 `9ff4fc58042c085e5e82a163d65f7b45e291bf8d3b168ff4a7237c807f3c9907`

## Authority boundary

This pass does not authorize or perform VM81 mutation, canonical Hash72/Hash216 minting, canonical state persistence, source rewriting, ordered-product commutation, chained-power associativity selection, conversion of projection equality into native identity, or scalarization of unresolved formal phase/radical surfaces.

## Remaining proof obligations

1. **O2 ordered matrix-power scalar witness** — bind the existing matrix-power source to an exact ordered matrix/tensor proof object without approximate matrix arithmetic or source-order changes.
2. **O3 `f == t/m` provenance** — establish the exact repository-authorized derivation/projection lineage or leave it fail-closed if the required premise is absent.
3. Formal phase surfaces such as `I²`, `I³`, and `x²` remain symbolic unless an existing repository projection explicitly authorizes scalar treatment.

## Restart procedure

Use the latest branch head carrying this file. The stable semantic validation anchor is `8714ea86a938433575e01cda1c4b81290c4814b0`; later commits in this checkpoint lineage are documentation-only. Verify `main` is still at the recorded base or reconcile forward if it has advanced. Preserve the frozen v1 manifests and the v2 manifest hashes above. Do not rerun unrelated suites unless a dependency changes.

Next implementation action: **Implement O2 as an additive exact ordered matrix-power projection proof surface, bind it to the existing scalar proof registry/corpus manifests, run dependency-scoped SPI tests, and repair forward without assigning authority outside VM81.**
