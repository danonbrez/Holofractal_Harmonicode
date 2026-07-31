import { $, $$, state, activeFile, sourcePayload, requestJson, ensureProject, inferExactExpression, setText, log, setStage, resetStages } from './visual-ide-state.mjs';
import { renderSnapshot, renderHash216, openBottomTab } from './visual-ide-ui.mjs';

export async function ingest({ signal } = {}) {
  setStage('ingress', 'running'); setText('#ide-terminal-state', 'INGRESS');
  try {
    state.ingress = await requestJson('/api/runtime/multimodal-ingress/ingest', { method: 'POST', signal, body: JSON.stringify(sourcePayload()) });
    setStage('ingress', 'complete'); setStage('index', 'complete');
    setText('#receipt-tip', state.ingress.receipt?.receipt_hash72?.slice(0, 16) || 'INGRESS');
    setText('#ide-receipt-output', JSON.stringify(state.ingress.receipt, null, 2));
    log('Pass 165 source-preserving ingress committed.', state.ingress);
    return await loadSnapshot(state.ingress.source?.source_hash, { signal });
  } catch (error) { setStage('ingress', 'failed'); log(`Ingress rejected: ${error.message}`); throw error; }
}
export async function loadSnapshot(sourceHash = state.ingress?.source?.source_hash, { signal } = {}) {
  if (!sourceHash) throw new Error('No ingested source');
  setStage('snapshot', 'running');
  state.snapshot = await requestJson(`/api/runtime/multimodal-ingress/snapshots/${encodeURIComponent(sourceHash)}`, { signal });
  setStage('snapshot', 'complete'); renderSnapshot(state.snapshot); renderHash216(state.snapshot);
  log('Loaded exact 648-byte / 5184-bit snapshot and 216 Hash216 position indexes.');
  return state.snapshot;
}
async function workspace(operation, payload = {}, { signal } = {}) {
  return requestJson('/api/runtime/workspace/command', { method: 'POST', signal, body: JSON.stringify({ operation, payload: { project_id: await ensureProject({ signal }), ...payload } }) });
}
export async function interpret({ signal } = {}) {
  setStage('interpret', 'running');
  const result = await workspace('interpret.execute', { source_object_id: `object:${activeFile().path}`, expression: inferExactExpression() }, { signal });
  setStage('interpret', result.ok ? 'complete' : 'failed'); setText('#ide-receipt-output', JSON.stringify(result, null, 2)); log('Interpreter returned.', result); return result;
}
export async function compile({ signal } = {}) {
  setStage('compile', 'running');
  const result = await workspace('compile.execute', { source_object_id: `object:${activeFile().path}`, source_text: $('#ide-source-editor').value, target: 'HHS_IR' }, { signal });
  state.compilation = result; setStage('compile', result.ok ? 'complete' : 'failed'); setText('#ide-receipt-output', JSON.stringify(result, null, 2)); log('Compiler returned.', result); return result;
}
export async function run({ signal } = {}) {
  if (!state.compilation?.ok) await compile({ signal });
  setStage('execute', 'running');
  const artifactId = state.compilation?.result?.artifact?.artifact_id || 'artifact:hhs-ir';
  if (!state.snapshot) await ingest({ signal });
  const created = await workspace('emulator.create', {
    program_artifact_id: artifactId,
    initial_state: {
      snapshot_bits: state.snapshot.snapshot_bits,
      snapshot_bytes: state.snapshot.snapshot_bytes,
      projection_b64: state.snapshot.projection_b64,
      projection_hash72: state.snapshot.projection_hash72,
      ingestion_operation_hash216: state.snapshot.ingestion_operation_hash216,
      ingestion_positions_hash216: state.snapshot.ingestion_positions_hash216,
    },
  }, { signal });
  const sessionId = created.result?.session?.session_id;
  const executed = await workspace('emulator.run', { session_id: sessionId, steps: Math.min(32, Math.max(1, Number($('#ide-run-steps').value || 8))) }, { signal });
  const snapshot = await workspace('emulator.snapshot', { session_id: sessionId }, { signal });
  state.execution = { created, executed, snapshot };
  setStage('execute', executed.ok && snapshot.ok ? 'complete' : 'failed'); setText('#ide-receipt-output', JSON.stringify(state.execution, null, 2)); log('VM81 bounded execution returned.', state.execution); return state.execution;
}
export async function runLifecycle({ signal } = {}) {
  if (state.busy) return;
  state.busy = true; resetStages(); $('#ide-run-lifecycle').disabled = true; setText('#ide-terminal-state', 'LIFECYCLE RUNNING');
  ['ingress', 'index', 'snapshot', 'interpret', 'compile', 'execute'].forEach((name) => setStage(name, 'running'));
  try {
    state.lifecycle = await requestJson('/api/runtime/development/lifecycle', {
      method: 'POST', signal, timeoutMs: 180000,
      body: JSON.stringify({ ...sourcePayload(), project_id: await ensureProject({ signal }), project_name: 'HHS Visual IDE Project', expression: inferExactExpression(), interpretation_scope: 'SOURCE_EXACT_NUMERIC_PROBE', target: 'HHS_IR', steps: Math.min(32, Math.max(1, Number($('#ide-run-steps').value || 8))) }),
    });
    state.ingress = state.lifecycle.ingress; state.snapshot = state.lifecycle.vm_snapshot; state.egress = state.lifecycle.egress;
    ['ingress', 'index', 'snapshot'].forEach((name) => setStage(name, 'complete'));
    setStage('interpret', state.lifecycle.interpretation?.ok === false ? 'failed' : 'complete');
    setStage('compile', state.lifecycle.compilation?.ok === false ? 'failed' : 'complete');
    setStage('execute', state.lifecycle.execution?.ok === false ? 'failed' : 'complete'); setStage('egress', 'complete');
    renderSnapshot(state.snapshot); renderHash216(state.snapshot);
    setText('#ide-receipt-output', JSON.stringify(state.lifecycle.receipts, null, 2)); setText('#ide-egress-output', JSON.stringify(state.egress, null, 2)); setText('#ide-egress-state', state.egress?.artifact_name || 'Bundle ready');
    setText('#receipt-tip', state.lifecycle.receipts?.lifecycle_receipt_hash72?.slice(0, 16) || 'COMPLETE');
    setText('#validation-state', 'INGRESS → HASH216 → 5184BIT → INTERPRET → COMPILE → VM81 → EGRESS');
    setText('#ide-terminal-state', state.lifecycle.ok ? 'LIFECYCLE COMPLETE' : 'LIFECYCLE PARTIAL');
    log('Full multimodal software lifecycle returned from backend authority.', state.lifecycle); openBottomTab('egress');
    return state.lifecycle;
  } catch (error) {
    $$('#ide-lifecycle-stages .running').forEach((node) => node.classList.replace('running', 'failed'));
    setText('#validation-state', 'LIFECYCLE REJECTED · NO FRONTEND FABRICATION'); log(`Lifecycle failed: ${error.message}`);
    throw error;
  } finally { state.busy = false; $('#ide-run-lifecycle').disabled = false; }
}
export async function replay({ signal } = {}) {
  const result = await requestJson('/api/runtime/development/replay', { method: 'POST', signal, body: '{}' });
  setText('#ide-receipt-output', JSON.stringify(result, null, 2)); log('Deterministic replay returned.', result); return result;
}
export function exportEgress() {
  if (!state.egress && !state.lifecycle) return log('No backend lifecycle evidence is available for egress.');
  const bundle = state.egress || { schema: 'HHS_VISUAL_IDE_EGRESS_BUNDLE_V1', backend_evidence_unmodified: true, lifecycle: state.lifecycle };
  const url = URL.createObjectURL(new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/vnd.hhs.lifecycle+json' }));
  const link = Object.assign(document.createElement('a'), { href: url, download: bundle.artifact_name || `${activeFile().name}.hhs-lifecycle.json` });
  document.body.append(link); link.click(); link.remove(); URL.revokeObjectURL(url); log('Receipt-bound egress bundle exported.');
}
