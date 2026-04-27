export type ExprNodeKind =
  | 'ROOT'
  | 'TOKEN'
  | 'NUMBER'
  | 'SYMBOL'
  | 'ORDERED_PRODUCT'
  | 'OPERATOR'
  | 'FUNCTION'
  | 'LIST'
  | 'GROUP'
  | 'INVARIANT'
  | 'GATE';

export type ExprNode = {
  id: string;
  kind: ExprNodeKind;
  text: string;
  children?: ExprNode[];
  phaseIndex?: number;
  metadata?: Record<string, unknown>;
};

export type ExprDocument = {
  version: 'HHS_CALC_EXPR_v1';
  nodes: ExprNode[];
  cursor: number;
};

export type InsertIntent = {
  raw: string;
  node: ExprNode;
  cursorDelta: number;
};

let NODE_COUNTER = 0;

function nextId(prefix: string): string {
  NODE_COUNTER += 1;
  return `${prefix}_${Date.now().toString(36)}_${NODE_COUNTER.toString(36)}`;
}

function phaseFromText(text: string): number {
  let acc = 0;
  for (const ch of text) acc = (acc * 131 + ch.charCodeAt(0)) % 72;
  return acc;
}

export function classifyToken(raw: string): ExprNodeKind {
  if (/^[0-9]+(?:\.[0-9]+)?$/.test(raw)) return 'NUMBER';
  if (['xy', 'yx', 'zw', 'wz'].includes(raw)) return 'ORDERED_PRODUCT';
  if (['Δe=0', 'Ψ=0', 'Θ15=true', 'Ω=true'].includes(raw)) return 'INVARIANT';
  if (/^[A-Z][A-Z0-9_]*\s*:=/.test(raw) || raw.includes('GATE')) return 'GATE';
  if (/^[A-Za-z_][A-Za-z0-9_]*\($/.test(raw)) return 'FUNCTION';
  if (['+', '-', '*', '/', '^', '=', '≠', '<', '>', '≤', '≥', ':='].includes(raw.trim())) return 'OPERATOR';
  if (['(', ')', '{', '}', '[', ']', ','].includes(raw)) return 'GROUP';
  if (/^[A-Za-zΩΨΔΘρπ]+(?:\^[0-9]+)?$/.test(raw)) return 'SYMBOL';
  return 'TOKEN';
}

export function makeNode(raw: string): ExprNode {
  const kind = classifyToken(raw);
  return {
    id: nextId(kind.toLowerCase()),
    kind,
    text: raw,
    phaseIndex: phaseFromText(raw),
    metadata: kind === 'ORDERED_PRODUCT' ? { commutative: false } : undefined,
  };
}

export function documentFromText(text: string): ExprDocument {
  const tokens = tokenizeExpression(text).map(makeNode);
  return { version: 'HHS_CALC_EXPR_v1', nodes: tokens, cursor: tokens.length };
}

export function renderDocument(doc: ExprDocument): string {
  return doc.nodes.map((n) => n.text).join('');
}

export function insertIntoDocument(doc: ExprDocument, raw: string): ExprDocument {
  const node = makeNode(raw);
  const cursor = Math.max(0, Math.min(doc.cursor, doc.nodes.length));
  const next = [...doc.nodes.slice(0, cursor), node, ...doc.nodes.slice(cursor)];
  return { ...doc, nodes: next, cursor: cursor + 1 };
}

export function backspaceDocument(doc: ExprDocument): ExprDocument {
  const cursor = Math.max(0, Math.min(doc.cursor, doc.nodes.length));
  if (cursor === 0) return doc;
  return { ...doc, nodes: [...doc.nodes.slice(0, cursor - 1), ...doc.nodes.slice(cursor)], cursor: cursor - 1 };
}

export function moveCursor(doc: ExprDocument, delta: number): ExprDocument {
  return { ...doc, cursor: Math.max(0, Math.min(doc.nodes.length, doc.cursor + delta)) };
}

export function clearDocument(): ExprDocument {
  return { version: 'HHS_CALC_EXPR_v1', nodes: [], cursor: 0 };
}

export function tokenizeExpression(text: string): string[] {
  const tokens: string[] = [];
  let buf = '';
  const flush = () => {
    if (buf) tokens.push(buf);
    buf = '';
  };
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    const two = text.slice(i, i + 2);
    if (['!=', '==', ':=', '<=', '>=', '->'].includes(two)) {
      flush();
      tokens.push(two === '!=' ? '≠' : two === '<=' ? '≤' : two === '>=' ? '≥' : two);
      i += 1;
      continue;
    }
    if ('()+-*/^={},{}[]<>\n '.includes(ch) || ch === '≠' || ch === '≤' || ch === '≥') {
      flush();
      if (ch !== '') tokens.push(ch);
      continue;
    }
    buf += ch;
  }
  flush();
  return tokens;
}

export function diagnosticsForDocument(doc: ExprDocument): { level: 'INFO' | 'WARN' | 'ERROR'; message: string; nodeIds: string[] }[] {
  const diagnostics: { level: 'INFO' | 'WARN' | 'ERROR'; message: string; nodeIds: string[] }[] = [];
  const nodes = doc.nodes;
  for (let i = 0; i < nodes.length - 2; i += 1) {
    const a = nodes[i];
    const op = nodes[i + 1];
    const b = nodes[i + 2];
    if (a.kind === 'ORDERED_PRODUCT' && b.kind === 'ORDERED_PRODUCT' && op.text === '=' && a.text === b.text.split('').reverse().join('')) {
      diagnostics.push({
        level: 'ERROR',
        message: `Illegal ordered-product collapse: ${a.text} = ${b.text}`,
        nodeIds: [a.id, op.id, b.id],
      });
    }
  }
  const invariantCount = nodes.filter((n) => n.kind === 'INVARIANT').length;
  if (invariantCount > 0) diagnostics.push({ level: 'INFO', message: `Invariant tokens present: ${invariantCount}`, nodeIds: nodes.filter((n) => n.kind === 'INVARIANT').map((n) => n.id) });
  return diagnostics;
}

export function phaseMapForDocument(doc: ExprDocument): Record<number, string[]> {
  const map: Record<number, string[]> = {};
  for (const node of doc.nodes) {
    const phase = node.phaseIndex ?? phaseFromText(node.text);
    map[phase] = map[phase] || [];
    map[phase].push(node.id);
  }
  return map;
}

export function expressionToCompilerPacket(doc: ExprDocument) {
  return {
    type: 'CALCULATOR_EXPRESSION_PACKET',
    version: doc.version,
    expression_text: renderDocument(doc),
    nodes: doc.nodes,
    phase_map: phaseMapForDocument(doc),
    diagnostics: diagnosticsForDocument(doc),
  };
}
