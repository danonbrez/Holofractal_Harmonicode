import React, { FormEvent, useEffect, useMemo, useState } from 'react';
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
type AssistantTurn = {
  ok?: boolean;
  status?: string;
  thread_id?: string;
  error?: string;
  assistant_message?: {
    content?: string;
    message_root_hash72?: string;
    tool_calls?: any[];
  };
  provider_invocation_receipt?: {
    provider_id?: string;
    raw_provider_result?: { model_id?: string; model?: string };
    provider_invocation_receipt_hash72?: string;
  };
  provider_result_ingress?: {
    ok?: boolean;
    status?: string;
    provider_result_ingress_root_hash72?: string;
  };
  thread?: { message_count?: number; message_tip_hash72?: string };
  turn_root_hash72?: string;
};
type AssistantHealth = {
  online?: boolean;
  status?: string;
  model_id?: string;
  provider_id?: string;
  error?: string;
};

function previewFor(input: string): string {
  const s = input.trim();
  if (!s) return 'Start typing to open an HHS AI thread.';
  if (/==|≠|:=|xy|yx|zw|wz|u\^?72|rho|ρ|PLASTIC|CLOSURE|GATE/i.test(s)) return 'HARMONICODE structure detected for the Gemma 4 thread.';
  if (/[+\-*/^()]/.test(s)) return 'Mathematical request detected for the governed assistant.';
  return 'Natural-language request ready for LiteRT-LM and HHS ingress.';
}

function StepList({ steps }: { steps: { label: string; status: StepStatus }[] }) {
  return <div className="hhs-step-list">{steps.map((s) => <div key={s.label} className={`hhs-step ${s.status}`}><span />{s.label}</div>)}</div>;
}

