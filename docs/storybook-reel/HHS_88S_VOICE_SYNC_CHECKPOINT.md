# HHS Storybook Reel 88s Voice Sync — Restart Checkpoint

## Identity

- Feature: automated cinematic voiceover synchronization for serialized storyboard reels
- Base main commit: `75a7912a6b204fd5cda5eb67e993a9af39f85fa6`
- Branch: `feature/storyboard-voice-sync-88s`
- Pull request: `#657`
- Current head: `73508e3ae9d5d7e95d6f2e3237794bb6d260609a`
- Merge target: `main`

## Canonical production contract

- Master duration: `88.000 s`
- Frame rate: `30 fps`
- Master video frames: `2640`
- Serialized storyboard frames/scenes: `22`
- Nominal storyboard window: `4.000 s`
- Output orientation: `9:16`
- Narration timing authority: measured ElevenLabs character timestamps, unscaled
- Voice transport: preserve fitted provider timing; resample/pad/trim container only; no post-generation `atempo`
- Provider speed bounds: `0.7..1.2`
- Accepted speech must end at or before `88.000 s`

## Implemented surfaces

- `hhs_backend/runtime/hhs_storyboard_voice_sync_v1.py`
  - exact 22 × 4-second master timeline
  - character-to-word timing
  - pause extraction
  - bounded native speed-fit planning
  - storyboard Markdown parser
  - frame binding for labels, full visual prompts, and transition anchors
  - producer JSON manifest

- `hhs_backend/runtime/hhs_storybook_elevenlabs_v1.py`
  - server-side ElevenLabs timestamped TTS
  - bounded iterative speed fitting
  - base64 voice-stem decoding
  - provider alignment retention
  - fail-closed overrun handling

- `hhs_backend/api/storybook_reel_routes.py`
  - `POST /api/runtime/storybook-reel/voiceover/sync`
  - voice stem download
  - voice-sync JSON download
  - DAW/NLE cue CSV download

- `hhs_backend/runtime/hhs_storybook_reel_v1.py`
  - preserves provider timing
  - removes post-TTS speed normalization from active audio path
  - stores JSON/CSV producer cues
  - packages voice-sync artifacts with reel output

- Native storybook ABI
  - duration changed from 90 to 88 seconds
  - scene count changed from 15 to 22
  - exact `2640 = 22 × 4 × 30` frame closure

- Storybook Reel Studio UI
  - ElevenLabs voice ID/model inputs
  - one-click **Generate + sync 88-second voiceover**
  - optional full 22-frame storyboard Markdown input
  - downloadable voice stem, JSON timing, and cue CSV
  - 88-second preview clock

## External interface

Current ElevenLabs production path uses:

`POST /v1/text-to-speech/{voice_id}/with-timestamps`

with `output_format=mp3_44100_128` by default.

Required server environment:

`ELEVENLABS_API_KEY`

The key is never sent to or embedded in frontend JavaScript.

## Tests added/updated

- `tests/test_hhs_storyboard_voice_sync_v1.py`
  - exact 22-window closure
  - speed-fit math
  - storyboard parser
  - visual prompt/transition binding
  - mocked iterative ElevenLabs fit

- `tests/test_hhs_storybook_reel_timing_v1.py`
  - 88-second timing authority
  - unscaled alignment behavior

- `tests/test_hhs_storybook_reel_studio_v1.py`
  - route and UI surface coverage

- native reel test
  - 2640-frame / 88-second contract

- full acceptance script/workflow
  - 88-second end-to-end media acceptance

## Repair-forward update — 2026-09-29

Observed CI failures on prior head `ce4d056c83063b03a1dde8c733305bc51a7bc260`:

1. **Native Storybook Reel Studio** failed during native build/test.
2. **Pass 203 Integrated Mainframe** failed during hydrated mainframe tests.

Root cause shared by both paths:
- `hhs_storybook_reel_timing_v1.py` contained literal escaped `\\n` sequences in the newly inserted timing functions, producing a Python `SyntaxError` at line 457.

Repair:
- commit `ad0e8cb52cdac659e11009d1cb3bc8e376af7af6` rewrote the block as real Python source lines.

Proactive dependency audit then found:
- native reel test still asserted legacy `scene_count == 15U`.

Repair:
- commit `73508e3ae9d5d7e95d6f2e3237794bb6d260609a` updates the invariant to `scene_count == 22U`.

Audited dependent Pass 203/high-fidelity tests and validation scripts show no remaining fixed `90`, `2700`, or `15` storyboard-duration assumptions.

Fresh CI on `73508e3ae9d5d7e95d6f2e3237794bb6d260609a`:
- Native Storybook Reel Studio: pending
- Pass 203 Integrated Mainframe: queued
- Validate Full Application IDE: pending
- HHS Consensus Gate: queued

## Validation state at checkpoint

Completed:

- GitHub repository writes committed to the feature branch
- PR #657 opened and mergeable
- branch has no known main drift at initial creation
- current high-fidelity wrapper duration guard repaired to 88 seconds
- CI path filters updated so future `hhs_storyboard_*.py` and tests trigger Storybook workflow
- repository-level static review performed for known 90-second assumptions in current Storybook runtime layers

Environment limitation:

- local/container validation could not clone GitHub because outbound DNS is unavailable in the execution container.
- repository GitHub Actions is therefore the authoritative validation environment.

Remaining:

1. Inspect the fresh PR checks on head `73508e3ae9d5d7e95d6f2e3237794bb6d260609a`.
2. Inspect **Native Storybook Reel Studio** first.
3. Repair-forward only concrete failures attributable to this change.
4. Require native build/test/sanitize, Python/JS compile, timing/UI tests, and full 88-second acceptance to pass.
5. Merge PR #657 after relevant checks are green.
6. Verify `main` contains the merged implementation.
7. A live ElevenLabs generation additionally requires `ELEVENLABS_API_KEY` and a valid voice ID; CI uses mocked provider behavior and does not require billable provider calls.

## Next action

Check PR #657 head workflow runs. If the Storybook workflow fails, inspect the failed job log, patch only the impacted files, and rerun. If green, merge and verify main.
