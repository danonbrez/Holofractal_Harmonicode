import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { PLATFORMER_LEVEL1_TEMPLATE } from '../src/platformer-template.mjs';

const target = resolve(process.argv[2] || 'dist/platformer-level1');
await mkdir(target, { recursive: true });
for (const [path, , content] of PLATFORMER_LEVEL1_TEMPLATE.files) {
  const relative = path.startsWith('platformer/') ? path.slice('platformer/'.length) : path;
  const output = resolve(target, relative);
  await mkdir(resolve(output, '..'), { recursive: true });
  await writeFile(output, content, 'utf8');
}
console.log(JSON.stringify({ classification: 'HHS_PLATFORMER_LEVEL1_MATERIALIZED', target, files: PLATFORMER_LEVEL1_TEMPLATE.files.length }));
