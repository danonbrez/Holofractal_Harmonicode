export type WorkspaceAuthorityStatus =
  | "WORKSPACE_DISCONNECTED"
  | "WORKSPACE_CONNECTING"
  | "WORKSPACE_READ_ONLY"
  | "WORKSPACE_LIVE"
  | "WORKSPACE_EXECUTING"
  | "WORKSPACE_REPLAYING"
  | "WORKSPACE_RECONSTRUCTING"
  | "WORKSPACE_DEGRADED"
  | "WORKSPACE_AUTHORITY_REJECTED"

export interface WorkspaceObjectReference {
  schema: "HHS_WORKSPACE_OBJECT_REFERENCE_V1"
  project_id: string
  object_id: string
  object_type: string
  source_uri: string
  root_hash72: string
  lifecycle_state: string
  authority: "HHS_RUNTIME_WORKSPACE_AUTHORITY_V1"
}

export interface WorkspaceProjectionState {
  schema: "HHS_VISUAL_RUNTIME_OS_WORKSPACE_V1"
  authorityStatus: WorkspaceAuthorityStatus
  projectId: string | null
  selectedObjectId: string | null
  objects: WorkspaceObjectReference[]
  commandHistory: unknown[]
  lastReceiptHash72: string | null
  frontendCacheIsAuthority: false
  workspaceRole: "REQUEST_AND_PROJECTION_ONLY"
}

export class WorkspaceProjectionStore {
  private state: WorkspaceProjectionState = {
    schema: "HHS_VISUAL_RUNTIME_OS_WORKSPACE_V1",
    authorityStatus: "WORKSPACE_CONNECTING",
    projectId: null,
    selectedObjectId: null,
    objects: [],
    commandHistory: [],
    lastReceiptHash72: null,
    frontendCacheIsAuthority: false,
    workspaceRole: "REQUEST_AND_PROJECTION_ONLY",
  }

  snapshot(): WorkspaceProjectionState {
    return {
      ...this.state,
      objects: [...this.state.objects],
      commandHistory: [...this.state.commandHistory],
      frontendCacheIsAuthority: false,
    }
  }

  applyAuthorityFeedback(feedback: any): WorkspaceProjectionState {
    const status = feedback?.ok === false
      ? "WORKSPACE_AUTHORITY_REJECTED"
      : "WORKSPACE_LIVE"
    this.state = {
      ...this.state,
      authorityStatus: status,
      projectId: feedback?.project?.project_id ?? feedback?.result?.project?.project_id ?? this.state.projectId,
      lastReceiptHash72: feedback?.receipt_hash72 ?? feedback?.result?.receipt_hash72 ?? this.state.lastReceiptHash72,
      commandHistory: [...this.state.commandHistory, feedback].slice(-64),
      frontendCacheIsAuthority: false,
    }
    return this.snapshot()
  }

  selectObject(objectId: string): WorkspaceProjectionState {
    this.state = {
      ...this.state,
      selectedObjectId: objectId,
      frontendCacheIsAuthority: false,
    }
    return this.snapshot()
  }
}
