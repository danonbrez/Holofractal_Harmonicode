import fs from "node:fs/promises"
import path from "node:path"
import { chromium } from "playwright"

const BASE_URL = process.env.HHS_PRODUCTION_BASE_URL
const EXPECTED_SHA = process.env.HHS_PRODUCTION_EXPECTED_SHA
const EXPECTED_SERVICE_COUNT = Number(process.env.HHS_PRODUCTION_EXPECTED_SERVICE_COUNT || "0")
const IGNORE_HTTPS_ERRORS = process.env.HHS_PRODUCTION_BROWSER_IGNORE_HTTPS_ERRORS === "1"
const EVIDENCE_DIR = process.env.HHS_PRODUCTION_BROWSER_EVIDENCE_DIR || "/tmp/hhs-production-browser"

if (!BASE_URL) throw new Error("HHS_PRODUCTION_BASE_URL is required")
if (!EXPECTED_SHA) throw new Error("HHS_PRODUCTION_EXPECTED_SHA is required")
if (!Number.isInteger(EXPECTED_SERVICE_COUNT) || EXPECTED_SERVICE_COUNT <= 0) {
  throw new Error("HHS_PRODUCTION_EXPECTED_SERVICE_COUNT must be a positive integer")
}

await fs.mkdir(EVIDENCE_DIR, { recursive: true })

const evidencePath = path.join(EVIDENCE_DIR, "production-live-browser.json")
const screenshotPath = path.join(EVIDENCE_DIR, "production-live-browser.png")
const startedAt = Date.now()
const consoleErrors = []
const pageErrors = []
const requestFailures = []
const intentionalRequestAborts = []
const http5xx = []
const BENIGN_BACKGROUND_ABORT_PATHS = new Set([
  "/api/assistant/deployment-health",
  "/api/product/health",
  "/health",
  "/api/v1/pass174/status",
])
const publicApiAttempts = {
  interface_status: [],
  service_registry: [],
}

let browser
let context
let page
let evidence = {
  schema: "HHS_DIGITALOCEAN_PUBLIC_FRONTEND_CAPABILITY_BROWSER_ACCEPTANCE_V1",
  ok: false,
  base_url: BASE_URL,
  expected_sha: EXPECTED_SHA,
  expected_service_count: EXPECTED_SERVICE_COUNT,
  ignore_https_errors: IGNORE_HTTPS_ERRORS,
  console_errors: consoleErrors,
  page_errors: pageErrors,
  request_failures: requestFailures,
  intentional_request_aborts: intentionalRequestAborts,
  http_5xx: http5xx,
  public_api_attempts: publicApiAttempts,
}

const serializeError = (error) => error instanceof Error
  ? { name: error.name, message: error.message, stack: error.stack }
  : { name: "Error", message: String(error) }

