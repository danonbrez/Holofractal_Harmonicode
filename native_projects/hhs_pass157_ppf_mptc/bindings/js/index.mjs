import { execFileSync } from 'node:child_process';

const binary = process.argv[2] ?? './dist/hhs-pass157';
const result = JSON.parse(execFileSync(binary, ['verify'], { encoding: 'utf8' }).trim());
if (result.contract !== 'HHS-P157-PPF-MPTC' || result.replay !== 'MATCH') {
  throw new Error('Pass 157 native verification mismatch');
}
process.stdout.write(JSON.stringify({
  schema: 'HHS_PASS_157_JS_BINDING_V1',
  contract: result.contract,
  result_hash216: result.result_hash216,
  receipt_hash72: result.receipt_hash72,
  replay: result.replay,
}));
