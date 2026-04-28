export type DisplayPhaseItem = {
  id: string;
  text: string;
  kind: string;
  phaseIndex: number;
};

export type DisplayPhaseInfluence = {
  id: string;
  text: string;
  kind: string;
  phaseIndex: number;
  influenceScore: number;
  projectedPhases: number[];
  reason: string;
};

const RING = 72;

function mod72(n: number): number {
  return ((Math.round(n) % RING) + RING) % RING;
}

function kindWeight(kind: string): number {
  if (kind === 'ORDERED_PRODUCT') return 34;
  if (kind === 'INVARIANT') return 30;
  if (kind === 'FUNCTION') return 24;
  if (kind === 'OPERATOR') return 20;
  if (kind === 'GATE') return 26;
  if (kind === 'NUMBER') return 12;
  return 16;
}

function textWeight(text: string): number {
  let acc = 0;
  for (const ch of text) acc += ch.charCodeAt(0);
  return acc % 29;
}

export function analyzeDisplayPhaseItems(items: DisplayPhaseItem[], activePhase: number | null | undefined): DisplayPhaseInfluence[] {
  const anchor = mod72(activePhase ?? items[0]?.phaseIndex ?? 0);
  return items.map((item, index) => {
    const base = mod72(item.phaseIndex);
    const weight = kindWeight(item.kind) + textWeight(item.text);
    const distance = Math.min(Math.abs(base - anchor), RING - Math.abs(base - anchor));
    const influenceScore = Math.max(0, Math.min(100, weight + Math.max(0, 24 - distance) + Math.min(18, index * 2)));
    const stride = Math.max(1, Math.min(9, Math.round(influenceScore / 14)));
    const projectedPhases = [base, mod72(base + stride), mod72(base + stride * 2), mod72(base + stride * 3)];
    const reason = `${item.kind} item contributes phase stride ${stride} from ${base}`;
    return { ...item, phaseIndex: base, influenceScore, projectedPhases, reason };
  }).sort((a, b) => b.influenceScore - a.influenceScore);
}

export function topDisplayInfluences(items: DisplayPhaseItem[], activePhase: number | null | undefined, limit = 8): DisplayPhaseInfluence[] {
  return analyzeDisplayPhaseItems(items, activePhase).slice(0, limit);
}
