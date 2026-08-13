import React from "react"

export type RuntimeApplicationAuthority =
  | "runtime"
  | "instrument"
  | "graph"
  | "transport"
  | "workspace"
  | "experimental"

export interface RuntimeApplicationWindowPreset {
  width: number
  height: number
  minWidth?: number
  minHeight?: number
  resizable?: boolean
}

export interface RuntimeApplicationDefinition {
  id: string
  title: string
  icon?: string
  authority: RuntimeApplicationAuthority
  description?: string
  lazyLoader: () => Promise<{ default: React.ComponentType<any> }>
  windowPreset: RuntimeApplicationWindowPreset
  singleton?: boolean
  mobileSupported?: boolean
  experimental?: boolean
}

/**
 * Compatibility projection used by inherited Runtime OS command surfaces.
 * The canonical registry definition remains authoritative; these aliases are
 * derived views only and do not create a second application registry.
 */
export interface RuntimeApplication extends RuntimeApplicationDefinition {
  name: string
  applicationType: RuntimeApplicationAuthority
  route: string
}

export class RuntimeApplicationRegistry {
  private readonly applications = new Map<string, RuntimeApplicationDefinition>()

  public register(definition: RuntimeApplicationDefinition): void {
    if (!definition.id || this.applications.has(definition.id)) {
      throw new Error(`Invalid or duplicate runtime application registration: ${definition.id}`)
    }
    this.applications.set(definition.id, definition)
  }

  public get(id: string): RuntimeApplicationDefinition | undefined {
    return this.applications.get(id)
  }

  public has(id: string): boolean {
    return this.applications.has(id)
  }

  public all(): RuntimeApplicationDefinition[] {
    return [...this.applications.values()]
  }

  public getApplications(): RuntimeApplication[] {
    return this.all().map((application) => ({
      ...application,
      name: application.title,
      applicationType: application.authority,
      route: `/apps/${encodeURIComponent(application.id)}`,
    }))
  }

  public mountApplication(id: string): RuntimeApplicationDefinition {
    const definition = this.get(id)
    if (!definition) {
      throw new Error(`Unregistered HHS runtime application: ${id}`)
    }
    return definition
  }

  public byAuthority(authority: RuntimeApplicationAuthority): RuntimeApplicationDefinition[] {
    return this.all().filter((application) => application.authority === authority)
  }

  public resolveLazyComponent(id: string): React.LazyExoticComponent<React.ComponentType<any>> {
    const definition = this.get(id)
    if (!definition) {
      return React.lazy(async () => {
        throw new Error(`Unregistered HHS runtime application: ${id}`)
      })
    }
    return React.lazy(definition.lazyLoader)
  }

  public metrics() {
    return {
      registeredApplications: this.applications.size,
      applicationIds: [...this.applications.keys()],
    }
  }
}

export const runtimeApplicationRegistry = new RuntimeApplicationRegistry()

runtimeApplicationRegistry.register({
  id: "runtime_console",
  title: "Runtime Console",
  authority: "runtime",
  description: "Core runtime instrumentation surface",
  lazyLoader: () => import("./RuntimeWindowContent").then((module) => ({
    default: module.RuntimeWindowContent,
  })),
  windowPreset: { width: 520, height: 420, minWidth: 320, minHeight: 220, resizable: true },
  singleton: true,
})

runtimeApplicationRegistry.register({
  id: "calculator",
  title: "Calculator",
  authority: "runtime",
  description: "HHS runtime calculator",
  lazyLoader: () => import("../../runtime_apps/calculator/HHSCalculatorSurface").then((module) => ({
    default: module.HHSCalculatorSurface,
  })),
  windowPreset: { width: 900, height: 620, minWidth: 480, minHeight: 320, resizable: true },
  mobileSupported: true,
})

runtimeApplicationRegistry.register({
  id: "graph_projection",
  title: "Graph Projection",
  authority: "graph",
  description: "Runtime replay graph projection",
  lazyLoader: () => import("../../runtime_apps/calculator/HHSCalculatorGraphProjection").then((module) => ({
    default: module.HHSCalculatorGraphProjection,
  })),
  windowPreset: { width: 720, height: 620, minWidth: 420, minHeight: 320, resizable: true },
})

runtimeApplicationRegistry.register({
  id: "breadboard",
  title: "Breadboard",
  authority: "transport",
  description: "Runtime transport topology surface",
  lazyLoader: () => import("../../runtime_apps/breadboard/HHSRuntimeBreadboard").then((module) => ({
    default: module.HHSRuntimeBreadboard,
  })),
  windowPreset: { width: 980, height: 680, minWidth: 620, minHeight: 420, resizable: true },
})

runtimeApplicationRegistry.register({
  id: "receipt_inspector",
  title: "Receipt Inspector",
  authority: "instrument",
  description: "Receipt lineage inspection surface",
  lazyLoader: () => import("../../runtime_apps/instruments/ReceiptInspector").then((module) => ({
    default: module.default,
  })),
  windowPreset: { width: 920, height: 620, minWidth: 520, minHeight: 320, resizable: true },
})

runtimeApplicationRegistry.register({
  id: "replay_timeline",
  title: "Replay Timeline",
  authority: "instrument",
  description: "Replay continuity timeline surface",
  lazyLoader: () => import("../../runtime_apps/instruments/ReplayTimeline").then((module) => ({
    default: module.default,
  })),
  windowPreset: { width: 920, height: 620, minWidth: 520, minHeight: 320, resizable: true },
})

runtimeApplicationRegistry.register({
  id: "pass189_hqlh",
  title: "Pass 189 HQLH Runtime",
  authority: "runtime",
  description: "Exact Lo Shu 41, P+1 membrane, XNOR ternary, V72, Hash72/Hash216 hydration authority",
  lazyLoader: () => import("../../runtime_apps/hqlh/Pass189HQLHSurface").then((module) => ({
    default: module.default,
  })),
  windowPreset: { width: 1180, height: 760, minWidth: 640, minHeight: 420, resizable: true },
  singleton: true,
  mobileSupported: true,
})

runtimeApplicationRegistry.register({
  id: "pass190_operation_fabric",
  title: "Pass 190 Operation Fabric",
  authority: "runtime",
  description: "Canonical operation registry, persistent Hash72 receipts, generated SDKs, and resumable WebSocket events",
  lazyLoader: () => import("../../runtime_apps/pass190/Pass190OperationFabricSurface").then((module) => ({
    default: module.default,
  })),
  windowPreset: { width: 1180, height: 760, minWidth: 680, minHeight: 440, resizable: true },
  singleton: true,
  mobileSupported: true,
})
