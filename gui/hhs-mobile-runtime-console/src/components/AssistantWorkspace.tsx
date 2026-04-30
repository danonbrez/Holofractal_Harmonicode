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

type AssistantMessage = { role: 'user' | 'assistant'; text: string; hint?: string; };
type AssistantAction = { label: string; kind: 'depth' | 'input' | 'tool'; value: string; };

type ContinuationResult = {
  convergence?: any;
  patchPlan?: any;
  continuation_hash72?: string;
  completed: boolean;
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

function isUnresolved(payload: any): boolean {
  const status = payload?.interpreter?.receipt?.status ?? 'IR_EMITTED';
  const solved = payload?.solver?.status ?? payload?.solver?.receipt?.status ?? 'checked';
  return status === 'QUARANTINED' || String(solved).toUpperCase().includes('UNRESOLVED') || Boolean(payload?.autocorrections?.suggestions?.length) || Boolean(payload?.correctionBranchFrontier?.branches?.length);
}

function summarizeEvaluation(payload: any, continuation?: ContinuationResult): AssistantMessage {
  const nodes = payload?.interpreter?.graph?.nodes?.length ?? 0;
  const edges = payload?.interpreter?.graph?.edges?.length ?? 0;
  const resultHash = continuation?.continuation_hash72 ?? payload?.result_hash72 ?? payload?.interpreter?.receipt?.receipt_hash72 ?? 'pending';
  const solved = payload?.solver?.status ?? payload?.solver?.receipt?.status ?? 'checked';
  const unresolved = isUnresolved(payload);
  return {
    role: 'assistant',
    text: unresolved
      ? (continuation?.completed ? 'This began as an unresolved constraint state, so I continued it through downstream solving and preserved the refinement path.' : 'This produced an unresolved constraint state. I preserved it for downstream solving instead of collapsing it early.')
      : 'I built the runnable structure and completed the first solving pass.',
    hint: `${solved} · ${nodes} nodes · ${edges} links · ${String(resultHash).slice(0, 18)}…`
  };
}

function actionsFor(intent: IntentKind, payload: any, continuation?: ContinuationResult): AssistantAction[] {
  const actions: AssistantAction[] = [];
  actions.push({ label: 'Show structure', kind: 'depth', value: 'structure' });
  actions.push({ label: 'Show proof', kind: 'depth', value: 'proof' });
  if (intent === 'math') actions.push({ label: 'Try symbolic form', kind: 'input', value: 'xy≠yx' });
  if (intent === 'symbolic' || intent === 'closure') actions.push({ label: continuation?.completed ? 'Refinement path' : 'Continue solving', kind: 'depth', value: 'structure' });
  if (payload?.correctionBranchFrontier?.branches?.length || payload?.autocorrections?.suggestions?.length || continuation?.patchPlan) actions.push({ label: 'Review refinements', kind: 'depth', value: 'structure' });
  actions.push({ label: 'Open receipt', kind: 'depth', value: 'proof' });
  return actions.slice(0, 5);
}

function Suggestion({ children, onClick }: { children: React.ReactNode; onClick: () => void }) { return <button className="hhs-suggestion" onClick={onClick}>{children}</button>; }
function StepList({ steps }: { steps: { label: string; status: StepStatus }[] }) { return <div className="hhs-step-list">{steps.map((s) => <div key={s.label} className={`hhs-step ${s.status}`}><span />{s.label}</div>)}</div>; }

export default function AssistantWorkspace({ data, activePhase, onActivePhase, onPhaseMapChange }: { data: RuntimeSnapshot; activePhase: number | null; onActivePhase: (phase: number | null) => void; onPhaseMapChange: (items: CalculatorPhaseToken[]) => void; }) {
  const [input, setInput] = useState('x + y');
  const [committed, setCommitted] = useState('x + y');
  const [depth, setDepth] = useState<Depth>('answer');
  const [busy, setBusy] = useState(false);
  const [autoContinue, setAutoContinue] = useState(true);
  const [lastEvaluation, setLastEvaluation] = useState<any>(null);
  const [lastContinuation, setLastContinuation] = useState<ContinuationResult | null>(null);
  const [actions, setActions] = useState<AssistantAction[]>([]);
  const [steps, setSteps] = useState<{ label: string; status: StepStatus }[]>([
    { label: 'Preview intent', status: 'idle' },
    { label: 'Run local tools', status: 'idle' },
    { label: 'Build structure', status: 'idle' },
    { label: 'Downstream solve', status: 'idle' },
    { label: 'Attach receipt', status: 'idle' }
  ]);
  const [messages, setMessages] = useState<AssistantMessage[]>([
    { role: 'assistant', text: 'Tell me what to calculate, build, prove, or explore. I’ll use the local tools, preserve unresolved states, and continue downstream when useful.', hint: 'Live preview while typing. Enter commits and verifies.' }
  ]);

  const intent = useMemo(() => classifyIntent(input), [input]);
  const preview = useMemo(() => input.trim() ? intentPreview(intent) : 'Start typing to preview structure.', [input, intent]);

  function setStep(label: string, status: StepStatus) { setSteps(prev => prev.map(s => s.label === label ? { ...s, status } : s)); }

  async function postJSON(path: string, body: any) {
    const res = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (!res.ok) throw new Error(`${path} returned ${res.status}`);
    return await res.json();
  }

  function itemsFromEvaluation(payload: any): any[] {
    const graphNodes = payload?.interpreter?.graph?.nodes ?? [];
    const graphEdges = payload?.interpreter?.graph?.edges ?? [];
    return [
      ...graphNodes.map((node: string, index: number) => ({ id: `node-${index}`, text: node, kind: 'GRAPH_NODE', phaseIndex: index % 72 })),
      ...graphEdges.map((edge: any, index: number) => ({ id: `edge-${index}`, text: `${edge.source ?? ''}→${edge.target ?? ''}`, kind: edge.type ?? 'GRAPH_EDGE', phaseIndex: (index + 9) % 72 }))
    ];
  }

  async function continueDownstream(expression: string, payload: any): Promise<ContinuationResult> {
    setStep('Downstream solve', 'running');
    const items = itemsFromEvaluation(payload);
    const influences = (payload?.correctionBranchFrontier?.branches ?? payload?.autocorrections?.suggestions ?? []).slice(0, 8);
    const convergence = await postJSON('/api/agent/convergence-packet', { expression, items, influences });
    const patchPlan = await postJSON('/api/agent/plan-patch', { expression, items, influences });
    setStep('Downstream solve', 'done');
    return { convergence, patchPlan, continuation_hash72: patchPlan?.patch?.patch_hash72 ?? convergence?.packet_hash72 ?? convergence?.convergence_hash72, completed: true };
  }

  async function evaluateExpression(expression: string) {
    const detected = classifyIntent(expression);
    setBusy(true);
    setActions([]);
    setLastContinuation(null);
    setSteps(prev => prev.map(s => ({ ...s, status: 'idle' })));
    setStep('Preview intent', 'done');
    setStep('Run local tools', 'running');
    try {
      const payload = await postJSON('/api/calculator/evaluate', { expression });
      setStep('Run local tools', 'done');
      setStep('Build structure', 'done');
      let continuation: ContinuationResult | undefined;
      if (autoContinue && isUnresolved(payload)) continuation = await continueDownstream(expression, payload);
      else setStep('Downstream solve', isUnresolved(payload) ? 'deferred' : 'done');
      setStep('Attach receipt', 'done');
      setLastEvaluation(payload);
      setLastContinuation(continuation ?? null);
      setMessages(prev => [...prev, { role: 'user', text: expression }, summarizeEvaluation(payload, continuation)]);
      setActions(actionsFor(detected, payload, continuation));
      setCommitted(expression);
      setDepth(detected === 'symbolic' || detected === 'closure' || continuation?.completed ? 'structure' : 'answer');
    } catch (err: any) {
      setStep('Run local tools', 'deferred');
      setStep('Downstream solve', 'deferred');
      setMessages(prev => [...prev, { role: 'user', text: expression }, { role: 'assistant', text: 'The local tool route did not complete. I preserved the input unchanged so the next solver path can continue from the same state.', hint: String(err?.message ?? err) }]);
    } finally { setBusy(false); }
  }

  function runAction(action: AssistantAction) { if (action.kind === 'depth') setDepth(action.value as Depth); if (action.kind === 'input') setInput(action.value); }
  function onSubmit(e: FormEvent) { e.preventDefault(); const expression = input.trim(); if (expression) evaluateExpression(expression); }

  const receipt = lastContinuation?.continuation_hash72 ?? lastEvaluation?.result_hash72 ?? lastEvaluation?.interpreter?.receipt?.receipt_hash72 ?? data.transpileReceipt?.receipt_hash72;

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
        {actions.length ? <div className="hhs-action-row">{actions.map((a) => <Suggestion key={`${a.label}-${a.value}`} onClick={() => runAction(a)}>{a.label}</Suggestion>)}</div> : null}
      </section>

      <section className="hhs-result-card">
        <div className="hhs-section-head"><div><div className="hhs-eyebrow">Result</div><h2>{committed}</h2></div><div className="hhs-receipt-pill">{receipt ? String(receipt).slice(0, 18) + '…' : 'no receipt yet'}</div></div>
        <div className="hhs-depth-switch"><button className={depth === 'answer' ? 'active' : ''} onClick={() => setDepth('answer')}>Answer</button><button className={depth === 'structure' ? 'active' : ''} onClick={() => setDepth('structure')}>Structure</button><button className={depth === 'proof' ? 'active' : ''} onClick={() => setDepth('proof')}>Proof</button></div>
        {depth === 'answer' && <CalculatorPanelV2 equationManifest={data.equationManifest} transpileReceipt={data.transpileReceipt} activePhase={activePhase} onActivePhase={onActivePhase} onPhaseMapChange={onPhaseMapChange} />}
        {depth === 'structure' && <div className="hhs-ide-grid"><OperatorPanel loop={data.operatorLoop} /><ExecutionPanel />{lastContinuation ? <pre style={{ whiteSpace: 'pre-wrap', opacity: .78 }}>{JSON.stringify(lastContinuation, null, 2)}</pre> : null}</div>}
        {depth === 'proof' && <div className="hhs-ide-grid"><LedgerPanel /><CertificationPanel /><AlertPanel anomalies={data.anomalies} /></div>}
      </section>
    </div>
  );
}
