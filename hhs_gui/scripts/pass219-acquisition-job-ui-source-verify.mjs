import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const here = path.dirname(fileURLToPath(import.meta.url))
const gui = path.resolve(here, "..")
const root = path.resolve(gui, "..")
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8")
const assert = (condition, message) => { if (!condition) throw new Error(message) }

const panel = read("hhs_gui/runtime_os/workspace/OpenSourceAcquisitionPanel.tsx")
const control = read("hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx")
const server = read("hhs_backend/pass174_server.py")
const routes = read("hhs_backend/api/pass219_acquisition_routes.py")
const service = read("hhs_backend/pass219_acquisition_job_service.py")

assert(control.includes('import OpenSourceAcquisitionPanel from "./OpenSourceAcquisitionPanel"'), "mobile control center does not import acquisition panel")
assert(control.includes("<OpenSourceAcquisitionPanel />"), "mobile control center does not mount acquisition panel")
for (const token of [
  "/api/v1/pass174/acquisition/status",
  "/api/v1/pass174/acquisition/jobs",
  "/replay",
  "SOURCE_ONLY_V1",
  "Acquire + verify",
  "Replay offline",
]) assert(panel.includes(token), `acquisition panel missing ${token}`)

for (const token of [
  '@router.get("/status")',
  '@router.get("/projectors")',
  '@router.post("/jobs")',
  '@router.get("/jobs")',
  '@router.get("/jobs/{job_id}")',
  '@router.get("/jobs/{job_id}/receipt")',
  '@router.post("/jobs/{job_id}/replay")',
]) assert(routes.includes(token), `acquisition routes missing ${token}`)

assert(server.includes("pass219_acquisition_router"), "Pass 174 server does not import acquisition router")
assert(server.indexOf("app.include_router(pass219_acquisition_router)") < server.indexOf("app.router.routes.extend(_deferred_api_fallback_routes)"), "acquisition router is registered after API fallback")
assert(service.includes("jobs.sqlite3"), "persistent acquisition job ledger missing")
assert(service.includes("REPLAY_VERIFIED"), "offline replay closure missing")
assert(service.includes("canonical_authority_minted"), "candidate authority boundary missing")

console.log(JSON.stringify({
  ok: true,
  surface: "PASS219_ACQUISITION_JOB_UI_V1",
  mobile_panel: true,
  persistent_jobs: true,
  replay: true,
  route_order: "BEFORE_FALLBACK",
}))
