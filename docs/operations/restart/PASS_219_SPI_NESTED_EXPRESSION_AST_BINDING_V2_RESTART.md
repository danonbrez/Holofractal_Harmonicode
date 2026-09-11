# Pass 219 SPI Nested-Expression AST Binding v2 — Restart Checkpoint

Validated additive syntax/provenance successor for the HARMONICODE scalar-projection proof layer. This checkpoint does **not** create canonical transition authority; VM81 remains the only canonical mutation/admission authority.

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Merge target/base: `main` @ `2def7910b99046821f34e1446bcec33ca4fd4090`
- Branch: `agent/pass219-spi-scalar-projection-registry-v1-20260910`
- Previous checkpoint: `ac452f0b1506eaea2ac07b0726a5162e47b60161`
- Validated semantic head: `8714ea86a938433575e01cda1c4b81290c4814b0`
- Restart checkpoint lineage begins: `b6caa79adbf9443b45618b74bb854b45feeaec9a`
- PR: `#427`

## Frozen predecessor evidence

- Executable HARMONICODE corpus: 6 paths / 5 unique bodies.
- Raw census: 472 = 389 `PROVEN` / 27 `SYMBOLIC` / 56 `MISSING_PROJECTION` / 0 `UNSUPPORTED_DOMAIN`.
- Raw manifest: `fc421b2f84d7186693ba02e40515d7dcf471efe4fd6ade3b3a3ab662e36ef5a7`.
- Reconciliation v1: 429 `PROVEN` / 43 `SYMBOLIC` / 0 `MISSING_PROJECTION` / 0 `UNSUPPORTED_DOMAIN`.
- Reconciliation v1 manifest: `d726356e1651df8e43ad56a47885b2d4aacbb4b5c56a106476cf48519dc50b4f`.
- `classification_complete=true`; `scalar_value_complete=false`.

## Implemented v2 surfaces

- `native_projects/hhs_harmonicode_language/hhs_harmonicode_nested_expression_ast_v2.py`
- `native_projects/hhs_harmonicode_language/hhs_harmonicode_nested_expression_ast_tests_v2.py`
- `hhs_spi_scalar_projection_corpus_ast_binding_v2.py`
- `hhs_spi_scalar_projection_corpus_ast_binding_tests_v2.py`
- `hhs_spi_scalar_projection_corpus_reconciliation_v2.py`
- `hhs_spi_scalar_projection_corpus_reconciliation_tests_v2.py`
- additive v1/v2 validation in `.github/workflows/pass219-spi-scalar-projection-registry.yml`.

Parser version: `HHS_HARMONICODE_NESTED_EXPRESSION_AST_PASS_219_V2`. Pass 075 remains frozen.

The successor recognizes `SuperscriptPower`, `PowerSurface`, `PowerChain`, and `RadicalPowerSurface` without scalar evaluation. `c^b^4` remains an ordered `[c,b,4]` chain with unresolved associativity; `√(pq+u⁷²)^x²` remains a complete radical/exponent source surface with explicit contained superscript nodes. No source rewrite or algebraic associativity is selected.

The lexer repair excludes Unicode superscript digits from identifier characters. This is lexical provenance repair only.

## Parser-limit migration

Exactly five v1 parser-limit occurrences are migrated:

- `(pq+u⁷²)^x`: 2 occurrences → full `√(pq+u⁷²)^x²` `RadicalPowerSurface`.
- `c^b`: 3 occurrences → full `c^b^4` `PowerChain`.

Result: 2 families, 5 before, 0 parser-limit occurrences after, 5 AST-bound symbolic occurrences, syntax binding complete, scalar-value completion still false.

AST binding manifest: `874e4b15850cece6996bf461d2f6d87d16ad455bfd117c2c3dd684051a2604ef`.

## Reconciliation v2

Scalar classification remains unchanged: 429 `PROVEN` / 43 `SYMBOLIC` / 0 `MISSING_PROJECTION` / 0 `UNSUPPORTED_DOMAIN`. The five migrated occurrences use `NESTED-AST-SYNTAX-WITNESS-v2`; parser-limit profile occurrence count is now 0. `syntax_provenance_complete_for_migrated_profiles=true`; `scalar_value_complete=false`.

Reconciliation v2 manifest: `481c0bb0264ad0771344ae068624dcfd7c9c5ba853a8c7963ad9a22971389aee`.

## Validation and receipts

Run `34574371362`, job `103183383669`: `SUCCESS`, validating semantic head `8714ea86a938433575e01cda1c4b81290c4814b0` through PR merge-test checkout `9fec10ce15477b11bc8a59ec610f6386eb8cfeac` on Python 3.12.14.

Suites: SPI registry v1 22/22; raw corpus v1 17/17; reconciliation v1 13/13; nested AST v2 8/8; AST binding v2 8/8; reconciliation v2 8/8. Raw strict completion and v1/v2 scalar-value completion all fail closed as designed.

Artifacts:
- `10189019717` scalar manifest — `f20a252c57d20742ec7a654702e466872e234c34b931d6497d048981a4972ec8`
- `10189020319` raw corpus — `e9b7403ac3cc2428745437e40cbabd6b6780fb773bb6acd0dc157953c4d53bdd`
- `10189020875` reconciled v1 — `af374d735e962d07d7bceecbaa76871d0e93b53bc546ff683715606a16b269ec`
- `10189021456` AST binding v2 — `223db7650a15470eb2918b4f8646776a6960941d1c545f1c622458a52bc7a30a`
- `10189021997` reconciled v2 — `9ff4fc58042c085e5e82a163d65f7b45e291bf8d3b168ff4a7237c807f3c9907`

## Authority boundary and next action

No VM81 mutation, canonical Hash72/Hash216 minting, source rewriting, ordered-product commutation, associativity selection, projection-to-native identity promotion, or unresolved phase/radical scalarization is authorized.

Next: **implement O2 ordered matrix-power scalar witness as an additive exact ordered matrix/tensor proof surface, bind it to SPI/corpus manifests, run dependency-scoped validation, and repair forward without creating secondary authority.** O3 `f == t/m` provenance follows. Formal `I²`, `I³`, and `x²` remain symbolic absent an explicit registered scalar projection.

Restart from the latest branch head carrying this file. The stable semantic validation anchor is `8714ea86a938433575e01cda1c4b81290c4814b0`; later commits in this checkpoint lineage are documentation-only.
