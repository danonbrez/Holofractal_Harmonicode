export type WitnessStatus = 'ADMISSIBLE' | 'EXPIRED' | 'RECURSION_BLOCKED' | 'UNKNOWN';
export type RuntimeStatus = 'LOCKED' | 'INCOMPLETE' | 'QUARANTINED' | 'PHASE_STALLED' | 'EXECUTED';

export type PhaseWitnessView = {
  modality: string;
  source_id: string;
  phase_index: number;
  phase_hash72: string;
  temporal_status: WitnessStatus | string;
  witness_hash72: string;
};

export type PhaseLockView = {
  status: RuntimeStatus | string;
  anchor_phase_index: number;
  anchor_phase_hash72: string;
  mandatory_present: boolean;
  temporal_ok: boolean;
  phase_locked: boolean;
  missing_mandatory: string[];
  receipt_hash72: string;
  witnesses: PhaseWitnessView[];
};

export type OperatorProposalView = {
  agent: string;
  phase_ok: boolean;
  phase_distance_from_anchor: number | null;
  local_score: number;
  risk_score: number;
  operators: string[];
  proposal_hash72: string;
};

export type OperatorLoopView = {
  status: RuntimeStatus | string;
  external_phase_anchor_used: boolean;
  selected_chain_hash72: string | null;
  receipt_hash72: string;
  proposals: OperatorProposalView[];
};

export type RuntimeSnapshot = {
  phase: PhaseLockView;
  operatorLoop: OperatorLoopView;
};

export const mockSnapshot: RuntimeSnapshot = {
  phase: {
    status: 'LOCKED',
    anchor_phase_index: 36,
    anchor_phase_hash72: 'H72-LIVE-PHASE-ANCHOR-DEMO',
    mandatory_present: true,
    temporal_ok: true,
    phase_locked: true,
    missing_mandatory: [],
    receipt_hash72: 'H72-LIVE-RECEIPT-DEMO',
    witnesses: [
      { modality: 'AUDIO', source_id: 'audio_frame_0', phase_index: 36, phase_hash72: 'H72-LIVE-PHASE-ANCHOR-DEMO', temporal_status: 'ADMISSIBLE', witness_hash72: 'H72-AUDIO-WITNESS' },
      { modality: 'HARMONICODE', source_id: 'kernel_phase', phase_index: 36, phase_hash72: 'H72-LIVE-PHASE-ANCHOR-DEMO', temporal_status: 'ADMISSIBLE', witness_hash72: 'H72-HARMONICODE-WITNESS' },
      { modality: 'XYZW', source_id: 'xyzw_algebra', phase_index: 36, phase_hash72: 'H72-LIVE-PHASE-ANCHOR-DEMO', temporal_status: 'ADMISSIBLE', witness_hash72: 'H72-XYZW-WITNESS' },
      { modality: 'HASH72', source_id: 'hash72_commit', phase_index: 36, phase_hash72: 'H72-LIVE-PHASE-ANCHOR-DEMO', temporal_status: 'ADMISSIBLE', witness_hash72: 'H72-HASH72-WITNESS' },
      { modality: 'TEXT', source_id: 'text_support', phase_index: 37, phase_hash72: 'H72-SUPPORT-PHASE', temporal_status: 'ADMISSIBLE', witness_hash72: 'H72-TEXT-WITNESS' }
    ]
  },
  operatorLoop: {
    status: 'EXECUTED',
    external_phase_anchor_used: true,
    selected_chain_hash72: 'H72-SELECTED-CHAIN-DEMO',
    receipt_hash72: 'H72-OPERATOR-LOOP-RECEIPT-DEMO',
    proposals: [
      { agent: 'LOGIC_AGENT', phase_ok: true, phase_distance_from_anchor: 0, local_score: 44, risk_score: 0, operators: ['HHS Alignment Axiom', 'Meaning Preservation Operator'], proposal_hash72: 'H72-LOGIC-PROPOSAL' },
      { agent: 'STYLE_AGENT', phase_ok: true, phase_distance_from_anchor: 1, local_score: 31, risk_score: 0, operators: ['Recursive Harmonic Prose'], proposal_hash72: 'H72-STYLE-PROPOSAL' },
      { agent: 'PROCESS_AGENT', phase_ok: true, phase_distance_from_anchor: 1, local_score: 28, risk_score: 0, operators: ['Draft Audit Compress Re-expand'], proposal_hash72: 'H72-PROCESS-PROPOSAL' },
      { agent: 'SYNTHESIS_AGENT', phase_ok: true, phase_distance_from_anchor: 0, local_score: 52, risk_score: 0, operators: ['Alignment Axiom', 'Recursive Harmonic Prose', 'Writing Process'], proposal_hash72: 'H72-SYNTHESIS-PROPOSAL' },
      { agent: 'AUDIT_AGENT', phase_ok: true, phase_distance_from_anchor: 0, local_score: 47, risk_score: 0, operators: ['Meaning Preservation Operator'], proposal_hash72: 'H72-AUDIT-PROPOSAL' }
    ]
  }
};

