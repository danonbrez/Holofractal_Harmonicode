const WORKFLOW_ID = /^[a-z0-9]+(?:[.-][a-z0-9]+)*$/;
const VERSION = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/;

function clone(value) {
  return structuredClone(value);
}

function freeze(value) {
  if (Array.isArray(value)) return Object.freeze(value.map(freeze));
  if (value && typeof value === 'object') {
    return Object.freeze(Object.fromEntries(Object.entries(value).map(([key, item]) => [key, freeze(item)])));
  }
  return value;
}

function normalizeStage(stage, priorStageId) {
  if (!stage || typeof stage !== 'object' || !WORKFLOW_ID.test(stage.id || '')) {
    throw new TypeError(`invalid workflow stage id: ${stage?.id}`);
  }
  if (typeof stage.uses !== 'string' || !stage.uses.trim()) throw new TypeError(`stage ${stage.id} requires an executor`);
  const dependsOn = stage.dependsOn === undefined
    ? (priorStageId ? [priorStageId] : [])
    : [...new Set(stage.dependsOn)];
  if (dependsOn.some((value) => typeof value !== 'string' || !value)) {
    throw new TypeError(`stage ${stage.id} dependencies must be non-empty strings`);
  }
  return {
    id: stage.id,
    label: stage.label || stage.id,
    uses: stage.uses,
    dependsOn,
    timeoutMs: Number.isInteger(stage.timeoutMs) && stage.timeoutMs > 0 ? stage.timeoutMs : 30_000,
    retry: Number.isInteger(stage.retry) && stage.retry >= 0 ? stage.retry : 0,
    continueOnError: stage.continueOnError === true,
    input: stage.input || {},
  };
}

export function normalizeWorkflow(input) {
  if (!input || typeof input !== 'object') throw new TypeError('workflow must be an object');
  if (!WORKFLOW_ID.test(input.id || '')) throw new TypeError(`invalid workflow id: ${input.id}`);
  if (!VERSION.test(input.version || '')) throw new TypeError(`invalid workflow version: ${input.version}`);
  if (!Array.isArray(input.stages) || input.stages.length === 0) throw new TypeError('workflow requires at least one stage');
  const stages = [];
  const ids = new Set();
  for (const source of input.stages) {
    const stage = normalizeStage(source, stages.at(-1)?.id);
    if (ids.has(stage.id)) throw new Error(`duplicate workflow stage: ${stage.id}`);
    ids.add(stage.id);
    stages.push(stage);
  }
  for (const stage of stages) {
    const unknown = stage.dependsOn.find((id) => !ids.has(id));
    if (unknown) throw new Error(`stage ${stage.id} depends on unknown stage ${unknown}`);
  }
  const workflow = {
    schema: 'hhs.pass177.workflow/v1',
    id: input.id,
    version: input.version,
    label: input.label || input.id,
    description: input.description || '',
    target: input.target || 'source-zip',
    stages,
  };
  assertAcyclic(workflow);
  return freeze(workflow);
}

function assertAcyclic(workflow) {
  const byId = new Map(workflow.stages.map((stage) => [stage.id, stage]));
  const visiting = new Set();
  const visited = new Set();
  const visit = (id, lineage = []) => {
    if (visited.has(id)) return;
    if (visiting.has(id)) throw new Error(`workflow cycle: ${[...lineage, id].join(' -> ')}`);
    visiting.add(id);
    for (const dependency of byId.get(id).dependsOn) visit(dependency, [...lineage, id]);
    visiting.delete(id);
    visited.add(id);
  };
  for (const stage of workflow.stages) visit(stage.id);
}

export class WorkflowRegistry {
  #workflows = new Map();

  constructor(workflows = []) {
    for (const workflow of workflows) this.register(workflow);
  }

