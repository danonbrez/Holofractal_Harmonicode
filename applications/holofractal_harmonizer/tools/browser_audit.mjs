#!/usr/bin/env node
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { auditBrowserSurface } from '../src/finalization.mjs';
const root=resolve(new URL('..',import.meta.url).pathname); const report=auditBrowserSurface(readFileSync(resolve(root,'index.html'),'utf8'),readFileSync(resolve(root,'src/styles.css'),'utf8'));
mkdirSync(resolve(root,'evidence/pass161'),{recursive:true}); writeFileSync(resolve(root,'evidence/pass161/P161_BROWSER_AUDIT.json'),JSON.stringify({schema:'P161_BROWSER_AUDIT_V1',...report,failures:report.failures.length},null,2)+'\n');
console.log(JSON.stringify(report)); if(report.failures.length) process.exit(1);