function Suggestion({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return <button className="hhs-suggestion" onClick={onClick}>{children}</button>;
}

function shortHash(value?: string): string {
  return value ? `${value.slice(0, 18)}…` : 'pending';
}

function summarizeTurn(turn: AssistantTurn): AssistantMessage {
  const content = turn.assistant_message?.content?.trim();
  const receipt = turn.provider_invocation_receipt?.provider_invocation_receipt_hash72;
  const ingress = turn.provider_result_ingress?.provider_result_ingress_root_hash72;
  const model = turn.provider_invocation_receipt?.raw_provider_result?.model_id
    ?? turn.provider_invocation_receipt?.raw_provider_result?.model
    ?? 'Gemma 4';

  if (!content) {
    return {
      role: 'assistant',
      text: turn.error
        ? `The LiteRT-LM turn closed without an assistant response: ${turn.error}`
        : `The assistant turn closed with status ${turn.status ?? 'UNKNOWN'}.`,
      hint: `No runtime mutation was admitted · ${shortHash(turn.turn_root_hash72)}`
    };
  }

  return {
    role: 'assistant',
    text: content,
    hint: `${model} · ingress ${turn.provider_result_ingress?.ok ? 'admitted' : 'projected'} · receipt ${shortHash(receipt ?? ingress)}`
  };
}

export default function AssistantWorkspace({ data, activePhase, onActivePhase, onPhaseMapChange }: { data: RuntimeSnapshot; activePhase: number | null; onActivePhase: (phase: number | null) => void; onPhaseMapChange: (items: CalculatorPhaseToken[]) => void }) {
  const [input, setInput] = useState('Explain the current HHS runtime state.');
  const [committed, setCommitted] = useState('HHS AI thread');
  const [depth, setDepth] = useState<Depth>('answer');
  const [busy, setBusy] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [lastTurn, setLastTurn] = useState<AssistantTurn | null>(null);
  const [health, setHealth] = useState<AssistantHealth | null>(null);
  const [steps, setSteps] = useState<{ label: string; status: StepStatus }[]>([
    { label: 'Capture thread message', status: 'idle' },
    { label: 'LiteRT-LM · Gemma 4', status: 'idle' },
    { label: 'HHS provider-result ingress', status: 'idle' }
  ]);
  const [messages, setMessages] = useState<AssistantMessage[]>([
    {
      role: 'assistant',
      text: 'This is the HHS AI thread interface. Messages are processed by local Gemma 4 through LiteRT-LM, then returned through HHS receipt and ingress controls.',
      hint: 'Model output is a governed provider result, never direct VM81 authority.'
    }
  ]);

  useEffect(() => {
    let mounted = true;
    fetch('/api/assistant/health')
      .then(async (res) => {
        const body = await res.json();
        if (!res.ok) throw new Error(body?.detail ?? `health returned ${res.status}`);
        return body;
      })
      .then((body) => { if (mounted) setHealth(body); })
      .catch((err) => {
        if (mounted) setHealth({ online: false, status: 'LITERT_LM_OFFLINE', error: String(err?.message ?? err) });
      });
    return () => { mounted = false; };
  }, []);

  const preview = useMemo(() => previewFor(input), [input]);

  function setStep(label: string, status: StepStatus) {
    setSteps(prev => prev.map(s => s.label === label ? { ...s, status } : s));
  }

  function startNewThread() {
    setThreadId(null);
    setLastTurn(null);
    setCommitted('HHS AI thread');
    setMessages([{
      role: 'assistant',
      text: 'New HHS AI thread opened. The next message will create a fresh Hash72-linked conversation chain.',
      hint: 'No previous thread state will be sent to Gemma 4.'
    }]);
    setSteps(prev => prev.map(s => ({ ...s, status: 'idle' })));
  }

  async function runConversation(message: string) {
    setBusy(true);
    setSteps(prev => prev.map(s => ({ ...s, status: 'idle' })));
    setStep('Capture thread message', 'done');
    setStep('LiteRT-LM · Gemma 4', 'running');
    setMessages(prev => [...prev, { role: 'user', text: message }]);

    try {
      const res = await fetch('/api/assistant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thread_id: threadId,
          project_id: 'project:hhs-mobile-runtime-console',
          title: 'HHS Gemma 4 AI Thread',
          content: message
        })
      });
      const turn: AssistantTurn = await res.json();
      if (!res.ok) throw new Error(JSON.stringify((turn as any)?.detail ?? turn));

      setStep('LiteRT-LM · Gemma 4', turn.assistant_message ? 'done' : 'deferred');
      setStep('HHS provider-result ingress', turn.provider_result_ingress ? 'done' : 'deferred');
      setThreadId(turn.thread_id ?? threadId);
      setLastTurn(turn);
      setCommitted(message);
      setMessages(prev => [...prev, summarizeTurn(turn)]);
      setDepth(turn.assistant_message?.tool_calls?.length ? 'structure' : 'answer');
    } catch (err: any) {
      setStep('LiteRT-LM · Gemma 4', 'deferred');
      setStep('HHS provider-result ingress', 'deferred');
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: 'The assistant transport did not complete. The user message remains visible, but no assistant result or VM81 mutation was fabricated.',
        hint: String(err?.message ?? err)
      }]);
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const message = input.trim();
    if (message) runConversation(message);
  }

  const receipt = lastTurn?.provider_invocation_receipt?.provider_invocation_receipt_hash72
    ?? lastTurn?.provider_result_ingress?.provider_result_ingress_root_hash72
    ?? lastTurn?.turn_root_hash72
    ?? data.transpileReceipt?.receipt_hash72;
  const healthLabel = health?.online
    ? `${health.model_id ?? 'Gemma 4'} online`
    : health?.status ?? 'checking model';

  return (
    <div className="hhs-assistant-shell">
      <section className="hhs-hero-input">
        <div className="hhs-eyebrow">LiteRT-LM · Gemma 4 · HHS</div>
        <h1>Converse with HHS through a receipted AI thread.</h1>
        <form onSubmit={onSubmit} className="hhs-command-form">
          <textarea value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask HHS about runtime state, HARMONICODE, proofs, tools, or repository operations" rows={3} />
          <button type="submit" disabled={busy}>{busy ? 'Thinking…' : 'Send'}</button>
        </form>
        <div className="hhs-preview-row"><span>{preview}</span><span>{healthLabel}</span></div>
        <StepList steps={steps} />
        <div className="hhs-suggestions">
          <Suggestion onClick={() => setInput('Explain the current HHS runtime state.')}>runtime state</Suggestion>
          <Suggestion onClick={() => setInput('Analyze xy≠yx under the active HARMONICODE constraints.')}>xy≠yx</Suggestion>
          <Suggestion onClick={() => setInput('Describe the active VM81, Hash72, and Hash216 authority boundaries.')}>authority map</Suggestion>
          <Suggestion onClick={startNewThread}>new thread</Suggestion>
        </div>
      </section>

      <section className="hhs-chat-card">
        {messages.slice(-12).map((m, i) => <div key={i} className={`hhs-message ${m.role}`}><div>{m.text}</div>{m.hint ? <small>{m.hint}</small> : null}</div>)}
        <div className="hhs-action-row">
          <Suggestion onClick={() => setDepth('structure')}>Show turn envelope</Suggestion>
          <Suggestion onClick={() => setDepth('proof')}>Show HHS proof surfaces</Suggestion>
        </div>
      </section>

      <section className="hhs-result-card">
        <div className="hhs-section-head"><div><div className="hhs-eyebrow">Thread Result</div><h2>{committed}</h2></div><div className="hhs-receipt-pill">{receipt ? shortHash(String(receipt)) : 'no receipt yet'}</div></div>
        <div className="hhs-depth-switch"><button className={depth === 'answer' ? 'active' : ''} onClick={() => setDepth('answer')}>Runtime</button><button className={depth === 'structure' ? 'active' : ''} onClick={() => setDepth('structure')}>Turn</button><button className={depth === 'proof' ? 'active' : ''} onClick={() => setDepth('proof')}>Proof</button></div>
        {depth === 'answer' && <CalculatorPanelV2 equationManifest={data.equationManifest} transpileReceipt={data.transpileReceipt} activePhase={activePhase} onActivePhase={onActivePhase} onPhaseMapChange={onPhaseMapChange} />}
        {depth === 'structure' && <div className="hhs-ide-grid"><OperatorPanel loop={data.operatorLoop} /><ExecutionPanel />{lastTurn ? <pre style={{ whiteSpace: 'pre-wrap', opacity: .78 }}>{JSON.stringify(lastTurn, null, 2)}</pre> : <div>No assistant turn has completed.</div>}</div>}
        {depth === 'proof' && <div className="hhs-ide-grid"><LedgerPanel /><CertificationPanel /><AlertPanel anomalies={data.anomalies} /></div>}
      </section>
    </div>
  );
}
