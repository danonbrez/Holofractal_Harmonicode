# HHS Game Development Tutorial — Lattice Run Platformer Level 1

## 1. Completion report

This delivery adds a complete browser-platformer Level 1 to the Holofractal Harmonizer Application Studio as an editable, runnable, compilable, and exportable project template.

The implementation is grounded in two existing repository surfaces:

1. `applications/holofractal_harmonizer/src/application-templates-runtime.mjs`, which is the production template registry used by the visual IDE.
2. `native_projects/hhs_vm81_game_level10`, which already defines the repository's native deterministic platform-game lineage, 60-tick cadence, lifecycle expectations, capture evidence, and presentation separation.

The browser Level 1 does **not** claim to replace the native C VM81 authority path. It is the visual IDE game-development surface: the source can be edited and previewed immediately, while future native compilation can bind the same level data and input trace to the VM81 admission kernel.

### Delivered gameplay

- 3,560-pixel scrolling Level 1 world rendered into a 960×540 logical viewport.
- Keyboard, pointer-safe UI, and mobile touch controls.
- Acceleration, drag, gravity, variable-height jump, double jump, coyote time, and jump buffering.
- One-way platforms, three phase hazards, four patrol sentinels, nine collectible shards, a midpoint checkpoint, lives, respawn, pause, restart, game-over, and victory closure.
- Camera follow, parallax stars and mountains, perspective grid, luminous platform materials, animated shards, enemy silhouettes, player motion trails, pooled particles, checkpoint pulse, and closure-gate effects.
- Deterministic `?autoplay=1` route and `?capture=1` fixed-step frame interface.

### Browser verification results

The executed Playwright/Chromium run reached `victory` with:

| Measurement | Result |
|---|---:|
| Simulated completion time | 12.9667 s |
| Lives remaining | 3 |
| Route-collected shards | 4 / 9 |
| Browser console errors | 0 |
| Page errors | 0 |
| Deterministic simulation cadence | 60 Hz |
| Headless benchmark | 1,229.5 simulation ticks/s |
| Headless render benchmark | 614.8 rendered frames/s |
| Particle-pool high-water result | 60 active/reused slots at victory |

The benchmark is host-specific and is not a promise of identical device performance. It establishes substantial headroom over the authoritative 60 Hz simulation target on the execution host.

### MP4 evidence

The browser-rendered playthrough was recorded from Chromium and transcoded to H.264:

| Property | Result |
|---|---:|
| Resolution | 1100×700 |
| Codec | H.264 |
| Frame rate | 25 fps capture |
| Duration | 15.76 s |
| File size | 1,073,106 bytes |
| Pixel format | yuv420p |
| Fast-start | enabled |

The video frame rate is the presentation capture rate. Gameplay state continues to advance through the fixed 60 Hz simulation loop.

## 2. Repository architecture for games

### Application Studio path

```text
Application Studio gallery
        ↓
application-templates-runtime.mjs
        ↓
platformer-template.mjs
        ↓
editable project files
  platformer/index.html
  platformer/style.css
  platformer/app.js
  README.md
        ↓
Build & Preview
        ↓
Deployable browser compiler / ZIP export
```

The template object has four required fields:

```js
{
  id: 'platformer',
  label: 'Platformer Game',
  description: '…',
  entrypoint: 'platformer/index.html',
  files: [
    ['platformer/index.html', 'HTML', htmlSource],
    ['platformer/style.css', 'SOURCE_CODE', cssSource],
    ['platformer/app.js', 'SOURCE_CODE', javascriptSource],
    ['README.md', 'MARKDOWN', tutorialSource],
  ],
}
```

The IDE materializes these tuples as editable working-tree files. The entrypoint is opened in the application preview.

### Native VM81 path

The native module remains the reference for authoritative deterministic execution:

```text
input trace
   ↓
hhs_vm81_game_execute
   ↓
fixed integer/fixed-subpixel physics
   ↓
Hash72 receipt + Hash216 state identity
   ↓
replay comparison
   ↓
frame projection / texture / MP4 evidence
```

Browser projects should keep simulation state separate from rendering so the same level rules can later be moved behind the VM81 API without rewriting the visual layer.

