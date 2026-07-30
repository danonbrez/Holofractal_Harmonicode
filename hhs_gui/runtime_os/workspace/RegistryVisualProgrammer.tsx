import React, { Suspense, useEffect, useMemo, useRef, useState } from "react"
import { runtimeApplicationRegistry } from "../core/RuntimeApplicationRegistry"
import type { RuntimeOS } from "../core/RuntimeOS"

type Json = Record<string, any>
type NodeKind = "service" | "workspace" | "application"
type NodeStatus = "idle" | "running" | "success" | "error"

interface RegistryDefinition {
  id: string
  registryId: string
  title: string
  kind: NodeKind
  category: string
  description: string
  inputSchema: Json
  outputSchema: Json
  requiresAuthority: boolean
}

interface VisualNode {
  id: string
  definitionId: string
  x: number
  y: number
  payload: Json
  status: NodeStatus
  result: Json | null
  error: string | null
  receiptHash72: string | null
}

interface VisualEdge {
  id: string
  from: string
  to: string
  sourcePath: string
  targetPath: string
}

interface StoredGraph {
  schema: "HHS_REGISTRY_VISUAL_PROGRAM_V1"
  nodes: VisualNode[]
  edges: VisualEdge[]
  updated_at: string
}

export interface RegistryVisualProgrammerProps {
  runtimeOS: RuntimeOS
  projectId: string | null
  sourceObjectId: string | null
  artifactId: string | null
  executeWorkspaceOperation: (operation: string, payload: Json) => Promise<Json>
  onExternalResult: (operation: string, feedback: Json) => void
}

const WORKSPACE_DEFINITIONS: RegistryDefinition[] = [
  {
    id: "workspace:project.create",
    registryId: "project.create",
    title: "Create Project",
    kind: "workspace",
    category: "workspace",
    description: "Create a canonical project and return its project identity.",
    inputSchema: { type: "object", properties: { name: { type: "string", default: "HHS Visual Program" } } },
    outputSchema: { type: "object", properties: { result: { type: "object" } } },
    requiresAuthority: true,
  },
  {
    id: "workspace:ingress.register",
    registryId: "ingress.register",
    title: "Register Object",
    kind: "workspace",
    category: "workspace",
    description: "Witness source or multimodal payload as a project object.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string" },
        source_name: { type: "string", default: "visual-node.hhs" },
        source_payload: { type: "string", default: "" },
        declared_modality: { type: "string", default: "HARMONICODE_SOURCE" },
      },
    },
    outputSchema: { type: "object", properties: { result: { type: "object" } } },
    requiresAuthority: true,
  },
  {
    id: "workspace:interpret.execute",
    registryId: "interpret.execute",
    title: "Exact Interpreter",
    kind: "workspace",
    category: "language",
    description: "Execute exact HARMONICODE interpretation through workspace authority.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string" },
        source_object_id: { type: "string" },
        expression: { type: "string", default: "1+2*3/4" },
      },
    },
    outputSchema: { type: "object", properties: { result: { type: "object" } } },
    requiresAuthority: true,
  },
  {
    id: "workspace:compile.execute",
    registryId: "compile.execute",
    title: "HHS Compiler",
    kind: "workspace",
    category: "language",
    description: "Compile witnessed source into an executable HHS artifact.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string" },
        source_object_id: { type: "string" },
        source_text: { type: "string", default: "" },
        target: { type: "string", default: "HHS_IR" },
      },
    },
    outputSchema: { type: "object", properties: { result: { type: "object" } } },
    requiresAuthority: true,
  },
  {
    id: "workspace:emulator.create",
    registryId: "emulator.create",
    title: "Create Emulator",
    kind: "workspace",
    category: "runtime",
    description: "Create an emulator session from a compiled artifact.",
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string" },
        program_artifact_id: { type: "string" },
      },
    },
    outputSchema: { type: "object", properties: { result: { type: "object" } } },
    requiresAuthority: true,
  },
  ...(["emulator.step", "emulator.run", "emulator.snapshot"] as const).map((operation) => ({
    id: `workspace:${operation}`,
    registryId: operation,
    title: operation === "emulator.step" ? "Emulator Step" : operation === "emulator.run" ? "Emulator Run" : "Emulator Snapshot",
    kind: "workspace" as const,
    category: "runtime",
    description: `Execute ${operation} against a canonical emulator session.`,
    inputSchema: {
      type: "object",
      properties: {
        project_id: { type: "string" },
        session_id: { type: "string" },
        ...(operation === "emulator.run" ? { steps: { type: "integer", default: 4 } } : {}),
      },
    },
    outputSchema: { type: "object", properties: { result: { type: "object" } } },
    requiresAuthority: true,
  })),
]

