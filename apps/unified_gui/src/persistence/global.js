import {
  deleteWorkspace,
  loadWorkspace,
  openWorkspaceDatabase,
  saveWorkspace,
} from "./indexeddb.js";

globalThis.HHSPersistence = Object.freeze({
  openWorkspaceDatabase,
  saveWorkspace,
  loadWorkspace,
  deleteWorkspace,
});