function normalizePhaseResponse(raw: any): PhaseLockView {
  const witnesses = Array.isArray(raw?.witnesses) ? raw.witnesses.map((w: any) => ({
    modality: w?.observation?.modality ?? w?.modality ?? 'UNKNOWN',
    source_id: w?.observation?.source_id ?? w?.source_id ?? 'unknown',
    phase_index: Number(w?.phase_index ?? 0),
    phase_hash72: String(w?.phase_hash72 ?? ''),
    temporal_status: String(w?.temporal_status ?? 'UNKNOWN'),
    witness_hash72: String(w?.witness_hash72 ?? '')
  })) : mockSnapshot.phase.witnesses;
  return {
    status: raw?.status ?? 'UNKNOWN',
    anchor_phase_index: Number(raw?.anchor_phase_index ?? 0),
    anchor_phase_hash72: String(raw?.anchor_phase_hash72 ?? ''),
    mandatory_present: Boolean(raw?.mandatory_present),
    temporal_ok: Boolean(raw?.temporal_ok),
    phase_locked: Boolean(raw?.phase_locked),
    missing_mandatory: Array.isArray(raw?.missing_mandatory) ? raw.missing_mandatory : [],
    receipt_hash72: String(raw?.receipt_hash72 ?? ''),
    witnesses
  };
}

function normalizeLoopResponse(raw: any): OperatorLoopView {
  const proposals = Array.isArray(raw?.phase_agent_proposals) ? raw.phase_agent_proposals.map((p: any) => ({
    agent: p?.proposal?.agent?.kind ?? p?.proposal?.agent?.name ?? 'AGENT',
    phase_ok: Boolean(p?.phase_ok),
    phase_distance_from_anchor: p?.phase_distance_from_anchor ?? null,
    local_score: Number(p?.proposal?.local_score ?? 0),
    risk_score: Number(p?.proposal?.risk_score ?? 0),
    operators: Array.isArray(p?.proposal?.selected_operators) ? p.proposal.selected_operators.map((op: any) => op?.title ?? op?.operator_signature ?? 'operator') : [],
    proposal_hash72: String(p?.proposal?.proposal_hash72 ?? p?.receipt_hash72 ?? '')
  })) : mockSnapshot.operatorLoop.proposals;
  return {
    status: raw?.status ?? 'UNKNOWN',
    external_phase_anchor_used: Boolean(raw?.external_phase_anchor_used),
    selected_chain_hash72: raw?.selected_candidate?.chain_hash72 ?? raw?.selected_chain_hash72 ?? null,
    receipt_hash72: String(raw?.receipt_hash72 ?? ''),
    proposals
  };
}

export async function loadRuntimeSnapshot(): Promise<RuntimeSnapshot> {
  try {
    const [phaseRes, loopRes] = await Promise.all([
      fetch('/api/latest-phase-lock'),
      fetch('/api/latest-operator-loop')
    ]);
    if (!phaseRes.ok || !loopRes.ok) throw new Error('API unavailable');
    return {
      phase: normalizePhaseResponse(await phaseRes.json()),
      operatorLoop: normalizeLoopResponse(await loopRes.json())
    };
  } catch {
    return mockSnapshot;
  }
}
