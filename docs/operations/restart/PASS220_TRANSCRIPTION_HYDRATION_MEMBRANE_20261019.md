# Pass220 transcription membrane restart 2026-10-19

- Branch: `pass220/transcription-hydration-proof-membrane-20261019` based on main; PR targets main.
- Changed: native candidate adapter `hhs_runtime/hhs_pass220_transcription_hydration_membrane_v1.py`, test `tests/pass220/test_hhs_pass220_transcription_hydration_membrane_v1.py`, workflow `.github/workflows/pass220-transcription-hydration.yml`, contract `contracts/pass220/PASS220_TRANSCRIPTION_HYDRATION_MEMBRANE_V1.md`, this restart record.
- Source commit `d91f308a3d409ac03fa7cab6fe7d94745bb66651`, tests commit `0f985bf98b4263df21fd1520c545ce8d2be18a17`.
- Behavior: reversible byte transcription, exact BigInt and 5184 coordinate addressing, native eight-role ordering without product scalarization; fail-closed negative probes. Candidate evidence is nonauthoritative.
- Validation: CI created, not yet observed; no native signed receipt or real RNA ABI has been tested. Remaining: inspect workflow, correct any failures; bind actual inherited RNA encoder/decoder, ordered phase gear and per-state Hash216 witness through Pass219 signed VM81.
- Base/merge target: main; no PR merged and no production deployed in this task.

## 2026-10-19 exact state-window proof replay increment
- Prior run 39280793652 was queued at inspection; no CI pass claimed.
- Inspected inherited C ABI `hhs_runtime/include/hhs_pass219_rna_transcription_1_10.h`. It provides `hhs_exact_pass219_rna_admit_composed`, `hhs_exact_pass219_hash216_indexes_complete`, `hhs_exact_pass219_coordinate_from_pass189` and native phase witness calls. This candidate adapter still does not invoke that C ABI.
- `0fe32cc063cb28ce31da4e710210dee41a5e5bb9`: derive exactly one deterministic BigInt p=P-1/P/q=P+1 window proof per candidate serialization address, carry exact native constraint source without interpreting slash as scalar division, and digest ordered slot identity.
- `aa8e553431bb8591b94fcd841212be4aa258a683`: reject tampered candidate proof under deterministic re-transcription replay.
- Scope remains candidate-only. This does not establish the one-witness-per-unique signed Hash216 rule, which requires real signed transition identity and repository admission integration.
- Next: run targeted CI, bind native coordinate/phase witness and RNA admission via actual compiled C API, validate parent/change/receipt indexed Hash216 transition, and integrate Lane5 gate without bypass.