try {
  browser = await chromium.launch({ headless: true })
  context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    ignoreHTTPSErrors: IGNORE_HTTPS_ERRORS,
  })
  page = await context.newPage()
  page.setDefaultTimeout(60_000)
  page.setDefaultNavigationTimeout(120_000)

  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text())
  })
  page.on("pageerror", (error) => pageErrors.push(String(error)))
  page.on("requestfailed", (request) => {
    const failure = request.failure()?.errorText || "unknown"
    let requestPath = ""
    try {
      requestPath = new URL(request.url()).pathname
    } catch {
      requestPath = ""
    }
    const entry = {
      method: request.method(),
      url: request.url(),
      path: requestPath,
      failure,
    }
    if (
      entry.method === "GET"
      && entry.failure === "net::ERR_ABORTED"
      && BENIGN_BACKGROUND_ABORT_PATHS.has(entry.path)
    ) {
      intentionalRequestAborts.push(entry)
      return
    }
    requestFailures.push(entry)
  })
  page.on("response", (response) => {
    if (response.status() >= 500) http5xx.push({ url: response.url(), status: response.status() })
  })

  const response = await page.goto(`${BASE_URL.replace(/\/$/, "")}/`, { waitUntil: "domcontentloaded" })
  if (!response?.ok()) throw new Error(`Production root returned HTTP ${response?.status() ?? "unknown"}`)

  await page.waitForSelector('[data-testid="hhs-canonical-runtime-ide"]', { timeout: 120_000 })
  await page.waitForSelector('[data-testid="hhs-product-workspace"]', { timeout: 120_000 })

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
  const requestJsonWithRetry = async (url, attempts) => {
    const absoluteUrl = new URL(url, BASE_URL).toString()
    let lastError = null
    for (let attempt = 1; attempt <= 6; attempt += 1) {
      const attemptStarted = Date.now()
      try {
        const response = await context.request.get(absoluteUrl, {
          headers: { accept: "application/json" },
          timeout: 20_000,
          failOnStatusCode: false,
        })
        const raw = await response.text()
        let body = null
        let parseError = null
        try {
          body = raw ? JSON.parse(raw) : {}
        } catch (error) {
          parseError = serializeError(error)
        }
        attempts.push({
          attempt,
          status: response.status(),
          elapsed_ms: Date.now() - attemptStarted,
          json: Boolean(body && typeof body === "object" && !Array.isArray(body)),
          parse_error: parseError,
          body_preview: raw.slice(0, 256),
        })
        if (response.ok() && body && typeof body === "object" && !Array.isArray(body)) {
          return body
        }
        lastError = new Error(`${url} HTTP ${response.status()}: ${raw.slice(0, 256)}`)
      } catch (error) {
        lastError = error
        attempts.push({
          attempt,
          status: null,
          elapsed_ms: Date.now() - attemptStarted,
          json: false,
          error: serializeError(error),
        })
      }
      if (attempt < 6) await sleep(2_500)
    }
    throw lastError || new Error(`${url} did not reach JSON-ready state`)
  }

  // Probe canonical public API state through the Playwright context with bounded
  // retries. The actual browser UI must still hydrate and render the same
  // registry below; retries do not substitute for the visible frontend gate.
  const interfaceStatus = await requestJsonWithRetry(
    "/api/interface/status",
    publicApiAttempts.interface_status,
  )
  const serviceRegistry = await requestJsonWithRetry(
    "/api/runtime/services",
    publicApiAttempts.service_registry,
  )
  const services = Array.isArray(serviceRegistry?.services)
    ? serviceRegistry.services
    : []
  const serviceNames = services
    .map((service) => String(service?.name ?? service?.runtime_contract?.name ?? "").trim())
    .filter(Boolean)
  const uniqueServiceNames = [...new Set(serviceNames)].sort((a, b) => a.localeCompare(b))

  if (interfaceStatus?.interface !== "HHS_VISUAL_RUNTIME_OS_WORKSPACE") {
    throw new Error(`Unexpected interface identity: ${JSON.stringify(interfaceStatus)}`)
  }
  if (interfaceStatus?.legacy_harmonizer_is_public_root !== false) {
    throw new Error("Legacy harmonizer is incorrectly serving as the public root")
  }
  if (!String(interfaceStatus?.asset_root ?? "").includes(EXPECTED_SHA)) {
    throw new Error(`Public asset root is not bound to exact main ${EXPECTED_SHA}: ${interfaceStatus?.asset_root}`)
  }
  if (services.length !== EXPECTED_SERVICE_COUNT) {
    throw new Error(`Browser registry count ${services.length} != pre-browser public registry count ${EXPECTED_SERVICE_COUNT}`)
  }
  if (uniqueServiceNames.length !== services.length) {
    throw new Error(`Service registry contains duplicate or unnamed descriptors: descriptors=${services.length} unique_names=${uniqueServiceNames.length}`)
  }

  const productNav = page.locator('[data-testid="hhs-product-workspace"] > nav')
  await productNav.getByRole("button", { name: "Visual Program", exact: true }).click()
  await page.waitForSelector('[data-testid="registry-visual-programmer"]', { timeout: 120_000 })
  await page.waitForFunction(
    (count) => document.querySelector('[data-testid="registry-visual-programmer"]')?.textContent?.includes(`${count} backend services`) === true,
    EXPECTED_SERVICE_COUNT,
    { timeout: 120_000 },
  )

  const renderedTitles = await page
    .locator('[data-testid="registry-visual-programmer"] aside button strong')
    .allTextContents()
  const renderedTitleSet = new Set(renderedTitles.map((value) => value.trim()).filter(Boolean))
  const missingServices = uniqueServiceNames.filter((name) => !renderedTitleSet.has(name))

  if (missingServices.length > 0) {
    throw new Error(`Production Visual Program is missing ${missingServices.length} registered services: ${missingServices.slice(0, 25).join(", ")}`)
  }

  const selectableService = "agent_economy.agent_algorithm_identity_v1_self_test"
  if (!renderedTitleSet.has(selectableService)) {
    throw new Error(`Deterministic execution probe service is not registered: ${selectableService}`)
  }

  const selected = await page.evaluate((serviceName) => {
    const root = document.querySelector('[data-testid="registry-visual-programmer"]')
    if (!root) return false
    const strong = [...root.querySelectorAll("aside button strong")]
      .find((element) => element.textContent?.trim() === serviceName)
    const button = strong?.closest("button")
    if (!button || button.disabled) return false
    button.click()
    return true
  }, selectableService)
  if (!selected) throw new Error(`Registered service is not selectable in the frontend: ${selectableService}`)

  const serviceNode = page.locator(
    `[data-testid="visual-program-node"][data-registry-id="${selectableService}"]`,
  ).last()
  await serviceNode.waitFor({ state: "visible", timeout: 30_000 })

  const dispatchResponsePromise = page.waitForResponse(
    (candidate) => candidate.request().method() === "POST"
      && new URL(candidate.url()).pathname === "/api/runtime/services/dispatch",
    { timeout: 90_000 },
  )
  await page.getByTestId("visual-program-run-node").click()
  const dispatchResponse = await dispatchResponsePromise
  const dispatchRaw = await dispatchResponse.text()
  let dispatchBody = null
  try {
    dispatchBody = dispatchRaw ? JSON.parse(dispatchRaw) : {}
  } catch (error) {
    throw new Error(`Visual Program dispatch did not return JSON: ${serializeError(error).message}; body=${dispatchRaw.slice(0, 256)}`)
  }
  if (!dispatchResponse.ok() || dispatchBody?.ok === false) {
    throw new Error(`Visual Program dispatch failed HTTP ${dispatchResponse.status()}: ${dispatchRaw.slice(0, 512)}`)
  }
  await page.waitForFunction(
    (serviceName) => document.querySelector(
      `[data-testid="visual-program-node"][data-registry-id="${serviceName}"]`,
    )?.getAttribute("data-node-status") === "success",
    selectableService,
    { timeout: 30_000 },
  )

  const registryText = await page.locator('[data-testid="registry-visual-programmer"]').innerText()
  if (registryText.includes("registry unavailable")) {
    throw new Error("Production Visual Program reports registry unavailable")
  }

  await productNav.getByRole("button", { name: "Build", exact: true }).click()
  await page.waitForSelector('[data-testid="mobile-quick-build-panel"]', { timeout: 60_000 })
  const quickBuildSource = "<!doctype html><html><body><main id=\"hhs-production-functional-probe\">HHS production functional probe</main></body></html>"
  await page.getByTestId("mobile-quick-build-source").fill(quickBuildSource)

  const quickBuildResponsePromise = page.waitForResponse(
    (candidate) => candidate.request().method() === "POST"
      && new URL(candidate.url()).pathname === "/api/v1/pass174/sdlc/run",
    { timeout: 180_000 },
  )
  await page.getByTestId("mobile-quick-build-run").click()
  const quickBuildResponse = await quickBuildResponsePromise
  const quickBuildRaw = await quickBuildResponse.text()
  let quickBuildBody = null
  try {
    quickBuildBody = quickBuildRaw ? JSON.parse(quickBuildRaw) : {}
  } catch (error) {
    throw new Error(`Quick Build did not return JSON: ${serializeError(error).message}; body=${quickBuildRaw.slice(0, 256)}`)
  }
  const quickBuildStatus = String(quickBuildBody?.classification ?? quickBuildBody?.status ?? "")
  if (
    !quickBuildResponse.ok()
    || quickBuildBody?.ok === false
    || /fail|reject|error/i.test(quickBuildStatus)
  ) {
    throw new Error(`Quick Build execution failed HTTP ${quickBuildResponse.status()}: ${quickBuildRaw.slice(0, 512)}`)
  }
  await page.getByTestId("mobile-quick-build-result").waitFor({ state: "visible", timeout: 180_000 })

  // Exercise the production mobile ingress/vector surface with a bounded text
  // fixture. This verifies file selection, exact-byte ingress, persistent
  // Hash216 lookup, and explicit user-controlled context attachment.
  await page.getByTestId("production-mobile-control-center").waitFor({ state: "visible", timeout: 60_000 })
  const ingressFixture = "HHS production frontend ingress probe\nA=1\n"
  await page.getByTestId("mobile-ingress-file-input").setInputFiles({
    name: "hhs-production-ingress-probe.txt",
    mimeType: "text/plain",
    buffer: Buffer.from(ingressFixture, "utf8"),
  })
  const ingressResponsePromise = page.waitForResponse(
    (candidate) => candidate.request().method() === "POST"
      && new URL(candidate.url()).pathname === "/api/v1/pass174/sdlc/run",
    { timeout: 180_000 },
  )
  await page.getByTestId("mobile-ingress-hydrate").click()
  const ingressResponse = await ingressResponsePromise
  const ingressRaw = await ingressResponse.text()
  let ingressBody = null
  try {
    ingressBody = ingressRaw ? JSON.parse(ingressRaw) : {}
  } catch (error) {
    throw new Error(`Mobile ingress did not return JSON: ${serializeError(error).message}; body=${ingressRaw.slice(0, 256)}`)
  }
  const ingressStatus = String(ingressBody?.classification ?? ingressBody?.status ?? "")
  if (!ingressResponse.ok() || ingressBody?.ok === false || /fail|reject|error/i.test(ingressStatus)) {
    throw new Error(`Mobile ingress failed HTTP ${ingressResponse.status()}: ${ingressRaw.slice(0, 512)}`)
  }
  await page.getByTestId("mobile-ingress-result").waitFor({ state: "visible", timeout: 180_000 })

  const vectorResponsePromise = page.waitForResponse(
    (candidate) => candidate.request().method() === "POST"
      && new URL(candidate.url()).pathname === "/api/v1/pass174/hash216/query",
    { timeout: 90_000 },
  )
  await page.getByTestId("mobile-vector-read").click()
  const vectorResponse = await vectorResponsePromise
  const vectorRaw = await vectorResponse.text()
  let vectorBody = null
  try {
    vectorBody = vectorRaw ? JSON.parse(vectorRaw) : {}
  } catch (error) {
    throw new Error(`Persisted vector read did not return JSON: ${serializeError(error).message}; body=${vectorRaw.slice(0, 256)}`)
  }
  if (
    !vectorResponse.ok()
    || vectorBody?.ok === false
    || String(vectorBody?.classification ?? "") !== "HHS_PASS_174_VECTOR_QUERY_HIT"
  ) {
    throw new Error(`Persisted vector read failed HTTP ${vectorResponse.status()}: ${vectorRaw.slice(0, 512)}`)
  }
  await page.getByTestId("mobile-vector-result").waitFor({ state: "visible", timeout: 90_000 })
  await page.getByTestId("mobile-vector-use-in-chat").click()
  await page.getByTestId("assistant-attached-context").waitFor({ state: "visible", timeout: 30_000 })

  // Exercise the production assistant as a real create-or-continue chatbot,
  // not merely as a one-shot text endpoint. The second visible turn must
  // continue the first thread and recall an exact token from conversation
  // history through backend authority.
  const assistantMemoryToken = "HHS-PRODUCTION-CHATBOT-E2E-7249"
  const assistantProbe = `Remember this exact token for my next message: ${assistantMemoryToken}. Reply briefly.`
  await page.getByTestId("assistant-composer").fill(assistantProbe)
  const assistantResponsePromise = page.waitForResponse(
    (candidate) => candidate.request().method() === "POST"
      && new URL(candidate.url()).pathname === "/api/assistant/chat",
    { timeout: 180_000 },
  )
  await page.getByTestId("assistant-send").click()
  const assistantResponse = await assistantResponsePromise
  const assistantRaw = await assistantResponse.text()
  let assistantBody = null
  try {
    assistantBody = assistantRaw ? JSON.parse(assistantRaw) : {}
  } catch (error) {
    throw new Error(`Assistant first turn did not return JSON: ${serializeError(error).message}; body=${assistantRaw.slice(0, 256)}`)
  }
  const assistantText = String(assistantBody?.assistant_message?.content ?? assistantBody?.response ?? "").trim()
  const assistantThreadId = String(assistantBody?.thread_id ?? assistantBody?.thread?.thread_id ?? "").trim()
  if (!assistantResponse.ok() || assistantBody?.ok === false || !assistantText || !assistantThreadId) {
    throw new Error(`Assistant first turn failed HTTP ${assistantResponse.status()}: ${assistantRaw.slice(0, 512)}`)
  }
  await page.getByTestId("assistant-message-user").last().waitFor({ state: "visible", timeout: 180_000 })
  await page.getByTestId("assistant-message-assistant").last().waitFor({ state: "visible", timeout: 180_000 })

  const assistantFollowUp = "What exact token did I ask you to remember in my previous message? Reply with only the token."
  await page.getByTestId("assistant-composer").fill(assistantFollowUp)
  const assistantSecondResponsePromise = page.waitForResponse(
    (candidate) => candidate.request().method() === "POST"
      && new URL(candidate.url()).pathname === "/api/assistant/chat",
    { timeout: 180_000 },
  )
  await page.getByTestId("assistant-send").click()
  const assistantSecondResponse = await assistantSecondResponsePromise
  const assistantSecondRaw = await assistantSecondResponse.text()
  let assistantSecondBody = null
  try {
    assistantSecondBody = assistantSecondRaw ? JSON.parse(assistantSecondRaw) : {}
  } catch (error) {
    throw new Error(`Assistant second turn did not return JSON: ${serializeError(error).message}; body=${assistantSecondRaw.slice(0, 256)}`)
  }
  const assistantSecondText = String(
    assistantSecondBody?.assistant_message?.content ?? assistantSecondBody?.response ?? "",
  ).trim()
  const assistantSecondThreadId = String(
    assistantSecondBody?.thread_id ?? assistantSecondBody?.thread?.thread_id ?? "",
  ).trim()
  if (!assistantSecondResponse.ok() || assistantSecondBody?.ok === false || !assistantSecondText) {
    throw new Error(`Assistant second turn failed HTTP ${assistantSecondResponse.status()}: ${assistantSecondRaw.slice(0, 512)}`)
  }
  if (!assistantSecondThreadId || assistantSecondThreadId !== assistantThreadId) {
    throw new Error(`Assistant thread continuity failed: first=${assistantThreadId} second=${assistantSecondThreadId || "missing"}`)
  }
  if (!assistantSecondText.includes(assistantMemoryToken)) {
    throw new Error(`Assistant conversation-history recall failed: expected token ${assistantMemoryToken}; response=${assistantSecondText.slice(0, 512)}`)
  }
  await page.getByTestId("assistant-message-assistant").last().waitFor({ state: "visible", timeout: 180_000 })
  const renderedUserTurns = await page.getByTestId("assistant-message-user").count()
  const renderedAssistantTurns = await page.getByTestId("assistant-message-assistant").count()
  if (renderedUserTurns < 2 || renderedAssistantTurns < 2) {
    throw new Error(`Assistant UI did not render a two-turn conversation: user=${renderedUserTurns} assistant=${renderedAssistantTurns}`)
  }
  const renderedAssistantSecondText = await page.getByTestId("assistant-message-assistant").last().innerText()
  if (!renderedAssistantSecondText.includes(assistantMemoryToken)) {
    throw new Error(`Assistant UI did not render recalled conversation token: ${renderedAssistantSecondText.slice(0, 512)}`)
  }

  // Reuse the repository's Pass 185 workbench acceptance sequence against the
  // deployed public Workspace surface: witness source, compile, create an
  // emulator session, and advance it by four bounded steps.
  await productNav.getByRole("button", { name: "Workspace", exact: true }).click()
  await page.getByTestId("hhs-visual-runtime-os-workspace").waitFor({ state: "visible", timeout: 90_000 })
  await page.getByTestId("pass185-new-file").click()
  const workspaceSource = "GENESIS\nPRODUCTION FRONTEND WORKSPACE PROBE\n1+2*3/4\n"
  await page.getByTestId("pass185-workbench-source-editor").fill(workspaceSource)

  const waitForWorkspaceOperation = (operation, timeout = 120_000) => page.waitForResponse(
    (candidate) => {
      if (
        candidate.request().method() !== "POST"
        || new URL(candidate.url()).pathname !== "/api/runtime/workspace/command"
      ) return false
      try {
        return candidate.request().postDataJSON()?.operation === operation
      } catch {
        return false
      }
    },
    { timeout },
  )
  const assertWorkspaceResponse = async (operation, response) => {
    const raw = await response.text()
    let body = null
    try {
      body = raw ? JSON.parse(raw) : {}
    } catch (error) {
      throw new Error(`${operation} did not return JSON: ${serializeError(error).message}; body=${raw.slice(0, 256)}`)
    }
    if (!response.ok() || body?.ok === false) {
      throw new Error(`${operation} failed HTTP ${response.status()}: ${raw.slice(0, 512)}`)
    }
    return body
  }

  const ingressWorkspaceResponsePromise = waitForWorkspaceOperation("ingress.register")
  await page.getByTestId("pass185-workbench-save").click()
  const ingressWorkspaceResponse = await ingressWorkspaceResponsePromise
  await assertWorkspaceResponse("ingress.register", ingressWorkspaceResponse)
  await page.getByTestId("pass185-workspace-object").last().waitFor({ state: "visible", timeout: 90_000 })

  const compileResponsePromise = waitForWorkspaceOperation("compile.execute")
  await page.getByTestId("pass185-workbench-build").click()
  const compileResponse = await compileResponsePromise
  await assertWorkspaceResponse("compile.execute", compileResponse)
  await page.waitForFunction(
    () => {
      const text = document.querySelector('[data-testid="pass185-workbench-artifact-state"]')?.textContent?.trim() || ""
      return Boolean(text && !text.includes("none"))
    },
    null,
    { timeout: 120_000 },
  )

  const emulatorCreateResponsePromise = waitForWorkspaceOperation("emulator.create")
  await page.getByTestId("pass185-workbench-create-emulator").click()
  const emulatorCreateResponse = await emulatorCreateResponsePromise
  await assertWorkspaceResponse("emulator.create", emulatorCreateResponse)
  await page.waitForFunction(
    () => {
      const text = document.querySelector('[data-testid="pass185-workbench-emulator-state"]')?.textContent?.trim() || ""
      return Boolean(text && !text.includes("none"))
    },
    null,
    { timeout: 120_000 },
  )

  const tickLocator = page.getByTestId("pass185-workbench-emulator-tick")
  const beforeTick = Number((await tickLocator.innerText()).replace(/[^0-9]/g, ""))
  if (!Number.isFinite(beforeTick)) throw new Error("Workspace emulator did not expose a numeric starting tick")
  const emulatorRunResponsePromise = waitForWorkspaceOperation("emulator.run")
  await page.getByTestId("pass185-workbench-run").click()
  const emulatorRunResponse = await emulatorRunResponsePromise
  await assertWorkspaceResponse("emulator.run", emulatorRunResponse)
  const afterTick = await page.waitForFunction(
    (before) => {
      const text = document.querySelector('[data-testid="pass185-workbench-emulator-tick"]')?.textContent || ""
      const match = text.match(/([0-9]+)/)
      const value = match ? Number(match[1]) : NaN
      return Number.isFinite(value) && value >= before + 4 ? value : false
    },
    beforeTick,
    { timeout: 120_000 },
  ).then((handle) => handle.jsonValue())

  // Verify the visible Terminal control path traverses the production
  // WebSocket membrane and receives an actual PONG before closing cleanly.
  await page.getByRole("button", { name: "Terminal", exact: true }).click()
  await page.getByTestId("pass185-terminal-panel").waitFor({ state: "visible", timeout: 60_000 })
  await page.getByTestId("pass185-terminal-open").click()
  const terminalOpenState = await page.waitForFunction(
    () => {
      const state = document.querySelector('[data-testid="pass185-terminal-state"]')?.textContent?.trim() || ""
      return ["READY", "ERROR"].includes(state) ? state : false
    },
    null,
    { timeout: 60_000 },
  ).then((handle) => handle.jsonValue())
  if (terminalOpenState !== "READY") {
    const terminalError = await page.getByTestId("pass185-terminal-error").innerText().catch(() => "")
    const terminalBootMessage = await page.getByTestId("pass185-terminal-message").innerText().catch(() => "")
    throw new Error(`Production terminal failed to become READY: state=${terminalOpenState} error=${terminalError} message=${terminalBootMessage}`)
  }
  await page.getByTestId("pass185-terminal-ping").click()
  await page.waitForFunction(
    () => document.querySelector('[data-testid="pass185-terminal-state"]')?.textContent?.trim() === "PONG",
    null,
    { timeout: 30_000 },
  )
  const terminalMessage = await page.getByTestId("pass185-terminal-message").innerText()
  if (!terminalMessage.includes("HHS_PASS_175_TERMINAL_WS_PONG")) {
    throw new Error(`Production terminal returned unexpected message: ${terminalMessage}`)
  }
  await page.getByTestId("pass185-terminal-close").click()
  await page.waitForFunction(
    () => document.querySelector('[data-testid="pass185-terminal-state"]')?.textContent?.trim() === "CLOSED",
    null,
    { timeout: 30_000 },
  )

  if (consoleErrors.length || pageErrors.length || requestFailures.length || http5xx.length) {
    throw new Error(JSON.stringify({
      console_errors: consoleErrors,
      page_errors: pageErrors,
      request_failures: requestFailures,
      intentional_request_aborts: intentionalRequestAborts,
      http_5xx: http5xx,
    }))
  }

  evidence = {
    ...evidence,
    ok: true,
    elapsed_ms: Date.now() - startedAt,
    interface: interfaceStatus.interface,
    asset_root: interfaceStatus.asset_root,
    service_count: services.length,
    unique_service_names: uniqueServiceNames.length,
    rendered_registry_titles: renderedTitleSet.size,
    missing_services: [],
    selectable_service: selectableService,
    visual_program_registry_ready: true,
    visual_program_execution_verified: true,
    visual_program_dispatch_status: dispatchResponse.status(),
    quick_build_execution_verified: true,
    quick_build_status: quickBuildStatus || "HTTP_OK",
    quick_build_http_status: quickBuildResponse.status(),
    mobile_ingress_execution_verified: true,
    mobile_ingress_http_status: ingressResponse.status(),
    persisted_vector_read_verified: true,
    persisted_vector_http_status: vectorResponse.status(),
    persisted_vector_classification: String(vectorBody?.classification ?? ""),
    assistant_execution_verified: true,
    assistant_chatbot_two_turn_verified: true,
    assistant_thread_continuity_verified: true,
    assistant_context_recall_verified: true,
    assistant_turn_count: 2,
    assistant_http_status: assistantResponse.status(),
    assistant_second_http_status: assistantSecondResponse.status(),
    assistant_response_nonempty: true,
    assistant_second_response_nonempty: true,
    workspace_workbench_execution_verified: true,
    workspace_emulator_before_tick: beforeTick,
    workspace_emulator_after_tick: afterTick,
    terminal_websocket_execution_verified: true,
    terminal_message: terminalMessage,
    guarded_dispatch_route: "/api/runtime/services/dispatch",
    quick_build_route: "/api/v1/pass174/sdlc/run",
    mobile_ingress_route: "/api/v1/pass174/sdlc/run",
    persisted_vector_route: "/api/v1/pass174/hash216/query",
    assistant_route: "/api/assistant/chat",
    workspace_command_route: "/api/runtime/workspace/command",
    frontend_authority: false,
  }

  console.log(`HHS_DIGITALOCEAN_PUBLIC_FRONTEND_CAPABILITY_SURFACE_VERIFIED=${services.length}`)
  console.log(`HHS_DIGITALOCEAN_PUBLIC_FRONTEND_SELECTABLE_SERVICE_VERIFIED=${selectableService}`)
  console.log(`HHS_DIGITALOCEAN_PUBLIC_FRONTEND_SERVICE_EXECUTION_VERIFIED=${selectableService}`)
  console.log("HHS_DIGITALOCEAN_PUBLIC_FRONTEND_QUICK_BUILD_EXECUTION_VERIFIED=1")
  console.log("HHS_DIGITALOCEAN_PUBLIC_FRONTEND_MOBILE_INGRESS_VECTOR_VERIFIED=1")
  console.log("HHS_DIGITALOCEAN_PUBLIC_FRONTEND_ASSISTANT_EXECUTION_VERIFIED=1")
  console.log("HHS_DIGITALOCEAN_PUBLIC_FRONTEND_ASSISTANT_CHATBOT_VERIFIED=1")
  console.log("HHS_DIGITALOCEAN_PUBLIC_FRONTEND_WORKSPACE_EXECUTION_VERIFIED=1")
  console.log("HHS_DIGITALOCEAN_PUBLIC_FRONTEND_TERMINAL_WEBSOCKET_VERIFIED=1")
} catch (error) {
  evidence = {
    ...evidence,
    ok: false,
    elapsed_ms: Date.now() - startedAt,
    error: serializeError(error),
  }
  throw error
} finally {
  if (page) {
    try {
      await page.screenshot({ path: screenshotPath, fullPage: true })
    } catch (error) {
      evidence.screenshot_error = serializeError(error)
    }
  }
  await fs.writeFile(evidencePath, `${JSON.stringify(evidence, null, 2)}\n`, "utf8")
  await context?.close().catch(() => {})
  await browser?.close().catch(() => {})
}