## 3. Creating the platformer in the visual IDE

1. Run the Holofractal Harmonizer application using the repository's normal deployment command.
2. Open **New Application**.
3. Select **Platformer Game**.
4. Name the project.
5. Press **Create & Run Project**.
6. Edit `platformer/app.js`, `platformer/style.css`, or `platformer/index.html`.
7. Press **Build & Preview** after each dependency-scoped change.
8. Use **Download App ZIP** when the level is ready to move to another environment.

The generated project is self-contained and does not require Phaser or an external asset CDN. This keeps first-run behavior reliable inside the repository deployment and on mobile browsers.

## 4. Core game-loop pattern

The runtime separates simulation cadence from display cadence:

```js
const FIXED = 1 / 60;
let accumulator = 0;
let last = performance.now();

function frame(now) {
  const delta = Math.min(0.05, (now - last) / 1000);
  last = now;
  accumulator += delta;
  while (accumulator >= FIXED) {
    step(FIXED);
    accumulator -= FIXED;
  }
  draw();
  requestAnimationFrame(frame);
}
```

This prevents physics from changing when the monitor refresh rate changes. The `0.05` clamp prevents a hidden tab or debugger pause from injecting an unbounded catch-up step.

Keep these boundaries strict:

```text
step(dt) = gameplay authority for the browser project
draw()   = disposable projection
DOM HUD  = human-readable status surface
```

Do not make collision outcomes depend on pixels read back from the canvas.

## 5. Editing the level

Level geometry is data, not hard-coded drawing commands:

```js
const platforms = [
  { x: 0, y: 486, w: 820, h: 54 },
  { x: 930, y: 486, w: 610, h: 54 },
  { x: 430, y: 390, w: 170, h: 24 },
];

const hazards = [
  { x: 820, y: 482, w: 110, h: 58 },
];
```

To add a new room:

1. Increase `WORLD.w`.
2. Add ground segments.
3. Leave explicit gaps for hazards.
4. Add elevated platforms with enough horizontal recovery space before the next mandatory jump.
5. Place collectibles on both the safe route and optional high-skill routes.
6. Add a checkpoint before a major difficulty increase.
7. Move the closure gate and victory threshold together.

### Encounter-spacing rule

Do not place an enemy jump trigger directly before a pit unless the combined jump arc is intentionally designed to clear both. The playtest caught this exact defect during development. The corrected Level 1 separates the second sentinel from the second hazard so the player can land, read the next obstacle, and jump again.

## 6. Collision design

The level uses axis-aligned bounding boxes. Horizontal resolution only treats thick ground bodies as side walls. Thin platforms are one-way surfaces: the player can rise through them and land from above.

```js
for (const platform of platforms) {
  if (platform.h > 30 && overlaps(player, platform)) {
    // Resolve only true wall-like bodies on the horizontal axis.
  }
}

for (const platform of platforms) {
  if (overlaps(player, platform) && player.vy > 0) {
    player.y = platform.y - player.h;
    player.vy = 0;
    player.onGround = true;
  }
}
```

For production expansion, preserve the player's previous bottom coordinate and require it to be at or above the platform top before landing. That prevents tunneling when fall velocity becomes larger.

## 7. Input and mobile controls

Keyboard state is stored in a `Set`, while touch buttons write into the same normalized action object:

```js
const input = {
  left: false,
  right: false,
  jump: false,
  jumpPressed: false,
};
```

The simulation consumes actions rather than browser events. This is required for deterministic replay and future VM81 ingress.

The touch layer uses pointer events and `touch-action: none` on the game surface. Buttons remain outside the canvas so they are accessible, responsive, and easy to resize without changing world coordinates.

## 8. Graphics workflow

The demo uses procedural graphics to avoid asset-loading failures:

- vertical sky gradient;
- deterministic star field;
- camera-relative parallax mountain silhouette;
- perspective grid;
- luminous platform edge and repeated material marks;
- animated diamond shards;
- compact geometric character and enemy silhouettes;
- additive-feeling glow using `shadowBlur` only on a limited number of objects;
- pooled square particles for jump, damage, shard, checkpoint, and victory effects.

