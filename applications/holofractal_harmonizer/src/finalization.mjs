import { createHash } from 'node:crypto';
import { readdirSync, readFileSync, statSync, lstatSync } from 'node:fs';
import { relative, resolve, extname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { Worker } from 'node:worker_threads';

export const TERMINAL_CLASSIFICATION = 'HHS_PASS_161_HOLOFRACTAL_HARMONIZER_UNIFIED_MULTIMODAL_OBJECT_CONTROL_ENVIRONMENT_VERIFIED';
export const PRETERMINAL_CLASSIFICATION = 'HHS_PASS_161_IMPLEMENTATION_ACTIVE_PENDING_FULL_CLOSURE';
export const PASS160_CLASSIFICATION = 'HHS_PASS_160_FIBONACCI_PRIME_PSEUDORANDOM_OVERLAP_RECEIPT_TIP_VALIDATED_TRANSITION_RUNTIME_VERIFIED';
export const PASS160_BINDING = Object.freeze({
  implementation_merge_commit: 'cd89c75afaaa9d9178ac102815dc7b0a75215bad',
  completion_receipt_sha256: 'a8b1811650d2694566c00be0bf72ff16ff8d2588d51324ae8f825fb938622c3f',
  terminal_evidence_archive_sha256: '7a91fd1a656e7d791f3f51b4a8582f508697ef7de712c59166d8a165d3290c17',
  release_bundle_sha256: 'c0ec91278176c9321288cc67a03310408d69ba23fd5e14ec5746476245ac2d2c',
  cross_architecture_root: '0b1fc8acc935539c68272ada161cbf3e66fe48908e0ffcd16076161438883545',
  main_closure_root: 'bd27cb36c7d3c70301f9edde7d5384d652f78da81206c21a7d46dd0c90eac774'
});

export class Pass161FinalizationError extends Error {
  constructor(code, message, details = {}) { super(message); this.name = 'Pass161FinalizationError'; this.code = code; this.details = details; }
}

export function canonicalize(value) {
  if (typeof value === 'bigint') return JSON.stringify(value.toString());
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(',')}]`;
  return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalize(value[key])}`).join(',')}}`;
}
export function sha256Hex(value) { return createHash('sha256').update(typeof value === 'string' || Buffer.isBuffer(value) ? value : canonicalize(value)).digest('hex'); }
function assert(condition, code, message, details = {}) { if (!condition) throw new Pass161FinalizationError(code, message, details); }
function isHex64(value) { return typeof value === 'string' && /^[0-9a-f]{64}$/.test(value); }

export class Pass160AuthorityBinding {
  constructor(closure) { this.closure = structuredClone(closure); }
  verify() {
    const c = this.closure;
    assert(c?.schema === 'P160_AUTHORITATIVE_MAIN_CLOSURE_V1', 'P160_SCHEMA_MISMATCH', 'Pass 160 main closure schema mismatch');
    assert(c.classification === PASS160_CLASSIFICATION, 'P160_CLASSIFICATION_MISMATCH', 'Pass 160 terminal classification missing');
    assert(c.omega_160 === true && c.terminal_claimed === true && c.main_closure_required === false, 'P160_NOT_CLOSED', 'Pass 160 closure is not terminal');
    for (const [key, expected] of Object.entries(PASS160_BINDING)) assert(c[key] === expected, 'P160_IDENTITY_MISMATCH', `Pass 160 ${key} mismatch`, { key, expected, actual: c[key] });
    return { verified: true, contract: c.contract, authority: c.authoritative_branch, main_closure_root: c.main_closure_root };
  }
}

const EXT_TYPES = Object.freeze({ '.c':'SOURCE','.h':'SOURCE','.mjs':'SOURCE','.js':'SOURCE','.ts':'SOURCE','.py':'SOURCE','.json':'DATA','.md':'DOCUMENT','.html':'APPLICATION','.css':'SHADER','.yml':'CONSTRAINT','.yaml':'CONSTRAINT','.wasm':'APPLICATION' });
export class RepositoryObjectDiscovery {
  constructor(root, { maxFiles = 10000, allowedRoots = ['applications','native_projects','hhs_runtime','.github'] } = {}) { this.root = resolve(root); this.maxFiles = maxFiles; this.allowedRoots = allowedRoots; }
  discover() {
    const out = [];
    const walk = (path) => {
      assert(out.length < this.maxFiles, 'DISCOVERY_BOUND_EXCEEDED', 'Repository discovery file bound exceeded');
      const stat = lstatSync(path);
      assert(!stat.isSymbolicLink(), 'SYMLINK_REJECTED', 'Repository discovery rejects symbolic links', { path });
      if (stat.isDirectory()) { for (const name of readdirSync(path).sort()) { if (['.git','node_modules','dist','evidence','.pass160-reconstructed'].includes(name)) continue; walk(resolve(path, name)); } return; }
      const rel = relative(this.root, path).replaceAll('\\','/');
      const ext = extname(path).toLowerCase();
      out.push({ object_id:`repo:${rel}`, object_type:EXT_TYPES[ext] ?? 'DATA', canonical_name:rel, display_name:rel.split('/').at(-1), lifecycle_state:'READY', authority_state:'VALIDATED_PROJECTION', validation_state:'DISCOVERED', metadata:{ bytes:stat.size, sha256:sha256Hex(readFileSync(path)), extension:ext } });
    };
    for (const base of this.allowedRoots) { const path = resolve(this.root, base); try { if (statSync(path).isDirectory()) walk(path); } catch (error) { if (error.code !== 'ENOENT') throw error; } }
    return out.sort((a,b) => a.object_id.localeCompare(b.object_id));
  }
}

export class NativePass160Bridge {
  constructor(cliPath) { this.cliPath = cliPath; }
  #run(args) {
    assert(this.cliPath, 'P160_CLI_UNAVAILABLE', 'Pass 160 native CLI path is not configured');
    const result = spawnSync(this.cliPath, args, { encoding:'utf8', timeout:30000 });
    assert(result.status === 0, 'P160_NATIVE_CALL_FAILED', 'Pass 160 native CLI call failed', { args, status:result.status, stderr:result.stderr });
    try { return JSON.parse(result.stdout); } catch { throw new Pass161FinalizationError('P160_NATIVE_JSON_INVALID', 'Pass 160 native CLI returned non-JSON output', { args, stdout:result.stdout }); }
  }
  probe() { const doctor = this.#run(['doctor']); const vectors = this.#run(['vectors']); return { native_bound:true, doctor, vectors, vector_root:sha256Hex(vectors) }; }
  verifyTransition() { const result = this.#run(['transition','verify']); assert(result && typeof result === 'object', 'P160_TRANSITION_VERIFY_FAILED', 'Pass 160 transition verification did not return an object'); return result; }
}

export class HashIdentityIndex {
  #entries = new Map();
  register({ object_id, hash216, sha256, hash72_receipt_tip }) {
    assert(typeof object_id === 'string' && object_id.length > 0, 'IDENTITY_SCHEMA', 'object_id required');
    assert(typeof hash216 === 'string' && hash216.length >= 64, 'HASH216_INVALID', 'Hash216 identity must be a canonical non-empty identity');
    assert(isHex64(sha256), 'SHA256_INVALID', 'SHA-256 identity must be lowercase hex');
    assert(typeof hash72_receipt_tip === 'string' && hash72_receipt_tip.length >= 64, 'HASH72_INVALID', 'Hash72 receipt tip is invalid');
    assert(!this.#entries.has(object_id), 'IDENTITY_DUPLICATE', 'Identity already registered');
    const entry = Object.freeze({ object_id, hash216, sha256, hash72_receipt_tip }); this.#entries.set(object_id, entry); return structuredClone(entry);
  }
  lookup(id) { const value = this.#entries.get(id); assert(value, 'IDENTITY_NOT_FOUND', 'Identity not found'); return structuredClone(value); }
  root() { return sha256Hex([...this.#entries.values()].sort((a,b)=>a.object_id.localeCompare(b.object_id))); }
}

export class ExactRational {
  constructor(numerator, denominator = 1n) {
    numerator = BigInt(numerator); denominator = BigInt(denominator);
    assert(denominator !== 0n, 'DIVISION_BY_ZERO', 'Exact rational denominator cannot be zero');
    if (denominator < 0n) { numerator = -numerator; denominator = -denominator; }
    const gcd = (a,b) => { a = a < 0n ? -a : a; while (b) [a,b] = [b,a%b]; return a || 1n; };
    const g = gcd(numerator, denominator); this.n = numerator/g; this.d = denominator/g; Object.freeze(this);
  }
  add(other) { other = other instanceof ExactRational ? other : new ExactRational(other); return new ExactRational(this.n*other.d + other.n*this.d, this.d*other.d); }
  multiply(other) { other = other instanceof ExactRational ? other : new ExactRational(other); return new ExactRational(this.n*other.n, this.d*other.d); }
  toJSON() { return { numerator:this.n.toString(), denominator:this.d.toString() }; }
  toString() { return `${this.n}/${this.d}`; }
}

export class AnalyticalWorkbench {
  evaluateExact({ a, b, operation }) {
    const left = new ExactRational(a.n, a.d); const right = new ExactRational(b.n, b.d);
    const result = operation === 'add' ? left.add(right) : operation === 'multiply' ? left.multiply(right) : null;
    assert(result, 'ANALYTICAL_OPERATION_REJECTED', 'Unsupported exact analytical operation');
    return { operation, left:left.toJSON(), right:right.toJSON(), result:result.toJSON(), authoritative_float:false };
  }
  synchronizeHarmonicode(source) { assert(typeof source === 'string' && source.length > 0, 'SOURCE_EMPTY', 'HARMONICODE source is empty'); assert(!/\b(?:NaN|Infinity)\b/.test(source), 'NONCANONICAL_SOURCE', 'Noncanonical numeric source rejected'); return { source_sha256:sha256Hex(source), bytes:Buffer.byteLength(source), preserved:true, semantic_authority:'HARMONICODE' }; }
}

export class ContainedPluginHost {
  constructor({ timeoutMs = 1500 } = {}) { this.timeoutMs = timeoutMs; }
  run({ plugin_id, requested_capabilities = [], granted_capabilities = [], operation, payload }) {
    assert(typeof plugin_id === 'string' && plugin_id, 'PLUGIN_ID_REQUIRED', 'plugin_id required');
    const missing = requested_capabilities.filter((c) => !granted_capabilities.includes(c));
    assert(missing.length === 0, 'PLUGIN_CAPABILITY_REJECTED', 'Plugin requested capabilities outside its grant', { missing });
    const workerSource = `const { parentPort, workerData } = require('node:worker_threads'); const allowed=new Set(workerData.grants); const op=workerData.operation; let result; if(op==='echo'){result=workerData.payload;} else if(op==='sum'){ if(!allowed.has('analysis.exact')) throw new Error('CAPABILITY_DENIED'); result=workerData.payload.reduce((a,b)=>a+BigInt(b),0n).toString(); } else { throw new Error('OPERATION_REJECTED'); } parentPort.postMessage({ok:true,result});`;
    return new Promise((resolvePromise, rejectPromise) => {
      const worker = new Worker(workerSource, { eval:true, workerData:{ grants:granted_capabilities, operation, payload } });
      const timer = setTimeout(() => { worker.terminate(); rejectPromise(new Pass161FinalizationError('PLUGIN_TIMEOUT', 'Contained plugin exceeded execution timeout')); }, this.timeoutMs);
      worker.once('message', (message) => { clearTimeout(timer); worker.terminate(); resolvePromise({ plugin_id, contained:true, process_access:false, filesystem_access:false, network_access:false, ...message }); });
      worker.once('error', (error) => { clearTimeout(timer); worker.terminate(); rejectPromise(new Pass161FinalizationError('PLUGIN_EXECUTION_REJECTED', error.message)); });
    });
  }
}

export function auditBrowserSurface(html, css) {
  const checks = {
    language:/<html[^>]+lang="[^"]+"/i.test(html), viewport:/name="viewport"/i.test(html), main:/<main\b/i.test(html), nav:/<nav\b/i.test(html), aside:/<aside\b/i.test(html), aria_labels:(html.match(/aria-label=/g)||[]).length >= 5,
    search_input:/type="search"/i.test(html), live_region:/aria-live=/i.test(html), mobile_media:/@media\s*\(max-width:\s*980px\)/i.test(css), reduced_motion:/prefers-reduced-motion/i.test(css), touch_target:/--touch:\s*44px/i.test(css), color_scheme:/color-scheme:\s*dark/i.test(css)
  };
  return { checks, passed:Object.values(checks).filter(Boolean).length, total:Object.keys(checks).length, failures:Object.entries(checks).filter(([,v])=>!v).map(([k])=>k) };
}

export class FinalizationRuntime {
  constructor({ closure, repoRoot, nativeCli }) { this.binding = new Pass160AuthorityBinding(closure); this.discovery = new RepositoryObjectDiscovery(repoRoot); this.native = new NativePass160Bridge(nativeCli); this.identities = new HashIdentityIndex(); this.workbench = new AnalyticalWorkbench(); this.plugins = new ContainedPluginHost(); }
  async execute({ html, css }) {
    const pass160 = this.binding.verify();
    const objects = this.discovery.discover(); assert(objects.length > 0, 'DISCOVERY_EMPTY', 'Live repository discovery returned no objects');
    const native = this.native.probe();
    const browser = auditBrowserSurface(html, css); assert(browser.failures.length === 0, 'BROWSER_AUDIT_FAILED', 'Browser/mobile/accessibility audit failed', browser);
    const exact = this.workbench.evaluateExact({ a:{n:1,d:3}, b:{n:2,d:5}, operation:'add' });
    const source = this.workbench.synchronizeHarmonicode('P^2 = AB; Hash72 -> VM81 -> Hash216');
    const plugin = await this.plugins.run({ plugin_id:'p161:plugin:exact-sum', requested_capabilities:['analysis.exact'], granted_capabilities:['analysis.exact'], operation:'sum', payload:['2','3','5','7'] });
    const replay = { pass160, repository_root:sha256Hex(objects.map((o)=>[o.object_id,o.metadata.sha256])), native_vector_root:native.vector_root, browser, exact, source, plugin };
    return { classification:PRETERMINAL_CLASSIFICATION, terminal_claimed:false, pass160, object_count:objects.length, native, browser, exact, source, plugin, replay_root:sha256Hex(replay) };
  }
}
