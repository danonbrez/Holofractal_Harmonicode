import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, chmodSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve } from 'node:path';
import {
  PASS160_BINDING, PASS160_CLASSIFICATION, Pass160AuthorityBinding, RepositoryObjectDiscovery,
  NativePass160Bridge, HashIdentityIndex, ExactRational, AnalyticalWorkbench, ContainedPluginHost,
  auditBrowserSurface, sha256Hex, Pass161FinalizationError
} from '../src/finalization.mjs';

const closure = { schema:'P160_AUTHORITATIVE_MAIN_CLOSURE_V1', contract:'HHS-P160-FPPORT-VTR', authoritative_branch:'main', classification:PASS160_CLASSIFICATION, omega_160:true, terminal_claimed:true, main_closure_required:false, ...PASS160_BINDING };
function rejectCode(fn, code) { return assert.rejects(fn, (e) => e instanceof Pass161FinalizationError && e.code === code); }

test('Pass 161 finalization positive matrix', async (t) => {
  await t.test('1 Pass 160 terminal closure binds exactly', () => assert.equal(new Pass160AuthorityBinding(closure).verify().verified, true));
  await t.test('2 canonical closure root is fixed', () => assert.equal(new Pass160AuthorityBinding(closure).verify().main_closure_root, PASS160_BINDING.main_closure_root));
  await t.test('3 SHA-256 canonicalization deterministic', () => assert.equal(sha256Hex({b:2,a:1}), sha256Hex({a:1,b:2})));
  await t.test('4 repository discovery registers live files', () => { const r=mkdtempSync(resolve(tmpdir(),'p161-')); mkdirSync(resolve(r,'applications')); writeFileSync(resolve(r,'applications/a.mjs'),'export default 1'); const x=new RepositoryObjectDiscovery(r).discover(); assert.equal(x[0].object_type,'SOURCE'); rmSync(r,{recursive:true,force:true}); });
  await t.test('5 discovery hashes exact bytes', () => { const r=mkdtempSync(resolve(tmpdir(),'p161-')); mkdirSync(resolve(r,'applications')); writeFileSync(resolve(r,'applications/a.json'),'{}'); const x=new RepositoryObjectDiscovery(r).discover(); assert.equal(x[0].metadata.sha256,sha256Hex('{}')); rmSync(r,{recursive:true,force:true}); });
  await t.test('6 native bridge parses doctor and vectors', () => { const r=mkdtempSync(resolve(tmpdir(),'p161-')); const p=resolve(r,'cli'); writeFileSync(p,'#!/bin/sh\nif [ "$1" = doctor ]; then echo "{\\"ok\\":true}"; else echo "{\\"vector\\":72}"; fi\n'); chmodSync(p,0o755); const v=new NativePass160Bridge(p).probe(); assert.equal(v.native_bound,true); rmSync(r,{recursive:true,force:true}); });
  await t.test('7 Hash identity registration', () => { const i=new HashIdentityIndex(); assert.equal(i.register({object_id:'o',hash216:'h'.repeat(216),sha256:'a'.repeat(64),hash72_receipt_tip:'r'.repeat(72)}).object_id,'o'); });
  await t.test('8 Hash identity root deterministic', () => { const a=new HashIdentityIndex(); const b=new HashIdentityIndex(); const e={object_id:'o',hash216:'h'.repeat(216),sha256:'a'.repeat(64),hash72_receipt_tip:'r'.repeat(72)}; a.register(e); b.register(e); assert.equal(a.root(),b.root()); });
  await t.test('9 exact rational reduction', () => assert.equal(new ExactRational(6,8).toString(),'3/4'));
  await t.test('10 exact rational addition', () => assert.equal(new ExactRational(1,3).add(new ExactRational(2,5)).toString(),'11/15'));
  await t.test('11 exact rational multiplication', () => assert.equal(new ExactRational(2,3).multiply(new ExactRational(9,10)).toString(),'3/5'));
  await t.test('12 workbench rejects float authority', () => assert.equal(new AnalyticalWorkbench().evaluateExact({a:{n:1,d:2},b:{n:1,d:3},operation:'add'}).authoritative_float,false));
  await t.test('13 HARMONICODE source preserved', () => assert.equal(new AnalyticalWorkbench().synchronizeHarmonicode('P^2=AB').preserved,true));
  await t.test('14 contained plugin exact sum', async () => assert.equal((await new ContainedPluginHost().run({plugin_id:'p',requested_capabilities:['analysis.exact'],granted_capabilities:['analysis.exact'],operation:'sum',payload:['1','2','3']})).result,'6'));
  await t.test('15 contained plugin has no process access', async () => assert.equal((await new ContainedPluginHost().run({plugin_id:'p',operation:'echo',payload:1})).process_access,false));
  const html='<html lang="en"><meta name="viewport"><nav aria-label="n"></nav><main aria-label="m"><input type="search" aria-label="s"><div aria-live="polite"></div></main><aside aria-label="a"></aside><button aria-label="b">b</button>';
  const css=':root{color-scheme:dark;--touch:44px}@media (max-width:980px){} @media (prefers-reduced-motion: reduce){}';
  await t.test('16 static browser audit', () => assert.equal(auditBrowserSurface(html,css).failures.length,0));
  await t.test('17 mobile media contract', () => assert.equal(auditBrowserSurface(html,css).checks.mobile_media,true));
  await t.test('18 reduced motion contract', () => assert.equal(auditBrowserSurface(html,css).checks.reduced_motion,true));
  await t.test('19 touch target contract', () => assert.equal(auditBrowserSurface(html,css).checks.touch_target,true));
  await t.test('20 terminal classification is reserved outside finalizer', async () => { const m=await import('../src/finalization.mjs'); assert.ok(m.TERMINAL_CLASSIFICATION.endsWith('_VERIFIED')); });
});

