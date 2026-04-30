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
type StepStatus = 'idle' | 'running' | 'done' | 'deferred';
type AssistantMessage = { role: 'user' | 'assistant'; text: string; hint?: string };
type AgentRun = { status?: string; expression?: string; unresolved?: boolean; passes?: any[]; run_hash72?: string; receipt_hash72?: string };

function previewFor(input: string): string {
  const s = input.trim();
  if (!s) return 'Start typing to preview structure.';
  if (/==|≠|:=|xy|yx|zw|wz|u\^?72|rho|ρ|PLASTIC|CLOSURE|GATE/i.test(s)) return 'Symbolic structure detected.';
  if (/[+\-*/^()]/.test(s)) return 'Calculator expression detected.';
  return 'Instruction detected. I’ll route it through the local runtime.';
}

function StepList({ steps }: { steps: { label: string; status: StepStatus }[] }) {
  return <div className="hhs-step-list">{steps.map((s) => <div key={s.label} className={`hhs-step ${s.status}`}><span />{s.label}</div>)}</div>;
}

function Suggestion({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return <button className="hhs-suggestion" onClick={onClick}>{children}</button>;
}

function summarizeRun(run: AgentRun): AssistantMessage {
  const passes = run.passes ?? [];
  const evalPass = passes.find((p: any) => p.kind === 'calculator-evaluate')?.payload;
  const nodes = evalPass?.interpreter?.graph?.nodes?.length ?? 0;
  const edges = evalPass?.interpreter?.graph?.edges?.length ?? 0;
  const receipt = run.receipt_hash72 ?? run.run_hash72 ?? 'pending';
  return {
    role: 'assistant',
    text: run.unresolved
      ? `This stayed open as a constraint state and was routed through ${passes.length} runtime pass${passes.length === 1 ? '' : 'es'}.`
      : `Completed ${passes.length} runtime pass${passes.length === 1 ? '' : 'es'}.`,
    hint: `${nodes} nodes · ${edges} links · ${String(receipt).slice(0, 18)}…`
  };
}

export default function AssistantWorkspace({ data, activePhase, onActivePhase, onPhaseMapChange }: { data: RuntimeSnapshot; activePhase: number | null; onActivePhase: (phase: number | null) => void; onPhaseMapChange: (items: CalculatorPhaseToken[]) => void }) {
  const [input, setInput] = useState('x + y');
  const [committed, setCommitted] = useState('x + y');
  const [depth, setDepth] = useState<Depth>('answer');
  const [busy, setBusy] = useState(false);
  const [autoContinue, setAutoContinue] = useState(true);
  const [lastRun, setLastRun] = useState<AgentRun | null>(null);
  const [steps, setSteps] = useState<{ label: string; status: StepStatus }[]>([
    { label: 'Preview intent', status: 'idle' },
    { label: 'Runtime route', status: 'idle' },
    { label: 'Attach receipt', status: 'idle' }
  ]);
  const [messages, setMessages] = useState<AssistantMessage[]>([
    { role: 'assistant', text: 'Tell me what to calculate, build, prove, or explore. I’ll send it through the local runtime and keep the proof available.', hint: 'The interface collects input and displays receipts.' }
  ]);

  const preview = useMemo(() => previewFor(input), [input]);

  function setStep(label: string, status: StepStatus) {
    setSteps(prev => prev.map(s => s.label === label ? { ...s, status } : s));
  }

  async function runExpression(expression: string) {
    setBusy(true);
    setSteps(prev => prev.map(s => ({ ...s, status: 'idle' })));
    setStep('Preview intent', 'done');
    setStep('Runtime route', 'running');
    try {
      const res = await fetch('/api/agent/run-loop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression, auto_continue: autoContinue, max_passes: 1 })
      });
      if (!res.ok) throw new Error(`/api/agent/run-loop returned ${res.status}`);
      const run = await res.json();
      setStep('Runtime route', 'done');
      setStep('Attach receipt', 'done');
      setLastRun(run);
      setCommitted(expression);
      setMessages(prev => [...prev, { role: 'user', text: expression }, summarizeRun(run)]);
      setDepth(run.unresolved ? 'structure' : 'answer');
    } catch (err: any) {
      setStep('Runtime route', 'deferred');
      setMessages(prev => [...prev, { role: 'user', text: expression }, { role: 'assistant', text: 'The runtime route did not complete. The input was preserved unchanged for the next run.', hint: String(err?.message ?? err) }]);
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const expression = input.trim();
    if (expression) runExpression(expression);
  }

  const receipt = lastRun?.receipt_hash72 ?? lastRun?.run_hash72 ?? data.transpileReceipt?.receipt_hash72;

  return (
    <div className="hhs-assistant-shell">
      <section className="hhs-hero-input">
        <div className="hhs-eyebrow">Local Agent Workspace</div>
        <h1>Ask it. Run it. Open the proof when you need it.</h1>
        <form onSubmit={onSubmit} className="hhs-command-form">
          <textarea value={input} onChange={(e) => setInput(e.target.value)} placeholder="Try: x + y, xy≠yx, or explain this relation" rows={3} />
          <button type="submit" disabled={busy}>{busy ? 'Running…' : 'Run'}</button>
        </form>
        <div className="hhs-preview-row"><span>{preview}</span><span>{busy ? 'working' : 'ready'}</span></div>
        <StepList steps={steps} />
        <div className="hhs-suggestions">
          <Suggestion onClick={() => setInput('x + y')}>x + y</Suggestion>
          <Suggestion onClick={() => setInput('xy≠yx')}>xy≠yx</Suggestion>
          <Suggestion onClick={() => setInput('PLASTIC_EIGENSTATE_CLOSURE_GATE')}>closure gate</Suggestion>
          <Suggestion onClick={() => setAutoContinue(!autoContinue)}>{autoContinue ? 'Auto-solve on' : 'Auto-solve off'}</Suggestion>
        </div>
      </section>

      <section className="hhs-chat-card">
        {messages.slice(-5).map((m, i) => <div key={i} className={`hhs-message ${m.role}`}><div>{m.text}</div>{m.hint ? <small>{m.hint}</small> : null}</div>)}
        <div className="hhs-action-row">
          <Suggestion onClick={() => setDepth('structure')}>Show structure</Suggestion>
          <Suggestion onClick={() => setDepth('proof')}>Show proof</Suggestion>
        </div>
      </section>

      <section className="hhs-result-card">
        <div className="hhs-section-head"><div><div className="hhs-eyebrow">Result</div><h2>{committed}</h2></div><div className="hhs-receipt-pill">{receipt ? String(receipt).slice(0, 18) + '…' : 'no receipt yet'}</div></div>
        <div className="hhs-depth-switch"><button className={depth === 'answer' ? 'active' : ''} onClick={() => setDepth('answer')}>Answer</button><button className={depth === 'structure' ? 'active' : ''} onClick={() => setDepth('structure')}>Structure</button><button className={depth === 'proof' ? 'active' : ''} onClick={() => setDepth('proof')}>Proof</button></div>
        {depth === 'answer' && <CalculatorPanelV2 equationManifest={data.equationManifest} transpileReceipt={data.transpileReceipt} activePhase={activePhase} onActivePhase={onActivePhase} onPhaseMapChange={onPhaseMapChange} />}
        {depth === 'structure' && <div className="hhs-ide-grid"><OperatorPanel loop={data.operatorLoop} /><ExecutionPanel />{lastRun ? <pre style={{ whiteSpace: 'pre-wrap', opacity: .78 }}>{JSON.stringify(lastRun, null, 2)}</pre> : null}</div>}
        {depth === 'proof' && <div className="hhs-ide-grid"><LedgerPanel /><CertificationPanel /><AlertPanel anomalies={data.anomalies} /></div>}
      </section>
    </div>
  );
}
