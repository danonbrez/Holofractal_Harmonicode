import React, { useEffect, useMemo, useState } from 'react';

function readEquation(manifest: any): string {
  return manifest?.manifest?.equation_text
    ?? manifest?.manifest?.compiler_packet?.equation_text
    ?? manifest?.manifest?.compiler_packet?.root_equation
    ?? manifest?.candidate?.equation?.equation
    ?? '';
}

function receipt(value: any, fallback = '—'): string {
  if (!value) return fallback;
  const s = String(value);
  return s.length > 28 ? `${s.slice(0, 16)}…${s.slice(-8)}` : s;
}

type KeyDef = {
  label: string;
  insert?: string;
  shift?: string;
  alpha?: string;
  wide?: boolean;
  accent?: 'shift' | 'alpha' | 'orange' | 'mode' | 'operator';
};

const mainKeys: KeyDef[][] = [
  [
    { label: 'SHIFT', accent: 'shift' },
    { label: 'ALPHA', accent: 'alpha' },
    { label: '◀', insert: 'LEFT' },
    { label: '▶', insert: 'RIGHT' },
    { label: 'MODE', accent: 'mode' },
    { label: '2nd', accent: 'mode' },
  ],
  [
    { label: 'CALC', insert: 'EVAL' },
    { label: '∫dx', insert: 'Integral(' },
    { label: '▲', insert: '\n' },
    { label: '▼', insert: ' ' },
    { label: 'x⁻¹', insert: '^(-1)', shift: 'x!' },
    { label: 'Logₓy', insert: 'Log(' },
  ],
  [
    { label: 'x/y', insert: '/' },
    { label: '√x', insert: 'Sqrt(' },
    { label: 'x²', insert: '^2' },
    { label: 'xʸ', insert: '^' },
    { label: 'Log', insert: 'Log(' },
    { label: 'Ln', insert: 'Ln(' },
  ],
  [
    { label: '(−)', insert: '-' },
    { label: "°'\"", insert: '°' },
    { label: 'hyp', insert: 'hyp(' },
    { label: 'Sin', insert: 'Sin(' },
    { label: 'Cos', insert: 'Cos(' },
    { label: 'Tan', insert: 'Tan(' },
  ],
  [
    { label: 'RCL', insert: 'RCL(' },
    { label: 'ENG', insert: 'ENG(' },
    { label: '(', insert: '(' },
    { label: ')', insert: ')' },
    { label: 'S⇔D', insert: 'Project(' },
    { label: 'M+', insert: 'M+' },
  ],
  [
    { label: '7', insert: '7' },
    { label: '8', insert: '8' },
    { label: '9', insert: '9' },
    { label: '⌫', insert: 'BACK', accent: 'orange' },
    { label: 'AC', insert: 'CLEAR', accent: 'orange' },
  ],
  [
    { label: '4', insert: '4' },
    { label: '5', insert: '5' },
    { label: '6', insert: '6' },
    { label: '×', insert: '*', accent: 'operator' },
    { label: '÷', insert: '/', accent: 'operator' },
  ],
  [
    { label: '1', insert: '1' },
    { label: '2', insert: '2' },
    { label: '3', insert: '3' },
    { label: '+', insert: '+', accent: 'operator' },
    { label: '−', insert: '-', accent: 'operator' },
  ],
  [
    { label: '0', insert: '0' },
    { label: '.', insert: '.' },
    { label: 'Exp', insert: 'Exp(' },
    { label: 'Ans', insert: 'Ans' },
    { label: '=', insert: '=', accent: 'operator' },
  ],
];