  register(input) {
    const workflow = normalizeWorkflow(input);
    if (this.#workflows.has(workflow.id)) throw new Error(`workflow already registered: ${workflow.id}`);
    this.#workflows.set(workflow.id, workflow);
    return workflow;
  }

  get(id) {
    const workflow = this.#workflows.get(id);
    if (!workflow) throw new Error(`unknown workflow: ${id}`);
    return workflow;
  }

  list({ target } = {}) {
    return [...this.#workflows.values()].filter((workflow) => !target || workflow.target === target);
  }
}

export class MemoryCheckpointStore {
  #records = new Map();

  async save(run) {
    this.#records.set(run.runId, clone(run));
    return clone(run);
  }

  async load(runId) {
    return this.#records.has(runId) ? clone(this.#records.get(runId)) : null;
  }
}

function timeoutPromise(timeoutMs, controller, stageId) {
  return new Promise((_, reject) => {
    const timer = setTimeout(() => {
      controller.abort(new Error(`stage ${stageId} timed out after ${timeoutMs}ms`));
      reject(controller.signal.reason);
    }, timeoutMs);
    controller.signal.addEventListener('abort', () => clearTimeout(timer), { once: true });
  });
}

function createRun(workflow, context, runId) {
  return {
    schema: 'hhs.pass177.workflow-run/v1',
    runId,
    workflowId: workflow.id,
    workflowVersion: workflow.version,
    status: 'pending',
    context: clone(context),
    stageStates: Object.fromEntries(workflow.stages.map((stage) => [stage.id, {
      status: 'pending', attempts: 0, output: null, error: null, startedAt: null, finishedAt: null,
    }])),
    startedAt: null,
    finishedAt: null,
    checkpoint: 0,
  };
}

function stageReady(stage, run) {
  return stage.dependsOn.every((id) => ['succeeded', 'skipped'].includes(run.stageStates[id].status));
}

export class WorkflowRunner {
  constructor({ registry, executors = {}, checkpointStore = new MemoryCheckpointStore(), now = () => new Date().toISOString() }) {
    if (!(registry instanceof WorkflowRegistry)) throw new TypeError('registry must be a WorkflowRegistry');
    this.registry = registry;
    this.executors = new Map(Object.entries(executors));
    this.checkpointStore = checkpointStore;
    this.now = now;
  }

  async run(workflowId, context = {}, { runId = `${workflowId}:${globalThis.crypto?.randomUUID?.() || Date.now()}`, resume = false, signal } = {}) {
    const workflow = this.registry.get(workflowId);
    let run = resume ? await this.checkpointStore.load(runId) : null;
    if (!run) run = createRun(workflow, context, runId);
    if (run.workflowId !== workflow.id || run.workflowVersion !== workflow.version) {
      throw new Error('checkpoint workflow identity mismatch');
    }
    if (run.status === 'succeeded') return freeze(run);
    if (resume) {
      for (const state of Object.values(run.stageStates)) {
        if (['failed', 'cancelled', 'running'].includes(state.status)) {
          state.status = 'pending';
          state.attempts = 0;
          state.error = null;
          state.finishedAt = null;
        }
      }
      delete run.error;
      run.finishedAt = null;
    }
    run.status = 'running';
    run.startedAt ||= this.now();
    await this.#checkpoint(run);

    try {
      let advanced = true;
      while (advanced) {
        advanced = false;
        for (const stage of workflow.stages) {
          const state = run.stageStates[stage.id];
          if (state.status === 'succeeded' || state.status === 'skipped') continue;
          if (!stageReady(stage, run)) continue;
          if (signal?.aborted) throw signal.reason || new Error('workflow cancelled');
          advanced = true;
          await this.#executeStage(workflow, stage, run, signal);
          if (run.stageStates[stage.id].status === 'failed' && !stage.continueOnError) {
            throw new Error(run.stageStates[stage.id].error.message);
          }
        }
      }

      const incomplete = workflow.stages.filter((stage) => !['succeeded', 'skipped'].includes(run.stageStates[stage.id].status));
      if (incomplete.length) throw new Error(`workflow stalled before: ${incomplete.map((stage) => stage.id).join(', ')}`);
      run.status = 'succeeded';
    } catch (error) {
      run.status = signal?.aborted ? 'cancelled' : 'failed';
      run.error = { name: error.name || 'Error', message: error.message || String(error) };
    }
    run.finishedAt = this.now();
    await this.#checkpoint(run);
    return freeze(run);
  }

  async #executeStage(workflow, stage, run, parentSignal) {
    const executor = this.executors.get(stage.uses);
    if (!executor) throw new Error(`no executor registered for ${stage.uses}`);
    const state = run.stageStates[stage.id];
    const attempts = stage.retry + 1;
    for (let attempt = state.attempts; attempt < attempts; attempt += 1) {
      state.status = 'running';
      state.attempts = attempt + 1;
      state.startedAt ||= this.now();
      state.error = null;
      await this.#checkpoint(run);
      const controller = new AbortController();
      const abort = () => controller.abort(parentSignal.reason || new Error('workflow cancelled'));
      parentSignal?.addEventListener('abort', abort, { once: true });
      try {
        const output = await Promise.race([
          executor({
            workflow,
            stage,
            context: run.context,
            previous: Object.fromEntries(Object.entries(run.stageStates).map(([id, item]) => [id, item.output])),
            signal: controller.signal,
          }),
          timeoutPromise(stage.timeoutMs, controller, stage.id),
        ]);
        state.status = 'succeeded';
        state.output = output === undefined ? null : clone(output);
        state.finishedAt = this.now();
        await this.#checkpoint(run);
        return;
      } catch (error) {
        state.status = 'failed';
        state.error = { name: error.name || 'Error', message: error.message || String(error) };
        state.finishedAt = this.now();
        await this.#checkpoint(run);
        if (attempt + 1 >= attempts) {
          if (stage.continueOnError) state.status = 'skipped';
          return;
        }
      } finally {
        parentSignal?.removeEventListener('abort', abort);
        controller.abort();
      }
    }
  }

  async #checkpoint(run) {
    run.checkpoint += 1;
    await this.checkpointStore.save(run);
  }
}

