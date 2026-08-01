// Generated Pass 190 TypeScript SDK. Do not edit by hand.
export type OperationId = "system.status" | "python.len" | "python.abs" | "python.sorted" | "list.with_appended" | "dict.get" | "text.join" | "math.gcd" | "pass189.context.decode" | "state.counter.advance"
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

}
