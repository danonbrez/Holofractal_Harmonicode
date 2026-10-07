# HHS Native Storybook Reel Studio

## Contract

| Field | Value |
|---|---|
| Identifier | `HHS-NATIVE-VM81-STORYBOOK-REEL-STUDIO-V1` |
| Primary application | `/storybook-reel/` |
| Runtime API | `/api/runtime/storybook-reel` |
| Canonical duration | 88 seconds |
| Canonical video | 1080×1920, 30 fps, H.264, yuv420p |
| Canonical audio | narration-normalized 48 kHz mono, AAC transport |
| Mutation authority | singleton VM81/HHS Runtime authority |
| Parallel computation | prohibited for this application workflow |

## User workflow

The complete product workflow requires no backend, programming, command-line, game-engine, ABI, or media-encoding knowledge.

1. Open the Storybook Reel Studio.
2. Paste the raw text used to create the narration.
3. Upload the narration audio file.
4. Optionally upload ElevenLabs alignment JSON.
5. Review the contextual template and x/y/z/w color defaults.
6. Adjust typography, 3D effect, motion, colors, phase origin, placement, caption density, and panel opacity while the vertical preview updates in real time.
7. Select **Generate 88-second reel**.
8. Review the generated video.
9. Select **Download MP4 + source ZIP**.

The ZIP contains the MP4, original narration, source text, style configuration, transcript timing, request record, native ABI manifest, Hash72 receipt, and README.

## Native rendering authority

Every final frame is produced through the repository-native game and storybook C surfaces:

```text
raw story text
→ exact UTF-8 ingress
→ deterministic scene and caption spans
→ VM81 platformer state transitions
→ native sprite-map projection
→ native governed texture projection
→ native storybook page projection
→ native 3D caption and reciprocal palette projection
→ ordered Hash72/Hash216 frame chains
→ raw RGBA frame stream
```

The application verifies:

- all 19 inherited platformer opcodes;
- canonical program round-trip;
- deterministic game replay;
- non-mutating sprite and texture projections;
- Hash72 and Hash216 story, state, frame, palette, timing, and receipt identities;
- exactly 2,640 ordered frames for the canonical output;
- `parallel_computation_used: false`.

## Twelve-tone reciprocal color logic

The native palette engine maps twelve chromatic pitch classes to twelve positions around a color wheel. Each position occupies six points of the 72-position phase clock:

```text
12 chromatic tones × 6 phase positions = 72 phases
```

For every scene:

- `x` is the deterministic tonic color plane;
- `z` is the reciprocal tritone plane at `x + 36 mod 72`;
- `y` is selected from compatible minor/major third, fourth, fifth, sixth, seventh, or controlled chromatic-neighbor relations;
- `w` supplies cadence, extension, or controlled chromatic tension;
- the story Hash216 identity and scene index seed the deterministic pseudorandom selection;
- repeated input produces the same palette sequence;
- manual x/y/z/w colors remain available when automatic harmony is disabled.

This is chromatic harmony logic, not arbitrary random RGB selection.

## Typography and motion

No external font or animation engine is required. Native bitmap glyphs support:

- classic;
- bold;
- serif;
- wide;
- shadow.

Native effects support:

- flat;
- extruded depth;
- parallax;
- orbital motion;
- 72-phase wave motion.

Font scale, letter spacing, extrusion depth, motion speed, motion amplitude, title placement, caption placement, line length, line count, and panel opacity are adjustable.

## Automated cinematic voiceover workflow

The studio can generate the narration directly through ElevenLabs without exposing the provider key to the browser.

1. Paste the exact narrative caption.
2. Optionally paste the complete 22-frame storyboard Markdown.
3. Enter an ElevenLabs voice ID and model.
4. Select **Generate + sync 88-second voiceover**.
5. The server synthesizes speech through the timestamped TTS endpoint and measures the returned character alignment.
6. If the narration overruns the master, the runtime iteratively regenerates with a bounded native ElevenLabs speed adjustment. It never accepts spoken audio that crosses 88.000 seconds.
7. If narration ends early, the remaining master time is preserved as silence rather than time-stretching the voice.
8. Download the original voice stem, JSON timing manifest, or DAW/NLE cue CSV.
9. The cue manifest binds every 4-second visual window to overlapping narration, word timestamps, pauses, storyboard label, full image prompt, and transition anchor when storyboard Markdown was supplied.

The backend reads `ELEVENLABS_API_KEY` from server environment state. The secret is never embedded in frontend JavaScript or returned in API responses.

The generated voice stem is preserved at provider timing. FFmpeg may resample to 48 kHz and pad or trim the master container boundary, but it does not use `atempo` to stretch a fitted narration.

## Narration synchronization

Synchronization uses the exact matching text and uploaded audio.

Priority order:

1. ElevenLabs character start/end alignment;
2. uploaded word or segment start/end alignment;
3. deterministic punctuation-weighted duration fitting.

External decimal timestamps are parsed into rational values and converted to exact integer frame indices. The uploaded narration preserves measured provider timing and is padded or trimmed only at the 88-second master boundary. The fallback is explicitly classified as duration-fitted rather than exact transcription alignment.

## External dependency boundary

FFmpeg and ffprobe are the only required external media tools. Their permitted roles are:

- inspect the uploaded audio stream;
- normalize narration duration and sample format;
- integer-scale and pad the native frame stream for vertical presentation;
- encode H.264 video and AAC audio;
- mux MP4;
- inspect the finished media.

They do not generate the story, captions, game state, animation, typography, reciprocal palette, frame identity, or Runtime receipts.

The frontend uses browser-native HTML, CSS, JavaScript, Canvas, File, Audio, Video, and Fetch APIs only.

## API

| Method | Route | Purpose |
|---|---|---|
| GET | `/status` | Runtime, tools, templates, geometry, and authority status |
| POST | `/defaults` | Contextual template and reciprocal palette defaults |
| POST | `/audio` | Raw-body audio ingress without multipart dependencies |
| POST | `/generate` | Serialized native generation and package creation |
| GET | `/artifacts/{artifact_id}` | Artifact metadata and receipts |
| GET | `/artifacts/{artifact_id}/video.mp4` | Generated reel playback |
| GET | `/artifacts/{artifact_id}/download.zip` | One-click complete package download |

## Acceptance

The dedicated hosted workflow must pass:

- canonical C ABI build;
- storybook shared library and CLI build;
- native positive and fail-closed tests;
- ASAN and UBSAN;
- Python and JavaScript syntax;
- deterministic timing and reciprocal palette tests;
- visual-server route precedence;
- no-code studio reachability;
- raw audio upload and inspection;
- full 88-second generation;
- ffprobe codec, dimensions, frame rate, audio, and duration checks;
- ZIP content and receipt checks;
- evidence artifact upload.

## Restartability

All implementation, workflows, tests, contracts, and recovery information are repository-visible. No private local state or conversation memory is required to rebuild, validate, operate, or continue the application.
