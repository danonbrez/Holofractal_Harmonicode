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

export type RuntimeSnapshot = {
  phase: PhaseLockView;
  operatorLoop: OperatorLoopView;
  projection?: ProjectionView;
  temporalShells?: TemporalShellView;
  anomalies?: RuntimeAnomalies;
  corrections?: any;
  lastRootCandidate?: any;
  lastRootCommit?: any;
  stream?: { connected: boolean; source: 'websocket' | 'rest' | 'mock'; last_event_type?: string; last_update_ms?: number; batch_size?: number; batch_index?: number; };
};

const clearAnomalies: RuntimeAnomalies = { status: 'CLEAR', critical: 0, warn: 0, info: 0, alerts: [], summary_hash72: 'H72-CLEAR' };
const mockProjection: ProjectionView = { phase_index: 36, u72_ok: true, loshu_ok: true, anchor_hash72: 'H72-PROJECTION-ANCHOR-DEMO', status: 'PROJECTED', target_layer: 'normalized', receipt_hash72: 'H72-PROJECTION-RECEIPT-DEMO' };
const mockTemporalShells: TemporalShellView = { seed_hash72: 'H72-SHELL-SEED-DEMO', cycles: 1, total_steps: 72, steps: Array.from({ length: 18 }).map((_, i) => ({ index: i, phase_index: (36 + i * 5) % 72, carrier: ['x', 'y', 'xy'][i % 3], phase_filter: i, shell_width: 1 + (i % 9), shell_hash72: `H72-SHELL-${i}`, status: 'LOCKED', expansion: {} })), carrier_balance: { x: 24, y: 24, xy: 24 }, aggregate_hash72: 'H72-SHELL-AGG-DEMO', status: 'LOCKED', receipt_hash72: 'H72-SHELL-RECEIPT-DEMO' };

export const mockSnapshot: RuntimeSnapshot = {
  phase: { status: 'LOCKED', anchor_phase_index: 36, anchor_phase_hash72: 'H72-LIVE-PHASE-ANCHOR-DEMO', mandatory_present: true, temporal_ok: true, phase_locked: true, missing_mandatory: [], receipt_hash72: 'H72-LIVE-RECEIPT-DEMO', witnesses: [
    { modality: 'AUDIO', source_id: 'audio_frame_0', phase_index: 36, phase_hash72: 'H72-LIVE-PHASE-ANCHOR-DEMO', temporal_status: 'ADMISSIBLE', witness_hash72: 'H72-AUDIO-WITNESS' },
    { modality: 'HARMONICODE', source_id: 'kernel_phase', phase_index: 36, phase_hash72: 'H72-LIVE-PHASE-ANCHOR-DEMO', temporal_status: 'ADMISSIBLE', witness_hash72: 'H72-HARMONICODE-WITNESS' },
    { modality: 'XYZW', source_id: 'xyzw_algebra', phase_index: 36, phase_hash72: 'H72-LIVE-PHASE-ANCHOR-DEMO', temporal_status: 'ADMISSIBLE', witness_hash72: 'H72-XYZW-WITNESS' },
    { modality: 'HASH72', source_id: 'hash72_commit', phase_index: 36, phase_hash72: 'H72-LIVE-PHASE-ANCHOR-DEMO', temporal_status: 'ADMISSIBLE', witness_hash72: 'H72-HASH72-WITNESS' },
    { modality: 'TEXT', source_id: 'text_support', phase_index: 37, phase_hash72: 'H72-SUPPORT-PHASE', temporal_status: 'ADMISSIBLE', witness_hash72: 'H72-TEXT-WITNESS' }
  ]},
  operatorLoop: { status: 'EXECUTED', external_phase_anchor_used: true, selected_chain_hash72: 'H72-SELECTED-CHAIN-DEMO', receipt_hash72: 'H72-OPERATOR-LOOP-RECEIPT-DEMO', proposals: [
    { agent: 'LOGIC_AGENT', phase_ok: true, phase_distance_from_anchor: 0, local_score: 44, risk_score: 0, operators: ['HHS Alignment Axiom'], proposal_hash72: 'H72-LOGIC-PROPOSAL' },
    { agent: 'PROCESS_AGENT', phase_ok: true, phase_distance_from_anchor: 1, local_score: 28, risk_score: 0, operators: ['Draft Audit Compress Re-expand'], proposal_hash72: 'H72-PROCESS-PROPOSAL' },
    { agent: 'SYNTHESIS_AGENT', phase_ok: true, phase_distance_from_anchor: 0, local_score: 52, risk_score: 0, operators: ['Alignment Axiom'], proposal_hash72: 'H72-SYNTHESIS-PROPOSAL' },
    { agent: 'AUDIT_AGENT', phase_ok: true, phase_distance_from_anchor: 0, local_score: 47, risk_score: 0, operators: ['Meaning Preservation'], proposal_hash72: 'H72-AUDIT-PROPOSAL' }
  ]},
  projection: mockProjection,
  temporalShells: mockTemporalShells,
  anomalies: clearAnomalies,
  corrections: {},
  stream: { connected: false, source: 'mock', last_event_type: 'mock_snapshot', last_update_ms: Date.now() }
};