test('Pass 161 finalization negative matrix', async (t) => {
  await t.test('1 stale Pass 160 classification rejected', () => assert.throws(()=>new Pass160AuthorityBinding({...closure,classification:'PENDING'}).verify(),/terminal classification/));
  await t.test('2 false omega rejected', () => assert.throws(()=>new Pass160AuthorityBinding({...closure,omega_160:false}).verify(),/not terminal/));
  await t.test('3 closure root mismatch rejected', () => assert.throws(()=>new Pass160AuthorityBinding({...closure,main_closure_root:'0'.repeat(64)}).verify(),/mismatch/));
  await t.test('4 discovery bound enforced', () => { const r=mkdtempSync(resolve(tmpdir(),'p161-')); mkdirSync(resolve(r,'applications')); writeFileSync(resolve(r,'applications/a'),'a'); writeFileSync(resolve(r,'applications/b'),'b'); assert.throws(()=>new RepositoryObjectDiscovery(r,{maxFiles:1}).discover(),/bound/); rmSync(r,{recursive:true,force:true}); });
  await t.test('5 missing native CLI rejected', () => assert.throws(()=>new NativePass160Bridge('').probe(),/not configured/));
  await t.test('6 native nonzero exit rejected', () => { const r=mkdtempSync(resolve(tmpdir(),'p161-')); const p=resolve(r,'cli'); writeFileSync(p,'#!/bin/sh\nexit 2\n'); chmodSync(p,0o755); assert.throws(()=>new NativePass160Bridge(p).probe(),/failed/); rmSync(r,{recursive:true,force:true}); });
  await t.test('7 malformed native JSON rejected', () => { const r=mkdtempSync(resolve(tmpdir(),'p161-')); const p=resolve(r,'cli'); writeFileSync(p,'#!/bin/sh\necho bad\n'); chmodSync(p,0o755); assert.throws(()=>new NativePass160Bridge(p).probe(),/non-JSON/); rmSync(r,{recursive:true,force:true}); });
  await t.test('8 malformed SHA-256 rejected', () => assert.throws(()=>new HashIdentityIndex().register({object_id:'o',hash216:'h'.repeat(216),sha256:'bad',hash72_receipt_tip:'r'.repeat(72)}),/SHA-256/));
  await t.test('9 malformed Hash216 rejected', () => assert.throws(()=>new HashIdentityIndex().register({object_id:'o',hash216:'x',sha256:'a'.repeat(64),hash72_receipt_tip:'r'.repeat(72)}),/Hash216/));
  await t.test('10 duplicate identity rejected', () => { const i=new HashIdentityIndex(); const e={object_id:'o',hash216:'h'.repeat(216),sha256:'a'.repeat(64),hash72_receipt_tip:'r'.repeat(72)}; i.register(e); assert.throws(()=>i.register(e),/already/); });
  await t.test('11 missing identity rejected', () => assert.throws(()=>new HashIdentityIndex().lookup('x'),/not found/));
  await t.test('12 exact division by zero rejected', () => assert.throws(()=>new ExactRational(1,0),/zero/));
  await t.test('13 unsupported analytical operation rejected', () => assert.throws(()=>new AnalyticalWorkbench().evaluateExact({a:{n:1,d:1},b:{n:1,d:1},operation:'sqrt'}),/Unsupported/));
  await t.test('14 empty source rejected', () => assert.throws(()=>new AnalyticalWorkbench().synchronizeHarmonicode(''),/empty/));
  await t.test('15 noncanonical source rejected', () => assert.throws(()=>new AnalyticalWorkbench().synchronizeHarmonicode('NaN'),/Noncanonical/));
  await t.test('16 plugin capability escalation rejected', () => assert.throws(()=>new ContainedPluginHost().run({plugin_id:'p',requested_capabilities:['filesystem.write'],granted_capabilities:[],operation:'echo',payload:1}), (e)=>e instanceof Pass161FinalizationError && e.code==='PLUGIN_CAPABILITY_REJECTED'));
  await t.test('17 plugin unknown operation rejected', () => rejectCode(()=>new ContainedPluginHost().run({plugin_id:'p',operation:'root',payload:1}),'PLUGIN_EXECUTION_REJECTED'));
  await t.test('18 browser without language rejected by audit', () => assert.ok(auditBrowserSurface('<html><main></main>','').failures.includes('language')));
  await t.test('19 browser without mobile profile rejected by audit', () => assert.ok(auditBrowserSurface('<html lang="en"><main></main>','').failures.includes('mobile_media')));
  await t.test('20 browser without reduced motion rejected by audit', () => assert.ok(auditBrowserSurface('<html lang="en"><main></main>','').failures.includes('reduced_motion')));
});
