import React, { FormEvent, useMemo, useState } from 'react';
import CalculatorPanelV2 from './CalculatorPanelV2';
import OperatorPanel from './OperatorPanel';
import ExecutionPanel from './ExecutionPanel';
import LedgerPanel from './LedgerPanel';
import CertificationPanel from './CertificationPanel';
import AlertPanel from './AlertPanel';
import { RuntimeSnapshot } from '../runtimeData';
import { CalculatorPhaseToken } from '../App';

type Depth = 'answer' | 'structure' | 'proof';

type AssistantMessage = {
  role: 'user' | 'assistant';
  text: string;
  hint?: string;
};

function summarizeEvaluation(expression: string, payload: any): AssistantMessage {
  const status = payload?.interpreter?.receipt?.status ?? 'IR_EMITTED';
  const nodes = payload?.interpreter?.graph?.nodes?.length ?? 0;
  const edges = payload?.interpreter?.graph?.edges?.length ?? 0;
  const resultHash = payload?.result_hash72 ?? payload?.interpreter?.receipt?.receipt_hash72 ?? 'pending';
  const solved = payload?.solver?.status ?? payload?.solver?.receipt?.status ?? 'checked';
  return {
    role: 'assistant',
    text: status === 'QUARANTINED'
      ? 'I found a structural issue. I kept the run contained and prepared corrections.'
      : `I read this as a structured expression and built the execution path.`,
    hint: `${solved} · ${nodes} nodes · ${edges} links · ${String(resultHash).slice(0, 18)}…`
  };
}

function Suggestion({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return <button className="hhs-suggestion" onClick={onClick}>{children}</button>;
}

export default function AssistantWorkspace({
  data,
  activePhase,
  onActivePhase,
  onPhaseMapChange
}: {
  data: RuntimeSnapshot;
  activePhase: number | null;
  onActivePhase: (phase: number | null) => void;
  onPhaseMapChange: (items: CalculatorPhaseToken[]) => void;
}) {
  const [input, setInput] = useState('x + y');
  const [committed, setCommitted] = useState('x + y');
  const [depth, setDepth] = useState<Depth>('answer');
  const [busy, setBusy] = useState(false);
  const [lastEvaluation, setLastEvaluation] = useState<any>(null);
  const [messages, setMessages] = useState<AssistantMessage[]>([
    { role: 'assistant', text: 'Give me an equation, symbolic relation, or plain English instruction. I’ll turn it into a runnable structure.', hint: 'Live preview while typing. Enter commits and verifies.' }
  ]);

  const preview = useMemo(() => {
    const trimmed = input.trim();
    if (!trimmed) return 'Start typing to preview structure.';
    if (/==|≠|:=|xy|yx|u\^?72|rho|ρ/.test(trimmed)) return 'Symbolic structure detected.';
    if (/[+\-*/^()]/.test(trimmed)) return 'Calculator expression detected.';
    return 'Instruction detected. I’ll translate it into a tool action.';
  }, [input]);

  async function evaluateExpression(expression: string) {
    setBusy(true);
    try {
      const res = await fetch('/api/calculator/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression })
      });
      const payload = await res.json();
      setLastEvaluation(payload);
      setMessages(prev => [...prev, { role: 'user', text: expression }, summarizeEvaluation(expression, payload)]);
      setCommitted(expression);
      setDepth('answer');
    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'user', text: expression }, { role: 'assistant', text: 'The local tool call failed. I kept the state unchanged.', hint: String(err?.message ?? err) }]);
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const expression = input.trim();
    if (expression) evaluateExpression(expression);
  }

  const receipt = lastEvaluation?.result_hash72 ?? lastEvaluation?.interpreter?.receipt?.receipt_hash72 ?? data.transpileReceipt?.receipt_hash72;

  return (
    <div className="hhs-assistant-shell">
      <section className="hhs-hero-input">
        <div className="hhs-eyebrow">HARMONICODE Assistant</div>
        <h1>Ask it. Run it. Open the proof when you need it.</h1>
        <form onSubmit={onSubmit} className="hhs-command-form">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Try: x + y, xy≠yx, or explain this relation"
            rows={3}
          />
          <button type="submit" disabled={busy}>{busy ? 'Running…' : 'Run'}</button>
        </form>
        <div className="hhs-preview-row">
          <span>{preview}</span>
          <span>{busy ? 'working' : 'ready'}</span>
        </div>
        <div className="hhs-suggestions">
          <Suggestion onClick={() => setInput('x + y')}>x + y</Suggestion>
          <Suggestion onClick={() => setInput('xy≠yx')}>xy≠yx</Suggestion>
          <Suggestion onClick={() => setInput('PLASTIC_EIGENSTATE_CLOSURE_GATE')}>closure gate</Suggestion>
        </div>
      </section>

      <section className="hhs-chat-card">
        {messages.slice(-5).map((m, i) => <div key={i} className={`hhs-message ${m.role}`}><div>{m.text}</div>{m.hint ? <small>{m.hint}</small> : null}</div>)}
      </section>

      <section className="hhs-result-card">
        <div className="hhs-section-head">
          <div><div className="hhs-eyebrow">Result</div><h2>{committed}</h2></div>
          <div className="hhs-receipt-pill">{receipt ? String(receipt).slice(0, 18) + '…' : 'no receipt yet'}</div>
        </div>
        <div className="hhs-depth-switch">
          <button className={depth === 'answer' ? 'active' : ''} onClick={() => setDepth('answer')}>Answer</button>
          <button className={depth === 'structure' ? 'active' : ''} onClick={() => setDepth('structure')}>Structure</button>
          <button className={depth === 'proof' ? 'active' : ''} onClick={() => setDepth('proof')}>Proof</button>
        </div>
        {depth === 'answer' && <CalculatorPanelV2 equationManifest={data.equationManifest} transpileReceipt={data.transpileReceipt} activePhase={activePhase} onActivePhase={onActivePhase} onPhaseMapChange={onPhaseMapChange} />}
        {depth === 'structure' && <div className="hhs-ide-grid"><OperatorPanel loop={data.operatorLoop} /><ExecutionPanel /></div>}
        {depth === 'proof' && <div className="hhs-ide-grid"><LedgerPanel /><CertificationPanel /><AlertPanel anomalies={data.anomalies} /></div>}
      </section>
    </div>
  );
}