const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback
const clone = <T,>(value: T): T => JSON.parse(JSON.stringify(value)) as T

async function requestJson(url: string, init?: RequestInit, timeoutMs = 45000): Promise<Json> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal,
      headers: {
        accept: "application/json",
        ...(init?.body ? { "content-type": "application/json" } : {}),
        ...(init?.headers ?? {}),
      },
    })
    const body = record(await response.json())
    if (!response.ok) throw new Error(text(body.detail ?? body.error ?? body.status, response.statusText))
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

function schemaDefaults(schema: Json): Json {
  const result: Json = {}
  const properties = record(schema.properties)
  for (const [name, propertyValue] of Object.entries(properties)) {
    const property = record(propertyValue)
    if (property.default !== undefined) result[name] = clone(property.default)
    else if (property.type === "object") result[name] = {}
    else if (property.type === "array") result[name] = []
    else if (property.type === "boolean") result[name] = false
  }
  return result
}

function getPath(value: unknown, path: string): unknown {
  if (!path.trim()) return value
  return path.split(".").filter(Boolean).reduce<unknown>((current, segment) => {
    if (!current || typeof current !== "object") return undefined
    return (current as Json)[segment]
  }, value)
}

function setPath(target: Json, path: string, value: unknown): void {
  const parts = path.split(".").filter(Boolean)
  if (parts.length === 0) return
  let cursor = target
  for (const part of parts.slice(0, -1)) {
    if (!cursor[part] || typeof cursor[part] !== "object") cursor[part] = {}
    cursor = cursor[part]
  }
  cursor[parts[parts.length - 1]] = clone(value)
}

function extractReceipt(value: Json): string | null {
  const candidates: unknown[] = [
    value.receipt_hash72,
    value.result_root_hash72,
    record(value.result).receipt_hash72,
    record(record(value.result).receipt).receipt_hash72,
    record(record(value.result).execution_receipt).receipt_hash72,
    record(record(value.result).artifact).receipt_hash72,
    record(value.runtime_contract).payload_hash72,
  ]
  return candidates.find((candidate) => typeof candidate === "string") as string | undefined ?? null
}

function normalizeServices(body: Json): RegistryDefinition[] {
  const services = Array.isArray(body.services) ? body.services : []
  return services.map((raw: unknown) => {
    const service = record(raw)
    const contract = record(service.runtime_contract)
    const name = text(service.name ?? contract.name)
    return {
      id: `service:${name}`,
      registryId: name,
      title: name,
      kind: "service" as const,
      category: text(service.service_type ?? contract.service_type, "runtime"),
      description: text(service.description ?? contract.description, `${text(service.module)}.${text(service.function)}`),
      inputSchema: record(service.schema ?? contract.request_schema),
      outputSchema: record(service.response_schema ?? contract.response_schema),
      requiresAuthority: Boolean(service.requires_authority ?? contract.requires_authority ?? true),
    }
  }).filter((definition: RegistryDefinition) => Boolean(definition.registryId))
}

function applicationDefinitions(): RegistryDefinition[] {
  return runtimeApplicationRegistry.all().map((application) => ({
    id: `application:${application.id}`,
    registryId: application.id,
    title: application.title,
    kind: "application" as const,
    category: application.authority,
    description: application.description ?? "Lazy HHS runtime application module",
    inputSchema: { type: "object", properties: {} },
    outputSchema: { type: "object", properties: { application_id: { type: "string" } } },
    requiresAuthority: false,
  }))
}

function firstInputPath(definition: RegistryDefinition): string {
  const properties = Object.keys(record(definition.inputSchema.properties))
  return properties[0] ?? "input"
}

function topologicalOrder(nodes: VisualNode[], edges: VisualEdge[]): string[] {
  const ids = new Set(nodes.map((node) => node.id))
  const indegree = new Map(nodes.map((node) => [node.id, 0]))
  const outgoing = new Map<string, string[]>()
  for (const edge of edges) {
    if (!ids.has(edge.from) || !ids.has(edge.to)) continue
    indegree.set(edge.to, (indegree.get(edge.to) ?? 0) + 1)
    outgoing.set(edge.from, [...(outgoing.get(edge.from) ?? []), edge.to])
  }
  const queue = nodes.filter((node) => (indegree.get(node.id) ?? 0) === 0).map((node) => node.id)
  const result: string[] = []
  while (queue.length > 0) {
    const id = queue.shift() as string
    result.push(id)
    for (const next of outgoing.get(id) ?? []) {
      const remaining = (indegree.get(next) ?? 0) - 1
      indegree.set(next, remaining)
      if (remaining === 0) queue.push(next)
    }
  }
  if (result.length !== nodes.length) throw new Error("Visual program contains a cycle. Remove or redirect an edge before execution.")
  return result
}

