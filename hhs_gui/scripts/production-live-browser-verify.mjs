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

  const publicState = await page.evaluate(async () => {
    const request = async (url) => {
      const response = await fetch(url, { headers: { accept: "application/json" } })
      const body = await response.json()
      if (!response.ok) throw new Error(`${url} HTTP ${response.status}: ${JSON.stringify(body)}`)
      return body
    }
    const [interfaceStatus, serviceRegistry] = await Promise.all([
      request("/api/interface/status"),
      request("/api/runtime/services"),
    ])
    return { interfaceStatus, serviceRegistry }
  })

  const interfaceStatus = publicState.interfaceStatus
  const services = Array.isArray(publicState.serviceRegistry?.services)
    ? publicState.serviceRegistry.services
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

  await page.waitForFunction(
    (serviceName) => {
      const root = document.querySelector('[data-testid="registry-visual-programmer"]')
      if (!root) return false
      const text = root.textContent || ""
      const runButtons = [...root.querySelectorAll("button")].filter((button) => /run/i.test(button.textContent || ""))
      return text.includes(serviceName) && runButtons.length > 0
    },
    selectableService,
    { timeout: 30_000 },
  )

  const registryText = await page.locator('[data-testid="registry-visual-programmer"]').innerText()
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
    frontend_authority: false,
  }

  console.log(`HHS_DIGITALOCEAN_PUBLIC_FRONTEND_CAPABILITY_SURFACE_VERIFIED=${services.length}`)
  console.log(`HHS_DIGITALOCEAN_PUBLIC_FRONTEND_SELECTABLE_SERVICE_VERIFIED=${selectableService}`)
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
