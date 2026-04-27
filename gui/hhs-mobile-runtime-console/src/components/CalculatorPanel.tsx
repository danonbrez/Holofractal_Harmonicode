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

export default function CalculatorPanel({ equationManifest }: { equationManifest?: any }) {
  const generatedEquation = useMemo(() => readEquation(equationManifest), [equationManifest]);
  const [expression, setExpression] = useState(generatedEquation || 'xy=-1/yx\nyx=-xy\nxy≠yx');
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (generatedEquation && !result) setExpression(generatedEquation);
  }, [generatedEquation]);

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

  const solverStatus = result?.solver?.receipt?.status ?? 'UNRUN';
  const contradictionCount = result?.solver?.contradictions?.length ?? 0;
  const manifestStatus = equationManifest?.manifest?.status ?? 'NO_MANIFEST';
  const phaseList = equationManifest?.manifest?.phases ?? equationManifest?.manifest?.compiler_packet?.phases ?? [];

  return (
    <section style={{ borderTop: '1px solid #063', borderBottom: '1px solid #063', padding: 10, background: '#020806', maxHeight: '36vh', overflow: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
        <div>
          <div style={{ color: '#8cffb0', fontWeight: 700 }}>HARMONICODE Calculator</div>
          <div style={{ fontSize: 11, opacity: 0.75 }}>manifest {manifestStatus} · phases {Array.isArray(phaseList) ? phaseList.length : 0}</div>
        </div>
        <button onClick={evaluate} disabled={busy} style={{ background: '#063', color: '#dff', border: '1px solid #0f6', borderRadius: 6, padding: '6px 10px' }}>
          {busy ? 'Evaluating…' : 'Evaluate'}
        </button>
      </div>

      <textarea
        value={expression}
        onChange={(e) => setExpression(e.target.value)}
        spellCheck={false}
        style={{ width: '100%', minHeight: 118, marginTop: 8, background: '#000', color: '#dff', border: '1px solid #075', borderRadius: 6, padding: 8, fontFamily: 'monospace', fontSize: 12 }}
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 8, fontSize: 11 }}>
        <div style={{ background: '#03110b', border: '1px solid #064', borderRadius: 6, padding: 8 }}>
          <div style={{ color: '#8cffb0' }}>Interpreter</div>
          <div>source {receipt(result?.interpreter?.receipt?.source_hash72)}</div>
          <div>ast {receipt(result?.interpreter?.receipt?.ast_hash72)}</div>
          <div>ir {receipt(result?.interpreter?.receipt?.ir_hash72)}</div>
        </div>
        <div style={{ background: solverStatus === 'QUARANTINED' ? '#1c0508' : '#03110b', border: `1px solid ${solverStatus === 'QUARANTINED' ? '#f04' : '#064'}`, borderRadius: 6, padding: 8 }}>
          <div style={{ color: solverStatus === 'QUARANTINED' ? '#ff8a8a' : '#8cffb0' }}>Solver</div>
          <div>status {solverStatus}</div>
          <div>contradictions {contradictionCount}</div>
          <div>receipt {receipt(result?.solver?.receipt?.receipt_hash72)}</div>
        </div>
      </div>

      {error && <div style={{ marginTop: 8, color: '#ff8a8a', fontSize: 12 }}>ERROR · {error}</div>}
      {result?.solver?.contradictions?.length ? (
        <div style={{ marginTop: 8, background: '#180509', border: '1px solid #f04', borderRadius: 6, padding: 8, fontSize: 11 }}>
          <div style={{ color: '#ff8a8a' }}>Contradictions</div>
          {result.solver.contradictions.slice(0, 4).map((c: any) => (
            <div key={c.contradiction_hash72}>{c.kind}: {c.left} ↔ {c.right}</div>
          ))}
        </div>
      ) : null}
    </section>
  );
}
