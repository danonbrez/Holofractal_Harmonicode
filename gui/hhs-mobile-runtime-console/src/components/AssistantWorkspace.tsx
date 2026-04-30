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
type IntentKind = 'math' | 'symbolic' | 'instruction' | 'relation' | 'closure';
type StepStatus = 'idle' | 'running' | 'done' | 'deferred';

type AssistantMessage = {
  role: 'user' | 'assistant';
  text: string;
  hint?: string;
};

type AssistantAction = {
  label: string;
  kind: 'depth' | 'input' | 'tool';
  value: string;
};

function classifyIntent(input: string): IntentKind {
  const s = input.trim();
  if (/PLASTIC|CLOSURE|GATE|Ω|omega/i.test(s)) return 'closure';
  if (/==|≠|:=|xy|yx|zw|wz|u\^?72|rho|ρ/.test(s)) return 'symbolic';
  if (/\b(combine|explain|show|build|map|prove|verify|simulate|transpile)\b/i.test(s)) return 'instruction';
  if (/[A-Za-z]+\s*[=<>≠]/.test(s)) return 'relation';
  if (/[+\-*/^()]/.test(s)) return 'math';
  return 'instruction';
}

function intentPreview(intent: IntentKind): string {
  if (intent === 'math') return 'Calculator expression detected.';
  if (intent === 'symbolic') return 'Symbolic structure detected.';
  if (intent === 'closure') return 'Closure gate detected.';
  if (intent === 'relation') return 'Relation detected.';
  return 'Instruction detected. I’ll translate it into a tool action.';
}

function summarizeEvaluation(expression: string, payload: any): AssistantMessage {
  const status = payload?.interpreter?.receipt?.status ?? 'IR_EMITTED';
  const nodes = payload?.interpreter?.graph?.nodes?.length ?? 0;
  const edges = payload?.interpreter?.graph?.edges?.length ?? 0;
  const resultHash = payload?.result_hash72 ?? payload?.interpreter?.receipt?.receipt_hash72 ?? 'pending';
  const solved = payload?.solver?.status ?? payload?.solver?.receipt?.status ?? 'checked';
  const unresolved = status === 'QUARANTINED' || String(solved).toUpperCase().includes('UNRESOLVED');
  return {
    role: 'assistant',
    text: unresolved
      ? 'This produced an unresolved constraint state. I preserved it for downstream solving instead of collapsing it early.'
      : 'I built the runnable structure and completed the first solving pass.',
    hint: `${solved} · ${nodes} nodes · ${edges} links · ${String(resultHash).slice(0, 18)}…`
  };
}

function actionsFor(intent: IntentKind, payload: any): AssistantAction[] {
  const actions: AssistantAction[] = [];
  actions.push({ label: 'Show structure', kind: 'depth', value: 'structure' });
  actions.push({ label: 'Show proof', kind: 'depth', value: 'proof' });
  if (intent === 'math') actions.push({ label: 'Try symbolic form', kind: 'input', value: 'xy≠yx' });
  if (intent === 'symbolic' || intent === 'closure') actions.push({ label: 'Continue solving', kind: 'input', value: 'PLASTIC_EIGENSTATE_CLOSURE_GATE' });
  if (payload?.correctionBranchFrontier?.branches?.length || payload?.autocorrections?.suggestions?.length) {
    actions.push({ label: 'Review refinements', kind: 'depth', value: 'structure' });
  }
  actions.push({ label: 'Open receipt', kind: 'depth', value: 'proof' });
  return actions.slice(0, 5);
}

function Suggestion({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return <button className="hhs-suggestion" onClick={onClick}>{children}</button>;
}

function StepList({ steps }: { steps: { label: string; status: StepStatus }[] }) {
  return <div className="hhs-step-list">{steps.map((s) => <div key={s.label} className={`hhs-step ${s.status}`}><span />{s.label}</div>)}</div>;
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
  const [actions, setActions] = useState<AssistantAction[]>([]);
  const [steps, setSteps] = useState<{ label: string; status: StepStatus }[]>([
    { label: 'Preview intent', status: 'idle' },
    { label: 'Run local tools', status: 'idle' },
    { label: 'Build structure', status: 'idle' },
    { label: 'Attach receipt', status: 'idle' }
  ]);
  const [messages, setMessages] = useState<AssistantMessage[]>([
    { role: 'assistant', text: 'Tell me what to calculate, build, prove, or explore. I’ll use the local tools, preserve unresolved states, and keep the proof available.', hint: 'Live preview while typing. Enter commits and verifies.' }
  ]);

  const intent = useMemo(() => classifyIntent(input), [input]);
  const preview = useMemo(() => input.trim() ? intentPreview(intent) : 'Start typing to preview structure.', [input, intent]);

  function setStep(label: string, status: StepStatus) {
    setSteps(prev => prev.map(s => s.label === label ? { ...s, status } : s));
  }

  async function evaluateExpression(expression: string) {
    const detected = classifyIntent(expression);
    setBusy(true);
    setActions([]);
    setSteps(prev => prev.map(s => ({ ...s, status: 'idle' })));
    setStep('Preview intent', 'done');
    setStep('Run local tools', 'running');
    try {
      const res = await fetch('/api/calculator/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression })
      });
      const payload = await res.json();
      setStep('Run local tools', 'done');
      setStep('Build structure', 'done');
      setStep('Attach receipt', 'done');
      setLastEvaluation(payload);
      setMessages(prev => [...prev, { role: 'user', text: expression }, summarizeEvaluation(expression, payload)]);
      setActions(actionsFor(detected, payload));
      setCommitted(expression);
      setDepth(detected === 'symbolic' || detected === 'closure' ? 'structure' : 'answer');
    } catch (err: any) {
      setStep('Run local tools', 'deferred');
      setMessages(prev => [...prev, { role: 'user', text: expression }, { role: 'assistant', text: 'The local tool route did not complete. I preserved the input unchanged so the next solver path can continue from the same state.', hint: String(err?.message ?? err) }]);
    } finally {
      setBusy(false);
    }
  }

  function runAction(action: AssistantAction) {
    if (action.kind === 'depth') setDepth(action.value as Depth);
    if (action.kind === 'input') setInput(action.value);
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
        <div className="hhs-eyebrow">Local Agent Workspace</div>
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
        <StepList steps={steps} />
        <div className="hhs-suggestions">
          <Suggestion onClick={() => setInput('x + y')}>x + y</Suggestion>
          <Suggestion onClick={() => setInput('xy≠yx')}>xy≠yx</Suggestion>
          <Suggestion onClick={() => setInput('PLASTIC_EIGENSTATE_CLOSURE_GATE')}>closure gate</Suggestion>
        </div>
      </section>

      <section className="hhs-chat-card">
        {messages.slice(-5).map((m, i) => <div key={i} className={`hhs-message ${m.role}`}><div>{m.text}</div>{m.hint ? <small>{m.hint}</small> : null}</div>)}
        {actions.length ? <div className="hhs-action-row">{actions.map((a) => <Suggestion key={`${a.label}-${a.value}`} onClick={() => runAction(a)}>{a.label}</Suggestion>)}</div> : null}
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
