export const WORKFLOW_TEMPLATE_SCHEMA = 'HHS_VISUAL_IDE_WORKFLOW_TEMPLATE_V1';

export const WORKFLOW_TEMPLATES = Object.freeze([
  Object.freeze({
    template_id: 'hhs:workflow:code-runtime',
    category: 'CODE_RUNTIME',
    label: 'Code & Runtime',
    glyph: 'λ',
    outcome: 'Source, dependency-scoped tests, runtime evidence',
    description: 'Implement or repair a callable runtime surface without bypassing VM81, capability, receipt, or replay authority.',
    prompt: 'Implement the requested dependency-scoped runtime change. Preserve source semantics and inherited invariants, run affected positive and negative tests, inspect receipts, and report admitted evidence without claiming unexecuted success.',
    stages: ['Scope', 'Implement', 'Test', 'Inspect', 'Close'],
    object_types: ['SOURCE', 'RUNTIME', 'CONSTRAINT', 'RECEIPT'],
    default_panels: ['Editor', 'Tests', 'Diagnostics', 'Receipts'],
  }),
  Object.freeze({
    template_id: 'hhs:workflow:api-automation',
    category: 'API_AUTOMATION',
    label: 'API & Automation',
    glyph: '↔',
    outcome: 'Governed callable API, schemas, failure handling',
    description: 'Create API and automation flows with explicit capability boundaries, tool contracts, negative tests, and execution receipts.',
    prompt: 'Create or update the governed API or automation workflow. Define request and response schemas, capability requirements, explicit failure behavior, targeted tests, and receipt-backed completion evidence.',
    stages: ['Contract', 'Route', 'Tools', 'Negative Tests', 'Receipt'],
    object_types: ['API', 'TOOL', 'AUTHORITY', 'RECEIPT'],
    default_panels: ['API Controller', 'Schema', 'Tool Trace', 'Authority'],
  }),
  Object.freeze({
    template_id: 'hhs:workflow:data-analytics',
    category: 'DATA_ANALYTICS',
    label: 'Data & Analytics',
    glyph: 'Σ',
    outcome: 'Validated dataset, metrics, charts, reproducible report',
    description: 'Inspect source quality, compute exact or explicitly bounded analytics, and preserve lineage from source to visualization.',
    prompt: 'Analyze the selected dataset. Preserve source identity, validate schema and quality, compute the requested metrics, create clear visual projections, and return reproducible lineage and validation evidence.',
    stages: ['Source', 'Quality', 'Compute', 'Visualize', 'Validate'],
    object_types: ['DATA', 'VECTOR', 'TENSOR', 'GRAPH'],
    default_panels: ['Source', 'Data Quality', 'Analysis', 'Visual Report'],
  }),
  Object.freeze({
    template_id: 'hhs:workflow:document-knowledge',
    category: 'DOCUMENT_KNOWLEDGE',
    label: 'Document & Knowledge',
    glyph: '¶',
    outcome: 'Preserved source, structured extraction, knowledge report',
    description: 'Ingest documents without source loss, separate evidence from interpretation, and expose structured claims and relations.',
    prompt: 'Ingest the selected document. Preserve immutable source identity, extract structure and claims, distinguish evidence from interpretation, validate relationships and contradictions, and produce a cited knowledge report.',
    stages: ['Ingest', 'Preserve', 'Extract', 'Relate', 'Report'],
    object_types: ['DOCUMENT', 'SOURCE', 'GRAPH', 'CONSTRAINT'],
    default_panels: ['Source', 'Structure', 'Knowledge Graph', 'Validation'],
  }),
  Object.freeze({
    template_id: 'hhs:workflow:image-ui',
    category: 'IMAGE_UI',
    label: 'Image & UI',
    glyph: '◫',
    outcome: 'Visual target, responsive implementation, capture evidence',
    description: 'Develop image and interface work through source-target comparison, responsive implementation, screenshots, and design QA.',
    prompt: 'Develop the selected image or interface workflow. Preserve the visual target, create responsive callable controls, capture stable screenshots, compare the implementation against the source, and record remaining accessibility limits.',
    stages: ['Target', 'Explore', 'Build', 'Capture', 'QA'],
    object_types: ['APPLICATION', 'IMAGE', 'SHADER', 'PANEL'],
    default_panels: ['Canvas', 'Components', 'Responsive Preview', 'Design QA'],
  }),
  Object.freeze({
    template_id: 'hhs:workflow:audio-video',
    category: 'AUDIO_VIDEO',
    label: 'Audio & Video',
    glyph: '♫',
    outcome: 'Timeline, deterministic transforms, renders, playback evidence',
    description: 'Coordinate audio/video analysis, transforms, previews, render jobs, and playback checks without hiding source lineage.',
    prompt: 'Build the selected audio or video workflow. Preserve source media identity, analyze timing and channels, apply deterministic transforms, render bounded previews and final outputs, and validate playback and artifact hashes.',
    stages: ['Import', 'Analyze', 'Transform', 'Render', 'Playback'],
    object_types: ['DATA', 'APPLICATION', 'VECTOR', 'RECEIPT'],
    default_panels: ['Media Bin', 'Timeline', 'Analysis', 'Render Evidence'],
  }),
  Object.freeze({
    template_id: 'hhs:workflow:spatial-3d',
    category: 'SPATIAL_3D',
    label: '3D & Spatial',
    glyph: '◈',
    outcome: 'Scene graph, registered objects, projection-only shaders',
    description: 'Build navigable registered-object scenes while keeping shader, sprite, camera, and simulation state projection-only.',
    prompt: 'Build the selected 3D or spatial workflow. Register every object identity, construct the scene graph, bind projection-only shaders and sprite surfaces, run bounded simulation checks, and verify 2D/3D identity parity.',
    stages: ['Scene', 'Objects', 'Materials', 'Simulate', 'Validate'],
    object_types: ['SCENE', 'THREE_D_OBJECT', 'SHADER', 'SPRITE_MAP'],
    default_panels: ['Scene Graph', 'Viewport', 'Materials', 'Spatial Validation'],
  }),
  Object.freeze({
    template_id: 'hhs:workflow:model-agent',
    category: 'MODEL_AGENT',
    label: 'Model & Agent',
    glyph: 'AI',
    outcome: 'Provider contract, bounded tools, evaluation, ingress evidence',
    description: 'Configure language, vision, or multimodal providers as governed capabilities rather than alternate runtime authorities.',
    prompt: 'Configure the selected model or agent workflow. Define the provider contract, capability policy, bounded tool set, evaluation cases, invocation receipts, and provider-result ingress without granting direct VM81 mutation authority.',
    stages: ['Provider', 'Policy', 'Tools', 'Evaluate', 'Admit'],
    object_types: ['MODEL', 'AGENT', 'TOOL', 'AUTHORITY'],
    default_panels: ['Provider', 'Policy', 'Tool Trace', 'Evaluation'],
  }),
]);

