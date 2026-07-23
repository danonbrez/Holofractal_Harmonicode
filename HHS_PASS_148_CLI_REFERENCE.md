# HHS Pass 148 CLI Reference

All operations are boundary-constructed and support global `--db` and `--format json|jsonl|text|markdown`.

- `hhs semantic analyze --expression EXPR --source-type TYPE --source-reference REF`
- `hhs semantic analyze-document PATH --source-type TYPE`
- `hhs semantic derive --proposition ID --rule RULE --substitutions JSON`
- `hhs semantic project --profile PROFILE --expression EXPR`
- `hhs semantic classify --proposition ID`
- `hhs semantic proposition ID`
- `hhs semantic derivation ID`
- `hhs semantic promotion-request --source ID --target CLASS --governing-rule RULE`
- `hhs semantic promotion-evaluate REQUEST --authorize|--reject --authority A3|A4 --rationale TEXT`
- `hhs semantic rule show RULE_ID`
- `hhs semantic replay TARGET_ID`
- `hhs semantic audit --dependency-scope pass148`
- `hhs semantic registry sync|audit`
- `hhs semantic serve --host 127.0.0.1 --port 8878 --token TOKEN`

External-agent profiles may use all analytical operations except `promotion-evaluate` and `registry sync`. They cannot claim `contract`, `runtime`, or `user_declaration` source authority through request fields.