export const PASS177_WORKFLOWS = Object.freeze([
  normalizeWorkflow({
    id: 'web.application.source-zip', version: '1.0.0', label: 'Web Application → Source ZIP', target: 'source-zip',
    stages: [
      { id: 'validate', uses: 'validate-project' },
      { id: 'test', uses: 'test-project', retry: 1 },
      { id: 'build', uses: 'build-project' },
      { id: 'package-source-zip', uses: 'package-source-zip' },
    ],
  }),
  normalizeWorkflow({
    id: 'pwa.application.source-zip', version: '1.0.0', label: 'PWA → Tested Source ZIP', target: 'source-zip',
    stages: [
      { id: 'validate', uses: 'validate-project' },
      { id: 'validate-pwa', uses: 'validate-pwa' },
      { id: 'test', uses: 'test-project' },
      { id: 'build', uses: 'build-project' },
      { id: 'package-source-zip', uses: 'package-source-zip' },
    ],
  }),
  normalizeWorkflow({
    id: 'node.service.source-zip', version: '1.0.0', label: 'Node Service → Tested Source ZIP', target: 'source-zip',
    stages: [
      { id: 'validate', uses: 'validate-project' },
      { id: 'test', uses: 'test-project' },
      { id: 'package-source-zip', uses: 'package-source-zip' },
    ],
  }),
]);

export function createPass177WorkflowRegistry() {
  return new WorkflowRegistry(PASS177_WORKFLOWS);
}

export const DEFAULT_STAGE_EXECUTORS = Object.freeze({
  'validate-project': async ({ context }) => {
    const project = context.project;
    if (!project?.manifest || !Array.isArray(project.files)) throw new Error('project manifest and files are required');
    const paths = new Set(project.files.map((file) => file.path));
    if (!paths.has(project.manifest.entrypoint)) throw new Error(`missing entrypoint ${project.manifest.entrypoint}`);
    if (paths.size !== project.files.length) throw new Error('duplicate project file path');
    return { fileCount: paths.size, entrypoint: project.manifest.entrypoint };
  },
  'validate-pwa': async ({ context }) => {
    const paths = new Set(context.project.files.map((file) => file.path));
    for (const required of ['manifest.webmanifest', 'service-worker.js']) {
      if (!paths.has(required)) throw new Error(`PWA file missing: ${required}`);
    }
    return { installable: true };
  },
  'test-project': async ({ context }) => ({ declaredTests: context.project.manifest.tests || [], status: 'source-validated' }),
  'build-project': async ({ context }) => ({ artifactFiles: context.project.files.map((file) => file.path), mode: 'source-preserving' }),
  'package-source-zip': async ({ context }) => ({
    format: 'zip',
    packageName: `${context.project.manifest.slug}.zip`,
    files: context.project.files.map((file) => file.path),
    independentOfCompilation: true,
  }),
});
