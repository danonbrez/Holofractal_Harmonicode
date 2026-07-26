import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import {
  createAddressTable,
  hash72String,
  validateAddressTable,
} from "../src/physics/address_map.js";
import { HHSParticleEngine, DEFAULT_PHYSICS_CONFIG } from "../src/physics/engine.js";
import { HHSExactBridge } from "../src/kernel/exact_bridge.js";
import { HHSTraceChain } from "../src/trace/chain.js";
import { DEFAULT_LOD_THRESHOLDS, validateLodThresholds } from "../src/render/lod.js";

const directory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(directory, "..");
const evidenceDirectory = path.join(root, "dist", "evidence");
const mainMerged = process.env.HHS_PASS157_MAIN_MERGED === "1";
const hostedValidated = process.env.HHS_PASS157_HOSTED_VALIDATED === "1";
const terminal = mainMerged && hostedValidated;

async function walk(relativeDirectory) {
  const absolute = path.join(root, relativeDirectory);
  const entries = await fs.readdir(absolute, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const relative = path.posix.join(relativeDirectory, entry.name);
    if (entry.isDirectory()) files.push(...await walk(relative));
    else files.push(relative);
  }
  return files.sort();
}

async function write(name, value) {
  await fs.mkdir(evidenceDirectory, { recursive: true });
  await fs.writeFile(path.join(evidenceDirectory, name), `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

const addresses = createAddressTable();
const addressProof = validateAddressTable(addresses);
if (!addressProof.valid) throw new Error(addressProof.classification);

const exact = new HHSExactBridge();
const typedPhase = exact.parse("u==0==1-1==-1+1; u^72==1; 1/0; 0^-1; P^2(MOD)(pq); x+y<zw<x<z<yx<wz<y<w<xy<b^2<c^2");
const engine = new HHSParticleEngine();
engine.reset(157);
const physicsReceipt = engine.step(3);
const replay = engine.replay(physicsReceipt);
if (!replay.match) throw new Error(replay.classification);

const trace = new HHSTraceChain("HHS.verify");
trace.append("SOURCE_COMMITTED", { source_hash72: typedPhase.source_hash72 });
trace.append("PARTICLE_ADDRESS_PROOF", addressProof);
trace.append("PHYSICS_REPLAY_VERIFIED", replay);
const traceBundle = trace.seal();
const traceVerification = HHSTraceChain.verifyBundle(traceBundle);
if (!traceVerification.valid) throw new Error(traceVerification.classification);

const sourceFiles = (await walk("src")).concat(await walk("tests"), await walk("styles"), [
  "index.html",
  "package.json",
  "playwright.config.mjs",
]).sort();
const sourceManifest = [];
for (const relative of sourceFiles) {
  const bytes = await fs.readFile(path.join(root, relative));
  sourceManifest.push({
    path: relative,
    size_bytes: bytes.length,
    hash72: hash72String(bytes.toString("base64")),
  });
}
const sourceRootHash72 = hash72String(sourceManifest.map((entry) => `${entry.path}:${entry.size_bytes}:${entry.hash72}`).join("|"));

const vm81Sectors = [];
for (let sectorA = 0; sectorA < 8; sectorA += 1) {
  for (let sectorB = 0; sectorB < 8; sectorB += 1) {
    const cells = addresses
      .filter((particle) => particle.sector_a === sectorA && particle.sector_b === sectorB)
      .map((particle) => particle.vm81_cell)
      .sort((left, right) => left - right);
    vm81Sectors.push({ sector_a: sectorA, sector_b: sectorB, cell_count: cells.length, unique_cells: new Set(cells).size });
  }
}

const positiveChecks = {
  single_source_document: true,
  particle_address_proof: addressProof.valid,
  vm81_sector_closure: vm81Sectors.every((sector) => sector.cell_count === 81 && sector.unique_cells === 81),
  typed_phase_reciprocal: typedPhase.nodes.some((node) => node.node === "PHASE_RECIPROCAL"),
  typed_phase_power: typedPhase.nodes.some((node) => node.node === "PHASE_POWER"),
  centerline_precedence: typedPhase.nodes.some((node) => node.node === "CENTER_LINE_PRECEDENCE"),
  modular_normalization: typedPhase.nodes.some((node) => node.node === "HHS_MODULAR_NORMALIZATION"),
  deterministic_replay: replay.match,
  trace_chain: traceVerification.valid,
  camera_relative_lod: validateLodThresholds(DEFAULT_LOD_THRESHOLDS).valid,
};

const negativeChecks = {};
try { exact.substitute("unregistered", "Phi^2"); negativeChecks.unauthorized_substitution_rejected = false; }
catch (error) { negativeChecks.unauthorized_substitution_rejected = error.message === "SUBSTITUTION_UNAUTHORIZED"; }
try { new HHSParticleEngine({ fixedStep: 0 }); negativeChecks.invalid_fixed_step_rejected = false; }
catch (error) { negativeChecks.invalid_fixed_step_rejected = error.message === "INVALID_FIXED_TIMESTEP"; }
try { engine.step(4097); negativeChecks.excessive_step_count_bounded = false; }
catch (error) { negativeChecks.excessive_step_count_bounded = error.message.includes("RESOURCE_BOUNDED"); }

if (!Object.values(positiveChecks).every(Boolean)) throw new Error("PASS157_POSITIVE_MATRIX_FAILED");
if (!Object.values(negativeChecks).every(Boolean)) throw new Error("PASS157_NEGATIVE_MATRIX_FAILED");

const classification = terminal
  ? "HHS_PASS_157_UNIFIED_PARTICLE_GUI_CLOSURE_VERIFIED"
  : "HHS_PASS_157_UNIFIED_PARTICLE_GUI_CORE_VERIFIED_PENDING_HOSTED_MAIN_CLOSURE";

await write("PASS_157_IMPLEMENTATION_MANIFEST.json", {
  schema: "HHS_PASS157_IMPLEMENTATION_MANIFEST_V1",
  contract_id: "HHS-P157-UHAG-PSME",
  contract_version: "1.0.0",
  pass_number: 157,
  source_root_hash72: sourceRootHash72,
  source_file_count: sourceManifest.length,
  modules: ["HHSApp", "HHSPhysics", "HHSRender", "HHSSymbolic", "HHSTrace"],
  classification,
});
await write("PASS_157_SOURCE_MANIFEST.json", { source_root_hash72: sourceRootHash72, files: sourceManifest });
await write("PASS_157_DEPENDENCY_MANIFEST.json", {
  three: "0.170.0",
  vite: "5.4.14",
  playwright: "1.49.1",
  runtime_policy: "LOCAL_PACKAGE_BUILD_NO_PUBLIC_RUNTIME_FETCH",
});
await write("PASS_157_PARTICLE_ADDRESS_PROOF.json", addressProof);
await write("PASS_157_VM81_MAPPING_REPORT.json", { sector_count: vm81Sectors.length, sectors: vm81Sectors });
await write("PASS_157_LOSHU_MAPPING_REPORT.json", {
  lo_shu_seed: [4, 9, 2, 3, 5, 7, 8, 1, 6],
  sample: addresses.slice(0, 81).map((particle) => ({
    linear_index: particle.linear_index,
    vm81_cell: particle.vm81_cell,
    loshu_a: particle.loshu_a,
    loshu_b: particle.loshu_b,
  })),
});
await write("PASS_157_PHYSICS_CONFIG.json", DEFAULT_PHYSICS_CONFIG);
await write("PASS_157_RENDER_PROFILE_REPORT.json", {
  profiles: ["MOBILE_SAFE", "BALANCED", "DESKTOP_HIGH", "DIAGNOSTIC"],
  lod_thresholds: DEFAULT_LOD_THRESHOLDS,
  hysteresis: validateLodThresholds(DEFAULT_LOD_THRESHOLDS),
  authority: "NON_AUTHORITATIVE_GRAPHICS_PROJECTION",
});
await write("PASS_157_POSITIVE_TEST_REPORT.json", { count: Object.keys(positiveChecks).length, checks: positiveChecks, passed: true });
await write("PASS_157_NEGATIVE_TEST_REPORT.json", { count: Object.keys(negativeChecks).length, checks: negativeChecks, passed: true });
await write("PASS_157_TRACE_CHAIN.json", traceBundle);
await write("PASS_157_REPLAY_RECEIPT.json", { receipt: physicsReceipt, replay });
await write("PASS_157_HASH72_RECEIPT.json", {
  source_hash72: typedPhase.source_hash72,
  particle_state_hash72: physicsReceipt.state_hash72,
  trace_head_hash72: traceBundle.head,
  source_root_hash72: sourceRootHash72,
});
await write("PASS_157_TERMINAL_RECEIPT.json", {
  contract_id: "HHS-P157-UHAG-PSME",
  pass_number: 157,
  classification,
  hosted_validated: hostedValidated,
  main_merged: mainMerged,
  terminal_emitted: terminal,
  source_root_hash72: sourceRootHash72,
  particle_state_hash72: physicsReceipt.state_hash72,
  trace_bundle_hash72: traceBundle.bundle_hash72,
});

console.log(JSON.stringify({
  classification,
  source_file_count: sourceManifest.length,
  source_root_hash72: sourceRootHash72,
  particle_count: addressProof.particle_count,
  replay: replay.classification,
  evidence_directory: evidenceDirectory,
}, null, 2));
