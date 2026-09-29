SERIALIZED STORYBOARD GENERATOR — COMPANION EXTENSIONS

PURPOSE

Extend "Storyboard_Generation_Template.md" without changing its canonical production contract:

- one approximately 2,200-character narrative
- exactly 22 serialized storyboard frames
- approximately 4 seconds per frame
- exactly 88 seconds of serialized visual timeline
- 9:16 vertical output

These extensions add:

1. persistent Midjourney character-reference handling
2. persistent Midjourney style-reference handling
3. version-aware Midjourney reference syntax
4. ElevenLabs voice generation
5. exact narration-to-frame synchronization
6. pauses and performance direction
7. sound-design cue generation
8. final 88-second audio manifest

The original storyboard remains the narrative and visual authority.

---

EXTENSION A — CHARACTER AND STYLE REFERENCE SYSTEM

OBJECTIVE

Allow an approved storyboard image, character sheet, character portrait, style image, or Midjourney style code to become a persistent reference for later serialized frames.

References supplement the written continuity bible.

They do not replace it.

Every image prompt must remain independently descriptive enough to preserve:

- character identity
- wardrobe
- age
- anatomy
- environment
- chronology
- lighting
- production design
- narrative state

---

REFERENCE INPUTS

MIDJOURNEY VERSION:

[V6 / NIJI 6 / V7 / V8.1 / V8.2 / CURRENT]

CHARACTER REFERENCE:

[NONE / IMAGE URL / APPROVED FRAME / CHARACTER SHEET / EDIT MODEL REFERENCE]

CHARACTER REFERENCE WEIGHT:

[OPTIONAL]

STYLE REFERENCE:

[NONE / IMAGE URL / SREF CODE / MULTIPLE REFERENCES]

STYLE REFERENCE WEIGHT:

[OPTIONAL]

STYLE VERSION:

[OPTIONAL]

REFERENCE LOCK FRAME:

[FRAME NUMBER OR EXTERNAL CHARACTER MASTER]

REFERENCE POLICY:

[GLOBAL / CHARACTER-SPECIFIC / SCENE-SPECIFIC]

---

VERSION-AWARE CHARACTER REFERENCE ADAPTER

The generator must not blindly append "--cref".

It must first determine the selected Midjourney generation mode.

MIDJOURNEY V6 / NIJI 6

Character-reference serialization:

"--cref [CHARACTER_REFERENCE_URL] --cw [WEIGHT]"

Use this when explicit legacy Character Reference behavior is required.

The written prompt must still state the character's important persistent physical attributes.

---

MIDJOURNEY V7

Character/object-reference serialization:

"--oref [REFERENCE_URL] --ow [WEIGHT]"

The same Omni Reference should remain stable across the serialized frame sequence unless the production explicitly changes reference identity.

---

MIDJOURNEY V8.1 / V8.2

Use the Midjourney Edit Model reference-image workflow.

Do not fabricate a "--cref" or "--oref" parameter for V8.

Instead output a reference manifest such as:

CHARACTER REFERENCE ATTACHMENT:
"CHARACTER_MASTER_01"

REFERENCE SOURCE:
"[APPROVED IMAGE / FILE / URL]"

REFERENCE ROLE:
"persistent character identity"

The production system or operator attaches that image as an Edit Model reference.

Up to the supported reference-image limit may be assigned where multiple persistent characters are present.

---

STYLE REFERENCE ADAPTER

When a style reference exists, append:

"--sref [STYLE_REFERENCE]"

Optional strength:

"--sw [STYLE_WEIGHT]"

The style reference may be:

- an image URL
- a Midjourney style-reference code
- multiple compatible style references

The text prompt must remain compatible with the reference style.

Do not add contradictory style descriptions simply because the original visual template contains generic cinema terminology.

---

REFERENCE HIERARCHY

The generator should resolve visual constraints in this order:

1. STORY FACTS
2. CHARACTER IDENTITY
3. TEMPORAL STATE
4. APPROVED CHARACTER REFERENCE
5. APPROVED WORLD / LOCATION REFERENCE
6. STYLE REFERENCE
7. FRAME-SPECIFIC COMPOSITION
8. OPTIONAL MODEL STYLIZATION

A reference may influence appearance.

It may not override a narrative fact.

Example:

If the canonical character reference shows an undamaged coat but the story establishes that the coat is torn in Frame 14, Frame 15 must retain the same character and same coat while preserving the tear.

Continuity evolves.

