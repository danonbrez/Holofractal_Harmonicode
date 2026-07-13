import type { WorkspaceObjectReference } from "./WorkspaceProjectionStore"

export class WorkspaceObjectRegistry {
  private readonly objects = new Map<string, WorkspaceObjectReference>()
  readonly frontendRegistryIsProjectionOnly = true

  upsert(reference: WorkspaceObjectReference): void {
    this.objects.set(reference.object_id, reference)
  }

  get(objectId: string): WorkspaceObjectReference | undefined {
    return this.objects.get(objectId)
  }

  list(): WorkspaceObjectReference[] {
    return Array.from(this.objects.values()).sort((a, b) => a.object_id.localeCompare(b.object_id))
  }
}
