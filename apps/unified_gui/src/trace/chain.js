import { hash72String } from "../physics/address_map.js";

function canonical(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`;
}

export class HHSTraceChain {
  constructor(moduleId = "HHS.gui") {
    this.moduleId = moduleId;
    this.events = [];
    this.sealed = false;
  }

  append(eventType, payload = {}, options = {}) {
    if (this.sealed) throw new Error("TRACE_ALREADY_SEALED");
    const sequence = this.events.length;
    const previous = this.events.at(-1);
    const event = {
      sequence,
      timestamp: options.timestamp ?? sequence,
      event_type: eventType,
      module_id: options.moduleId ?? this.moduleId,
      authority_level: options.authorityLevel ?? "A1_EXECUTION_EVIDENCE",
      input_commitment: options.inputCommitment ?? null,
      prior_state_hash: options.priorStateHash ?? null,
      resulting_state_hash: options.resultingStateHash ?? null,
      payload,
      previous_event_hash: previous?.event_hash ?? null,
    };
    const eventHash = hash72String(canonical(event));
    const committed = Object.freeze({ ...event, event_hash: eventHash });
    this.events.push(committed);
    return committed;
  }

  getHead() {
    return this.events.at(-1) ?? null;
  }

  getEvents(start = 0, end = this.events.length) {
    return Object.freeze(this.events.slice(start, end));
  }

  verify() {
    let previous = null;
    for (const event of this.events) {
      const body = { ...event };
      delete body.event_hash;
      if (body.previous_event_hash !== previous) {
        return { valid: false, classification: "RECEIPT_CHAIN_INVALID", sequence: event.sequence };
      }
      const expected = hash72String(canonical(body));
      if (expected !== event.event_hash) {
        return { valid: false, classification: "RECEIPT_CHAIN_INVALID", sequence: event.sequence };
      }
      previous = event.event_hash;
    }
    return {
      valid: true,
      classification: "PASS157_TRACE_CHAIN_VERIFIED",
      event_count: this.events.length,
      head: previous,
    };
  }

  seal() {
    const verification = this.verify();
    if (!verification.valid) throw new Error(verification.classification);
    this.sealed = true;
    return Object.freeze({
      schema: "HHS_PASS157_TRACE_BUNDLE_V1",
      event_count: this.events.length,
      head: verification.head,
      events: Object.freeze([...this.events]),
      bundle_hash72: hash72String(canonical(this.events)),
    });
  }

  static verifyBundle(bundle) {
    if (!bundle || !Array.isArray(bundle.events)) {
      return { valid: false, classification: "RECEIPT_CHAIN_INVALID" };
    }
    const chain = new HHSTraceChain();
    chain.events = [...bundle.events];
    const verification = chain.verify();
    const bundleHash = hash72String(canonical(bundle.events));
    return {
      ...verification,
      bundle_hash_match: bundleHash === bundle.bundle_hash72,
      valid: verification.valid && bundleHash === bundle.bundle_hash72,
      classification: verification.valid && bundleHash === bundle.bundle_hash72
        ? "PASS157_TRACE_BUNDLE_VERIFIED"
        : "RECEIPT_CHAIN_INVALID",
    };
  }
}
