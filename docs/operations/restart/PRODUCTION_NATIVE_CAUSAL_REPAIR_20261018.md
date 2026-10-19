# Production native causal model acceptance repair — restartable checkpoint

- Base: main at PR #823 creation `cf5eb2a96abc58346d0371958ffc9bd6b4d28566`.
- Working branch: `repair/native-causal-model-production-acceptance-20261017`.
- Merge target: `main`; PR #823 is draft.
- Source patch: `fb6590ec4abb7a336f02da4c0a3f727467973d3f` updates `.github/workflows/digitalocean-production-main.yml` with pinned provisioning in actual `/opt/hhs/venv/bin/python` before direct CLI acceptance.
- CI run `39052596707`: deployment-contract validation SUCCESS, backend closure SUCCESS, deploy-exact-main SKIPPED. Lane 5 Native Capability Provider run `39052596731` SUCCESS. These are PR scoped, *not production deployment evidence*.
- Initial production failure: cf5eb2a9 promotion reported, native-chat exit 27, `transformers` unavailable, four canned responses, no serialized blocks, HTTPS/Chromium skipped.
- Retained source authority: existing pinned `tools/provision_native_causal_model.py` and `requirements-native-causal-lm.txt`, strict `tools/hhs_native_chat_cli.py`, Pass219 signed VM81/Hash72/Hash216 boundary. No canonical mutation changes.
- Remaining: review current main drift; ensure exact provisioner/model pins remain valid and service permissions correct; merge only after PR acceptance; run *main push* exact deployment and inspect native-chat generated distinct outputs and serialized blocks, HTTPS+Chromium artifacts.
- Do not equate green PR workflow (deploy skipped) with successful deployed model installation or production delivery. Production SHA must be checked from actual promotion receipt.
- Next action: verify PR #823 against current main and add native preflight regression/negative tests if missing; complete guarded merge and main deployment validation.
