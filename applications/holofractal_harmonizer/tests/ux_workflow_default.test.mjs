import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { WORKFLOW_TEMPLATES, validateWorkflowTemplates } from '../src/workflow-templates.mjs';

const root = resolve(new URL('..', import.meta.url).pathname);

test('workflow templates are complete, unique, and bounded', () => {
  const validation = validateWorkflowTemplates();
  assert.equal(validation.ok, true, JSON.stringify(validation.failures));
  assert.equal(validation.count, 8);
  assert.equal(new Set(WORKFLOW_TEMPLATES.map((item) => item.template_id)).size, 8);
  assert.equal(new Set(WORKFLOW_TEMPLATES.map((item) => item.category)).size, 8);
  for (const template of WORKFLOW_TEMPLATES) {
    assert.equal(template.stages.length, 5);
    assert.ok(template.prompt.length >= 80);
    assert.ok(template.default_panels.length >= 3);
    assert.ok(template.object_types.length >= 2);
  }
});

test('global home loads workflow-first enhancement after canonical browser runtime', () => {
  const html = readFileSync(resolve(root, 'index.html'), 'utf8');
  assert.match(html, /src\/styles\.css/);
  assert.match(html, /src\/ux-default\.css/);
  assert.ok(html.indexOf('src/browser.mjs') < html.indexOf('src/ux-default.mjs'));
  assert.match(html, /id="assistant-view"/);
  assert.match(html, /id="inspector"/);
});

test('workflow-first CSS clears the operation strip and preserves mobile progressive disclosure', () => {
  const css = readFileSync(resolve(root, 'src/ux-default.css'), 'utf8');
  assert.match(css, /--ux-footer-clearance:\s*78px/);
  assert.match(css, /padding-bottom:\s*var\(--ux-footer-clearance\)/);
  assert.match(css, /@media\s*\(max-width:\s*980px\)/);
  assert.match(css, /workflow-mobile-tabs/);
  assert.match(css, /prefers-reduced-motion/);
});

test('workflow-first module preserves advanced object controls and command access', () => {
  const source = readFileSync(resolve(root, 'src/ux-default.mjs'), 'utf8');
  assert.match(source, /Advanced Object Controls/);
  assert.match(source, /window\.HHSHarmonizer/);
  assert.match(source, /ctrlKey \|\| event\.metaKey/);
  assert.match(source, /ASSISTANT TURN ADMITTED/);
  assert.doesNotMatch(source, /direct_vm81_mutation_allowed\s*=\s*true/);
});