When replacing procedural art with sprites:

1. Keep stable asset keys.
2. Preload before entering gameplay.
3. Normalize sprite baselines and collision anchors.
4. Keep hitboxes independent of transparent pixel bounds.
5. Use sprite atlases to reduce requests.
6. Preserve the procedural fallback until the new asset path is verified.

## 9. Performance rules used in Level 1

### Fixed simulation

Physics is always 60 Hz, independent of display FPS.

### Device-pixel-ratio cap

```js
const dpr = Math.min(devicePixelRatio || 1, 1.5);
```

A modern phone may report DPR 3 or 4. Rendering the full 960×540 canvas at that scale can multiply fill cost and memory without improving gameplay clarity. The cap keeps the image sharp while bounding cost.

### Camera culling

Platforms, hazards, shards, and enemies outside the camera window are skipped before drawing.

### Particle pooling

Dead particle records are reused. The hot loop does not continuously allocate short-lived objects and wait for garbage collection.

### Throttled HUD updates

DOM text updates are limited to ten times per second. The canvas may render every frame, but score/time nodes do not need sixty DOM writes per second.

### Bounded effects

Glow, trails, and particles are deliberately capped. Visual effects support readability rather than occupying unbounded render time.

## 10. Deterministic playthrough and capture

The game exposes two development query parameters:

```text
?autoplay=1  deterministic rightward completion route
?capture=1   disables the live RAF loop and exposes fixed frame stepping
```

The capture interface is:

```js
window.__HHS_CAPTURE_STEP__(2)
```

Two simulation ticks per captured frame produce a deterministic 30 fps evidence sequence while preserving the 60 Hz simulation.

A successful run publishes:

```js
window.__HHS_LEVEL1_COMPLETE__ = {
  elapsed,
  shards,
  lives,
};
```

### Reproducing the MP4

```sh
cd applications/holofractal_harmonizer
node tools/materialize-platformer-level1.mjs dist/platformer-level1
python3 tools/capture-platformer-level1.py \
  --project dist/platformer-level1 \
  --output dist/HHS_VM81_PLATFORMER_LEVEL1_PLAYTHROUGH.mp4
```

Required host tools:

```text
Node.js 22+
Python 3
Python Playwright
Chromium
ffmpeg
ffprobe
```

The script records the actual Chromium page, waits for the victory witness, holds the completion screen, and transcodes to broadly compatible H.264/yuv420p with fast-start metadata.

## 11. Testing strategy

Use bounded, dependency-scoped gates:

### Template gate

- `platformer` exists in `APPLICATION_TEMPLATES`.
- entrypoint exists in the materialized file list.
- all source files are non-empty.
- `app.js` parses with `new Function(...)`.

### Simulation gate

- fixed-step capture reaches victory within a bounded number of ticks;
- lives remain positive;
- checkpoint is crossed;
- no browser console or page errors occur.

### Presentation gate

- capture has non-zero duration and size;
- codec, dimensions, and pixel format are inspected with `ffprobe`;
- representative frames show the player, platforms, hazards, HUD, and closure screen.

### Regression gate

After changes, rerun only the Application Studio tests and the platformer browser playtest. The complete inherited repository suite should be rerun only when shared runtime or deployment dependencies change.

## 12. Extending to Level 2

Recommended next additions:

1. Move level data into JSON so designers can edit geometry without changing the engine.
2. Add moving platforms with deterministic phase functions.
3. Add a state-machine enemy with patrol, alert, and recovery states.
4. Add a shard-completion bonus route rather than requiring every shard for base victory.
5. Serialize input traces and compare final state hashes.
6. Add audio through a pooled Web Audio graph with a user-gesture unlock.
7. Add sprite-atlas support while retaining procedural fallbacks.
8. Add a VM81 adapter that converts normalized actions into admitted native instruction calls.

## 13. Acceptance summary

Level 1 is complete as a real visual-IDE game project, not a landing-page mockup. It boots, accepts keyboard and touch input, simulates and renders a full side-scrolling course, handles failure and recovery, reaches an explicit victory state, exposes deterministic capture hooks, and has a browser-recorded MP4 playthrough plus reproducible tooling.
