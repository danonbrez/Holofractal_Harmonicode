import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#boot-status")).toHaveText("READY", { timeout: 30_000 });
});

test("one application document boots all required modules once", async ({ page }) => {
  const documentCount = await page.locator("html").count();
  expect(documentCount).toBe(1);
  const status = await page.evaluate(() => globalThis.HHSApp.getStatus());
  expect(status.booted).toBe(true);
  expect(status.physics.particle_count).toBe(5184);
  expect(status.state.exact_runtime_state.render_float_is_authority).toBe(false);

  const duplicateIds = await page.evaluate(() => {
    const ids = [...document.querySelectorAll("[id]")].map((element) => element.id);
    return ids.filter((id, index) => ids.indexOf(id) !== index);
  });
  expect(duplicateIds).toEqual([]);
  await expect(page.locator(".workspace-nav button")).toHaveCount(9);
});

test("address proof and VM81 mapping remain complete", async ({ page }) => {
  const proof = await page.evaluate(() => {
    const table = globalThis.HHSApp.physics.addresses;
    const sectors = new Map();
    for (const particle of table) {
      const key = `${particle.sector_a}:${particle.sector_b}`;
      if (!sectors.has(key)) sectors.set(key, new Set());
      sectors.get(key).add(particle.vm81_cell);
    }
    return {
      count: table.length,
      unique: new Set(table.map((particle) => particle.linear_index)).size,
      sectors: sectors.size,
      complete: [...sectors.values()].every((cells) => cells.size === 81),
    };
  });
  expect(proof).toEqual({ count: 5184, unique: 5184, sectors: 64, complete: true });
});

test("exact calculator round-trips and marks approximation authority", async ({ page }) => {
  await page.getByRole("button", { name: "Calculator" }).click();
  await page.locator("#calc-left").fill("1/3");
  await page.locator("#calc-right").fill("2/3");
  await page.locator("#calc-run").click();
  const output = await page.locator("#calc-output").textContent();
  const result = JSON.parse(output);
  expect(result.exact).toBe("1");
  expect(result.display.authority).toBe("RENDER_ONLY_APPROXIMATION");
});

test("phase reciprocal and center-line operators remain typed", async ({ page }) => {
  await page.getByRole("button", { name: "Symbolic" }).click();
  await page.locator("#symbolic-source").fill("1/0; 0^-1; u^72; x+y<zw<x<z<yx<wz<y<w<xy<b^2<c^2");
  await page.locator("#symbolic-parse").click();
  const output = JSON.parse(await page.locator("#symbolic-output").textContent());
  expect(output.nodes.some((node) => node.node === "PHASE_RECIPROCAL")).toBe(true);
  expect(output.nodes.some((node) => node.node === "PHASE_POWER")).toBe(true);
  expect(output.nodes.some((node) => node.node === "CENTER_LINE_PRECEDENCE")).toBe(true);
});

test("pause and single-step advance exactly once", async ({ page }) => {
  await page.evaluate(() => globalThis.HHSPhysics.pause());
  const before = await page.evaluate(() => globalThis.HHSPhysics.serialize());
  await page.locator("#physics-step").click();
  const after = await page.evaluate(() => globalThis.HHSPhysics.serialize());
  expect(after.step_count).toBe(before.step_count + 1);
  expect(after.state_hash72).not.toBe(before.state_hash72);
});

test("registered equality is required for substitution", async ({ page }) => {
  const result = await page.evaluate(() => {
    let rejected = null;
    try {
      globalThis.HHSSymbolic.substitute("missing", "Phi^2");
    } catch (error) {
      rejected = error.message;
    }
    const link = globalThis.HHSSymbolic.registerEquality("browser-golden", "Phi^2", "Phi+1");
    const admitted = globalThis.HHSSymbolic.substitute("browser-golden", "Phi^2-t");
    return { rejected, link, admitted };
  });
  expect(result.rejected).toBe("SUBSTITUTION_UNAUTHORIZED");
  expect(result.link.proof_hash72).toHaveLength(72);
  expect(result.admitted.result).toBe("(Phi+1)-t");
});

test("trace bundle seals and verifies", async ({ page }) => {
  const result = await page.evaluate(() => {
    globalThis.HHSApp.loadWorkspace("u^72==1");
    const bundle = globalThis.HHSTrace.seal();
    return { bundle, verification: globalThis.HHSTrace.verifyBundle(bundle) };
  });
  expect(result.bundle.event_count).toBeGreaterThan(0);
  expect(result.verification.valid).toBe(true);
  expect(result.verification.classification).toBe("PASS157_TRACE_BUNDLE_VERIFIED");
});

test("workspace persistence stores and reloads a versioned bundle", async ({ page }) => {
  const result = await page.evaluate(async () => {
    const bundle = globalThis.HHSApp.exportWorkspace();
    await globalThis.HHSPersistence.saveWorkspace("browser-test", bundle);
    const loaded = await globalThis.HHSPersistence.loadWorkspace("browser-test");
    await globalThis.HHSPersistence.deleteWorkspace("browser-test");
    return {
      schema: loaded.bundle.schema,
      contract: loaded.contract_version,
      stateHash: loaded.bundle.state.state_hash72,
      physicsHash: loaded.bundle.physics.state_hash72,
    };
  });
  expect(result.schema).toBe("HHS_PASS157_WORKSPACE_BUNDLE_V1");
  expect(result.contract).toBe("HHS-P157-UHAG-PSME@1.0.0");
  expect(result.stateHash).toHaveLength(72);
  expect(result.physicsHash).toHaveLength(72);
});

test("shutdown and reboot do not duplicate the application lifecycle", async ({ page }) => {
  const result = await page.evaluate(async () => {
    const before = globalThis.HHSApp.getStatus();
    const shutdown = globalThis.HHSApp.shutdown();
    const after = await globalThis.HHSApp.boot({ profile: "MOBILE_SAFE" });
    return {
      beforeBooted: before.booted,
      shutdown: shutdown.classification,
      afterBooted: after.booted,
      population: after.physics.particle_count,
    };
  });
  expect(result).toEqual({
    beforeBooted: true,
    shutdown: "HHS_APP_SHUTDOWN_COMPLETE",
    afterBooted: true,
    population: 5184,
  });
});
