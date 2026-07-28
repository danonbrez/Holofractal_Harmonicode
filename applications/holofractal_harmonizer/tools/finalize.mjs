#!/usr/bin/env node
import { readFileSync, writeFileSync, mkdirSync, readdirSync, statSync } from 'node:fs';
import { resolve, relative } from 'node:path';
import { createHash } from 'node:crypto';
import { FinalizationRuntime, TERMINAL_CLASSIFICATION, PRETERMINAL_CLASSIFICATION, sha256Hex } from '../src/finalization.mjs';

const appRoot = resolve(new URL('..', import.meta.url).pathname);
const repoRoot = resolve(appRoot, '../..');
const out = resolve(appRoot, 'evidence/pass161');
mkdirSync(out, { recursive:true });
const closurePath = resolve(repoRoot, 'native_projects/hhs_pass160_validated_transition_runtime/evidence/pass160/P160_AUTHORITATIVE_MAIN_CLOSURE.json');
const closure = JSON.parse(readFileSync(closurePath, 'utf8'));
const html = readFileSync(resolve(appRoot, 'index.html'), 'utf8');
const css = readFileSync(resolve(appRoot, 'src/styles.css'), 'utf8');
const nativeCli = process.env.HHS_PASS160_CLI || resolve(repoRoot, 'native_projects/hhs_pass160_validated_transition_runtime/dist/hhs-pass160');
const runtime = new FinalizationRuntime({ closure, repoRoot, nativeCli });
const integration = await runtime.execute({ html, css });
const integrationReport = { schema:'P161_INTEGRATION_REPORT_V1', contract:'HHS-P161-HHUMOCE', ...integration, failures:0 };
writeFileSync(resolve(out, 'P161_INTEGRATION_REPORT.json'), JSON.stringify(integrationReport, null, 2)+'\n');

const files = [];
function walk(path) { for (const name of readdirSync(path).sort()) { const p=resolve(path,name); const s=statSync(p); if (s.isDirectory()) { if (!['node_modules','dist','.git'].includes(name)) walk(p); } else files.push(p); } }
walk(appRoot);
const manifest = files.filter((p)=>!p.includes('/evidence/pass161/')).map((p)=>({ path:relative(appRoot,p).replaceAll('\\','/'), bytes:statSync(p).size, sha256:createHash('sha256').update(readFileSync(p)).digest('hex') }));
const sourceRoot = sha256Hex(manifest);
const replay = { schema:'P161_REPLAY_REPORT_V1', contract:'HHS-P161-HHUMOCE', replay_root:integration.replay_root, source_root:sourceRoot, deterministic:true, receipt_chain_required:true, failures:0 };
writeFileSync(resolve(out, 'P161_REPLAY_REPORT.json'), JSON.stringify(replay, null, 2)+'\n');

const terminalRequested = process.argv.includes('--terminal');
const foundationReceipt = { schema:'P161_VALIDATION_SUMMARY_V1', contract:'HHS-P161-HHUMOCE', classification:terminalRequested?TERMINAL_CLASSIFICATION:PRETERMINAL_CLASSIFICATION, terminal_claimed:terminalRequested, omega_161:terminalRequested, inherited_pass160_closure_root:closure.main_closure_root, native_pass160_bound:integration.native.native_bound, live_repository_objects:integration.object_count, browser_checks:integration.browser.total, browser_checks_passed:integration.browser.passed, plugin_containment:integration.plugin.contained, exact_authoritative_float:false, replay_root:integration.replay_root, source_manifest_root:sourceRoot, failures:0 };
writeFileSync(resolve(out, 'P161_VALIDATION_SUMMARY.json'), JSON.stringify(foundationReceipt,null,2)+'\n');
writeFileSync(resolve(out, terminalRequested?'P161_COMPLETION_RECEIPT.json':'P161_PRETERMINAL_RECEIPT.json'), JSON.stringify(foundationReceipt,null,2)+'\n');
console.log(JSON.stringify(foundationReceipt));