function normalizePhaseResponse(raw: any): PhaseLockView {
  const witnesses = Array.isArray(raw?.witnesses) ? raw.witnesses.map((w: any) => ({ modality: w?.observation?.modality ?? w?.modality ?? 'UNKNOWN', source_id: w?.observation?.source_id ?? w?.source_id ?? 'unknown', phase_index: Number(w?.phase_index ?? 0), phase_hash72: String(w?.phase_hash72 ?? ''), temporal_status: String(w?.temporal_status ?? 'UNKNOWN'), witness_hash72: String(w?.witness_hash72 ?? '') })) : mockSnapshot.phase.witnesses;
  return { status: raw?.status ?? 'UNKNOWN', anchor_phase_index: Number(raw?.anchor_phase_index ?? 0), anchor_phase_hash72: String(raw?.anchor_phase_hash72 ?? ''), mandatory_present: Boolean(raw?.mandatory_present), temporal_ok: Boolean(raw?.temporal_ok), phase_locked: Boolean(raw?.phase_locked), missing_mandatory: Array.isArray(raw?.missing_mandatory) ? raw.missing_mandatory : [], receipt_hash72: String(raw?.receipt_hash72 ?? ''), witnesses };
}

function normalizeLoopResponse(raw: any): OperatorLoopView {
  const proposals = Array.isArray(raw?.phase_agent_proposals) ? raw.phase_agent_proposals.map((p: any) => ({ agent: p?.proposal?.agent?.kind ?? p?.proposal?.agent?.name ?? 'AGENT', phase_ok: Boolean(p?.phase_ok), phase_distance_from_anchor: p?.phase_distance_from_anchor ?? null, local_score: Number(p?.proposal?.local_score ?? 0), risk_score: Number(p?.proposal?.risk_score ?? 0), operators: Array.isArray(p?.proposal?.selected_operators) ? p.proposal.selected_operators.map((op: any) => op?.title ?? op?.operator_signature ?? 'operator') : [], proposal_hash72: String(p?.proposal?.proposal_hash72 ?? p?.receipt_hash72 ?? '') })) : mockSnapshot.operatorLoop.proposals;
  return { status: raw?.status ?? 'UNKNOWN', external_phase_anchor_used: Boolean(raw?.external_phase_anchor_used), selected_chain_hash72: raw?.selected_candidate?.chain_hash72 ?? raw?.selected_chain_hash72 ?? null, receipt_hash72: String(raw?.receipt_hash72 ?? ''), proposals };
}

function normalizeAnomalies(raw: any): RuntimeAnomalies { if (!raw) return clearAnomalies; return { status: raw.status ?? 'CLEAR', critical: Number(raw.critical ?? 0), warn: Number(raw.warn ?? 0), info: Number(raw.info ?? 0), alerts: Array.isArray(raw.alerts) ? raw.alerts : [], summary_hash72: String(raw.summary_hash72 ?? ''), drift_prediction: raw.drift_prediction }; }