const moreKeys: KeyDef[][] = [
  [
    { label: 'FACTOR', insert: 'Factor(' },
    { label: 'EXPAND', insert: 'Expand(' },
    { label: 'SIMPLY', insert: 'Simplify(' },
    { label: 'GRAPH', insert: 'Graph(' },
    { label: '∫□dx', insert: 'Integral(' },
    { label: 'd/dx□', insert: 'Derivative(' },
  ],
  [
    { label: 'r', insert: 'r' },
    { label: 'u', insert: 'u' },
    { label: 'x', insert: 'x' },
    { label: '{', insert: '{' },
    { label: '}', insert: '}' },
    { label: ',', insert: ',' },
  ],
  [
    { label: '=', insert: '=' },
    { label: '<', insert: '<' },
    { label: '>', insert: '>' },
    { label: 'True', insert: 'True' },
    { label: '→', insert: ' -> ' },
    { label: ':=', insert: ':=' },
  ],
  [
    { label: '≠', insert: '≠' },
    { label: 'and', insert: ' and ' },
    { label: '≤', insert: '≤' },
    { label: 'or', insert: ' or ' },
    { label: '≥', insert: '≥' },
    { label: 'xor', insert: ' xor ' },
  ],
  [
    { label: '[:::]', insert: 'List(' },
    { label: '•', insert: '*' },
    { label: 'Det', insert: 'Det(' },
    { label: 'Rank', insert: 'Rank(' },
    { label: '[ ]⁻¹', insert: '^(-1)' },
    { label: 'EiVal', insert: 'EigenValues(' },
  ],
  [
    { label: 'arith', insert: 'arith:' },
    { label: 'algebra', insert: 'algebra:' },
    { label: 'solver', insert: 'solver:' },
    { label: 'calculus', insert: 'calculus:' },
  ],
  [
    { label: 'list', insert: 'List(' },
    { label: 'linear\nalgebra', insert: 'Matrix(' },
    { label: 'combinat\norics', insert: 'Combinatorics(' },
    { label: 'stat\ndist', insert: 'Distribution(' },
  ],
  [
    { label: 'number', insert: 'Number(' },
    { label: 'boolean', insert: 'Boolean(' },
    { label: 'special', insert: 'Special(' },
    { label: 'others', insert: 'Other(' },
  ],
];

const hhsKeys: KeyDef[][] = [
  [
    { label: 'xy', insert: 'xy' },
    { label: 'yx', insert: 'yx' },
    { label: 'zw', insert: 'zw' },
    { label: 'wz', insert: 'wz' },
    { label: 'u⁷²', insert: 'u^72' },
    { label: 'u⁷¹', insert: 'u^71' },
  ],
  [
    { label: 'Δe=0', insert: 'Δe=0' },
    { label: 'Ψ=0', insert: 'Ψ=0' },
    { label: 'Θ15', insert: 'Θ15=true' },
    { label: 'Ω', insert: 'Ω=true' },
    { label: 'Hash72', insert: 'Hash72(' },
    { label: 'ERS', insert: 'ERS(' },
  ],
  [
    { label: 'List', insert: 'List(' },
    { label: 'Mod', insert: 'Mod(' },
    { label: 'Sqrt', insert: 'Sqrt(' },
    { label: 'Power', insert: 'Power(' },
    { label: 'Project', insert: 'Project(' },
    { label: 'Gate', insert: 'GATE := { ' },
  ],
  [
    { label: 'x=1/y', insert: 'x=1/y' },
    { label: 'y=-x', insert: 'y=-x' },
    { label: 'xy≠yx', insert: 'xy≠yx' },
    { label: 'xy=-1/yx', insert: 'xy=-1/yx' },
  ],
];

function buttonStyle(key: KeyDef): React.CSSProperties {
  const base: React.CSSProperties = {
    border: '1px solid rgba(255,255,255,0.18)',
    borderRadius: 10,
    color: '#f4f4f4',
    fontFamily: 'monospace',
    fontSize: 18,
    minHeight: 48,
    whiteSpace: 'pre-line',
    boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.18), 0 2px 0 rgba(0,0,0,0.7)',
  };
  if (key.accent === 'shift') return { ...base, background: '#ffc21c', color: '#161000' };
  if (key.accent === 'alpha') return { ...base, background: '#7662b7' };
  if (key.accent === 'orange') return { ...base, background: '#ff893a', color: '#140600' };
  if (key.accent === 'operator') return { ...base, background: '#252a34' };
  if (key.accent === 'mode') return { ...base, background: '#4b4950', fontStyle: 'italic' };
  return { ...base, background: '#535157' };
}

