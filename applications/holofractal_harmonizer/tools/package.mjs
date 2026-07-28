#!/usr/bin/env node
import { readFileSync, writeFileSync, mkdirSync, readdirSync, statSync } from 'node:fs';
import { resolve, relative } from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
const root=resolve(new URL('..',import.meta.url).pathname), dist=resolve(root,'dist'); mkdirSync(dist,{recursive:true});
const include=['README.md','index.html','package.json','src','schemas','tests','tools','evidence'];
const manifest=[]; const walk=(p)=>{const s=statSync(p); if(s.isDirectory()) for(const n of readdirSync(p).sort()) walk(resolve(p,n)); else manifest.push({path:relative(root,p).replaceAll('\\','/'),bytes:s.size,sha256:createHash('sha256').update(readFileSync(p)).digest('hex')});}; for(const item of include) walk(resolve(root,item));
writeFileSync(resolve(dist,'P161_FILE_MANIFEST.json'),JSON.stringify({schema:'P161_FILE_MANIFEST_V1',files:manifest},null,2)+'\n');
const archive=resolve(dist,'HHS_PASS_161_RELEASE_BUNDLE.tar.gz'); const args=['--sort=name','--mtime=UTC 1980-01-01','--owner=0','--group=0','--numeric-owner','-czf',archive,...include]; const r=spawnSync('tar',args,{cwd:root,encoding:'utf8'}); if(r.status!==0) throw new Error(r.stderr);
const payload={schema:'HHS_PASS_161_RELEASE_BUNDLE_V1',contract:'HHS-P161-HHUMOCE',archive:'dist/HHS_PASS_161_RELEASE_BUNDLE.tar.gz',archive_bytes:statSync(archive).size,archive_sha256:createHash('sha256').update(readFileSync(archive)).digest('hex'),file_count:manifest.length,deterministic:true}; writeFileSync(resolve(root,'HHS_PASS_161_RELEASE_BUNDLE.json'),JSON.stringify(payload,null,2)+'\n'); console.log(JSON.stringify(payload));