function normalizeProjection(raw: any): ProjectionView {
  const receipt = raw?.projection?.receipt ?? raw?.receipt ?? {};
  const witness = raw?.projection?.phase_witness ?? raw?.phase_witness ?? receipt?.phase_witness ?? {};
  const steps = raw?.projection?.projection_steps ?? raw?.projection_steps ?? [];
  const targetLayer = steps?.[0]?.target_layer ?? 'normalized';
  return { phase_index: Number(witness?.phase_index ?? mockProjection.phase_index), u72_ok: Boolean(witness?.u72_ok ?? true), loshu_ok: Boolean(witness?.loshu_ok ?? true), anchor_hash72: String(witness?.anchor_hash72 ?? mockProjection.anchor_hash72), status: String(receipt?.status ?? raw?.status ?? 'PROJECTED'), target_layer: String(targetLayer), receipt_hash72: String(receipt?.receipt_hash72 ?? raw?.receipt_hash72 ?? mockProjection.receipt_hash72), raw };
}

function normalizeTemporalShells(raw: any): TemporalShellView | undefined {
  if (!raw) return undefined;
  return { seed_hash72: String(raw.seed_hash72 ?? ''), cycles: Number(raw.cycles ?? 0), total_steps: Number(raw.total_steps ?? 0), steps: Array.isArray(raw.steps) ? raw.steps.map((s: any) => ({ index: Number(s.index ?? 0), phase_index: Number(s.phase_index ?? 0), carrier: String(s.carrier ?? 'x'), phase_filter: Number(s.phase_filter ?? 0), shell_width: Number(s.shell_width ?? 1), shell_hash72: String(s.shell_hash72 ?? ''), status: String(s.status ?? 'UNKNOWN'), expansion: s.expansion })) : [], carrier_balance: raw.carrier_balance ?? {}, aggregate_hash72: String(raw.aggregate_hash72 ?? ''), status: String(raw.status ?? 'UNKNOWN'), receipt_hash72: String(raw.receipt_hash72 ?? '') };
}

export function normalizeRuntimeSnapshot(raw: any, source: RuntimeSnapshot['stream']['source'] = 'websocket', eventType = 'runtime_snapshot', batchMeta: Partial<RuntimeSnapshot['stream']> = {}): RuntimeSnapshot {
  const snapshot = raw?.phase && raw?.operatorLoop ? { phase: normalizePhaseResponse(raw.phase), operatorLoop: normalizeLoopResponse(raw.operatorLoop), projection: normalizeProjection(raw.projection), temporalShells: normalizeTemporalShells(raw.temporalShells), anomalies: normalizeAnomalies(raw.anomalies), corrections: raw.corrections, lastRootCandidate: raw.lastRootCandidate, lastRootCommit: raw.lastRootCommit } : { phase: normalizePhaseResponse(raw?.phase ?? raw?.phase_lock ?? raw?.latest_phase_lock ?? raw), operatorLoop: normalizeLoopResponse(raw?.operatorLoop ?? raw?.operator_loop ?? raw?.latest_operator_loop ?? raw), projection: normalizeProjection(raw?.projection), temporalShells: normalizeTemporalShells(raw?.temporalShells), anomalies: normalizeAnomalies(raw?.anomalies), corrections: raw?.corrections, lastRootCandidate: raw?.lastRootCandidate, lastRootCommit: raw?.lastRootCommit };
  return { ...snapshot, stream: { connected: source === 'websocket', source, last_event_type: eventType, last_update_ms: Date.now(), ...batchMeta } };
}

export async function loadRuntimeSnapshot(): Promise<RuntimeSnapshot> {
  try {
    const [phaseRes, loopRes, projectionRes, shellRes] = await Promise.all([fetch('/api/latest-phase-lock'), fetch('/api/latest-operator-loop'), fetch('/api/latest-projection'), fetch('/api/latest-temporal-shells')]);
    if (!phaseRes.ok || !loopRes.ok) throw new Error('API unavailable');
    return normalizeRuntimeSnapshot({ phase: await phaseRes.json(), operatorLoop: await loopRes.json(), projection: projectionRes.ok ? await projectionRes.json() : undefined, temporalShells: shellRes.ok ? await shellRes.json() : undefined }, 'rest', 'rest_snapshot');
  } catch { return mockSnapshot; }
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
