import React, { useEffect, useMemo, useState } from "react"
type Json = Record<string, any>
const rec = (v: unknown): Json => v && typeof v === "object" ? v as Json : {}
const txt = (v: unknown, fallback = "—"): string => typeof v === "string" && v ? v : fallback
async function request(path: string, init?: RequestInit): Promise<Json> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 20000)
  try {
    const response = await fetch(path, {
      ...init,
      signal: controller.signal,
      headers: { accept: "application/json", ...(init?.body ? { "content-type": "application/json" } : {}), ...(init?.headers ?? {}) },
    })
    const body = rec(await response.json())
    if (!response.ok) {
      const detail = rec(body.detail)
      throw new Error(txt(detail.message ?? detail.status ?? body.status, response.statusText))
    }
    return body
  } finally { window.clearTimeout(timeout) }
}
export const Pass184RuntimePackagePanel: React.FC = () => {
  const [profile,setProfile]=useState("full")
  const [installName,setInstallName]=useState("hhs-runtime")
  const [host,setHost]=useState("0.0.0.0")
  const [port,setPort]=useState("8080")
  const [status,setStatus]=useState<Json|null>(null)
  const [result,setResult]=useState<Json|null>(null)
  const [busy,setBusy]=useState<string|null>("status")
  const [error,setError]=useState<string|null>(null)
  const profiles=useMemo(()=>Object.keys(rec(status?.profiles)).sort(),[status])
  const refresh=async()=>{setBusy("status");setError(null);try{const next=await request("/api/v1/pass184/status");setStatus(next);setResult((current)=>current??next)}catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setBusy(null)}}
  useEffect(()=>{void refresh()},[])
  const payload=()=>({profile,install_name:installName,host,port:Number(port)})
  const run=async(name:string,task:()=>Promise<Json>)=>{if(busy)return;setBusy(name);setError(null);try{setResult(await task())}catch(reason){setError(reason instanceof Error?reason.message:String(reason))}finally{setBusy(null)}}
  const components=Array.isArray(result?.components)?result?.components.map(String):Array.isArray(rec(result?.plan).components)?rec(result?.plan).components.map(String):[]
  const env=rec(status?.environment)
  return <section data-testid="pass184-runtime-package-panel" className="grid gap-3 xl:grid-cols-[360px_minmax(0,1fr)]">
    <aside className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-4">
      <div className="flex items-start justify-between gap-3"><div><h2 className="text-sm font-semibold text-cyan-200">Portable Runtime Package</h2><p className="mt-1 text-[10px] leading-4 text-neutral-500">Build and verify a foreground-supervised Runtime OS package without creating a second VM81 authority.</p></div><button type="button" onClick={()=>void refresh()} className="runtime-button min-h-9 px-3 text-xs">Refresh</button></div>
      <div className="mt-4 space-y-3">
        <label className="block text-[10px] text-neutral-500">Profile<select data-testid="pass184-profile" value={profile} onChange={e=>setProfile(e.target.value)} className="mt-1 min-h-10 w-full rounded-lg border border-neutral-700 bg-black px-3 text-sm">{(profiles.length?profiles:["full"]).map(x=><option key={x}>{x}</option>)}</select></label>
        <label className="block text-[10px] text-neutral-500">Install name<input data-testid="pass184-install-name" value={installName} onChange={e=>setInstallName(e.target.value)} className="mt-1 min-h-10 w-full rounded-lg border border-neutral-700 bg-black px-3 text-sm"/></label>
        <div className="grid grid-cols-[minmax(0,1fr)_110px] gap-2">
          <label className="block text-[10px] text-neutral-500">Host<input data-testid="pass184-host" value={host} onChange={e=>setHost(e.target.value)} className="mt-1 min-h-10 w-full rounded-lg border border-neutral-700 bg-black px-3 text-sm"/></label>
          <label className="block text-[10px] text-neutral-500">Port<input data-testid="pass184-port" inputMode="numeric" value={port} onChange={e=>setPort(e.target.value.replace(/[^0-9]/g,""))} className="mt-1 min-h-10 w-full rounded-lg border border-neutral-700 bg-black px-3 text-sm"/></label>
        </div>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2">
        <button data-testid="pass184-plan" disabled={Boolean(busy)} onClick={()=>void run("plan",()=>request("/api/v1/pass184/plan",{method:"POST",body:JSON.stringify(payload())}))} className="runtime-button min-h-10 text-xs">Plan</button>
        <button data-testid="pass184-build" disabled={Boolean(busy)} onClick={()=>void run("build",()=>request("/api/v1/pass184/package",{method:"POST",body:JSON.stringify({...payload(),clean:true})}))} className="runtime-button min-h-10 text-xs">Build + verify</button>
        <button data-testid="pass184-verify" disabled={Boolean(busy)} onClick={()=>void run("verify",()=>request("/api/v1/pass184/verify",{method:"POST",body:JSON.stringify({install_name:installName})}))} className="runtime-button min-h-10 text-xs">Verify package</button>
        <button data-testid="pass184-probe" disabled={Boolean(busy)} onClick={()=>void run("probe",()=>request("/api/v1/pass184/probe",{method:"POST",body:JSON.stringify({host,port:Number(port),health_path:"/health",timeout:2})}))} className="runtime-button min-h-10 text-xs">Probe service</button>
      </div>
      {error?<p data-testid="pass184-error" className="mt-3 rounded-lg border border-red-900 bg-red-950/30 p-3 text-xs text-red-200">{error}</p>:null}
      {busy?<p className="mt-3 text-[10px] text-cyan-300">{busy}…</p>:null}
    </aside>
    <div className="space-y-3">
      <section className="rounded-2xl border border-neutral-800 bg-neutral-900/50 p-4"><div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4"><Metric label="authority" value={txt(status?.authority)}/><Metric label="application" value={txt(status?.public_application)}/><Metric label="classification" value={txt(result?.classification??status?.classification)}/><Metric label="ready" value={String(result?.ready??false)}/></div></section>
      <section className="rounded-2xl border border-neutral-800 bg-neutral-900/50 p-4"><h3 className="text-xs font-semibold text-cyan-200">Environment</h3><div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3"><Metric label="OS" value={txt(env.os)}/><Metric label="machine" value={txt(env.machine)}/><Metric label="Python" value={txt(env.python_version)}/><Metric label="package root" value={txt(result?.package_root??result?.install_root)}/><Metric label="manifest" value={txt(result?.manifest_identity)}/><Metric label="plan" value={txt(result?.plan_identity)}/></div></section>
      <section className="rounded-2xl border border-neutral-800 bg-neutral-900/50 p-4"><h3 className="text-xs font-semibold text-cyan-200">Resolved component closure</h3>{components.length?<div className="mt-3 flex flex-wrap gap-2">{components.map((x:string)=><span key={x} className="rounded-full border border-cyan-950 bg-cyan-950/30 px-2 py-1 text-[10px] text-cyan-200">{x}</span>)}</div>:<p className="mt-3 text-xs text-neutral-500">Run Plan to inspect the deterministic profile closure.</p>}</section>
    </div>
  </section>
}
const Metric:React.FC<{label:string;value:string}>=({label,value})=><div className="min-w-0 rounded-xl border border-neutral-800 bg-black/50 p-3"><div className="text-[9px] uppercase tracking-wide text-neutral-600">{label}</div><div className="mt-1 break-words font-mono text-[10px] text-neutral-200">{value}</div></div>