It does not reset to the reference image every frame.

---

CHARACTER MASTER GENERATION MODE

If no approved character reference exists, the generator may create a CHARACTER MASTER PROMPT before generating the serialized sequence.

Output:

CHARACTER MASTER — [CHARACTER NAME]

Create a neutral, high-information visual reference of the canonical character.

Include:

- face
- age
- skin
- eyes
- hairstyle
- body proportions
- default wardrobe
- footwear
- accessories
- recurring props
- front-biased readable lighting
- production style
- minimal environmental distraction
- 9:16 composition when appropriate

After the resulting image is approved, its URL or reference identity becomes the persistent character reference.

Do not count Character Master images among the canonical 22 storyboard frames.

---

STYLE MASTER GENERATION MODE

If no style reference exists, the generator may create a STYLE MASTER PROMPT.

The Style Master should emphasize:

- medium
- color science
- contrast
- lighting
- texture
- atmospheric density
- lens language
- production design
- environmental treatment
- rendering philosophy

It should avoid unnecessary unique characters or narrative events.

After approval, convert it into a reusable Style Reference image or style code.

Do not count Style Master images among the canonical 22 frames.

---

STORYBOARD PROMPT EXTENSION

Each completed frame may now contain:

FRAME [##] — [LABEL]

[CORE SERIALIZED IMAGE PROMPT]

REFERENCE PARAMETERS:
[version-correct reference information]

TRANSITION ANCHOR:
[existing transition anchor]

For a V6 example:

"--cref [URL] --cw 100 --sref [STYLE] --sw 150 --ar 9:16 --v 6"

For a V7 example:

"--oref [URL] --ow 120 --sref [STYLE] --sw 150 --ar 9:16 --v 7"

For V8.x:

REFERENCE ATTACHMENTS:

- Character: "[CHARACTER_MASTER_01]"
- Style: "[STYLE_REFERENCE_01]"

PROMPT PARAMETERS:
"--sref [STYLE] --sw [WEIGHT] --ar 9:16"

Do not output incompatible parameters merely to preserve identical syntax between model generations.

---

EXTENSION B — 88-SECOND VOICEOVER AND AUDIO TIMELINE

OBJECTIVE

Convert the Narrative Caption into a synchronized spoken performance aligned to the exact storyboard timeline.

Canonical timeline:

FRAME 01 = 00:00.000–00:04.000
FRAME 02 = 00:04.000–00:08.000
FRAME 03 = 00:08.000–00:12.000

Continue in four-second increments.

FRAME 22 = 01:24.000–01:28.000

TOTAL MASTER TIMELINE:

"88.000 seconds"

---

AUDIO INPUTS

VOICE PROVIDER:

ElevenLabs

VOICE ID:

[VOICE_ID]

MODEL:

[SELECTED ELEVENLABS TTS MODEL]

LANGUAGE:

[AUTO / LANGUAGE CODE]

NARRATOR TYPE:

[MALE / FEMALE / ANDROGYNOUS / CHARACTER / DOCUMENTARY / OTHER]

VOCAL CHARACTER:

[LOW / INTIMATE / AUTHORITATIVE / FRAGILE / CINEMATIC / RESTRAINED / OTHER]

DELIVERY:

[DESCRIPTION]

DEFAULT SPEED:

1.0

TARGET MASTER DURATION:

88.000 seconds

SOUND DESIGN:

[OFF / MINIMAL / CINEMATIC / DENSE]

MUSIC BED:

[NONE / EXTERNAL / GENERATED SEPARATELY]

---

FUNDAMENTAL AUDIO RULE

Do not assume that approximately 2,200 characters equals 88 seconds of speech.

Narrative character count controls caption scale.

Generated audio controls actual temporal duration.

Therefore:

"NarrativeLength ≠ AudioDuration"

and:

"ActualTimestamps → TimelineAuthority"

The final voice generation must be measured.

---

TTS GENERATION PASS

Generate the narration using ElevenLabs Text-to-Speech with timestamps.

Preferred API operation:

"POST /v1/text-to-speech/{voice_id}/with-timestamps"

Retain:

- generated audio
- original text
- character sequence
- character start timestamps
- character end timestamps
- normalized alignment when applicable
- model
- voice
- voice settings
- generation identity / request metadata when available

---

RUNTIME FIT LOOP

After generation:

"D = measured narration duration"

Target:

"T = 88.000 seconds"

Calculate:

"Δ = T - D"

Then classify:

WITHIN ACCEPTANCE WINDOW

If narration naturally fits the intended performance and the remaining time can be assigned to deliberate pauses or final ambience:

ACCEPT.

NARRATION TOO SHORT

Adjust in this order:

1. restore intended dramatic pauses
2. slow delivery moderately
3. extend purposeful silence around important lines
4. add nonverbal breathing room between dramatic units
5. only then revise prose if necessary

NARRATION TOO LONG

Adjust in this order:

1. reduce unnecessary pauses
2. increase supported speech speed moderately
3. remove redundant language without losing narrative information
4. regenerate
5. remeasure

Do not destroy intelligibility merely to preserve the original wording.

Do not arbitrarily time-stretch finished speech when a native regeneration can solve the timing problem.

The canonical narrative meaning must survive timing optimization.

---

VOICE SPEED LIMIT

When using ElevenLabs native speed control:

Minimum:

"0.7"

Maximum:

"1.2"

Default:

"1.0"

Prefer the smallest adjustment required.

Extreme speed values should not be the first solution to a narration-length mismatch.

---

EXACT ALIGNMENT PASS

After the final voice performance exists, obtain exact alignment.

If the final audio is the untouched TTS result, use the timestamps returned by the TTS-with-timestamps request.

If the narration audio has been edited, assembled, cleaned, processed, or externally mastered, use ElevenLabs Forced Alignment:

"POST /v1/forced-alignment"

Inputs:

- final narration audio
- exact spoken transcript

Retain:

- word
- word start
- word end
- character
- character start
- character end
- alignment loss/confidence information

The final edited audio alignment supersedes all predicted timing.

---

22-FRAME NARRATION MAP

Divide the authoritative timing result into these windows:

01 — 00:00.000–00:04.000
02 — 00:04.000–00:08.000
03 — 00:08.000–00:12.000
04 — 00:12.000–00:16.000
05 — 00:16.000–00:20.000
06 — 00:20.000–00:24.000
07 — 00:24.000–00:28.000
08 — 00:28.000–00:32.000
09 — 00:32.000–00:36.000
10 — 00:36.000–00:40.000
11 — 00:40.000–00:44.000
12 — 00:44.000–00:48.000
13 — 00:48.000–00:52.000
14 — 00:52.000–00:56.000
15 — 00:56.000–01:00.000
16 — 01:00.000–01:04.000
17 — 01:04.000–01:08.000
18 — 01:08.000–01:12.000
19 — 01:12.000–01:16.000
20 — 01:16.000–01:20.000
21 — 01:20.000–01:24.000
22 — 01:24.000–01:28.000

Words may cross frame boundaries naturally.

Do not cut spoken words merely because an image changes.

Instead use the actual timestamp of the phrase to determine where the visual transition should emotionally land.

---

AUDIO TIMELINE OUTPUT FORMAT

For each frame output:

FRAME [##] AUDIO

TIME:
"HH:MM.mmm–HH:MM.mmm"

NARRATION:
"[exact words spoken during or overlapping this interval]"

DELIVERY:
"[performance direction]"

PAUSE:
"[duration and dramatic purpose, if any]"

AMBIENCE:
"[environmental bed]"

SFX:
"[specific sound event or NONE]"

SFX START:
"[timestamp]"

SFX DURATION:
"[seconds]"

TRANSITION AUDIO:
"[sound or silence connecting the next frame]"

DUCKING:
"[optional narration/music/SFX balance instruction]"

---

PERFORMANCE DIRECTION

Performance notes should control characteristics such as:

- restrained
- intimate
- urgent
- reflective
- detached
- frightened
- awed
- whispered
- measured
- accelerating
- slowing
- emotionally neutral
- deliberate silence

Performance instructions are production metadata unless deliberately encoded using syntax supported by the selected ElevenLabs model.

Do not accidentally make stage directions audible.

---

PAUSE SYSTEM

Pauses should be purposeful.

Valid uses include:

- revelation
- scene transition
- emotional processing
- visual emphasis
- allowing sound design to become foreground
- preserving a final silent beat

For every pause record:

"START"
"END"
"DURATION"
"PURPOSE"

When supported by the selected TTS model, native pause/break controls may be used.

Otherwise generate narration in controlled segments and assemble the segments according to the timing manifest.

---

SOUND DESIGN GENERATION

Sound design should remain separate from spoken narration.

For every generated effect create:

SFX ID:
"SFX_###"

PROMPT:
"[concise sound-generation description]"

START:
"[exact master timeline position]"

DURATION:
"[requested duration]"

LOOP:
"true / false"

PROMPT INFLUENCE:
"[optional]"

GAIN:
"[mix recommendation]"

FADE IN:
"[duration]"

FADE OUT:
"[duration]"

DUCK UNDER VOICE:
"true / false"

ASSOCIATED FRAME:
"[01–22]"

ASSOCIATED TRANSITION:
"[optional]"

---

ELEVENLABS SOUND EFFECT GENERATION

Preferred operation:

"POST /v1/sound-generation"

Use individual effects where practical rather than attempting to generate the entire 88-second soundscape as one effect.

Examples:

- subglacial wind
- distant geological fracture
- rain against stone
- low geothermal resonance
- membrane activation
- electrical failure
- falling mineral dust
- deep structural tremor
- final power collapse
- residual machine tone

Complex sound design should be assembled from discrete controllable layers.

---

AUDIO LAYER MODEL

Use separate logical lanes:

A0 — MASTER CLOCK
A1 — NARRATION
A2 — ENVIRONMENTAL AMBIENCE
A3 — TRANSIENT SOUND EFFECTS
A4 — TRANSITION EFFECTS
A5 — MUSIC / TONAL BED
A6 — OPTIONAL CHARACTER DIALOGUE

All lanes resolve against the same:

"00:00.000 → 01:28.000"

master timeline.

---

FRAME / AUDIO COUPLING

The soundtrack and storyboard should reinforce the same dramatic event without becoming mechanically synchronized.

Not every frame requires:

- a new sentence
- a new sound
- a musical hit
- a pause

The system should favor semantic synchronization.

Examples:

A revelation may begin during Frame 13 and complete during Frame 14.

A geological rumble may begin under Frame 08 and peak at the transition into Frame 09.

A final sentence may end before Frame 22 so the last image remains in silence.

---

FINAL OUTPUT EXTENSION

After the normal Storyboard section, append:

REFERENCE MANIFEST

MIDJOURNEY VERSION:
[...]

CHARACTER REFERENCES:
[...]

STYLE REFERENCES:
[...]

REFERENCE PARAMETERS:
[...]

---

VOICEOVER DIRECTION

VOICE:
[...]

MODEL:
[...]

PERFORMANCE:
[...]

MEASURED NARRATION DURATION:
[...]

MASTER DURATION:
88.000 seconds

---

88-SECOND AUDIO MAP

FRAME 01 AUDIO
[...]

Continue through:

FRAME 22 AUDIO
[...]

---

SOUND DESIGN MANIFEST

SFX_001
[...]

SFX_002
[...]

Continue as required.

---

ELEVENLABS GENERATION MANIFEST

TTS ENDPOINT:
[...]

VOICE ID:
[...]

MODEL:
[...]

VOICE SETTINGS:
[...]

FINAL ALIGNMENT SOURCE:
[TTS TIMESTAMPS / FORCED ALIGNMENT]

SOUND EFFECT ENDPOINT:
[...]

---

EXTENDED CONSISTENCY TEST

Before returning the complete production package verify:

- base narrative remains authoritative
- approximately 2,200-character caption preserved
- exactly 22 storyboard frames
- exactly 88.000 seconds of master timeline
- character reference identity remains stable
- style reference remains stable
- reference syntax matches selected Midjourney version
- no legacy "--cref" silently inserted into incompatible versions
- V8 reference images are represented as Edit Model attachments
- "--sref" values remain consistent where required
- reference images do not overwrite narrative state changes
- voiceover uses the same narrative as the reel
- actual generated timing, not estimated reading speed, determines synchronization
- no spoken word is artificially split at a four-second frame boundary
- pauses are intentional
- performance directions are not accidentally spoken
- SFX are separate from narrative text
- sound-design cues have exact timeline positions
- audio transitions support visual transition anchors
- final frame concludes at exactly 88.000 seconds
- final audio alignment has been regenerated if the narration audio changed after initial TTS generation

---

GENERATION PRINCIPLE

The complete serialized reel now consists of four synchronized layers:

"NARRATIVE"
→ what the reel means

"STORYBOARD"
→ what the reel shows

"REFERENCE MANIFEST"
→ what must remain visually invariant

"AUDIO TIMELINE"
→ when the narrative and sonic events occur

All four resolve onto one canonical 88-second timeline.

The storyboard is therefore no longer merely a collection of image prompts.

It becomes a reproducible serialized audiovisual production specification.