class ApplicationBoundary extends React.Component<{ children: React.ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null }
  static getDerivedStateFromError(error: Error) { return { error } }
  render() {
    if (this.state.error) {
      return <pre className="h-full overflow-auto whitespace-pre-wrap bg-black p-4 text-xs text-red-200">{this.state.error.stack ?? this.state.error.message}</pre>
    }
    return this.props.children
  }
}

export const RegistryVisualProgrammer: React.FC<RegistryVisualProgrammerProps> = ({
  runtimeOS,
  projectId,
  sourceObjectId,
  artifactId,
  executeWorkspaceOperation,
  onExternalResult,
}) => {
  const [services, setServices] = useState<RegistryDefinition[]>([])
  const [registryError, setRegistryError] = useState<string | null>(null)
  const [registryLoading, setRegistryLoading] = useState(true)
  const [query, setQuery] = useState("")
  const [category, setCategory] = useState("all")
  const [nodes, setNodes] = useState<VisualNode[]>([])
  const [edges, setEdges] = useState<VisualEdge[]>([])
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [connectingFrom, setConnectingFrom] = useState<string | null>(null)
  const [graphRunning, setGraphRunning] = useState(false)
  const [activeApplicationId, setActiveApplicationId] = useState<string | null>(null)
  const [paletteOpen, setPaletteOpen] = useState(true)
  const canvasRef = useRef<HTMLDivElement | null>(null)
  const dragRef = useRef<{ nodeId: string; offsetX: number; offsetY: number } | null>(null)

  const definitions = useMemo(
    () => [...WORKSPACE_DEFINITIONS, ...services, ...applicationDefinitions()],
    [services],
  )
  const definitionMap = useMemo(() => new Map(definitions.map((definition) => [definition.id, definition])), [definitions])
  const selectedNode = nodes.find((node) => node.id === selectedNodeId) ?? null
  const selectedDefinition = selectedNode ? definitionMap.get(selectedNode.definitionId) ?? null : null
  const storageKey = `hhs.registry.visual-program.v1:${projectId ?? "unbound"}`

  useEffect(() => {
    let active = true
    setRegistryLoading(true)
    requestJson("/api/runtime/services")
      .then((body) => { if (active) setServices(normalizeServices(body)) })
      .catch((reason: unknown) => { if (active) setRegistryError(reason instanceof Error ? reason.message : String(reason)) })
      .finally(() => { if (active) setRegistryLoading(false) })
    return () => { active = false }
  }, [])

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(storageKey)
      if (!stored) return
      const graph = JSON.parse(stored) as StoredGraph
      if (graph.schema !== "HHS_REGISTRY_VISUAL_PROGRAM_V1") return
      setNodes(Array.isArray(graph.nodes) ? graph.nodes : [])
      setEdges(Array.isArray(graph.edges) ? graph.edges : [])
    } catch (reason) {
      setRegistryError(`Stored graph could not be restored: ${reason instanceof Error ? reason.message : String(reason)}`)
    }
  }, [storageKey])

  useEffect(() => {
    const graph: StoredGraph = {
      schema: "HHS_REGISTRY_VISUAL_PROGRAM_V1",
      nodes,
      edges,
      updated_at: new Date().toISOString(),
    }
    window.localStorage.setItem(storageKey, JSON.stringify(graph))
  }, [edges, nodes, storageKey])

  const visibleDefinitions = useMemo(() => {
    const normalized = query.trim().toLowerCase()
    return definitions.filter((definition) => {
      if (category !== "all" && definition.category !== category && definition.kind !== category) return false
      if (!normalized) return true
      return [definition.title, definition.registryId, definition.description, definition.category, definition.kind]
        .join(" ").toLowerCase().includes(normalized)
    })
  }, [category, definitions, query])

  const categories = useMemo(
    () => ["all", ...Array.from(new Set(definitions.flatMap((definition) => [definition.kind, definition.category]))).sort()],
    [definitions],
  )

  const updateNode = (nodeId: string, updater: (node: VisualNode) => VisualNode): void => {
    setNodes((current) => current.map((node) => node.id === nodeId ? updater(node) : node))
  }

  const addNode = (definition: RegistryDefinition): void => {
    const index = nodes.length
    const node: VisualNode = {
      id: `${definition.id}:${Date.now()}:${index}`,
      definitionId: definition.id,
      x: 36 + (index % 3) * 285,
      y: 36 + Math.floor(index / 3) * 190,
      payload: schemaDefaults(definition.inputSchema),
      status: "idle",
      result: null,
      error: null,
      receiptHash72: null,
    }
    setNodes((current) => [...current, node])
    setSelectedNodeId(node.id)
    if (window.innerWidth < 900) setPaletteOpen(false)
  }

  const removeNode = (nodeId: string): void => {
    setNodes((current) => current.filter((node) => node.id !== nodeId))
    setEdges((current) => current.filter((edge) => edge.from !== nodeId && edge.to !== nodeId))
    setSelectedNodeId((current) => current === nodeId ? null : current)
  }

  const connectTo = (targetNodeId: string): void => {
    if (!connectingFrom || connectingFrom === targetNodeId) {
      setConnectingFrom(null)
      return
    }
    const target = nodes.find((node) => node.id === targetNodeId)
    const targetDefinition = target ? definitionMap.get(target.definitionId) : null
    if (!targetDefinition) return
    const edge: VisualEdge = {
      id: `edge:${connectingFrom}:${targetNodeId}:${Date.now()}`,
      from: connectingFrom,
      to: targetNodeId,
      sourcePath: "result",
      targetPath: firstInputPath(targetDefinition),
    }
    setEdges((current) => [...current.filter((item) => !(item.from === edge.from && item.to === edge.to)), edge])
    setConnectingFrom(null)
  }

  const executeDefinition = async (definition: RegistryDefinition, payload: Json): Promise<Json> => {
    if (definition.kind === "workspace") {
      return executeWorkspaceOperation(definition.registryId, payload)
    }
    if (definition.kind === "service") {
      const feedback = await requestJson("/api/runtime/services/dispatch", {
        method: "POST",
        body: JSON.stringify({ service: definition.registryId, payload }),
      })
      onExternalResult(`service:${definition.registryId}`, feedback)
      return feedback
    }
    setActiveApplicationId(definition.registryId)
    return {
      schema: "HHS_RUNTIME_APPLICATION_ACTIVATION_V1",
      ok: true,
      status: "APPLICATION_MODULE_ACTIVE",
      application_id: definition.registryId,
    }
  }

  const payloadForNode = (node: VisualNode, resultMap: Map<string, Json>): Json => {
    const payload = clone(node.payload)
    if (projectId && payload.project_id === undefined) payload.project_id = projectId
    if (sourceObjectId && payload.source_object_id === undefined) payload.source_object_id = sourceObjectId
    if (artifactId && payload.program_artifact_id === undefined) payload.program_artifact_id = artifactId
    for (const edge of edges.filter((candidate) => candidate.to === node.id)) {
      const sourceNode = nodes.find((candidate) => candidate.id === edge.from)
      const sourceResult = resultMap.get(edge.from) ?? sourceNode?.result
      if (!sourceResult) throw new Error(`Upstream node ${edge.from} has no result for ${edge.targetPath}`)
      const value = getPath(sourceResult, edge.sourcePath)
      if (value === undefined) throw new Error(`Upstream path ${edge.sourcePath || "<root>"} is undefined`)
      setPath(payload, edge.targetPath, value)
    }
    return payload
  }

  const executeNode = async (nodeId: string, resultMap = new Map<string, Json>()): Promise<Json> => {
    const node = nodes.find((candidate) => candidate.id === nodeId)
    if (!node) throw new Error(`Unknown visual node: ${nodeId}`)
    const definition = definitionMap.get(node.definitionId)
    if (!definition) throw new Error(`Definition is not available: ${node.definitionId}`)
    updateNode(nodeId, (current) => ({ ...current, status: "running", error: null }))
    try {
      const payload = payloadForNode(node, resultMap)
      const result = await executeDefinition(definition, payload)
      const receiptHash72 = extractReceipt(result)
      resultMap.set(nodeId, result)
      updateNode(nodeId, (current) => ({ ...current, status: "success", result, error: null, receiptHash72 }))
      return result
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : String(reason)
      updateNode(nodeId, (current) => ({ ...current, status: "error", error: message }))
      throw new Error(`${definition.title}: ${message}`)
    }
  }

  const runGraph = async (): Promise<void> => {
    if (graphRunning || nodes.length === 0) return
    setGraphRunning(true)
    setRegistryError(null)
    try {
      const results = new Map<string, Json>()
      for (const nodeId of topologicalOrder(nodes, edges)) await executeNode(nodeId, results)
    } catch (reason) {
      setRegistryError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setGraphRunning(false)
    }
  }

  const createStarterGraph = (): void => {
    const ids = [
      "workspace:project.create",
      "workspace:ingress.register",
      "workspace:compile.execute",
      "workspace:emulator.create",
    ]
    const nextNodes = ids.map((definitionId, index) => {
      const definition = definitionMap.get(definitionId) as RegistryDefinition
      return {
        id: `starter:${definition.registryId}:${Date.now()}:${index}`,
        definitionId,
        x: 40 + index * 280,
        y: 90 + (index % 2) * 160,
        payload: schemaDefaults(definition.inputSchema),
        status: "idle" as NodeStatus,
        result: null,
        error: null,
        receiptHash72: null,
      }
    })
    const nextEdges: VisualEdge[] = [
      { id: `starter-edge-0-${Date.now()}`, from: nextNodes[0].id, to: nextNodes[1].id, sourcePath: "result.project.project_id", targetPath: "project_id" },
      { id: `starter-edge-1-${Date.now()}`, from: nextNodes[1].id, to: nextNodes[2].id, sourcePath: "result.workspace_object.object_id", targetPath: "source_object_id" },
      { id: `starter-edge-2-${Date.now()}`, from: nextNodes[2].id, to: nextNodes[3].id, sourcePath: "result.artifact.artifact_id", targetPath: "program_artifact_id" },
    ]
    setNodes(nextNodes)
    setEdges(nextEdges)
    setSelectedNodeId(nextNodes[0].id)
  }

  const witnessGraph = async (): Promise<void> => {
    const graph: StoredGraph = { schema: "HHS_REGISTRY_VISUAL_PROGRAM_V1", nodes, edges, updated_at: new Date().toISOString() }
    try {
      await executeWorkspaceOperation("ingress.register", {
        project_id: projectId,
        source_name: "visual-program.hhsgraph.json",
        source_payload: JSON.stringify(graph),
        declared_modality: "JSON_EXECUTION_GRAPH",
      })
    } catch (reason) {
      setRegistryError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  const activeApplicationDefinition = activeApplicationId ? runtimeApplicationRegistry.get(activeApplicationId) : undefined
  const ActiveApplication = useMemo(
    () => activeApplicationId ? runtimeApplicationRegistry.resolveLazyComponent(activeApplicationId) : null,
    [activeApplicationId],
  )

  return (
    <section data-testid="registry-visual-programmer" className="min-h-[calc(100vh-116px)] bg-neutral-950 text-neutral-100">
      <header className="flex flex-wrap items-center justify-between gap-2 border-b border-neutral-800 bg-black/80 p-3">
        <div>
          <h2 className="text-sm font-semibold text-cyan-200">Executable registry canvas</h2>
          <p className="text-[10px] text-neutral-500">{definitions.length} typed modules · guarded services, workspace objects, and lazy applications</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button type="button" className="runtime-button min-h-9 px-3 text-xs" onClick={() => setPaletteOpen((value) => !value)}>Registry</button>
          <button type="button" className="runtime-button min-h-9 px-3 text-xs" onClick={createStarterGraph}>Starter graph</button>
          <button type="button" className="runtime-button min-h-9 px-3 text-xs" onClick={() => void witnessGraph()} disabled={!projectId || nodes.length === 0}>Witness graph</button>
          <button type="button" className="runtime-button min-h-9 px-3 text-xs" onClick={() => void runGraph()} disabled={graphRunning || nodes.length === 0}>{graphRunning ? "Running graph…" : "Run graph"}</button>
        </div>
      </header>

      {registryError ? (
        <div className="m-3 flex items-start justify-between gap-3 rounded-xl border border-red-900 bg-red-950/30 p-3 text-xs text-red-200">
          <span>{registryError}</span>
          <button type="button" onClick={() => setRegistryError(null)}>dismiss</button>
        </div>
      ) : null}

      <div className="grid min-h-[720px] grid-cols-1 xl:grid-cols-[260px_minmax(0,1fr)_320px]">
        {paletteOpen ? (
          <aside className="border-r border-neutral-800 bg-neutral-900/50 p-3 xl:block">
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search every registered function…" className="w-full rounded-lg border border-neutral-700 bg-black p-2 text-xs" />
            <select value={category} onChange={(event) => setCategory(event.target.value)} className="mt-2 w-full rounded-lg border border-neutral-700 bg-black p-2 text-xs">
              {categories.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
            <div className="mt-3 flex items-center justify-between text-[9px] text-neutral-500">
              <span>{visibleDefinitions.length} available</span>
              <span>{registryLoading ? "loading registry" : services.length ? `${services.length} backend services` : "registry unavailable"}</span>
            </div>
            <div className="mt-2 max-h-[66vh] space-y-2 overflow-auto pr-1">
              {visibleDefinitions.map((definition) => (
                <button key={definition.id} type="button" onClick={() => addNode(definition)} className="w-full rounded-xl border border-neutral-800 bg-black/60 p-3 text-left hover:border-cyan-800">
                  <div className="flex items-start justify-between gap-2">
                    <strong className="break-all text-xs text-cyan-100">{definition.title}</strong>
                    <span className="rounded bg-neutral-800 px-1.5 py-0.5 text-[8px] text-neutral-400">{definition.kind}</span>
                  </div>
                  <p className="mt-1 line-clamp-3 text-[9px] leading-4 text-neutral-500">{definition.description}</p>
                  <div className="mt-2 font-mono text-[8px] text-cyan-800">{definition.category}{definition.requiresAuthority ? " · authority" : " · local/lazy"}</div>
                </button>
              ))}
            </div>
          </aside>
        ) : null}

        <div className="min-w-0 overflow-auto bg-black/50">
          <div
            ref={canvasRef}
            className="relative min-h-[760px] min-w-[1200px] bg-[radial-gradient(circle_at_center,rgba(8,145,178,0.08),transparent_62%)]"
            onPointerUp={() => { dragRef.current = null }}
          >
            <svg className="pointer-events-none absolute inset-0 h-full w-full" aria-hidden="true">
              {edges.map((edge) => {
                const source = nodes.find((node) => node.id === edge.from)
                const target = nodes.find((node) => node.id === edge.to)
                if (!source || !target) return null
                const startX = source.x + 238
                const startY = source.y + 72
                const endX = target.x
                const endY = target.y + 72
                const bend = Math.max(70, Math.abs(endX - startX) / 2)
                return <path key={edge.id} d={`M ${startX} ${startY} C ${startX + bend} ${startY}, ${endX - bend} ${endY}, ${endX} ${endY}`} fill="none" stroke="rgba(34,211,238,0.55)" strokeWidth="2" />
              })}
            </svg>

            {nodes.length === 0 ? (
              <div className="absolute left-8 top-8 max-w-md rounded-2xl border border-dashed border-cyan-900 bg-neutral-950/90 p-5 text-sm leading-6 text-neutral-400">
                Add any registered service, workspace operation, or application from the registry. Connect output ports to input ports, edit the schema-derived payload, then execute one node or the complete dependency graph.
              </div>
            ) : null}

            {nodes.map((node) => {
              const definition = definitionMap.get(node.definitionId)
              if (!definition) return null
              const selected = node.id === selectedNodeId
              return (
                <article key={node.id} className={`absolute w-[238px] rounded-2xl border bg-neutral-950/95 shadow-xl ${selected ? "border-cyan-500" : "border-neutral-800"}`} style={{ left: node.x, top: node.y }} onClick={() => setSelectedNodeId(node.id)}>
                  <header
                    className="cursor-move rounded-t-2xl border-b border-neutral-800 bg-neutral-900 px-3 py-2 touch-none"
                    onPointerDown={(event) => {
                      const rect = canvasRef.current?.getBoundingClientRect()
                      if (!rect) return
                      dragRef.current = { nodeId: node.id, offsetX: event.clientX - rect.left + (canvasRef.current?.scrollLeft ?? 0) - node.x, offsetY: event.clientY - rect.top + (canvasRef.current?.scrollTop ?? 0) - node.y }
                      event.currentTarget.setPointerCapture(event.pointerId)
                    }}
                    onPointerMove={(event) => {
                      const drag = dragRef.current
                      const rect = canvasRef.current?.getBoundingClientRect()
                      if (!drag || drag.nodeId !== node.id || !rect) return
                      const x = Math.max(0, event.clientX - rect.left + (canvasRef.current?.scrollLeft ?? 0) - drag.offsetX)
                      const y = Math.max(0, event.clientY - rect.top + (canvasRef.current?.scrollTop ?? 0) - drag.offsetY)
                      updateNode(node.id, (current) => ({ ...current, x, y }))
                    }}
                    onPointerUp={() => { dragRef.current = null }}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <strong className="break-all text-xs text-cyan-100">{definition.title}</strong>
                      <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${node.status === "success" ? "bg-emerald-400" : node.status === "error" ? "bg-red-400" : node.status === "running" ? "bg-amber-300" : "bg-neutral-600"}`} />
                    </div>
                    <div className="mt-1 truncate font-mono text-[8px] text-neutral-500">{definition.registryId}</div>
                  </header>
                  <div className="space-y-2 p-3">
                    <p className="line-clamp-3 min-h-10 text-[9px] leading-4 text-neutral-500">{definition.description}</p>
                    {node.error ? <p className="line-clamp-3 text-[9px] text-red-300">{node.error}</p> : null}
                    {node.receiptHash72 ? <div className="truncate font-mono text-[8px] text-cyan-700">{node.receiptHash72}</div> : null}
                    <div className="flex items-center justify-between gap-2">
                      <button type="button" className={`rounded-full border px-2 py-1 text-[9px] ${connectingFrom === node.id ? "border-cyan-400 text-cyan-200" : "border-neutral-700 text-neutral-400"}`} onClick={(event) => { event.stopPropagation(); setConnectingFrom((current) => current === node.id ? null : node.id) }}>output</button>
                      <button type="button" className="runtime-button px-3 py-1 text-[9px]" onClick={(event) => { event.stopPropagation(); void executeNode(node.id).catch((reason) => setRegistryError(reason.message)) }}>run</button>
                      <button type="button" className={`rounded-full border px-2 py-1 text-[9px] ${connectingFrom ? "border-cyan-500 text-cyan-200" : "border-neutral-700 text-neutral-400"}`} onClick={(event) => { event.stopPropagation(); connectTo(node.id) }}>input</button>
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        </div>

        <aside className="border-l border-neutral-800 bg-neutral-900/50 p-3">
          {selectedNode && selectedDefinition ? (
            <NodeInspector
              node={selectedNode}
              definition={selectedDefinition}
              incoming={edges.filter((edge) => edge.to === selectedNode.id)}
              outgoing={edges.filter((edge) => edge.from === selectedNode.id)}
              nodes={nodes}
              onPayload={(payload) => updateNode(selectedNode.id, (current) => ({ ...current, payload }))}
              onEdge={(edgeId, patch) => setEdges((current) => current.map((edge) => edge.id === edgeId ? { ...edge, ...patch } : edge))}
              onRemoveEdge={(edgeId) => setEdges((current) => current.filter((edge) => edge.id !== edgeId))}
              onRun={() => void executeNode(selectedNode.id).catch((reason) => setRegistryError(reason.message))}
              onRemove={() => removeNode(selectedNode.id)}
            />
          ) : (
            <div className="rounded-xl border border-neutral-800 bg-black/50 p-4 text-xs leading-5 text-neutral-500">Select a node to edit its typed payload, edge mappings, execution result, and receipt evidence.</div>
          )}
        </aside>
      </div>

      {ActiveApplication && activeApplicationDefinition ? (
        <section className="border-t border-cyan-900 bg-black">
          <header className="flex items-center justify-between gap-3 border-b border-neutral-800 p-3">
            <div>
              <h3 className="text-sm font-semibold text-cyan-200">{activeApplicationDefinition.title}</h3>
              <p className="text-[9px] text-neutral-500">Lazy application module · loaded only while active</p>
            </div>
            <button type="button" className="runtime-button min-h-9 px-3 text-xs" onClick={() => setActiveApplicationId(null)}>Close module</button>
          </header>
          <div className="h-[70vh] min-h-[480px] overflow-auto">
            <ApplicationBoundary key={activeApplicationId}>
              <Suspense fallback={<div className="p-6 text-sm text-cyan-300">Loading registered application module…</div>}>
                <ActiveApplication runtimeOS={runtimeOS} applicationId={activeApplicationId} />
              </Suspense>
            </ApplicationBoundary>
          </div>
        </section>
      ) : null}
    </section>
  )
}

const NodeInspector: React.FC<{
  node: VisualNode
  definition: RegistryDefinition
  incoming: VisualEdge[]
  outgoing: VisualEdge[]
  nodes: VisualNode[]
  onPayload: (payload: Json) => void
  onEdge: (edgeId: string, patch: Partial<VisualEdge>) => void
  onRemoveEdge: (edgeId: string) => void
  onRun: () => void
  onRemove: () => void
}> = ({ node, definition, incoming, outgoing, nodes, onPayload, onEdge, onRemoveEdge, onRun, onRemove }) => {
  const properties = record(definition.inputSchema.properties)
  const [rawPayload, setRawPayload] = useState(JSON.stringify(node.payload, null, 2))
  const [payloadError, setPayloadError] = useState<string | null>(null)

  useEffect(() => setRawPayload(JSON.stringify(node.payload, null, 2)), [node.id, node.payload])

  const updateField = (name: string, property: Json, rawValue: string | boolean): void => {
    const payload = clone(node.payload)
    if (property.type === "boolean") payload[name] = Boolean(rawValue)
    else if (property.type === "integer" || property.type === "number") payload[name] = rawValue === "" ? undefined : Number(rawValue)
    else payload[name] = rawValue
    onPayload(payload)
  }

  return (
    <div className="space-y-3">
      <section className="rounded-xl border border-neutral-800 bg-black/60 p-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="break-all text-sm font-semibold text-cyan-200">{definition.title}</h3>
            <p className="mt-1 font-mono text-[8px] text-neutral-600">{definition.registryId}</p>
          </div>
          <span className="rounded bg-neutral-800 px-2 py-1 text-[8px] text-neutral-400">{definition.kind}</span>
        </div>
        <p className="mt-3 text-[10px] leading-5 text-neutral-500">{definition.description}</p>
        <div className="mt-3 grid grid-cols-2 gap-2">
          <button type="button" className="runtime-button min-h-9 text-xs" onClick={onRun}>Run node</button>
          <button type="button" className="min-h-9 rounded-lg border border-red-900 bg-red-950/30 text-xs text-red-300" onClick={onRemove}>Remove</button>
        </div>
      </section>

      {Object.keys(properties).length > 0 ? (
        <section className="rounded-xl border border-neutral-800 bg-black/60 p-3">
          <h4 className="text-[10px] font-semibold uppercase tracking-wide text-neutral-400">Schema inputs</h4>
          <div className="mt-3 space-y-2">
            {Object.entries(properties).map(([name, propertyValue]) => {
              const property = record(propertyValue)
              const value = node.payload[name]
              if (property.type === "boolean") {
                return <label key={name} className="flex items-center justify-between gap-3 text-[10px] text-neutral-400"><span>{name}</span><input type="checkbox" checked={Boolean(value)} onChange={(event) => updateField(name, property, event.target.checked)} /></label>
              }
              if (["string", "integer", "number"].includes(text(property.type, "string"))) {
                return <label key={name} className="block text-[9px] text-neutral-500"><span>{name} · {text(property.type, "string")}</span><input value={value === undefined ? "" : String(value)} onChange={(event) => updateField(name, property, event.target.value)} className="mt-1 w-full rounded-lg border border-neutral-700 bg-black p-2 text-xs text-white" /></label>
              }
              return <div key={name} className="rounded-lg border border-neutral-800 p-2 text-[9px] text-neutral-500">{name} · edit in raw payload</div>
            })}
          </div>
        </section>
      ) : null}

      <section className="rounded-xl border border-neutral-800 bg-black/60 p-3">
        <h4 className="text-[10px] font-semibold uppercase tracking-wide text-neutral-400">Raw payload</h4>
        <textarea value={rawPayload} onChange={(event) => setRawPayload(event.target.value)} onBlur={() => {
          try {
            const parsed = record(JSON.parse(rawPayload))
            onPayload(parsed)
            setPayloadError(null)
          } catch (reason) {
            setPayloadError(reason instanceof Error ? reason.message : String(reason))
          }
        }} className="mt-2 min-h-40 w-full resize-y rounded-lg border border-neutral-700 bg-black p-2 font-mono text-[10px] text-cyan-50" spellCheck={false} />
        {payloadError ? <p className="mt-2 text-[9px] text-red-300">{payloadError}</p> : null}
      </section>

      <section className="rounded-xl border border-neutral-800 bg-black/60 p-3">
        <h4 className="text-[10px] font-semibold uppercase tracking-wide text-neutral-400">Data edges</h4>
        {incoming.length + outgoing.length === 0 ? <p className="mt-2 text-[9px] text-neutral-600">No connected data ports.</p> : null}
        <div className="mt-2 space-y-2">
          {incoming.map((edge) => {
            const source = nodes.find((candidate) => candidate.id === edge.from)
            return <div key={edge.id} className="rounded-lg border border-cyan-950 bg-cyan-950/10 p-2">
              <div className="text-[9px] text-cyan-300">from {source?.definitionId ?? edge.from}</div>
              <input value={edge.sourcePath} onChange={(event) => onEdge(edge.id, { sourcePath: event.target.value })} className="mt-2 w-full rounded border border-neutral-700 bg-black p-1.5 font-mono text-[9px]" aria-label="Source result path" />
              <input value={edge.targetPath} onChange={(event) => onEdge(edge.id, { targetPath: event.target.value })} className="mt-1 w-full rounded border border-neutral-700 bg-black p-1.5 font-mono text-[9px]" aria-label="Target payload path" />
              <button type="button" onClick={() => onRemoveEdge(edge.id)} className="mt-2 text-[9px] text-red-300">remove edge</button>
            </div>
          })}
          {outgoing.map((edge) => {
            const target = nodes.find((candidate) => candidate.id === edge.to)
            return <div key={edge.id} className="rounded-lg border border-neutral-800 p-2 text-[9px] text-neutral-500">to {target?.definitionId ?? edge.to} · {edge.sourcePath} → {edge.targetPath}</div>
          })}
        </div>
      </section>

      {node.result ? (
        <section className="rounded-xl border border-neutral-800 bg-black/60 p-3">
          <div className="flex items-center justify-between gap-2"><h4 className="text-[10px] font-semibold uppercase tracking-wide text-neutral-400">Result</h4><span className="font-mono text-[8px] text-cyan-700">{node.receiptHash72 ?? "no receipt"}</span></div>
          <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap break-all text-[9px] text-neutral-400">{JSON.stringify(node.result, null, 2)}</pre>
        </section>
      ) : null}
    </div>
  )
}
