import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';

export function verify(binary = resolve('native_projects/hhs_pass156_1_lshpvs/dist/hhs-lshpvs')) {
  const output = execFileSync(binary, ['verify'], { encoding: 'utf8' }).trim();
  const result = JSON.parse(output);
  if (result.replay !== 'MATCH') throw new Error('LSHPVS replay mismatch');
  return result;
}
