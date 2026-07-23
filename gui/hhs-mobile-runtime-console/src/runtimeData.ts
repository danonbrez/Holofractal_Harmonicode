export type WitnessStatus = 'ADMISSIBLE' | 'EXPIRED' | 'RECURSION_BLOCKED' | 'UNKNOWN';
export type RuntimeStatus = 'LOCKED' | 'INCOMPLETE' | 'QUARANTINED' | 'PHASE_STALLED' | 'EXECUTED';
export type AlertSeverity = 'INFO' | 'WARN' | 'CRITICAL';

export type RuntimeAlert = { code: string; severity: AlertSeverity | string; message: string; subject_hash72?: string | null; alert_hash72: string; affected_phase_indices?: number[]; affected_modalities?: string[]; };
export type RuntimeAnomalies = { status: 'CLEAR' | 'WARN' | 'CRITICAL' | string; critical: number; warn: number; info: number; alerts: RuntimeAlert[]; summary_hash72: string; drift_prediction?: any; };
export type PhaseWitnessView = { modality: string; source_id: string; phase_index: number; phase_hash72: string; temporal_status: WitnessStatus | string; witness_hash72: string; };
export type PhaseLockView = { status: RuntimeStatus | string; anchor_phase_index: number; anchor_phase_hash72: string; mandatory_present: boolean; temporal_ok: boolean; phase_locked: boolean; missing_mandatory: string[]; receipt_hash72: string; witnesses: PhaseWitnessView[]; };
export type OperatorProposalView = { agent: string; phase_ok: boolean; phase_distance_from_anchor: number | null; local_score: number; risk_score: number; operators: string[]; proposal_hash72: string; };
export type OperatorLoopView = { status: RuntimeStatus | string; external_phase_anchor_used: boolean; selected_chain_hash72: string | null; receipt_hash72: string; proposals: OperatorProposalView[]; };
export type ProjectionView = { phase_index: number; u72_ok: boolean; loshu_ok: boolean; anchor_hash72: string; status: string; target_layer: string; receipt_hash72: string; raw?: any; };
export type TemporalShellStepView = { index: number; phase_index: number; carrier: 'x' | 'y' | 'xy' | string; phase_filter: number; shell_width: number; shell_hash72: string; status: string; expansion?: any; };
export type TemporalShellView = { seed_hash72: string; cycles: number; total_steps: number; steps: TemporalShellStepView[]; carrier_balance: Record<string, number>; aggregate_hash72: string; status: string; receipt_hash72: string; };
export type EquationManifestView = { status: string; phases: number[]; equation_text: string; equation_hash72: string; projection_receipt_hash72: string; manifest_hash72: string; compiler_packet?: any; raw?: any; };
export type TranspileArtifactView = { target: string; source: string; source_hash72: string; status: string; notes: string[]; };
export type TranspileReceiptView = { input_hash72: string; artifacts: TranspileArtifactView[]; receipt_hash72: string; raw?: any; };

export type RuntimeSnapshot = {
  phase: PhaseLockView;
  operatorLoop: OperatorLoopView;
  projection?: ProjectionView;
  temporalShells?: TemporalShellView;
  equationManifest?: EquationManifestView;
  transpileReceipt?: TranspileReceiptView;
  anomalies?: RuntimeAnomalies;
  corrections?: any;
  lastRootCandidate?: any;
  lastRootCommit?: any;
  stream?: { connected: boolean; source: 'websocket' | 'rest' | 'unavailable'; last_event_type?: string; last_update_ms?: number; batch_size?: number; batch_index?: number; };
};

const clearAnomalies: RuntimeAnomalies = { status: 'CLEAR', critical: 0, warn: 0, info: 0, alerts: [], summary_hash72: '' };

export const unavailableSnapshot: RuntimeSnapshot = {
  phase: { status: 'INCOMPLETE', anchor_phase_index: 0, anchor_phase_hash72: '', mandatory_present: false, temporal_ok: false, phase_locked: false, missing_mandatory: ['RUNTIME_STATE_UNAVAILABLE'], receipt_hash72: '', witnesses: [] },
  operatorLoop: { status: 'INCOMPLETE', external_phase_anchor_used: false, selected_chain_hash72: null, receipt_hash72: '', proposals: [] },
  anomalies: { status: 'CRITICAL', critical: 1, warn: 0, info: 0, alerts: [{ code: 'RUNTIME_STATE_UNAVAILABLE', severity: 'CRITICAL', message: 'Canonical runtime state could not be retrieved.', alert_hash72: '' }], summary_hash72: '' },
  corrections: {},
  stream: { connected: false, source: 'unavailable', last_event_type: 'runtime_state_unavailable', last_update_ms: Date.now() }
};

