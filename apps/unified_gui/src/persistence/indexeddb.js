const DATABASE_NAME = "hhs-pass157-unified-gui";
const DATABASE_VERSION = 1;
const STORE_NAME = "workspaces";

function requestResult(request) {
  return new Promise((resolve, reject) => {
    request.addEventListener("success", () => resolve(request.result), { once: true });
    request.addEventListener("error", () => reject(request.error ?? new Error("PERSISTENCE_FAILED")), { once: true });
  });
}

export async function openWorkspaceDatabase() {
  if (typeof indexedDB === "undefined") throw new Error("CAPABILITY_UNAVAILABLE:INDEXEDDB");
  const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION);
  request.addEventListener("upgradeneeded", () => {
    const database = request.result;
    if (!database.objectStoreNames.contains(STORE_NAME)) {
      database.createObjectStore(STORE_NAME, { keyPath: "workspace_id" });
    }
  }, { once: true });
  return requestResult(request);
}

function validateBundle(bundle) {
  if (!bundle || typeof bundle !== "object") throw new TypeError("workspace bundle required");
  if (bundle.schema !== "HHS_PASS157_WORKSPACE_BUNDLE_V1") throw new Error("PERSISTENCE_CORRUPTED");
  if (!bundle.state?.state_hash72 || !bundle.physics?.state_hash72) throw new Error("PERSISTENCE_CORRUPTED");
}

export async function saveWorkspace(workspaceId, bundle) {
  if (!/^[A-Za-z0-9_.:-]{1,128}$/.test(workspaceId)) throw new Error("INVALID_WORKSPACE_IDENTIFIER");
  validateBundle(bundle);
  const database = await openWorkspaceDatabase();
  const transaction = database.transaction(STORE_NAME, "readwrite");
  const record = Object.freeze({
    workspace_id: workspaceId,
    schema_version: 1,
    contract_version: "HHS-P157-UHAG-PSME@1.0.0",
    source_commitment: bundle.state.state_hash72,
    content_hash72: bundle.physics.state_hash72,
    migration_version: 1,
    bundle,
  });
  await requestResult(transaction.objectStore(STORE_NAME).put(record));
  await new Promise((resolve, reject) => {
    transaction.addEventListener("complete", resolve, { once: true });
    transaction.addEventListener("abort", () => reject(transaction.error ?? new Error("PERSISTENCE_FAILED")), { once: true });
  });
  database.close();
  return record;
}

export async function loadWorkspace(workspaceId) {
  const database = await openWorkspaceDatabase();
  const transaction = database.transaction(STORE_NAME, "readonly");
  const record = await requestResult(transaction.objectStore(STORE_NAME).get(workspaceId));
  database.close();
  if (!record) return null;
  try {
    validateBundle(record.bundle);
  } catch (error) {
    return Object.freeze({ classification: "PERSISTENCE_CORRUPTED", quarantined: true, workspace_id: workspaceId });
  }
  return record;
}

export async function deleteWorkspace(workspaceId) {
  const database = await openWorkspaceDatabase();
  const transaction = database.transaction(STORE_NAME, "readwrite");
  await requestResult(transaction.objectStore(STORE_NAME).delete(workspaceId));
  database.close();
  return Object.freeze({ classification: "WORKSPACE_DELETED", workspace_id: workspaceId });
}