export function validateWorkflowTemplates(templates = WORKFLOW_TEMPLATES) {
  const ids = new Set();
  const categories = new Set();
  const failures = [];
  for (const template of templates) {
    if (!template || typeof template !== 'object') { failures.push('template_not_object'); continue; }
    if (template.template_id === undefined || ids.has(template.template_id)) failures.push(`duplicate_or_missing_id:${template.template_id}`);
    ids.add(template.template_id);
    if (!template.category || categories.has(template.category)) failures.push(`duplicate_or_missing_category:${template.category}`);
    categories.add(template.category);
    if (!template.label || !template.outcome || !template.description || !template.prompt) failures.push(`missing_copy:${template.template_id}`);
    if (!Array.isArray(template.stages) || template.stages.length !== 5) failures.push(`invalid_stages:${template.template_id}`);
    if (!Array.isArray(template.object_types) || template.object_types.length < 2) failures.push(`invalid_object_types:${template.template_id}`);
    if (!Array.isArray(template.default_panels) || template.default_panels.length < 3) failures.push(`invalid_panels:${template.template_id}`);
  }
  return { schema: WORKFLOW_TEMPLATE_SCHEMA, ok: failures.length === 0, count: templates.length, failures };
}

export function templateById(templateId) {
  return WORKFLOW_TEMPLATES.find((template) => template.template_id === templateId) ?? WORKFLOW_TEMPLATES[0];
}
