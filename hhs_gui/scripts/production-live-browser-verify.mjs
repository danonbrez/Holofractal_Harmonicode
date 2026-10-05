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
const http5xx = []
const publicApiAttempts = {
  interface_status: [],
  service_registry: [],
}
const functionalActions = {
  quick_build: null,
  assistant_chat: null,
  service_dispatch: null,
  workspace_project_create: null,
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
  http_5xx: http5xx,
  public_api_attempts: publicApiAttempts,
  functional_actions: functionalActions,
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
    requestFailures.push({
      url: request.url(),
      failure: request.failure()?.errorText || "unknown",
    })
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

  // Production acceptance must prove user-facing execution, not only rendered
  // controls. Exercise the same browser paths a user invokes from the default
  // Build surface before entering Visual Program.
  const quickBuildPanel = page.locator('[data-testid="mobile-quick-build-panel"]')
  await quickBuildPanel.locator('[data-testid="mobile-quick-build-source"]').fill(
    '<!doctype html><html><body><h1>HHS production functional acceptance</h1></body></html>',
  )
  await quickBuildPanel.locator('[data-testid="mobile-quick-build-run"]').click()
  await quickBuildPanel.getByText("Build evidence", { exact: true }).waitFor({ timeout: 240_000 })
  const quickBuildRaw = await quickBuildPanel.locator("details pre").innerText()
  const quickBuildResult = JSON.parse(quickBuildRaw)
  if (quickBuildResult?.ok === false) {
    throw new Error(`Production Quick Build returned ok=false: ${quickBuildRaw.slice(0, 1000)}`)
  }
  if (!quickBuildResult?.runtime_contract || quickBuildResult.runtime_contract.contract_type !== "api_response") {
    throw new Error(`Production Quick Build did not return a canonical API response contract: ${quickBuildRaw.slice(0, 1000)}`)
  }
  functionalActions.quick_build = {
    ok: true,
    schema: quickBuildResult.schema ?? null,
    classification: quickBuildResult.classification ?? quickBuildResult.status ?? null,
    receipt_hash72: quickBuildResult.lifecycle_receipt_hash72
      ?? quickBuildResult?.pass174_continuation?.receipt_hash72
      ?? quickBuildResult?.pass174_continuation?.receipt?.receipt_hash72
      ?? null,
    lifecycle_hash216: quickBuildResult.lifecycle_hash216
      ?? quickBuildResult?.pass174_continuation?.lifecycle_hash216
      ?? null,
  }

  const assistantRoot = page.locator('[data-testid="production-mobile-assistant"]')
  const assistantComposer = assistantRoot.getByLabel("Message HHS assistant")
  await assistantComposer.fill("Reply with a concise confirmation that the production functional probe completed.")
  await assistantRoot.getByRole("button", { name: "Send", exact: true }).click()
  await page.waitForFunction(
    () => {
      const root = document.querySelector('[data-testid="production-mobile-assistant"]')
      if (!root) return false
      const articles = root.querySelectorAll("article")
      const text = root.textContent || ""
      return articles.length >= 2 && !text.includes("Generating response…") && !text.includes("The assistant request did not complete.")
    },
    undefined,
    { timeout: 180_000 },
  )
  const assistantArticles = await assistantRoot.locator("article").allTextContents()
  const assistantResponse = String(assistantArticles.at(-1) || "").trim()
  if (!assistantResponse || assistantResponse.includes("The assistant request did not complete.")) {
    throw new Error(`Production assistant did not return a real response: ${assistantResponse}`)
  }
  functionalActions.assistant_chat = {
    ok: true,
    response_preview: assistantResponse.slice(0, 240),
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

  const selectableService = uniqueServiceNames[0]
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

  const visualProgram = page.locator('[data-testid="registry-visual-programmer"]')
  await visualProgram.getByRole("button", { name: "Run node", exact: true }).click()
  await page.waitForFunction(
    (serviceName) => {
      const root = document.querySelector('[data-testid="registry-visual-programmer"]')
      if (!root) return false
      const text = root.textContent || ""
      return text.includes(serviceName) && text.includes("HHS_SERVICE_DISPATCH_RECORD_V1")
    },
    selectableService,
    { timeout: 180_000 },
  )
  const serviceResultHeading = visualProgram.getByRole("heading", { name: "Result", exact: true }).last()
  const serviceResultRaw = await serviceResultHeading.locator("xpath=..").locator("pre").innerText()
  const serviceResult = JSON.parse(serviceResultRaw)
  if (serviceResult?.schema !== "HHS_SERVICE_DISPATCH_RECORD_V1") {
    throw new Error(`Registered service did not return a dispatch record: ${serviceResultRaw.slice(0, 1000)}`)
  }
  if (serviceResult?.zero_bypass_interposition?.status && String(serviceResult.zero_bypass_interposition.status).includes("REJECT")) {
    throw new Error(`Registered service was rejected by zero-bypass interposition: ${serviceResultRaw.slice(0, 1000)}`)
  }
  if (!serviceResult?.runtime_contract || serviceResult.runtime_contract.contract_type !== "api_response") {
    throw new Error(`Registered service dispatch lacks canonical API response contract: ${serviceResultRaw.slice(0, 1000)}`)
  }
  functionalActions.service_dispatch = {
    ok: true,
    service: selectableService,
    schema: serviceResult.schema,
    ledger_tip_hash72: serviceResult?.unified_ledger?.tip_hash72 ?? null,
    receipt_hash72: serviceResult?.authorized_tick?.receipt?.receipt_hash72 ?? null,
  }

  // Prove the visual programmer's workspace-command path as a second real
  // backend mutation surface.
  const registrySearch = visualProgram.locator('input[placeholder="Search every registered function…"]')
  await registrySearch.fill("Create Project")
  const createProjectEntry = visualProgram.locator("aside button").filter({ hasText: "Create Project" }).first()
  await createProjectEntry.click()
  await visualProgram.getByRole("button", { name: "Run node", exact: true }).click()
  await page.waitForFunction(
    () => {
      const root = document.querySelector('[data-testid="registry-visual-programmer"]')
      if (!root) return false
      const text = root.textContent || ""
      return text.includes("Create Project") && text.includes("HHS_WORKSPACE")
    },
    undefined,
    { timeout: 120_000 },
  )
  const workspaceResultHeading = visualProgram.getByRole("heading", { name: "Result", exact: true }).last()
  const workspaceResultRaw = await workspaceResultHeading.locator("xpath=..").locator("pre").innerText()
  const workspaceResult = JSON.parse(workspaceResultRaw)
  if (workspaceResult?.ok === false) {
    throw new Error(`Workspace project creation returned ok=false: ${workspaceResultRaw.slice(0, 1000)}`)
  }
  if (!workspaceResult?.runtime_contract || workspaceResult.runtime_contract.contract_type !== "api_response") {
    throw new Error(`Workspace project creation lacks canonical API response contract: ${workspaceResultRaw.slice(0, 1000)}`)
  }
  functionalActions.workspace_project_create = {
    ok: true,
    schema: workspaceResult.schema ?? null,
    status: workspaceResult.status ?? null,
    project_id: workspaceResult?.result?.project?.project_id
      ?? workspaceResult?.project?.project_id
      ?? null,
  }

  const registryText = await visualProgram.innerText()
  if (registryText.includes("registry unavailable")) {
    throw new Error("Production Visual Program reports registry unavailable")
  }

  if (consoleErrors.length || pageErrors.length || requestFailures.length || http5xx.length) {
    throw new Error(JSON.stringify({
      console_errors: consoleErrors,
      page_errors: pageErrors,
      request_failures: requestFailures,
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
    guarded_dispatch_route: "/api/runtime/services/dispatch",
    functional_actions: functionalActions,
    frontend_authority: false,
  }

  console.log(`HHS_DIGITALOCEAN_PUBLIC_FRONTEND_CAPABILITY_SURFACE_VERIFIED=${services.length}`)
  console.log(`HHS_DIGITALOCEAN_PUBLIC_FRONTEND_SELECTABLE_SERVICE_VERIFIED=${selectableService}`)
  console.log("HHS_DIGITALOCEAN_PUBLIC_FRONTEND_FUNCTIONAL_ACTIONS_VERIFIED=4")
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