export default function CalculatorPanel({ equationManifest, transpileReceipt, activePhase }: { equationManifest?: any; transpileReceipt?: any; activePhase?: number | null }) {
  const generatedEquation = useMemo(() => readEquation(equationManifest), [equationManifest]);
  const [expression, setExpression] = useState(generatedEquation || 'xy=-1/yx\nyx=-xy\nxy≠yx');
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<'main' | 'more' | 'hhs'>('main');
  const [cursor, setCursor] = useState(expression.length);

  useEffect(() => {
    if (generatedEquation && !result) {
      setExpression(generatedEquation);
      setCursor(generatedEquation.length);
    }
  }, [generatedEquation]);

  function insertText(raw?: string) {
    if (!raw) return;
    if (raw === 'EVAL') return void evaluate();
    if (raw === 'CLEAR') {
      setExpression('');
      setCursor(0);
      return;
    }
    if (raw === 'BACK') {
      const next = expression.slice(0, Math.max(0, cursor - 1)) + expression.slice(cursor);
      setExpression(next);
      setCursor(Math.max(0, cursor - 1));
      return;
    }
    if (raw === 'LEFT') return setCursor(Math.max(0, cursor - 1));
    if (raw === 'RIGHT') return setCursor(Math.min(expression.length, cursor + 1));
    const next = expression.slice(0, cursor) + raw + expression.slice(cursor);
    setExpression(next);
    setCursor(cursor + raw.length);
  }

  async function evaluate() {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch('/api/calculator/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
    } catch (err: any) {
      setError(err?.message ?? 'evaluation failed');
    } finally {
      setBusy(false);
    }
  }

  const keys = page === 'more' ? moreKeys : page === 'hhs' ? hhsKeys : mainKeys;
  const solverStatus = result?.solver?.receipt?.status ?? 'UNRUN';
  const contradictionCount = result?.solver?.contradictions?.length ?? 0;
  const manifestStatus = equationManifest?.status ?? equationManifest?.manifest?.status ?? 'NO_MANIFEST';
  const phaseList = equationManifest?.phases ?? equationManifest?.manifest?.phases ?? equationManifest?.manifest?.compiler_packet?.phases ?? [];
  const pythonArtifact = transpileReceipt?.artifacts?.find?.((a: any) => a.target === 'python') ?? transpileReceipt?.artifacts?.[0];
  const autocorrectionSuggestions = result?.autocorrections?.suggestions ?? [];
  const branchFrontier = result?.correctionBranchFrontier;

  return (
    <section style={{ borderTop: '1px solid #063', borderBottom: '1px solid #063', padding: 10, background: '#08090b', maxHeight: '62vh', overflow: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#f4f4f4', fontFamily: 'monospace', fontWeight: 700, letterSpacing: 1 }}>
        <span>NORM&nbsp; MATH&nbsp; FRAC</span>
        <span>{activePhase == null ? 'PHASE --' : `PHASE ${activePhase}`}</span>
      </div>

      <div style={{ marginTop: 8, background: '#d6ebea', color: '#111', borderRadius: 12, minHeight: 118, padding: 10, fontFamily: 'monospace', fontSize: 16, whiteSpace: 'pre-wrap', overflow: 'auto' }}>
        <div>{expression.slice(0, cursor)}<span style={{ color: '#e00' }}>|</span>{expression.slice(cursor)}</div>
        <div style={{ marginTop: 8, color: '#333' }}>
          {solverStatus !== 'UNRUN' ? `{{${contradictionCount}}} = ${solverStatus}` : ' '}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 8, marginTop: 10 }}>
        <button onClick={() => setPage('main')} style={buttonStyle({ label: 'main', accent: page === 'main' ? 'alpha' : undefined })}>☰</button>
        <button onClick={() => setPage('hhs')} style={buttonStyle({ label: 'Σ' })}>Σ</button>
        <button onClick={() => setPage('more')} style={buttonStyle({ label: 'gear' })}>⚙</button>
        <button onClick={() => insertText('±')} style={buttonStyle({ label: '±' })}>±</button>
        <button onClick={() => setPage('more')} style={buttonStyle({ label: 'MORE', accent: page === 'more' ? 'alpha' : undefined })}>MORE</button>
        <button onClick={evaluate} disabled={busy} style={buttonStyle({ label: 'SCAN' })}>{busy ? '...' : 'SCAN'}</button>
      </div>

      <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {keys.map((row, r) => (
          <div key={r} style={{ display: 'grid', gridTemplateColumns: `repeat(${row.length}, 1fr)`, gap: 8 }}>
            {row.map((key) => (
              <button key={`${r}-${key.label}`} onClick={() => insertText(key.insert)} style={buttonStyle(key)}>{key.label}</button>
            ))}
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 10, fontSize: 11 }}>
        <div style={{ background: '#03110b', border: '1px solid #064', borderRadius: 6, padding: 8 }}>
          <div style={{ color: '#8cffb0' }}>Interpreter</div>
          <div>source {receipt(result?.interpreter?.receipt?.source_hash72)}</div>
          <div>stress {receipt(result?.interpreter?.receipt?.stress_hash72)}</div>
          <div>ir {receipt(result?.interpreter?.receipt?.ir_hash72)}</div>
        </div>
        <div style={{ background: solverStatus === 'QUARANTINED' ? '#1c0508' : '#03110b', border: `1px solid ${solverStatus === 'QUARANTINED' ? '#f04' : '#064'}`, borderRadius: 6, padding: 8 }}>
          <div style={{ color: solverStatus === 'QUARANTINED' ? '#ff8a8a' : '#8cffb0' }}>Solver</div>
          <div>status {solverStatus}</div>
          <div>contradictions {contradictionCount}</div>
          <div>manifest {manifestStatus} · phases {Array.isArray(phaseList) ? phaseList.length : 0}</div>
        </div>
      </div>

      {autocorrectionSuggestions.length ? (
        <div style={{ marginTop: 8, background: '#120f04', border: '1px solid #cc9b00', borderRadius: 6, padding: 8, fontSize: 11 }}>
          <div style={{ color: '#ffd35a', fontWeight: 700 }}>Auto-Correction Suggestions</div>
          {autocorrectionSuggestions.slice(0, 4).map((s: any) => (
            <div key={s.suggestion_hash72} style={{ marginTop: 4 }}>
              <b>{s.priority}</b> · {s.kind} · {s.message}
            </div>
          ))}
        </div>
      ) : null}

      {branchFrontier?.branches?.length ? (
        <div style={{ marginTop: 8, background: '#050b14', border: '1px solid #08c', borderRadius: 6, padding: 8, fontSize: 11 }}>
          <div style={{ color: '#72d6ff', fontWeight: 700 }}>Branch Frontier</div>
          {branchFrontier.branches.slice(0, 6).map((b: any) => (
            <div key={b.branch_hash72} style={{ marginTop: 4, color: b.branch_hash72 === branchFrontier.selected_branch_hash72 ? '#ffff66' : '#dff' }}>
              {b.correction_kind} · score {b.total_score} · path [{b.projected_phases?.join(' → ')}]
            </div>
          ))}
        </div>
      ) : null}

      {pythonArtifact?.source ? (
        <div style={{ marginTop: 8, background: '#020806', border: '1px solid #075', borderRadius: 6, padding: 8, fontSize: 11 }}>
          <div style={{ color: '#8cffb0', fontWeight: 700 }}>Transpiler · {pythonArtifact.target} · {receipt(pythonArtifact.source_hash72)}</div>
          <pre style={{ whiteSpace: 'pre-wrap', maxHeight: 150, overflow: 'auto', color: '#cfffff' }}>{pythonArtifact.source}</pre>
        </div>
      ) : null}

      {error && <div style={{ marginTop: 8, color: '#ff8a8a', fontSize: 12 }}>ERROR · {error}</div>}
    </section>
  );
}
