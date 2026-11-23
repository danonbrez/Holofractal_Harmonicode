# Pass220 exact ordered List-power parser restart

- Branch: `pass220/harmonicode-list-power-ordered-parser-20261019` from `main` 2026-10-19; merge target main. Determine exact base SHA before merge.
- Changed native successor: `native_projects/hhs_harmonicode_language/hhs_harmonicode_nested_expression_ast_v2.py`. Does not alter frozen Pass075 statement parser.
- The inherited AST v2 previously isolated just parenthesized operands and right-side bare `List` identifiers during caret parsing. This change recognizes complete `List(...)` function-call operands without selecting mathematical power semantics, changing List boundaries or commuting operator order.
- Exact source: `List(x,x^2,y,y^4,z,z^2,w,w^4)^List(-List(0,1),List(0,1)-List(List(1,0),(-List(1,0)))/{{0,-1},List(List(-1,1),{{3,2},{-1,0}})},-(List((-List(0,1)),List(0,1)-List(List(1,0),(-List(1,0))))/{{0,-1},List(List(-1,1),{{3,2},{-1,0}})}+List(List(4,1,2,3),List(3,4,1,2),List(2,3,4,1),List(1,2,3,4))))`
- Commits: `392f829b9f14d1813e8e640732a272a198279259` parser, `be3b924485a360cf7b2e6d1257371797a40b60ae` tests, `750676ddd41153b32323ee94782d5cada898493d` AST field repair, `514d5cdf03d0cbbf4fbb1e4299f2d5e1b32e7599` CI.
- Scoped proof obligation: whole 8-term base and complete nested List exponent become source-spanned `PowerSurface.ordered_operands`; swapped carrier order changes root; diagnostics do not report malformed delimiter. Source syntax evidence only.
- No VM81 state changes, Hash72 canonical mint, Hash216 closure, or semantics of ranked tensor power verified. Existing v2 capability explicitly says general nested expression AST incomplete.
- Next: observe CI, fix failures, extend HARMONICODE ordered List tree syntax with inherited grammar and constraint-lowering contracts, then bind to 5184 proof verification and signed VM81 admission. Validation currently unconfirmed.