function normalizePhaseResponse(raw: any): PhaseLockView {
  const witnesses = Array.isArray(raw?.witnesses) ? raw.witnesses.map((w: any) => ({ modality: w?.observation?.modality ?? w?.modality ?? 'UNKNOWN', source_id: w?.observation?.source_id ?? w?.source_id ?? 'unknown', phase_index: Number(w?.phase_index ?? 0), phase_hash72: String(w?.phase_hash72 ?? ''), temporal_status: String(w?.temporal_status ?? 'UNKNOWN'), witness_hash72: String(w?.witness_hash72 ?? '') })) : [];
  return { status: raw?.status ?? 'UNKNOWN', anchor_phase_index: Number(raw?.anchor_phase_index ?? 0), anchor_phase_hash72: String(raw?.anchor_phase_hash72 ?? ''), mandatory_present: Boolean(raw?.mandatory_present), temporal_ok: Boolean(raw?.temporal_ok), phase_locked: Boolean(raw?.phase_locked), missing_mandatory: Array.isArray(raw?.missing_mandatory) ? raw.missing_mandatory : [], receipt_hash72: String(raw?.receipt_hash72 ?? ''), witnesses };
}

function normalizeLoopResponse(raw: any): OperatorLoopView {
  const proposals = Array.isArray(raw?.phase_agent_proposals) ? raw.phase_agent_proposals.map((p: any) => ({ agent: p?.proposal?.agent?.kind ?? p?.proposal?.agent?.name ?? 'AGENT', phase_ok: Boolean(p?.phase_ok), phase_distance_from_anchor: p?.phase_distance_from_anchor ?? null, local_score: Number(p?.proposal?.local_score ?? 0), risk_score: Number(p?.proposal?.risk_score ?? 0), operators: Array.isArray(p?.proposal?.selected_operators) ? p.proposal.selected_operators.map((op: any) => op?.title ?? op?.operator_signature ?? 'operator') : [], proposal_hash72: String(p?.proposal?.proposal_hash72 ?? p?.receipt_hash72 ?? '') })) : [];
  return { status: raw?.status ?? 'UNKNOWN', external_phase_anchor_used: Boolean(raw?.external_phase_anchor_used), selected_chain_hash72: raw?.selected_candidate?.chain_hash72 ?? raw?.selected_chain_hash72 ?? null, receipt_hash72: String(raw?.receipt_hash72 ?? ''), proposals };
}

function normalizeAnomalies(raw: any): RuntimeAnomalies { if (!raw) return clearAnomalies; return { status: raw.status ?? 'CLEAR', critical: Number(raw.critical ?? 0), warn: Number(raw.warn ?? 0), info: Number(raw.info ?? 0), alerts: Array.isArray(raw.alerts) ? raw.alerts : [], summary_hash72: String(raw.summary_hash72 ?? ''), drift_prediction: raw.drift_prediction }; }

function normalizeProjection(raw: any): ProjectionView | undefined {
  if (!raw) return undefined;
  const receipt = raw?.projection?.receipt ?? raw?.receipt ?? {};
  const witness = raw?.projection?.phase_witness ?? raw?.phase_witness ?? receipt?.phase_witness ?? {};
  const steps = raw?.projection?.projection_steps ?? raw?.projection_steps ?? [];
  const targetLayer = steps?.[0]?.target_layer ?? 'normalized';
  return { phase_index: Number(witness?.phase_index ?? 0), u72_ok: Boolean(witness?.u72_ok ?? false), loshu_ok: Boolean(witness?.loshu_ok ?? false), anchor_hash72: String(witness?.anchor_hash72 ?? ''), status: String(receipt?.status ?? raw?.status ?? 'PROJECTED'), target_layer: String(targetLayer), receipt_hash72: String(receipt?.receipt_hash72 ?? raw?.receipt_hash72 ?? ''), raw };
}

function normalizeTemporalShells(raw: any): TemporalShellView | undefined {
  if (!raw) return undefined;
  return { seed_hash72: String(raw.seed_hash72 ?? ''), cycles: Number(raw.cycles ?? 0), total_steps: Number(raw.total_steps ?? 0), steps: Array.isArray(raw.steps) ? raw.steps.map((s: any) => ({ index: Number(s.index ?? 0), phase_index: Number(s.phase_index ?? 0), carrier: String(s.carrier ?? 'x'), phase_filter: Number(s.phase_filter ?? 0), shell_width: Number(s.shell_width ?? 1), shell_hash72: String(s.shell_hash72 ?? ''), status: String(s.status ?? 'UNKNOWN'), expansion: s.expansion })) : [], carrier_balance: raw.carrier_balance ?? {}, aggregate_hash72: String(raw.aggregate_hash72 ?? ''), status: String(raw.status ?? 'UNKNOWN'), receipt_hash72: String(raw.receipt_hash72 ?? '') };
}

function normalizeEquationManifest(raw: any): EquationManifestView | undefined {
  if (!raw) return undefined;
  const manifest = raw.manifest ?? raw;
  const packet = manifest.compiler_packet ?? manifest.review_packet ?? {};
  return { status: String(manifest.status ?? 'UNKNOWN'), phases: Array.isArray(manifest.phases) ? manifest.phases.map(Number) : Array.isArray(packet.phases) ? packet.phases.map(Number) : [], equation_text: String(manifest.equation_text ?? packet.equation_text ?? packet.root_equation ?? ''), equation_hash72: String(manifest.equation_hash72 ?? packet.equation_hash72 ?? ''), projection_receipt_hash72: String(manifest.projection_receipt_hash72 ?? packet.projection_receipt_hash72 ?? ''), manifest_hash72: String(manifest.manifest_hash72 ?? raw.aggregate_hash72 ?? ''), compiler_packet: packet, raw };
}

