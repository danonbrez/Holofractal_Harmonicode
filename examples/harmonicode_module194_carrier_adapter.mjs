/**
 * HARMONICODE Module 194 read-only carrier adapter.
 * Target: V150 source branch; no mutation of simulation, scheduler, or renderer.
 * This membrane verifies published identity/tick observations only.
 * It deliberately does NOT claim native VM81/HNAN admission or infer live 4D
 * phase registers from 3D spawn provenance.
 */
export const MODULE194_PAIR_COUNT = 5184;
export const MODULE194_PARTICLE_COUNT = 10368;
export const MODULE194_GROUP_COUNT = 81;
export const MODULE194_LOCAL_SLOTS = 64;

export function attachModule194Carrier(scope = globalThis) {
  const api = scope?.HHSModule194;
  if (typeof api?.inspect !== "function" || typeof api?.address !== "function") {
    throw new Error("HHS_M194_OBSERVER_UNAVAILABLE");
  }

  function readStatus() {
    const status = api.inspect();
    if (!status || status.particles !== MODULE194_PARTICLE_COUNT ||
        status.groups !== MODULE194_GROUP_COUNT ||
        status.perGroup !== 128) {
      throw new Error("HHS_M194_UNEXPECTED_TOPOLOGY");
    }
    return status;
  }

  function readTick() {
    const s = readStatus();
    if (!s.ready || !Number.isSafeInteger(s.physicsTick) || s.physicsTick < 0) {
      throw new Error("HHS_M194_NOT_READY");
    }
    return BigInt(s.physicsTick);
  }

  function readAddress(index) {
    if (!Number.isSafeInteger(index) ||
        index < 0 || index >= MODULE194_PARTICLE_COUNT) {
      throw new RangeError("HHS_M194_PARTICLE_INDEX");
    }
    const a = api.address(index);
    if (!a || a.index !== index || !Array.isArray(a.spawn) || a.spawn.length !== 3 ||
        !a.spawn.every(Number.isFinite)) {
      throw new Error("HHS_M194_INVALID_ADDRESS_RECORD");
    }
    return Object.freeze({
      index: a.index,
      group: a.group,
      reciprocalCluster: a.reciprocalCluster,
      localSlot: a.localSlot,
      partner: a.partner,
      loShu: a.loShu,
      hnan: a.hnan,
      spawn: Object.freeze([...a.spawn])
    });
  }

  function auditPairs() {
    const startTick = readTick();
    let broken = 0;
    const firstViolations = [];
    for (let i = 0; i < MODULE194_PAIR_COUNT; i++) {
      const a = readAddress(i);
      const b = readAddress(i + MODULE194_PAIR_COUNT);
      const valid = a.partner === b.index && b.partner === a.index &&
        a.group === b.group && a.group === Math.floor(i / MODULE194_LOCAL_SLOTS) &&
        a.localSlot === b.localSlot && a.localSlot === i % MODULE194_LOCAL_SLOTS &&
        a.reciprocalCluster === 0 && b.reciprocalCluster === 1;
      if (!valid) {
        broken++;
        if (firstViolations.length < 16) firstViolations.push(i);
      }
    }
    const endTick = readTick();
    // Reject mixed-tick reads instead of silently assigning one tick.
    if (startTick !== endTick) {
      return Object.freeze({status: "RETRY_NONATOMIC_OBSERVATION",
        startTick: startTick.toString(), endTick: endTick.toString(),
        admitted: false});
    }
    return Object.freeze({
      status: broken === 0 ? "PAIR_INDEX_PASS" : "PAIR_INDEX_FAIL",
      tick: endTick.toString(),
      checkedPairs: MODULE194_PAIR_COUNT,
      brokenPairCount: broken,
      firstViolations: Object.freeze(firstViolations),
      scope: "PUBLISHED_PAIR_INDEX_ONLY",
      manifoldComplementTested: false,
      phaseTransportTested: false,
      nativeAdmissionVerified: false,
      admitted: false
    });
  }

  return Object.freeze({
    mode: "MODULE194_READONLY_METADATA",
    readTick,
    readStatus,
    readAddress,
    auditPairs,
    getLiveFourRegisterFrame: () => {
      throw new Error("HHS_M194_LIVE_4D_STATE_GETTER_NOT_VERIFIED");
    }
  });
}
