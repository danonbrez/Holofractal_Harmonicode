import { content as index } from './harmonic-puzzle-template-parts/index.mjs';
import { content as style } from './harmonic-puzzle-template-parts/style.mjs';
import { content as model } from './harmonic-puzzle-template-parts/model.mjs';
import { content as renderer } from './harmonic-puzzle-template-parts/renderer.mjs';
import { content as controls } from './harmonic-puzzle-template-parts/controls.mjs';
import { content as app } from './harmonic-puzzle-template-parts/app.mjs';
import { content as readme } from './harmonic-puzzle-template-parts/readme.mjs';

export const HARMONIC_PUZZLE_TEMPLATE = Object.freeze({
  id: 'harmonic-puzzle',
  label: 'Harmonicode Geometry',
  description: 'A deterministic Lo Shu resonance puzzle with touch, keyboard, save state, hints, audio, and six levels.',
  entrypoint: 'harmonic-puzzle/index.html',
  files: Object.freeze([
    Object.freeze(['harmonic-puzzle/index.html', 'HTML', index]),
    Object.freeze(['harmonic-puzzle/style.css', 'SOURCE_CODE', style]),
    Object.freeze(['harmonic-puzzle/model.js', 'SOURCE_CODE', model]),
    Object.freeze(['harmonic-puzzle/renderer.js', 'SOURCE_CODE', renderer]),
    Object.freeze(['harmonic-puzzle/controls.js', 'SOURCE_CODE', controls]),
    Object.freeze(['harmonic-puzzle/app.js', 'SOURCE_CODE', app]),
    Object.freeze(['harmonic-puzzle/README.md', 'MARKDOWN', readme]),
  ]),
});