function normalizeTranspileReceipt(raw: any): TranspileReceiptView | undefined {
  if (!raw) return undefined;
  return { input_hash72: String(raw.input_hash72 ?? ''), receipt_hash72: String(raw.receipt_hash72 ?? ''), artifacts: Array.isArray(raw.artifacts) ? raw.artifacts.map((a: any) => ({ target: String(a.target ?? ''), source: String(a.source ?? ''), source_hash72: String(a.source_hash72 ?? ''), status: String(a.status ?? ''), notes: Array.isArray(a.notes) ? a.notes.map(String) : [] })) : [], raw };
}

export function normalizeRuntimeSnapshot(raw: any, source: RuntimeSnapshot['stream']['source'] = 'websocket', eventType = 'runtime_snapshot', batchMeta: Partial<RuntimeSnapshot['stream']> = {}): RuntimeSnapshot {
  const snapshot = raw?.phase && raw?.operatorLoop ? { phase: normalizePhaseResponse(raw.phase), operatorLoop: normalizeLoopResponse(raw.operatorLoop), projection: normalizeProjection(raw.projection), temporalShells: normalizeTemporalShells(raw.temporalShells), equationManifest: normalizeEquationManifest(raw.equationManifest), transpileReceipt: normalizeTranspileReceipt(raw.transpileReceipt), anomalies: normalizeAnomalies(raw.anomalies), corrections: raw.corrections, lastRootCandidate: raw.lastRootCandidate, lastRootCommit: raw.lastRootCommit } : { phase: normalizePhaseResponse(raw?.phase ?? raw?.phase_lock ?? raw?.latest_phase_lock ?? raw), operatorLoop: normalizeLoopResponse(raw?.operatorLoop ?? raw?.operator_loop ?? raw?.latest_operator_loop ?? raw), projection: normalizeProjection(raw?.projection), temporalShells: normalizeTemporalShells(raw?.temporalShells), equationManifest: normalizeEquationManifest(raw?.equationManifest), transpileReceipt: normalizeTranspileReceipt(raw?.transpileReceipt), anomalies: normalizeAnomalies(raw?.anomalies), corrections: raw?.corrections, lastRootCandidate: raw?.lastRootCandidate, lastRootCommit: raw?.lastRootCommit };
  return { ...snapshot, stream: { connected: source === 'websocket', source, last_event_type: eventType, last_update_ms: Date.now(), ...batchMeta } };
}

export async function loadRuntimeSnapshot(): Promise<RuntimeSnapshot> {
  try {
    const [phaseRes, loopRes, projectionRes, shellRes, manifestRes, transpileRes] = await Promise.all([fetch('/api/latest-phase-lock'), fetch('/api/latest-operator-loop'), fetch('/api/latest-projection'), fetch('/api/latest-temporal-shells'), fetch('/api/latest-equation-manifest'), fetch('/api/latest-transpile-receipt')]);
    if (!phaseRes.ok || !loopRes.ok) throw new Error('API unavailable');
    return normalizeRuntimeSnapshot({ phase: await phaseRes.json(), operatorLoop: await loopRes.json(), projection: projectionRes.ok ? await projectionRes.json() : undefined, temporalShells: shellRes.ok ? await shellRes.json() : undefined, equationManifest: manifestRes.ok ? await manifestRes.json() : undefined, transpileReceipt: transpileRes.ok ? await transpileRes.json() : undefined }, 'rest', 'rest_snapshot');
  } catch { return unavailableSnapshot; }
}

export function connectRuntimeStream(onSnapshot: (snapshot: RuntimeSnapshot) => void, onStatus?: (connected: boolean) => void): () => void {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const url = `${protocol}//${window.location.host}/ws/runtime`;
  let socket: WebSocket | null = null;
  try {
    socket = new WebSocket(url);
    socket.onopen = () => onStatus?.(true);
    socket.onmessage = (event) => { try { const message = JSON.parse(event.data); const eventType = message?.type ?? 'runtime_snapshot'; if (eventType === 'runtime_batch' && Array.isArray(message.payload)) { const latest = message.payload[message.payload.length - 1]; onSnapshot(normalizeRuntimeSnapshot(latest, 'websocket', eventType, { batch_size: message.payload.length, batch_index: message.payload.length - 1 })); return; } onSnapshot(normalizeRuntimeSnapshot(message?.payload ?? message, 'websocket', eventType)); } catch {} };
    socket.onerror = () => onStatus?.(false);
    socket.onclose = () => onStatus?.(false);
  } catch { onStatus?.(false); }
  return () => { if (socket && socket.readyState <= WebSocket.OPEN) socket.close(); };
}
