import { THEMES, themeById, customTheme } from "./theme-registry.js";
import { TEMPLATES, templateById } from "./template-registry.js";
import { FEATURES, featureById, MODES } from "./feature-registry.js";
import { APPLICATIONS, applicationById, applicationsForFeature } from "./application-registry.js";
import { extractRuntimeSummary, RUNTIME_COMMANDS } from "./runtime-bridge.js";
import { AgenticSelfPlayHarness } from "./self-play-harness.js";
import { V1_SCOPE } from "./prompt-contracts.js";

const escapeHTML = (value) => String(value ?? "").replace(/[&<>'"]/g, (character) => ({
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  "'": "&#39;",
  '"': "&quot;"
})[character]);

const clone = (value) => JSON.parse(JSON.stringify(value));

function downloadJSON(name, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

createSelfPlayHarness() {
  return new AgenticSelfPlayHarness({
    executeRuntimeCommand: (commandName, args = {}) => this.commands.execute(`runtime.${commandName}`, args, { ui: this, source: "self-play" }),
    extractRuntimeSummary,
    telemetry: this.telemetry
  });
}

async runSelfPlaySuite() {
  try {
    const report = await this.createSelfPlayHarness().runSuite();
    this.journal.append("SELF_PLAY_SUITE_REPORT", {
      completionRate: report.summary.completionRate,
      failures: report.summary.failures,
      apiCoverage: Object.keys(report.apiCoverage)
    }, "NON_AUTHORITATIVE_USABILITY_EVALUATION");
    this.renderTelemetry();
    this.refreshSurfacesByApplication("telemetry");
    this.toast(`Self-play suite complete (${Math.round(report.summary.completionRate * 100)}%).`, report.summary.failures ? "error" : "success");
    return report;
  } catch (error) {
    this.toast(String(error.message ?? error), "error");
    return null;
  }
}

async runCapabilityLoop() {
  try {
    const report = await this.createSelfPlayHarness().runCapabilityLoop();
    this.journal.append("SELF_PLAY_LOOP_REPORT", {
      completionDelta: report.delta.completionDelta,
      meanLatencyDeltaMs: report.delta.meanLatencyDeltaMs,
      errorDelta: report.delta.errorDelta
    }, "NON_AUTHORITATIVE_USABILITY_EVALUATION");
    this.renderTelemetry();
    this.refreshSurfacesByApplication("telemetry");
    this.toast(`Capability loop complete (Δcompletion ${report.delta.completionDelta.toFixed(2)}).`, report.delta.errorDelta > 0 ? "error" : "success");
    return report;
  } catch (error) {
    this.toast(String(error.message ?? error), "error");
    return null;
  }
}

function hexToRgb(hex) {
  const value = hex.replace("#", "");
  return [0, 2, 4].map((offset) => parseInt(value.slice(offset, offset + 2), 16));
}

function compact(value, limit = 280) {
  let text;
  try {
    text = JSON.stringify(value);
  } catch {
    text = String(value);
  }
  return text.length > limit ? `${text.slice(0, limit)}…` : text;
}

export class UIShell {
  constructor({ renderer, bridge, world, journal, sessions, workspace, replay, telemetry, commands, projects, scene, assets, routes, simulation }) {
    this.renderer = renderer;
    this.bridge = bridge;
    this.world = world;
    this.journal = journal;
    this.sessions = sessions;
    this.workspace = workspace;
    this.replay = replay;
    this.telemetry = telemetry;
    this.commands = commands;
    this.projects = projects;
    this.scene = scene;
    this.assets = assets;
    this.routes = routes;
    this.simulation = simulation;
    this.themeId = "cyan-blue";
    this.templateId = "operator-default";
    this.modeId = "overview";
    this.activeFeature = "dashboard";
    this.runtimeSummary = {};
    this.events = [];
    this.eventCount = 0;
    this.metricsHistory = [];
    this.explore = false;
    this.customThemeValue = null;
    this.sessionSaveTimer = null;
    this.projectSaveTimer = null;
    this.loadingProject = false;
    this.dragState = null;
    this.resizeState = null;
    this.cache();
    this.registerCommands();
    this.renderStaticControls();
    this.bind();
    this.restoreCustomTheme();
    this.restoreActiveProject();
    this.restoreActiveSession();
    this.journal.append("ENVIRONMENT_BOOT", {
      stage: "PASS_152",
      renderer: this.renderer.backend,
      session: this.sessions.activeSessionId
    }, "PRESENTATION_ONLY");
  }

  cache() {
    const ids = [
      "renderer-status", "runtime-status", "fps-value", "connection-mode", "session-name",
      "vm81-state", "runtime-step", "active-cell", "active-opcode", "receipt-hash", "event-count",
      "channel-list", "event-log", "dock", "mode-switcher", "workspace-card", "workspace-eyebrow",
      "workspace-title", "workspace-description", "workspace-content", "theme-grid", "template-select",
      "command-palette", "palette-search", "palette-results", "toast-region", "cell-inspector",
      "cell-inspector-content", "explore-mode-button", "workspace-file-input", "surface-layer",
      "application-library", "session-select", "session-summary", "replay-range", "replay-status",
      "replay-current", "telemetry-summary", "journal-integrity", "crosshair"
    ];
    this.el = Object.fromEntries(ids.map((id) => [id, document.getElementById(id)]));
  }

  registerCommands() {
    for (const commandName of Object.keys(RUNTIME_COMMANDS)) {
      this.commands.registerRuntime(commandName, { label: `Runtime: ${commandName}` });
    }

    this.commands
      .register({
        id: "local.visual-pulse",
        label: "Visual pulse",
        handler: () => this.renderer.pulse()
      })
      .register({
        id: "local.camera-reset",
        label: "Reset camera",
        handler: () => this.renderer.resetCamera(templateById(this.templateId))
      })
      .register({
        id: "local.surface-grid",
        label: "Arrange surfaces in grid",
        handler: () => this.workspace.arrange("grid")
      })
      .register({
        id: "local.surface-cascade",
        label: "Arrange surfaces in cascade",
        handler: () => this.workspace.arrange("cascade")
      })
      .register({
        id: "local.replay-load",
        label: "Load projection replay",
        authority: "NON_AUTHORITATIVE_REPLAY",
        handler: () => this.replay.load(this.journal.timeline())
      })
      .register({
        id: "local.replay-toggle",
        label: "Toggle projection replay",
        authority: "NON_AUTHORITATIVE_REPLAY",
        handler: () => this.replay.toggle()
      })
      .register({
        id: "local.session-snapshot",
        label: "Save session snapshot",
        handler: () => this.saveSessionSnapshot("Command snapshot")
      })
      .register({
        id: "local.entity-create",
        label: "Create holographic entity",
        authority: "PRESENTATION_SCENE_AUTHORING",
        handler: ({ kind = "orb" } = {}) => this.scene.createPrimitive(kind)
      })
      .register({
        id: "local.world-snapshot",
        label: "Save deterministic world snapshot",
        authority: "PROJECT_AUTHORING_METADATA",
        handler: () => this.saveWorldSnapshot("Command world snapshot")
      })
      .register({
        id: "local.simulation-step",
        label: "Advance presentation simulation",
        authority: "NON_AUTHORITATIVE_PRESENTATION_SIMULATION",
        handler: ({ steps = 1 } = {}) => this.simulation.step(steps)
      })
      .register({
        id: "local.self-play-suite",
        label: "Run agentic self-play suite",
        authority: "NON_AUTHORITATIVE_USABILITY_EVALUATION",
        handler: () => this.runSelfPlaySuite()
      })
      .register({
        id: "local.self-play-loop",
        label: "Run capability-maximization loop",
        authority: "NON_AUTHORITATIVE_USABILITY_EVALUATION",
        handler: () => this.runCapabilityLoop()
      });
  }

  renderStaticControls() {
    this.renderDock();
    this.renderModes();
    this.renderThemes();
    this.renderTemplates();
    this.renderChannels();
    this.renderApplications();
    this.renderSessions();
    this.renderReplay();
    this.renderTelemetry();
  }

  bind() {
    this.renderer.addEventListener("metrics", ({ detail }) => {
      this.metricsHistory.push(detail.fps);
      this.metricsHistory = this.metricsHistory.slice(-60);
      this.telemetry.recordRenderer(detail);
      this.el["fps-value"].textContent = String(detail.fps);
      this.el["renderer-status"].className = "status-chip online";
      this.el["renderer-status"].innerHTML = `<i></i> ${detail.backend.toUpperCase()} ACTIVE`;
      this.renderTelemetry();
      this.refreshSurfacesByApplication("telemetry");
    });

    this.renderer.addEventListener("cell-select", ({ detail }) => {
      this.world.select(detail.cellId, "spatial-pointer");
    });

    this.renderer.addEventListener("explore-change", ({ detail }) => {
      this.explore = detail.enabled;
      document.documentElement.dataset.explore = String(this.explore);
      this.el["explore-mode-button"].classList.toggle("active", this.explore);
      this.el["explore-mode-button"].textContent = this.explore ? "EXIT EXPLORE" : "EXPLORE";
      this.scheduleSessionSave();
    });

    this.world.addEventListener("selection", ({ detail }) => {
      this.renderer.setSelection(detail.cell?.id ?? -1);
      this.renderCell(detail.cell);
      this.refreshSurfacesByApplication("vm81-lattice");
      this.scheduleSessionSave();
    });

    this.world.addEventListener("cell-update", () => {
      this.refreshSurfacesByApplication("vm81-lattice");
      this.scheduleSessionSave();
    });

    this.world.addEventListener("runtime-binding", ({ detail }) => {
      this.renderer.setActiveCell(detail.activeCell);
      this.el["active-cell"].textContent = detail.activeCell === null || detail.activeCell === undefined
        ? "—"
        : String(detail.activeCell + 1);
      this.refreshRuntimeFields();
      for (const id of ["system-overview", "vm81-lattice", "opcode-trace", "runtime-control", "telemetry"]) {
        this.refreshSurfacesByApplication(id);
      }
    });

    this.journal.addEventListener("entry", ({ detail }) => {
      this.events.unshift(detail);
      this.events = this.events.slice(0, 80);
      this.replay.append(detail);
      this.renderEvents();
      this.renderReplay();
    });

    this.journal.addEventListener("view-clear", () => {
      this.events = [];
      this.renderEvents();
    });

    this.bridge.addEventListener("channel-status", ({ detail }) => {
      this.telemetry.recordChannel(detail.channel, detail.status);
      this.renderChannels(detail.statuses);
      this.refreshRuntimeStatus(detail.statuses);
      this.renderTelemetry();
    });

    this.bridge.addEventListener("runtime-event", ({ detail }) => {
      this.eventCount += 1;
      this.el["event-count"].textContent = String(this.eventCount);
      const summary = extractRuntimeSummary(detail.payload);
      this.telemetry.recordRuntime(summary, detail.channel);
      this.ingestPayload(detail.payload);
      this.journal.append(`RUNTIME_${String(detail.channel).toUpperCase()}_EVENT`, {
        summary,
        preview: compact(detail.payload)
      }, "BACKEND_EVENT_PROJECTION");
    });

    this.bridge.addEventListener("bridge-error", ({ detail }) => {
      this.journal.append("CHANNEL_ERROR", detail, "ERROR_PROJECTION");
    });

    this.bridge.addEventListener("command-result", ({ detail }) => {
      this.ingestPayload(detail.payload);
      this.refreshSurfacesByApplication("elastic-closure");
      this.journal.append(`COMMAND_${detail.command.toUpperCase()}_RESULT`, {
        durationMs: detail.durationMs,
        preview: compact(detail.payload)
      }, "BACKEND_RESPONSE_PROJECTION");
    });

    this.bridge.addEventListener("command-error", ({ detail }) => {
      this.journal.append(`COMMAND_${detail.command.toUpperCase()}_ERROR`, detail, "ERROR_PROJECTION");
    });

    this.commands.addEventListener("command-complete", ({ detail }) => {
      this.toast(`${detail.label} completed.`, "success");
    });
    this.commands.addEventListener("command-failure", ({ detail }) => {
      this.toast(`${detail.label}: ${detail.error}`, "error");
    });

    this.workspace.addEventListener("changed", () => {
      this.renderSurfaces();
      this.scheduleSessionSave();
    });
    this.workspace.addEventListener("surface-updated", () => {
      this.renderSurfaces();
      this.scheduleSessionSave();
    });

    this.sessions.addEventListener("session-selected", ({ detail }) => {
      this.applySession(detail);
      this.renderSessions();
    });
    this.sessions.addEventListener("session-created", () => this.renderSessions());
    this.sessions.addEventListener("session-updated", () => this.renderSessions());
    this.sessions.addEventListener("session-deleted", () => this.renderSessions());
    this.sessions.addEventListener("storage-error", ({ detail }) => this.toast(detail.error, "error"));

    this.projects.addEventListener("project-selected", () => {
      this.restoreActiveProject();
      this.renderSurfaces();
      this.journal.append("PROJECT_SELECTED", { projectId: this.projects.activeProjectId }, "PROJECT_AUTHORING_METADATA");
    });
    this.projects.addEventListener("world-selected", () => {
      this.restoreActiveProject();
      this.renderSurfaces();
      this.journal.append("WORLD_SELECTED", { worldId: this.projects.activeWorld?.id }, "PROJECT_AUTHORING_METADATA");
    });
    this.projects.addEventListener("storage-error", ({ detail }) => this.toast(detail.error, "error"));

    this.scene.addEventListener("changed", () => {
      if (!this.loadingProject) this.scheduleProjectSave();
      this.refreshSurfacesByApplication("scene-composer");
      this.refreshSurfacesByApplication("entity-inspector");
      this.refreshSurfacesByApplication("simulation-console");
    });
    this.scene.addEventListener("selection", () => this.refreshSurfacesByApplication("entity-inspector"));
    this.assets.addEventListener("changed", () => {
      if (!this.loadingProject) this.scheduleProjectSave();
      this.refreshSurfacesByApplication("asset-vault");
    });
    this.routes.addEventListener("changed", () => {
      if (!this.loadingProject) this.scheduleProjectSave();
      this.refreshSurfacesByApplication("world-router");
    });
    this.routes.addEventListener("navigation", ({ detail }) => {
      this.projects.selectWorld(detail.to);
      this.journal.append("WORLD_ROUTE_NAVIGATION", detail, "PRESENTATION_NAVIGATION_ONLY");
    });
    this.simulation.addEventListener("step", ({ detail }) => {
      this.scheduleProjectSave();
      this.refreshSurfacesByApplication("simulation-console");
      this.refreshSurfacesByApplication("entity-inspector");
      this.journal.append("SIMULATION_STEP", detail, "NON_AUTHORITATIVE_PRESENTATION_SIMULATION");
    });
    this.simulation.addEventListener("state", () => this.refreshSurfacesByApplication("simulation-console"));

    this.replay.addEventListener("frame", ({ detail }) => {
      this.renderer.setReplayPhase(detail.total > 1 ? detail.cursor / (detail.total - 1) : 0);
      this.world.applyReplayFrame(detail);
      this.renderReplay();
      this.refreshSurfacesByApplication("replay-timeline");
    });
    this.replay.addEventListener("state", () => this.renderReplay());
    this.replay.addEventListener("loaded", () => this.renderReplay());
    this.replay.addEventListener("timeline-change", () => this.renderReplay());

    for (const [id, key] of [
      ["modulus-control", "modulus"],
      ["curiosity-control", "curiosity"],
      ["rigidity-control", "rigidity"]
    ]) {
      document.getElementById(id).addEventListener("input", (event) => {
        const value = Number(event.target.value);
        const output = document.getElementById(id.replace("control", "output"));
        output.value = key === "modulus" ? String(value) : value.toFixed(2);
        this.renderer.setParameters({ [key]: value });
        this.journal.append("PRESENTATION_PARAMETER", { key, value }, "PRESENTATION_ONLY");
        this.scheduleSessionSave();
      });
    }

    document.getElementById("visual-pulse-button").addEventListener("click", () => this.runCommand("local.visual-pulse"));
    document.getElementById("reset-camera-button").addEventListener("click", () => this.runCommand("local.camera-reset"));
    document.getElementById("focus-active-button").addEventListener("click", () => {
      if (this.world.activeCell === null) {
        this.toast("No runtime-active cell is available.", "error");
        return;
      }
      this.world.select(this.world.activeCell, "active-focus");
      this.renderer.focusCell(this.world.activeCell);
    });
    document.getElementById("explore-mode-button").addEventListener("click", () => this.renderer.setExplore(!this.explore));
    document.getElementById("reconnect-button").addEventListener("click", () => {
      this.bridge.connectAll();
      this.journal.append("RECONNECT_REQUEST", {}, "ORCHESTRATION_REQUEST");
    });
    document.getElementById("clear-events-button").addEventListener("click", () => this.journal.clearView());
    document.getElementById("export-journal-button").addEventListener("click", () => downloadJSON("hhs_projection_journal_v3.json", this.journal.export()));
    document.getElementById("verify-journal-button").addEventListener("click", () => this.verifyJournal());
    document.getElementById("workspace-close").addEventListener("click", () => this.el["workspace-card"].classList.remove("open"));
    document.getElementById("clear-selection-button").addEventListener("click", () => {
      this.world.clearSelection();
      this.renderer.clearFocus();
    });
    document.getElementById("command-palette-button").addEventListener("click", () => this.openPalette());
    document.getElementById("reduce-motion-button").addEventListener("click", (event) => this.toggleReducedMotion(event.currentTarget));
    document.getElementById("surface-grid-button").addEventListener("click", () => this.workspace.arrange("grid"));
    document.getElementById("surface-cascade-button").addEventListener("click", () => this.workspace.arrange("cascade"));
    document.getElementById("new-session-button").addEventListener("click", () => this.createSession());
    document.getElementById("rename-session-button").addEventListener("click", () => this.renameSession());
    document.getElementById("snapshot-session-button").addEventListener("click", () => this.saveSessionSnapshot());
    document.getElementById("delete-session-button").addEventListener("click", () => this.deleteSession());
    document.getElementById("export-sessions-button").addEventListener("click", () => downloadJSON("hhs_spatial_sessions_v3.json", this.sessions.export()));
    document.getElementById("replay-load-button").addEventListener("click", () => this.replay.load(this.journal.timeline()));
    document.getElementById("replay-play-button").addEventListener("click", () => this.replay.toggle());
    document.getElementById("replay-prev-button").addEventListener("click", () => this.replay.step(-1));
    document.getElementById("replay-next-button").addEventListener("click", () => this.replay.step(1));
    document.getElementById("replay-speed").addEventListener("change", (event) => this.replay.setSpeed(event.target.value));

    document.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        this.openPalette();
      }
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        this.saveSessionSnapshot("Keyboard snapshot");
      }
      if (event.key === "Escape" && this.explore) {
        this.renderer.setExplore(false);
      }
    });

    this.el["palette-search"].addEventListener("input", () => this.renderPalette(this.el["palette-search"].value));
    this.el["template-select"].addEventListener("change", (event) => this.applyTemplate(event.target.value));
    this.el["session-select"].addEventListener("change", (event) => this.sessions.select(event.target.value));
    this.el["replay-range"].addEventListener("input", (event) => this.replay.seek(Number(event.target.value)));
    document.querySelectorAll("[data-command]").forEach((button) => button.addEventListener("click", () => this.runCommand(`runtime.${button.dataset.command}`, {}, button)));
    document.getElementById("apply-custom-theme").addEventListener("click", () => this.applyCustomTheme());
    document.getElementById("export-workspace-button").addEventListener("click", () => this.exportWorkspace());
    document.getElementById("import-workspace-button").addEventListener("click", () => this.el["workspace-file-input"].click());
    this.el["workspace-file-input"].addEventListener("change", (event) => this.importWorkspace(event.target.files?.[0]));

    window.addEventListener("pointermove", (event) => this.handleGlobalPointerMove(event));
    window.addEventListener("pointerup", () => this.endSurfaceInteraction());
    window.addEventListener("resize", () => {
      this.renderSurfaces();
      this.scheduleSessionSave();
    });
  }

  restoreActiveProject() {
    const project = this.projects.activeProject;
    const world = this.projects.activeWorld;
    if (!project || !world) return;
    this.loadingProject = true;
    try {
      this.scene.load(world.scene ?? {});
      this.assets.load({ assets: project.assets ?? [] });
      this.routes.load({
        worlds: project.worlds.map(({ id, name }) => ({ id, name })),
        routes: world.routes ?? [],
        currentWorldId: world.id
      });
    } finally {
      this.loadingProject = false;
    }
  }

  restoreActiveSession() {
    this.applySession(this.sessions.activeSession);
  }

  applySession(session) {
    if (!session) {
      return;
    }
    this.themeId = session.activeTheme || "cyan-blue";
    this.templateId = session.activeTemplate || "operator-default";
    this.modeId = session.activeMode || "overview";
    this.activeFeature = session.activeFeature || "dashboard";
    if (session.activeProjectId && session.activeProjectId !== this.projects.activeProjectId && this.projects.list().some((project) => project.id === session.activeProjectId)) {
      this.projects.select(session.activeProjectId);
    }
    if (session.activeWorldId && this.projects.activeProject?.worlds.some((world) => world.id === session.activeWorldId)) {
      this.projects.selectWorld(session.activeWorldId);
    }
    if (session.selectedEntityId && this.scene.get(session.selectedEntityId)) this.scene.select(session.selectedEntityId);
    this.applyTheme(this.themeId, false);
    this.applyTemplate(this.templateId, false);
    this.applyMode(this.modeId, false);
    this.openFeature(this.activeFeature, false);
    this.workspace.load(session.surfaces ?? []);
    if (session.camera) {
      this.renderer.loadCamera(session.camera);
    }
    if (session.parameters) {
      this.renderer.setParameters(session.parameters);
      this.syncParameterControls(session.parameters);
    }
    if (Number.isInteger(session.selectedCell)) {
      this.world.select(session.selectedCell, "session");
      this.renderer.focusCell(session.selectedCell);
    } else {
      this.world.clearSelection();
      this.renderer.setSelection(-1);
    }
    this.el["session-name"].textContent = session.name;
    this.renderSessions();
    this.renderSurfaces();
  }

  syncParameterControls(parameters) {
    for (const [id, key] of [
      ["modulus-control", "modulus"],
      ["curiosity-control", "curiosity"],
      ["rigidity-control", "rigidity"]
    ]) {
      const input = document.getElementById(id);
      const value = parameters[key];
      if (value !== undefined) {
        input.value = String(value);
        document.getElementById(id.replace("control", "output")).value = key === "modulus" ? String(value) : Number(value).toFixed(2);
      }
    }
  }

  renderDock() {
    this.el.dock.innerHTML = "";
    for (const feature of FEATURES) {
      const button = document.createElement("button");
      button.className = "dock-button";
      button.dataset.feature = feature.id;
      button.innerHTML = `<span class="glyph">${feature.glyph}</span><span>${feature.label.toUpperCase()}</span>`;
      button.addEventListener("click", () => this.openFeature(feature.id));
      this.el.dock.appendChild(button);
    }
  }

  renderModes() {
    this.el["mode-switcher"].innerHTML = "";
    for (const mode of MODES) {
      const button = document.createElement("button");
      button.className = "mode-button";
      button.dataset.mode = mode.id;
      button.textContent = mode.label.toUpperCase();
      button.addEventListener("click", () => this.applyMode(mode.id));
      this.el["mode-switcher"].appendChild(button);
    }
  }

  applyMode(id, record = true) {
    const mode = MODES.find((candidate) => candidate.id === id) ?? MODES[0];
    this.modeId = mode.id;
    this.renderer.setMode(mode.id);
    document.documentElement.dataset.mode = mode.id;
    document.querySelectorAll(".mode-button").forEach((button) => button.classList.toggle("active", button.dataset.mode === mode.id));
    if (mode.id === "game") {
      this.renderer.setExplore(true);
    }
    if (record) {
      this.journal.append("INTERFACE_MODE", { mode: mode.id }, "PRESENTATION_ONLY");
      this.scheduleSessionSave();
    }
  }

  openFeature(id, open = true) {
    const feature = featureById(id);
    this.activeFeature = feature.id;
    document.querySelectorAll(".dock-button").forEach((button) => button.classList.toggle("active", button.dataset.feature === feature.id));
    this.el["workspace-eyebrow"].textContent = "SPATIAL FEATURE DOMAIN";
    this.el["workspace-title"].textContent = feature.label;
    this.el["workspace-description"].textContent = feature.description;
    this.el["workspace-content"].innerHTML = feature.tiles.map(([title, description, route]) => `
      <section class="feature-tile" data-feature-route="${escapeHTML(route)}">
        <strong>${escapeHTML(title)}</strong>
        <span>${escapeHTML(description)}</span>
        <small class="route">${escapeHTML(route)}</small>
      </section>
    `).join("");
    const applications = applicationsForFeature(feature.id);
    if (applications.length) {
      this.el["workspace-content"].insertAdjacentHTML("beforeend", applications.map((application) => `
        <button class="feature-tile application-tile" data-open-application="${application.id}">
          <strong>${application.glyph} ${escapeHTML(application.label)}</strong>
          <span>${escapeHTML(application.description)}</span>
          <small class="route">${escapeHTML(application.authority)}</small>
        </button>
      `).join(""));
    }
    this.el["workspace-content"].querySelectorAll("[data-open-application]").forEach((button) => {
      button.addEventListener("click", () => this.openApplication(button.dataset.openApplication));
    });
    if (open) {
      this.el["workspace-card"].classList.add("open");
      this.journal.append("FEATURE_OPEN", { feature: feature.id }, "PRESENTATION_ONLY");
      this.scheduleSessionSave();
    }
  }

  renderThemes() {
    this.el["theme-grid"].innerHTML = "";
    for (const theme of THEMES) {
      const button = document.createElement("button");
      button.className = "theme-button";
      button.dataset.theme = theme.id;
      button.title = theme.label;
      button.innerHTML = `<span style="background:linear-gradient(135deg,${theme.colors.join(",")})"></span>`;
      button.addEventListener("click", () => this.applyTheme(theme.id));
      this.el["theme-grid"].appendChild(button);
    }
  }

  restoreCustomTheme() {
    try {
      const raw = localStorage.getItem("hhs-spatial-custom-theme-v3");
      if (raw) {
        this.customThemeValue = JSON.parse(raw);
      }
    } catch {
      this.customThemeValue = null;
    }
  }

  applyTheme(id, record = true) {
    const theme = id === "custom" && this.customThemeValue
      ? customTheme(this.customThemeValue.colors, this.customThemeValue.background)
      : themeById(id);
    this.themeId = theme.id;
    const [primary, secondary, tertiary] = theme.colors;
    const rgb = hexToRgb(primary);
    document.documentElement.style.setProperty("--primary", primary);
    document.documentElement.style.setProperty("--secondary", secondary);
    document.documentElement.style.setProperty("--tertiary", tertiary);
    document.documentElement.style.setProperty("--glow", rgb.join(","));
    document.documentElement.style.setProperty("--environment", theme.background ?? "#020712");
    document.documentElement.dataset.lightTheme = String(Boolean(theme.light));
    this.renderer.setTheme(theme);
    document.querySelectorAll(".theme-button").forEach((button) => button.classList.toggle("active", button.dataset.theme === theme.id));
    if (record) {
      this.journal.append("THEME_CHANGE", { theme: theme.id }, "PRESENTATION_ONLY");
      this.scheduleSessionSave();
    }
  }

  applyCustomTheme() {
    const colors = ["custom-primary", "custom-secondary", "custom-tertiary"].map((id) => document.getElementById(id).value);
    const background = document.getElementById("custom-background").value;
    this.customThemeValue = { colors, background };
    localStorage.setItem("hhs-spatial-custom-theme-v3", JSON.stringify(this.customThemeValue));
    this.applyTheme("custom");
    this.toast("Custom theme applied.", "success");
  }

  renderTemplates() {
    this.el["template-select"].innerHTML = TEMPLATES.map((template) => `<option value="${template.id}">${escapeHTML(template.label)}</option>`).join("");
  }

  applyTemplate(id, record = true) {
    const template = templateById(id);
    this.templateId = template.id;
    this.el["template-select"].value = template.id;
    this.renderer.applyTemplate(template);
    this.applyMode(template.mode, false);
    this.openFeature(template.feature, false);
    if (record) {
      this.journal.append("TEMPLATE_CHANGE", { template: template.id }, "PRESENTATION_ONLY");
      this.scheduleSessionSave();
    }
  }

  renderApplications() {
    this.el["application-library"].innerHTML = APPLICATIONS.map((application) => `
      <button class="application-card" data-application="${application.id}">
        <span class="application-glyph">${application.glyph}</span>
        <span><strong>${escapeHTML(application.label)}</strong><small>${escapeHTML(application.category)} · ${escapeHTML(application.authority)}</small></span>
      </button>
    `).join("");
    this.el["application-library"].querySelectorAll("[data-application]").forEach((button) => {
      button.addEventListener("click", () => this.openApplication(button.dataset.application));
    });
  }

  openApplication(applicationId) {
    const application = applicationById(applicationId);
    this.workspace.open(application);
    this.openFeature(application.feature, false);
    this.journal.append("APPLICATION_OPEN", {
      application: application.id,
      authority: application.authority
    }, "PRESENTATION_ONLY");
  }

  renderSurfaces() {
    const snapshot = this.workspace.snapshot();
    this.el["surface-layer"].innerHTML = snapshot.surfaces.map((surface) => {
      const application = applicationById(surface.applicationId);
      return `
        <article class="spatial-surface ${surface.minimized ? "minimized" : ""} ${surface.maximized ? "maximized" : ""} ${surface.pinned ? "pinned" : ""}"
          data-surface-id="${surface.id}"
          style="left:${surface.x}px;top:${surface.y}px;width:${surface.width}px;height:${surface.height}px;z-index:${surface.z}">
          <header class="surface-header" data-surface-drag="${surface.id}">
            <span class="surface-title"><b>${application.glyph}</b> ${escapeHTML(surface.title)}</span>
            <span class="surface-authority">${escapeHTML(surface.authority)}</span>
            <nav>
              <button data-surface-action="dock-left" aria-label="Dock left">↤</button>
              <button data-surface-action="dock-right" aria-label="Dock right">↦</button>
              <button data-surface-action="dock-bottom" aria-label="Dock bottom">↧</button>
              <button data-surface-action="pin" aria-label="Pin">${surface.pinned ? "◆" : "◇"}</button>
              <button data-surface-action="minimize" aria-label="Minimize">—</button>
              <button data-surface-action="maximize" aria-label="Maximize">□</button>
              <button data-surface-action="close" aria-label="Close">×</button>
            </nav>
          </header>
          <div class="surface-body">${surface.minimized ? "" : this.surfaceBody(application, surface)}</div>
          ${surface.minimized || surface.maximized || surface.pinned ? "" : `<div class="surface-resize" data-surface-resize="${surface.id}"></div>`}
        </article>
      `;
    }).join("");

    this.el["surface-layer"].querySelectorAll(".spatial-surface").forEach((element) => {
      const id = element.dataset.surfaceId;
      element.addEventListener("pointerdown", () => this.workspace.focus(id));
      element.querySelectorAll("[data-surface-action]").forEach((button) => {
        button.addEventListener("click", (event) => {
          event.stopPropagation();
          const action = button.dataset.surfaceAction;
          if (action === "close") this.workspace.close(id);
          if (action === "minimize") this.workspace.minimize(id);
          if (action === "maximize") this.workspace.maximize(id);
          if (action === "pin") this.workspace.pin(id);
          if (action === "dock-left") this.workspace.dock(id, "left");
          if (action === "dock-right") this.workspace.dock(id, "right");
          if (action === "dock-bottom") this.workspace.dock(id, "bottom");
        });
      });
      const header = element.querySelector("[data-surface-drag]");
      header?.addEventListener("pointerdown", (event) => this.beginSurfaceDrag(event, id));
      const resize = element.querySelector("[data-surface-resize]");
      resize?.addEventListener("pointerdown", (event) => this.beginSurfaceResize(event, id));
    });

    this.bindSurfaceContentActions();
  }

  surfaceBody(application, surface) {
    if (application.id === "vm81-lattice") {
      return this.vm81Surface();
    }
    if (application.id === "runtime-control") {
      return this.runtimeControlSurface();
    }
    if (application.id === "elastic-closure") {
      return this.elasticClosureSurface();
    }
    if (application.id === "telemetry") {
      return this.telemetrySurface();
    }
    if (application.id === "replay-timeline") {
      return this.replaySurface();
    }
    if (application.id === "session-manager") {
      return this.sessionSurface();
    }
    if (application.id === "scene-composer") {
      return this.sceneComposerSurface();
    }
    if (application.id === "project-manager") {
      return this.projectManagerSurface();
    }
    if (application.id === "entity-inspector") {
      return this.entityInspectorSurface();
    }
    if (application.id === "asset-vault") {
      return this.assetVaultSurface();
    }
    if (application.id === "world-router") {
      return this.worldRouterSurface();
    }
    if (application.id === "simulation-console") {
      return this.simulationConsoleSurface();
    }
    if (application.id === "opcode-trace") {
      return this.opcodeSurface();
    }
    if (application.id === "system-overview") {
      return this.overviewSurface();
    }
    const feature = featureById(application.feature);
    return `
      <p class="surface-description">${escapeHTML(application.description)}</p>
      <div class="surface-tile-grid">
        ${feature.tiles.map(([title, description, route]) => `
          <section class="surface-data-card"><strong>${escapeHTML(title)}</strong><span>${escapeHTML(description)}</span><small>${escapeHTML(route)}</small></section>
        `).join("")}
      </div>
    `;
  }

  overviewSurface() {
    const connected = Object.values(this.bridge.status).filter((status) => status === "connected").length;
    return `
      <div class="surface-metrics">
        <section><small>Renderer</small><strong>${escapeHTML(this.renderer.backend.toUpperCase())}</strong></section>
        <section><small>Projection nodes</small><strong>${this.renderer.pointCount.toLocaleString()}</strong></section>
        <section><small>Connected channels</small><strong>${connected}/4</strong></section>
        <section><small>Open surfaces</small><strong>${this.workspace.surfaces.length}</strong></section>
        <section><small>Runtime step</small><strong>${escapeHTML(this.runtimeSummary.step ?? "UNAVAILABLE")}</strong></section>
        <section><small>Session</small><strong>${escapeHTML(this.sessions.activeSession?.name ?? "—")}</strong></section>
      </div>
      <p class="authority-banner">Frontend classification: PROJECTION_AND_ORCHESTRATION_ONLY</p>
    `;
  }

  vm81Surface() {
    return `
      <div class="vm81-grid">
        ${this.world.cells.map((cell) => `<button class="vm81-cell ${cell.id === this.world.selectedCell ? "selected" : ""} ${cell.id === this.world.activeCell ? "active" : ""} ${cell.pinned ? "pinned" : ""}" data-vm81-cell="${cell.id}" title="${cell.binding}"><b>${cell.index}</b><small>${cell.loshu}</small></button>`).join("")}
      </div>
      <div class="surface-inline-actions">
        <button data-cell-action="focus">Focus selected</button>
        <button data-cell-action="pin">Pin selected</button>
        <button data-cell-action="clear">Clear</button>
      </div>
    `;
  }

  runtimeControlSurface() {
    return `
      <div class="surface-metrics compact">
        <section><small>State</small><strong>${escapeHTML(this.runtimeSummary.state ?? "UNAVAILABLE")}</strong></section>
        <section><small>Step</small><strong>${escapeHTML(this.runtimeSummary.step ?? "—")}</strong></section>
        <section><small>Opcode</small><strong>${escapeHTML(this.runtimeSummary.opcode ?? "—")}</strong></section>
        <section><small>Receipt</small><strong title="${escapeHTML(this.runtimeSummary.receipt ?? "")}">${escapeHTML(String(this.runtimeSummary.receipt ?? "—").slice(0, 18))}</strong></section>
      </div>
      <div class="surface-command-grid">
        ${Object.keys(RUNTIME_COMMANDS).map((command) => `<button data-surface-command="${command}">${command.toUpperCase()}</button>`).join("")}
      </div>
      <p class="authority-banner">All state-changing calls use guarded backend routes. Offline requests fail explicitly.</p>
    `;
  }

  elasticClosureSurface() {
    const payload = this.bridge.lastPayload && typeof this.bridge.lastPayload === "object"
      ? this.bridge.lastPayload
      : {};
    const execution = payload.execution ?? payload;
    const proof = execution.proof ?? {};
    const metrics = execution.metrics ?? {};
    const recursive = proof.recursive_control ?? {};
    const flags = proof.flags ?? {};
    return `
      <div class="surface-metrics compact">
        <section><small>Closure</small><strong>${proof.omega_closure === true ? "CLOSED" : "UNVERIFIED"}</strong></section>
        <section><small>VM81 commit</small><strong>${execution.commit?.vm81_admitted === true ? "ADMITTED" : "—"}</strong></section>
        <section><small>Replay</small><strong>${escapeHTML(execution.replay?.replay_status ?? "—")}</strong></section>
        <section><small>History</small><strong>${recursive.history_valid === true ? "APPEND-ONLY" : "—"}</strong></section>
        <section><small>Propagated</small><strong>${metrics.N_propagated ?? 0}</strong></section>
        <section><small>Reused / skipped</small><strong>${metrics.N_reused ?? 0} / ${metrics.N_skipped ?? 0}</strong></section>
      </div>
      <div class="surface-command-grid">
        <button data-surface-command="pass152Status">STATUS</button>
        <button data-surface-command="pass152Capabilities">CAPABILITIES</button>
        <button data-surface-command="pass152Latest">LATEST</button>
        <button data-surface-command="pass152Execute">EXECUTE CYCLE</button>
      </div>
      <div class="surface-tile-grid">
        <section class="surface-data-card"><strong>Authority core</strong><span>VM81 commit only; Hash72 follows admitted closure.</span><small>${escapeHTML(String(flags.authority ?? "—"))}</small></section>
        <section class="surface-data-card"><strong>Recursive control</strong><span>Higher layers optimize policy, never lower-layer truth.</span><small>${escapeHTML(recursive.active_plan_digest?.slice(0, 24) ?? "—")}</small></section>
        <section class="surface-data-card"><strong>Causal continuity</strong><span>Plans may change; committed history remains monotonic.</span><small>${escapeHTML(recursive.committed_prefix_digest?.slice(0, 24) ?? "—")}</small></section>
      </div>
      <p class="authority-banner">Delay authority, not computation. Exploit freedom recursively, preserve invariants absolutely, extend history monotonically.</p>
    `;
  }

  telemetrySurface() {
    const fps = this.telemetry.numericSummary("renderer.fps");
    const values = this.telemetry.getSeries("renderer.fps", 40).map((sample) => Number(sample.value) || 0);
    const max = Math.max(1, ...values);
    return `
      <div class="surface-metrics compact">
        <section><small>FPS latest</small><strong>${fps.latest ?? 0}</strong></section>
        <section><small>FPS mean</small><strong>${fps.mean === null ? "—" : fps.mean.toFixed(1)}</strong></section>
        <section><small>Runtime events</small><strong>${this.telemetry.counters.runtimeEvents}</strong></section>
        <section><small>Command errors</small><strong>${this.telemetry.counters.commandErrors}</strong></section>
        <section><small>Self-play runs</small><strong>${this.telemetry.counters.selfPlayRuns}</strong></section>
        <section><small>Prompt passes</small><strong>${this.telemetry.counters.promptPasses}</strong></section>
      </div>
      <p class="surface-description">Scope: ${escapeHTML(V1_SCOPE.journey)} · ${escapeHTML(V1_SCOPE.authorityBoundary)}</p>
      <p class="surface-description">API coverage: ${escapeHTML(Object.keys(this.telemetry.selfPlay.apiCoverage || {}).join(", ") || "none")}</p>
      <div class="telemetry-bars">${values.map((value) => `<i style="height:${Math.max(2, value / max * 100)}%"></i>`).join("")}</div>
      <button data-export-telemetry>EXPORT TELEMETRY</button>
    `;
  }

  replaySurface() {
    const state = this.replay.snapshot();
    return `
      <div class="replay-surface-controls">
        <button data-replay-action="load">LOAD JOURNAL</button>
        <button data-replay-action="previous">◀</button>
        <button data-replay-action="toggle">${state.playing ? "PAUSE" : "PLAY"}</button>
        <button data-replay-action="next">▶</button>
      </div>
      <input type="range" data-replay-surface-range min="0" max="${Math.max(0, state.total - 1)}" value="${Math.max(0, state.cursor)}">
      <p class="surface-description">${escapeHTML(state.current?.type ?? "No replay frame loaded")}</p>
      <p class="authority-banner">${state.classification}</p>
    `;
  }

  sessionSurface() {
    const active = this.sessions.activeSession;
    return `
      <div class="session-surface-list">
        ${this.sessions.list().map((session) => `<button class="${session.id === this.sessions.activeSessionId ? "active" : ""}" data-session-open="${session.id}"><strong>${escapeHTML(session.name)}</strong><small>${session.snapshotCount} snapshots · ${escapeHTML(session.modifiedAt)}</small></button>`).join("")}
      </div>
      <div class="surface-inline-actions">
        <button data-session-action="new">New</button>
        <button data-session-action="snapshot">Snapshot</button>
        <button data-session-action="export">Export</button>
      </div>
      <h4 class="surface-subheading">ACTIVE SESSION SNAPSHOTS</h4>
      <div class="snapshot-list">
        ${(active?.snapshots ?? []).slice().reverse().map((snapshot) => `<button data-snapshot-restore="${snapshot.id}"><strong>${escapeHTML(snapshot.label)}</strong><small>${escapeHTML(snapshot.createdAt)}</small></button>`).join("") || "<p>No snapshots saved.</p>"}
      </div>
    `;
  }

  sceneComposerSurface() {
    const entities = this.scene.list();
    return `
      <div class="surface-inline-actions">
        <button data-entity-create="orb">New Orb</button>
        <button data-entity-create="membrane">New Membrane</button>
        <button data-entity-create="portal">New Portal</button>
        <button data-arrange="grid">Grid UI</button>
      </div>
      <h4 class="surface-subheading">ENTITY SCENE GRAPH · ${entities.length}/${this.scene.maxEntities}</h4>
      <div class="composer-list entity-tree">
        ${entities.map((entity) => `<button class="${entity.id === this.scene.selectedEntityId ? "active" : ""}" data-entity-select="${entity.id}"><strong>${escapeHTML(entity.name)}</strong><small>${escapeHTML(entity.id)} · ${Object.keys(entity.components ?? {}).join(", ")}</small></button>`).join("")}
      </div>
      <h4 class="surface-subheading">INTERFACE SURFACES</h4>
      <div class="composer-list">
        ${this.workspace.surfaces.map((surface) => `<button data-focus-surface="${surface.id}"><strong>${escapeHTML(surface.title)}</strong><small>${surface.width}×${surface.height} · ${surface.dock ?? "free"}</small></button>`).join("") || "<p>No open surfaces.</p>"}
      </div>
    `;
  }

  projectManagerSurface() {
    const project = this.projects.activeProject;
    const world = this.projects.activeWorld;
    return `
      <div class="surface-inline-actions">
        <button data-project-action="new">New Project</button>
        <button data-project-action="world">New World</button>
        <button data-project-action="snapshot">World Snapshot</button>
        <button data-project-action="verify">Verify Chain</button>
        <button data-project-action="import">Import</button>
        <button data-project-action="export">Export</button>
      </div>
      <div class="project-list">
        ${this.projects.list().map((item) => `<button class="${item.id === this.projects.activeProjectId ? "active" : ""}" data-project-select="${item.id}"><strong>${escapeHTML(item.name)}</strong><small>${item.worlds} worlds · ${item.assets} assets</small></button>`).join("")}
      </div>
      <h4 class="surface-subheading">WORLDS · ACTIVE ${escapeHTML(world?.name ?? "—")}</h4>
      <div class="project-list">
        ${(project?.worlds ?? []).map((item) => `<button class="${item.id === project.activeWorldId ? "active" : ""}" data-world-select="${item.id}"><strong>${escapeHTML(item.name)}</strong><small>${item.snapshots?.length ?? 0} snapshots · ${escapeHTML(item.id)}</small></button>`).join("")}
      </div>
      <h4 class="surface-subheading">ACTIVE WORLD SNAPSHOTS</h4>
      <div class="snapshot-list">
        ${(world?.snapshots ?? []).slice().reverse().map((snapshot) => `<button data-world-snapshot-restore="${snapshot.id}"><strong>${escapeHTML(snapshot.label)}</strong><small>${escapeHTML(snapshot.createdAt)} · ${snapshot.digest.slice(0, 18)}…</small></button>`).join("") || "<p>No world snapshots saved.</p>"}
      </div>
      <p class="authority-banner">${escapeHTML(project?.manifest?.runtimeAuthority ?? "VM81_BACKEND_AUTHORITATIVE")} · world snapshot digests are project-integrity records, not Hash72 receipts.</p>
    `;
  }

  entityInspectorSurface() {
    const entity = this.scene.get(this.scene.selectedEntityId);
    if (!entity) return `<p class="surface-description">No scene entity selected.</p>`;
    const transform = entity.components?.Transform ?? { position: [0,0,0], rotation: [0,0,0], scale: [1,1,1] };
    return `
      <div class="surface-metrics compact">
        <section><small>Entity</small><strong>${escapeHTML(entity.name)}</strong></section>
        <section><small>ID</small><strong>${escapeHTML(entity.id)}</strong></section>
        <section><small>Parent</small><strong>${escapeHTML(entity.parentId ?? "—")}</strong></section>
        <section><small>Components</small><strong>${Object.keys(entity.components ?? {}).length}</strong></section>
      </div>
      <div class="vector-editor">
        ${["X","Y","Z"].map((axis, index) => `<label>${axis}<input type="number" step="0.1" data-transform-axis="${index}" value="${Number(transform.position[index] ?? 0)}"></label>`).join("")}
      </div>
      <div class="surface-inline-actions">
        <button data-entity-action="apply-transform">Apply Position</button>
        <button data-entity-action="add-motion">Add Motion</button>
        <button data-entity-action="delete" ${entity.id === "world-root" ? "disabled" : ""}>Delete</button>
      </div>
      <pre class="component-json">${escapeHTML(JSON.stringify(entity.components, null, 2))}</pre>
    `;
  }

  assetVaultSurface() {
    const assets = this.assets.list();
    return `
      <label class="asset-drop">IMPORT LOCAL ASSETS<input type="file" data-asset-input multiple></label>
      <p class="authority-banner">SHA-256 is calculated on import. Script and shader files are stored as inert text until separately validated.</p>
      <div class="asset-list">
        ${assets.map((asset) => `<article><strong>${escapeHTML(asset.name)}</strong><small>${asset.category} · ${asset.size.toLocaleString()} bytes</small><code>${asset.sha256.slice(0, 24)}…</code><button data-asset-remove="${asset.id}">Remove</button></article>`).join("") || "<p>No assets imported.</p>"}
      </div>
    `;
  }

  worldRouterSurface() {
    const state = this.routes.snapshot();
    return `
      <div class="surface-metrics compact">
        <section><small>Current world</small><strong>${escapeHTML(this.projects.activeWorld?.name ?? "—")}</strong></section>
        <section><small>Worlds</small><strong>${state.worlds.length}</strong></section>
        <section><small>Routes</small><strong>${state.routes.length}</strong></section>
        <section><small>Classification</small><strong>NAVIGATION</strong></section>
      </div>
      <div class="surface-inline-actions">
        <button data-route-action="connect">Connect First Pair</button>
      </div>
      <div class="route-list">
        ${state.worlds.map((item) => `<button data-route-navigate="${item.id}" ${item.id === state.currentWorldId ? "disabled" : ""}><strong>${escapeHTML(item.name)}</strong><small>${escapeHTML(item.id)}</small></button>`).join("")}
        ${state.routes.map((route) => `<article><strong>${escapeHTML(route.label)}</strong><small>${escapeHTML(route.from)} ⇄ ${escapeHTML(route.to)}</small></article>`).join("")}
      </div>
    `;
  }

  simulationConsoleSurface() {
    const state = this.simulation.snapshot();
    return `
      <div class="surface-metrics compact">
        <section><small>Status</small><strong>${state.running ? "RUNNING" : "PAUSED"}</strong></section>
        <section><small>Tick</small><strong>${state.tick}</strong></section>
        <section><small>Elapsed</small><strong>${state.elapsed}s</strong></section>
        <section><small>Dynamic entities</small><strong>${state.dynamicEntities}</strong></section>
        <section><small>Kinetic energy</small><strong>${state.kineticEnergy}</strong></section>
        <section><small>Fixed Δt</small><strong>${state.fixedDt.toFixed(6)}</strong></section>
      </div>
      <div class="surface-inline-actions">
        <button data-simulation-action="step">Step</button>
        <button data-simulation-action="ten">10 Steps</button>
        <button data-simulation-action="toggle">${state.running ? "Pause" : "Run"}</button>
        <button data-simulation-action="reset">Reset Clock</button>
      </div>
      <p class="authority-banner">${state.classification}. This engine cannot fabricate or replace VM81 execution receipts.</p>
    `;
  }

  opcodeSurface() {
    const events = this.events.filter((event) => /OPCODE|RUNTIME|COMMAND/.test(event.type)).slice(0, 14);
    return `
      <ol class="opcode-surface-list">
        ${events.map((event) => `<li><b>${escapeHTML(event.type)}</b><span>${escapeHTML(compact(event.payload, 160))}</span></li>`).join("") || "<li><span>No backend opcode events received.</span></li>"}
      </ol>
    `;
  }

  bindSurfaceContentActions() {
    this.el["surface-layer"].querySelectorAll("[data-vm81-cell]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        this.world.select(Number(button.dataset.vm81Cell), "surface-grid");
      });
    });
    this.el["surface-layer"].querySelectorAll("[data-cell-action]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        const action = button.dataset.cellAction;
        if (action === "focus" && this.world.selectedCell !== null) this.renderer.focusCell(this.world.selectedCell);
        if (action === "pin" && this.world.selectedCell !== null) this.world.togglePin(this.world.selectedCell);
        if (action === "clear") { this.world.clearSelection(); this.renderer.clearFocus(); }
      });
    });
    this.el["surface-layer"].querySelectorAll("[data-surface-command]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        this.runCommand(`runtime.${button.dataset.surfaceCommand}`, {}, button);
      });
    });
    this.el["surface-layer"].querySelectorAll("[data-export-telemetry]").forEach((button) => button.addEventListener("click", () => downloadJSON("hhs_spatial_telemetry_v3.json", this.telemetry.snapshot())));
    this.el["surface-layer"].querySelectorAll("[data-replay-action]").forEach((button) => button.addEventListener("click", () => {
      const action = button.dataset.replayAction;
      if (action === "load") this.replay.load(this.journal.timeline());
      if (action === "toggle") this.replay.toggle();
      if (action === "previous") this.replay.step(-1);
      if (action === "next") this.replay.step(1);
    }));
    this.el["surface-layer"].querySelectorAll("[data-replay-surface-range]").forEach((input) => input.addEventListener("input", () => this.replay.seek(Number(input.value))));
    this.el["surface-layer"].querySelectorAll("[data-session-open]").forEach((button) => button.addEventListener("click", () => this.sessions.select(button.dataset.sessionOpen)));
    this.el["surface-layer"].querySelectorAll("[data-session-action]").forEach((button) => button.addEventListener("click", () => {
      if (button.dataset.sessionAction === "new") this.createSession();
      if (button.dataset.sessionAction === "snapshot") this.saveSessionSnapshot();
      if (button.dataset.sessionAction === "export") downloadJSON("hhs_spatial_sessions_v3.json", this.sessions.export());
    }));
    this.el["surface-layer"].querySelectorAll("[data-snapshot-restore]").forEach((button) => button.addEventListener("click", () => this.restoreSessionSnapshot(button.dataset.snapshotRestore)));
    this.el["surface-layer"].querySelectorAll("[data-arrange]").forEach((button) => button.addEventListener("click", () => this.workspace.arrange(button.dataset.arrange)));
    this.el["surface-layer"].querySelectorAll("[data-focus-surface]").forEach((button) => button.addEventListener("click", () => this.workspace.focus(button.dataset.focusSurface)));

    this.el["surface-layer"].querySelectorAll("[data-project-select]").forEach((button) => button.addEventListener("click", () => this.projects.select(button.dataset.projectSelect)));
    this.el["surface-layer"].querySelectorAll("[data-world-select]").forEach((button) => button.addEventListener("click", () => this.projects.selectWorld(button.dataset.worldSelect)));
    this.el["surface-layer"].querySelectorAll("[data-world-snapshot-restore]").forEach((button) => button.addEventListener("click", () => this.restoreWorldSnapshot(button.dataset.worldSnapshotRestore)));
    this.el["surface-layer"].querySelectorAll("[data-project-action]").forEach((button) => button.addEventListener("click", async () => {
      const action = button.dataset.projectAction;
      if (action === "new") this.createProject();
      if (action === "world") this.createWorld();
      if (action === "snapshot") await this.saveWorldSnapshot();
      if (action === "verify") await this.verifyWorldSnapshotChain();
      if (action === "import") this.el["workspace-file-input"].click();
      if (action === "export") downloadJSON("hhs_spatial_projects_v4.json", this.projects.export());
    }));

    this.el["surface-layer"].querySelectorAll("[data-entity-create]").forEach((button) => button.addEventListener("click", () => this.scene.createPrimitive(button.dataset.entityCreate)));
    this.el["surface-layer"].querySelectorAll("[data-entity-select]").forEach((button) => button.addEventListener("click", () => this.scene.select(button.dataset.entitySelect)));
    this.el["surface-layer"].querySelectorAll("[data-entity-action]").forEach((button) => button.addEventListener("click", () => {
      const action = button.dataset.entityAction;
      const id = this.scene.selectedEntityId;
      if (action === "apply-transform") {
        const inputs = [...button.closest(".surface-body").querySelectorAll("[data-transform-axis]")];
        const entity = this.scene.get(id);
        const transform = clone(entity.components.Transform);
        transform.position = inputs.sort((a,b) => Number(a.dataset.transformAxis)-Number(b.dataset.transformAxis)).map((input) => Number(input.value));
        this.scene.setComponent(id, "Transform", transform);
      }
      if (action === "add-motion") this.scene.setComponent(id, "Kinematics", { velocity: [0.18, 0.09, -0.04], acceleration: [0, -0.015, 0], damping: 0.02 });
      if (action === "delete" && id !== "world-root") this.scene.removeEntity(id);
    }));

    this.el["surface-layer"].querySelectorAll("[data-asset-input]").forEach((input) => input.addEventListener("change", async () => {
      for (const file of input.files ?? []) {
        try { await this.assets.ingest(file); } catch (error) { this.toast(String(error.message ?? error), "error"); }
      }
      input.value = "";
    }));
    this.el["surface-layer"].querySelectorAll("[data-asset-remove]").forEach((button) => button.addEventListener("click", () => this.assets.remove(button.dataset.assetRemove)));

    this.el["surface-layer"].querySelectorAll("[data-route-action]").forEach((button) => button.addEventListener("click", () => {
      const worlds = this.projects.activeProject?.worlds ?? [];
      if (button.dataset.routeAction === "connect" && worlds.length >= 2) {
        try { this.routes.addRoute({ from: worlds[0].id, to: worlds[1].id, label: `${worlds[0].name} / ${worlds[1].name}` }); }
        catch (error) { this.toast(String(error.message ?? error), "error"); }
      } else if (worlds.length < 2) this.toast("Create a second world before adding a route.", "error");
    }));
    this.el["surface-layer"].querySelectorAll("[data-route-navigate]").forEach((button) => button.addEventListener("click", () => {
      try { this.routes.navigate(button.dataset.routeNavigate); } catch (error) { this.toast(String(error.message ?? error), "error"); }
    }));

    this.el["surface-layer"].querySelectorAll("[data-simulation-action]").forEach((button) => button.addEventListener("click", () => {
      const action = button.dataset.simulationAction;
      if (action === "step") this.simulation.step(1);
      if (action === "ten") this.simulation.step(10);
      if (action === "toggle") this.simulation.running ? this.simulation.pause() : this.simulation.start();
      if (action === "reset") this.simulation.reset();
    }));
  }

  beginSurfaceDrag(event, id) {
    if (event.target.closest("button")) return;
    const surface = this.workspace.get(id);
    if (!surface || surface.pinned || surface.maximized) return;
    event.preventDefault();
    this.dragState = { id, startX: event.clientX, startY: event.clientY, x: surface.x, y: surface.y };
    this.workspace.focus(id);
  }

  beginSurfaceResize(event, id) {
    const surface = this.workspace.get(id);
    if (!surface || surface.pinned || surface.maximized) return;
    event.preventDefault();
    event.stopPropagation();
    this.resizeState = { id, startX: event.clientX, startY: event.clientY, width: surface.width, height: surface.height };
    this.workspace.focus(id);
  }

  handleGlobalPointerMove(event) {
    if (this.dragState) {
      this.workspace.move(this.dragState.id, this.dragState.x + event.clientX - this.dragState.startX, this.dragState.y + event.clientY - this.dragState.startY);
      this.renderSurfaces();
    }
    if (this.resizeState) {
      this.workspace.resize(this.resizeState.id, this.resizeState.width + event.clientX - this.resizeState.startX, this.resizeState.height + event.clientY - this.resizeState.startY);
      this.renderSurfaces();
    }
  }

  endSurfaceInteraction() {
    if (this.dragState || this.resizeState) {
      this.dragState = null;
      this.resizeState = null;
      this.workspace.dispatchEvent(new CustomEvent("changed", { detail: this.workspace.snapshot() }));
    }
  }

  refreshSurfacesByApplication(applicationId) {
    if (this.workspace.surfaces.some((surface) => surface.applicationId === applicationId)) {
      this.renderSurfaces();
    }
  }

  renderChannels(statuses = this.bridge.status) {
    this.el["channel-list"].innerHTML = Object.entries(statuses).map(([name, status]) => `<li><span>${escapeHTML(name.toUpperCase())}</span><b class="${status === "connected" ? "online" : ""}">${escapeHTML(status.toUpperCase())}</b></li>`).join("");
  }

  refreshRuntimeStatus(statuses = this.bridge.status) {
    const connected = statuses.runtime === "connected";
    this.el["runtime-status"].className = `status-chip ${connected ? "online" : "offline"}`;
    this.el["runtime-status"].innerHTML = `<i></i> ${connected ? "VM81 CONNECTED" : "RUNTIME UNAVAILABLE"}`;
    this.el["connection-mode"].textContent = connected ? "WEBSOCKET" : "POLL/FALLBACK";
  }

  ingestPayload(payload) {
    const summary = extractRuntimeSummary(payload);
    this.runtimeSummary = { ...this.runtimeSummary, ...Object.fromEntries(Object.entries(summary).filter(([, value]) => value !== undefined)) };
    this.world.bindRuntime(this.runtimeSummary);
    this.refreshRuntimeFields();
  }

  refreshRuntimeFields() {
    this.el["vm81-state"].textContent = String(this.runtimeSummary.state ?? "UNAVAILABLE");
    this.el["runtime-step"].textContent = String(this.runtimeSummary.step ?? "—");
    this.el["active-opcode"].textContent = String(this.runtimeSummary.opcode ?? "—");
    this.el["receipt-hash"].textContent = String(this.runtimeSummary.receipt ?? "—");
  }

  renderCell(cell) {
    if (!cell) {
      this.el["cell-inspector"].classList.remove("open");
      this.el["cell-inspector-content"].innerHTML = "";
      return;
    }
    this.el["cell-inspector"].classList.add("open");
    this.el["cell-inspector-content"].innerHTML = `
      <dl>
        <dt>Cell</dt><dd>${cell.index}</dd>
        <dt>Binding</dt><dd>${escapeHTML(cell.binding)}</dd>
        <dt>Lo Shu</dt><dd>${cell.loshu}</dd>
        <dt>Lane</dt><dd>${escapeHTML(cell.lane)}</dd>
        <dt>Reciprocal</dt><dd>${cell.reciprocalCell + 1}</dd>
        <dt>State</dt><dd>${escapeHTML(cell.runtimeState)}</dd>
        <dt>Opcode</dt><dd>${escapeHTML(cell.opcode ?? "—")}</dd>
        <dt>Activations</dt><dd>${cell.activationCount}</dd>
        <dt>Pinned</dt><dd>${cell.pinned ? "YES" : "NO"}</dd>
      </dl>
    `;
  }

  renderEvents() {
    this.el["event-log"].innerHTML = this.events.map((event) => `
      <li class="${/ERROR|FAILURE/.test(event.type) ? "error" : /COMPLETE|RESULT/.test(event.type) ? "success" : ""}">
        <strong>${escapeHTML(event.type)}</strong>
        ${escapeHTML(compact(event.payload))}
      </li>
    `).join("") || "<li><strong>NO EVENTS</strong>Awaiting local projection or backend activity.</li>";
  }

  renderSessions() {
    const sessions = this.sessions.list();
    this.el["session-select"].innerHTML = sessions.map((session) => `<option value="${session.id}">${escapeHTML(session.name)}</option>`).join("");
    this.el["session-select"].value = this.sessions.activeSessionId;
    const active = this.sessions.activeSession;
    this.el["session-name"].textContent = active?.name ?? "—";
    this.el["session-summary"].textContent = `${sessions.length} sessions · ${active?.snapshots?.length ?? 0} snapshots`;
    this.refreshSurfacesByApplication("session-manager");
  }

  createSession() {
    const name = prompt("Session name", `Workspace ${this.sessions.list().length + 1}`);
    if (!name) return;
    this.sessions.create(name, {
      activeTemplate: this.templateId,
      activeTheme: this.themeId,
      activeMode: this.modeId,
      activeFeature: this.activeFeature,
      camera: this.renderer.snapshotCamera(),
      parameters: clone(this.renderer.parameters)
    });
  }

  renameSession() {
    const active = this.sessions.activeSession;
    if (!active) return;
    const name = prompt("Rename session", active.name);
    if (!name) return;
    this.sessions.rename(active.id, name);
  }

  deleteSession() {
    const active = this.sessions.activeSession;
    if (!active || !confirm(`Delete session “${active.name}”?`)) return;
    try {
      this.sessions.delete(active.id);
    } catch (error) {
      this.toast(String(error.message ?? error), "error");
    }
  }

  captureSessionState() {
    return {
      activeTemplate: this.templateId,
      activeTheme: this.themeId,
      activeMode: this.modeId,
      activeFeature: this.activeFeature,
      activeProjectId: this.projects.activeProjectId,
      activeWorldId: this.projects.activeWorld?.id ?? null,
      selectedEntityId: this.scene.selectedEntityId,
      selectedCell: this.world.selectedCell,
      surfaces: this.workspace.snapshot().surfaces,
      camera: this.renderer.snapshotCamera(),
      parameters: clone(this.renderer.parameters),
      world: this.world.snapshot()
    };
  }

  scheduleSessionSave() {
    clearTimeout(this.sessionSaveTimer);
    this.sessionSaveTimer = setTimeout(() => {
      this.sessions.update(this.captureSessionState(), { emit: false });
      this.renderSessions();
    }, 220);
  }

  saveSessionSnapshot(label = "Manual snapshot") {
    const snapshot = this.sessions.saveSnapshot(label, this.captureSessionState());
    this.toast(`Snapshot saved: ${snapshot.label}`, "success");
    this.renderSessions();
    return snapshot;
  }


  restoreSessionSnapshot(snapshotId) {
    try {
      const state = this.sessions.restoreSnapshot(snapshotId);
      this.applySession({ ...this.sessions.activeSession, ...state });
      this.sessions.update(state);
      this.toast("Session snapshot restored.", "success");
      this.journal.append("SESSION_SNAPSHOT_RESTORE", { snapshotId }, "PRESENTATION_ONLY");
    } catch (error) {
      this.toast(String(error.message ?? error), "error");
    }
  }

  createProject() {
    const name = prompt("Project name", `Spatial Project ${this.projects.list().length + 1}`);
    if (!name) return;
    try { this.projects.create(name); }
    catch (error) { this.toast(String(error.message ?? error), "error"); }
  }

  createWorld() {
    const name = prompt("World name", `World ${(this.projects.activeProject?.worlds.length ?? 0) + 1}`);
    if (!name) return;
    try {
      const world = this.projects.addWorld(name);
      this.routes.syncWorlds(this.projects.activeProject.worlds);
      this.projects.selectWorld(world.id);
    } catch (error) {
      this.toast(String(error.message ?? error), "error");
    }
  }

  captureProjectState() {
    return {
      schema: "HHS_SPATIAL_WORLD_STATE_V4",
      classification: "PROJECT_PRESENTATION_AND_SIMULATION_STATE",
      projectId: this.projects.activeProjectId,
      worldId: this.projects.activeWorld?.id ?? null,
      scene: this.scene.snapshot(),
      routes: this.routes.snapshot(),
      assets: this.assets.export(),
      simulation: this.simulation.snapshot(),
      camera: this.renderer.snapshotCamera(),
      vm81Projection: this.world.snapshot()
    };
  }

  scheduleProjectSave() {
    if (this.loadingProject) return;
    clearTimeout(this.projectSaveTimer);
    this.projectSaveTimer = setTimeout(() => {
      const state = this.captureProjectState();
      this.projects.saveWorldState({ scene: state.scene, routes: state.routes.routes });
      this.projects.saveAssets(state.assets);
      this.refreshSurfacesByApplication("project-manager");
    }, 260);
  }

  async saveWorldSnapshot(label = "Manual world snapshot") {
    try {
      const snapshot = await this.projects.saveWorldSnapshot(label, this.captureProjectState());
      this.toast(`World snapshot saved: ${snapshot.label}`, "success");
      this.journal.append("WORLD_SNAPSHOT_SAVED", { id: snapshot.id, digest: snapshot.digest }, "PROJECT_AUTHORING_METADATA");
      this.refreshSurfacesByApplication("project-manager");
      return snapshot;
    } catch (error) {
      this.toast(String(error.message ?? error), "error");
      return null;
    }
  }

  async verifyWorldSnapshotChain() {
    const result = await this.projects.verifyWorldSnapshots();
    this.toast(result.valid ? `World snapshot chain valid · ${result.checked}` : `World snapshot chain invalid · ${result.failures.length}`, result.valid ? "success" : "error");
    this.journal.append("WORLD_SNAPSHOT_VERIFY", result, result.valid ? "PROJECT_AUTHORING_METADATA" : "ERROR_PROJECTION");
    return result;
  }

  async restoreWorldSnapshot(snapshotId) {
    try {
      const state = await this.projects.restoreWorldSnapshot(snapshotId);
      this.loadingProject = true;
      try {
        this.scene.load(state.scene ?? {});
        this.assets.load(state.assets ?? { assets: [] });
        this.routes.load(state.routes ?? { worlds: this.projects.activeProject.worlds, routes: [], currentWorldId: this.projects.activeWorld.id });
        if (state.camera) this.renderer.loadCamera(state.camera);
      } finally {
        this.loadingProject = false;
      }
      this.scheduleProjectSave();
      this.renderSurfaces();
      this.toast("World snapshot restored.", "success");
      this.journal.append("WORLD_SNAPSHOT_RESTORE", { snapshotId }, "PROJECT_AUTHORING_METADATA");
      return state;
    } catch (error) {
      this.toast(String(error.message ?? error), "error");
      return null;
    }
  }

  renderReplay() {
    const state = this.replay.snapshot();
    this.el["replay-range"].max = String(Math.max(0, state.total - 1));
    this.el["replay-range"].value = String(Math.max(0, state.cursor));
    this.el["replay-status"].textContent = state.playing ? "PLAYING" : state.total ? "READY" : "EMPTY";
    this.el["replay-current"].textContent = state.current?.type ?? "No frame";
    const playButton = document.getElementById("replay-play-button");
    if (playButton) playButton.textContent = state.playing ? "PAUSE" : "PLAY";
  }

  renderTelemetry() {
    const fps = this.telemetry.numericSummary("renderer.fps");
    this.el["telemetry-summary"].innerHTML = `
      <span><b>${fps.latest ?? 0}</b> FPS</span>
      <span><b>${this.telemetry.counters.runtimeEvents}</b> runtime events</span>
      <span><b>${this.telemetry.counters.commandErrors}</b> command errors</span>
      <span><b>${this.telemetry.counters.promptPasses}</b> prompt passes</span>
      <span><b>${this.telemetry.counters.selfPlayRuns}</b> self-play runs</span>
    `;
  }

  async verifyJournal() {
    const result = await this.journal.verify();
    this.el["journal-integrity"].textContent = result.valid ? `VALID · ${result.checked}` : `FAILED · ${result.failures.length}`;
    this.toast(result.valid ? "Projection journal chain verified." : "Projection journal chain failure.", result.valid ? "success" : "error");
  }

  openPalette() {
    this.el["command-palette"].showModal();
    this.el["palette-search"].value = "";
    this.renderPalette("");
    setTimeout(() => this.el["palette-search"].focus(), 0);
  }

  renderPalette(query) {
    const normalized = String(query ?? "").trim().toLowerCase();
    const items = [
      ...FEATURES.map((feature) => ({ type: "feature", id: feature.id, label: `Open ${feature.label}`, hint: feature.description })),
      ...APPLICATIONS.map((application) => ({ type: "application", id: application.id, label: `Launch ${application.label}`, hint: `${application.category} · ${application.authority}` })),
      ...this.commands.list().map((command) => ({ type: "command", id: command.id, label: command.label, hint: `${command.category} · ${command.authority}` }))
    ].filter((item) => !normalized || `${item.label} ${item.hint}`.toLowerCase().includes(normalized)).slice(0, 50);

    this.el["palette-results"].innerHTML = items.map((item) => `
      <button class="palette-item" data-palette-type="${item.type}" data-palette-id="${item.id}">
        <span>${escapeHTML(item.label)}</span><small>${escapeHTML(item.hint)}</small>
      </button>
    `).join("");
    this.el["palette-results"].querySelectorAll(".palette-item").forEach((button) => button.addEventListener("click", async () => {
      this.el["command-palette"].close();
      if (button.dataset.paletteType === "feature") this.openFeature(button.dataset.paletteId);
      if (button.dataset.paletteType === "application") this.openApplication(button.dataset.paletteId);
      if (button.dataset.paletteType === "command") await this.runCommand(button.dataset.paletteId);
    }));
  }

  async runCommand(id, args = {}, button = null) {
    if (button) button.classList.add("busy");
    try {
      return await this.commands.execute(id, args, { ui: this });
    } catch {
      return null;
    } finally {
      if (button) button.classList.remove("busy");
    }
  }

  toggleReducedMotion(button) {
    const reduced = document.documentElement.dataset.motion !== "reduced";
    document.documentElement.dataset.motion = reduced ? "reduced" : "full";
    this.renderer.setMotion(!reduced);
    button.classList.toggle("active", reduced);
    this.journal.append("REDUCED_MOTION", { enabled: reduced }, "PRESENTATION_ONLY");
  }

  exportWorkspace() {
    const payload = {
      schema: "HHS_SPATIAL_WORKSPACE_EXPORT_V4",
      classification: "PRESENTATION_STATE_ONLY",
      exportedAt: new Date().toISOString(),
      session: clone(this.sessions.activeSession),
      state: this.captureSessionState(),
      customTheme: this.customThemeValue,
      projectionJournal: this.journal.export(),
      telemetry: this.telemetry.snapshot(),
      projectStore: this.projects.export(),
      projectState: this.captureProjectState()
    };
    downloadJSON("hhs_spatial_workspace_v4.json", payload);
  }

  async importWorkspace(file) {
    if (!file) return;
    try {
      const payload = JSON.parse(await file.text());
      if (payload.schema === "HHS_SPATIAL_SESSION_EXPORT_V3") {
        this.sessions.import(payload);
      } else if (payload.schema === "HHS_SPATIAL_PROJECT_EXPORT_V4") {
        this.projects.import(payload);
      } else if (["HHS_SPATIAL_WORKSPACE_EXPORT_V3", "HHS_SPATIAL_WORKSPACE_EXPORT_V4"].includes(payload.schema) && payload.state) {
        if (payload.customTheme) {
          this.customThemeValue = payload.customTheme;
          localStorage.setItem("hhs-spatial-custom-theme-v3", JSON.stringify(payload.customTheme));
        }
        if (payload.projectStore?.schema === "HHS_SPATIAL_PROJECT_EXPORT_V4") this.projects.import(payload.projectStore);
        const session = this.sessions.create(payload.session?.name ? `${payload.session.name} (Imported)` : "Imported Workspace", payload.state);
        this.applySession(session);
      } else {
        throw new Error("INVALID_WORKSPACE_EXPORT");
      }
      this.toast("Workspace imported.", "success");
    } catch (error) {
      this.toast(String(error.message ?? error), "error");
    } finally {
      this.el["workspace-file-input"].value = "";
    }
  }

  toast(message, kind = "") {
    const toast = document.createElement("div");
    toast.className = `toast ${kind}`;
    toast.textContent = message;
    this.el["toast-region"].appendChild(toast);
    setTimeout(() => toast.remove(), 3600);
  }
}
