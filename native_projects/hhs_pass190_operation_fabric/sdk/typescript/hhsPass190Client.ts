// Generated Pass 190 TypeScript SDK. Do not edit by hand.
export type OperationId = "system.status" | "python.len" | "python.abs" | "python.sorted" | "list.with_appended" | "dict.get" | "text.join" | "math.gcd" | "pass189.context.decode" | "state.counter.advance" | "workspace.create" | "workspace.get" | "workspace.list" | "workspace.update" | "workspace.archive" | "artifact.register" | "artifact.get" | "artifact.list" | "provider.register" | "provider.get" | "provider.list" | "provider.set_enabled" | "capability.define" | "capability.get" | "capability.list" | "job.submit" | "job.get" | "job.list" | "job.claim" | "job.complete" | "job.fail" | "worker.register" | "worker.get" | "worker.list" | "worker.heartbeat" | "worker.set_enabled" | "job.submit_execution" | "job.cancel" | "job.retry" | "job.claim_next" | "job.execute_claimed" | "scheduler.tick"
export type InvokeOptions = { capabilityToken?: string; idempotencyKey?: string; expectedState?: string }
export class HHSClient {
  constructor(readonly baseUrl = "http://127.0.0.1:8190") {}
  private async request(path: string, init: RequestInit = {}) {
    const response = await fetch(this.baseUrl.replace(/\/$/, "") + path, init)
    const payload = await response.json()
    if (!response.ok) throw new Error(payload.message || payload.error || `HTTP ${response.status}`)
    return payload
  }
  operations() { return this.request("/api/pass190/operations") }
  integrity() { return this.request("/api/pass190/integrity") }
  arbitration() { return this.request("/api/pass190/arbitration") }
  resourceRegistry() { return this.request("/api/pass190/resource-registry") }
  executionRuntime() { return this.request("/api/pass190/execution-runtime") }
  leaseReceipts(after = 0, limit = 100) { return this.request(`/api/pass190/lease-receipts?after=${after}&limit=${limit}`) }
  events(after = 0, limit = 100) { return this.request(`/api/pass190/events?after=${after}&limit=${limit}`) }
  receipts(after = 0, limit = 100) { return this.request(`/api/pass190/receipts?after=${after}&limit=${limit}`) }
  replay(hash72: string) { return this.request("/api/pass190/replay", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({hash72}) }) }
  invoke(operationId: OperationId, arguments_: Record<string, unknown>, options: InvokeOptions = {}) {
    const headers: Record<string,string> = {"Content-Type":"application/json"}
    if (options.capabilityToken) headers["Authorization"] = `HHS-Capability ${options.capabilityToken}`
    if (options.idempotencyKey) headers["Idempotency-Key"] = options.idempotencyKey
    if (options.expectedState) headers["X-HHS-Expected-State"] = options.expectedState
    return this.request("/api/pass190/invoke", {method:"POST", headers, body:JSON.stringify({operation_id:operationId, arguments:arguments_})})
  }
  websocket(after = 0) { return new WebSocket(this.baseUrl.replace(/^http/, "ws").replace(/\/$/, "") + `/api/pass190/ws?after=${after}`) }
  system_status(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("system.status", arguments, options)
  }

  python_len(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("python.len", arguments, options)
  }

  python_abs(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("python.abs", arguments, options)
  }

  python_sorted(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("python.sorted", arguments, options)
  }

  list_with_appended(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("list.with_appended", arguments, options)
  }

  dict_get(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("dict.get", arguments, options)
  }

  text_join(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("text.join", arguments, options)
  }

  math_gcd(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("math.gcd", arguments, options)
  }

  pass189_context_decode(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("pass189.context.decode", arguments, options)
  }

  state_counter_advance(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("state.counter.advance", arguments, options)
  }

  workspace_create(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("workspace.create", arguments, options)
  }

  workspace_get(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("workspace.get", arguments, options)
  }

  workspace_list(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("workspace.list", arguments, options)
  }

  workspace_update(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("workspace.update", arguments, options)
  }

  workspace_archive(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("workspace.archive", arguments, options)
  }

  artifact_register(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("artifact.register", arguments, options)
  }

  artifact_get(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("artifact.get", arguments, options)
  }

  artifact_list(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("artifact.list", arguments, options)
  }

  provider_register(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("provider.register", arguments, options)
  }

  provider_get(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("provider.get", arguments, options)
  }

  provider_list(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("provider.list", arguments, options)
  }

  provider_set_enabled(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("provider.set_enabled", arguments, options)
  }

  capability_define(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("capability.define", arguments, options)
  }

  capability_get(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("capability.get", arguments, options)
  }

  capability_list(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("capability.list", arguments, options)
  }

  job_submit(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("job.submit", arguments, options)
  }

  job_get(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("job.get", arguments, options)
  }

  job_list(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("job.list", arguments, options)
  }

  job_claim(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("job.claim", arguments, options)
  }

  job_complete(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("job.complete", arguments, options)
  }

  job_fail(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("job.fail", arguments, options)
  }

  worker_register(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("worker.register", arguments, options)
  }

  worker_get(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("worker.get", arguments, options)
  }

  worker_list(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("worker.list", arguments, options)
  }

  worker_heartbeat(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("worker.heartbeat", arguments, options)
  }

  worker_set_enabled(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("worker.set_enabled", arguments, options)
  }

  job_submit_execution(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("job.submit_execution", arguments, options)
  }

  job_cancel(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("job.cancel", arguments, options)
  }

  job_retry(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("job.retry", arguments, options)
  }

  job_claim_next(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("job.claim_next", arguments, options)
  }

  job_execute_claimed(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("job.execute_claimed", arguments, options)
  }

  scheduler_tick(arguments: Record<string, unknown> = {}, options: InvokeOptions = {}) {
    return this.invoke("scheduler.tick", arguments, options)
  }

}
