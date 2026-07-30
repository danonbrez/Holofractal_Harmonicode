import { content as index } from './harmonic-puzzle-template-parts/index.mjs';
import { content as style } from './harmonic-puzzle-template-parts/style.mjs';
import { content as model } from './harmonic-puzzle-template-parts/model.mjs';
import { content as renderer } from './harmonic-puzzle-template-parts/renderer.mjs';
import { content as controls } from './harmonic-puzzle-template-parts/controls.mjs';
import { content as app } from './harmonic-puzzle-template-parts/app.mjs';
import { content as readme } from './harmonic-puzzle-template-parts/readme.mjs';

function stripModuleSyntax(source) {
  return source
    .replace(/^import\s+[\s\S]*?\s+from\s+['"][^'"]+['"];\n?/gm, '')
    .replace(/^export\s+/gm, '');
}

const bundledApplication = [model, renderer, controls, app]
  .map(stripModuleSyntax)
  .join('\n');

export const HARMONIC_PUZZLE_TEMPLATE = Object.freeze({
  id: 'harmonic-puzzle',
  label: 'Harmonicode Geometry',
  description: 'A deterministic Lo Shu resonance puzzle with touch, keyboard, save state, hints, audio, and six levels.',
  entrypoint: 'harmonic-puzzle/index.html',
  files: Object.freeze([
    Object.freeze(['harmonic-puzzle/index.html', 'HTML', index]),
    Object.freeze(['harmonic-puzzle/style.css', 'SOURCE_CODE', style]),
    Object.freeze(['harmonic-puzzle/app.js', 'SOURCE_CODE', bundledApplication]),
    Object.freeze(['harmonic-puzzle/README.md', 'MARKDOWN', readme]),
  ]),
});
