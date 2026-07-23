function stable(value) {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map(stable).join(",")}]`;
  }
  return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
}

async function sha256(text) {
  if (globalThis.crypto?.subtle) {
    const bytes = new TextEncoder().encode(text);
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
  }
  let hash = 2166136261;
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return `FNV1A_${(hash >>> 0).toString(16).padStart(8, "0")}`;
}

export class ProjectionJournal extends EventTarget {
  constructor({ limit = 512 } = {}) {
    super();
    this.limit = limit;
    this.entries = [];
    this.head = "0".repeat(64);
    this.sequence = 0;
  }

  async append(type, payload = {}, authority = "PRESENTATION_ONLY") {
    const entry = {
      schema: "HHS_PROJECTION_JOURNAL_ENTRY_V2",
      sequence: ++this.sequence,
      time: new Date().toISOString(),
      type,
      authority,
      payload,
      previous: this.head
    };
    entry.digest = await sha256(stable(entry));
    this.head = entry.digest;
    this.entries.push(entry);
    this.entries = this.entries.slice(-this.limit);
    this.dispatchEvent(new CustomEvent("entry", { detail: entry }));
    return entry;
  }

  clearView() {
    this.dispatchEvent(new CustomEvent("view-clear"));
  }

  timeline() {
    return this.entries.map((entry) => ({ ...entry }));
  }

  async verify() {
    let previous = "0".repeat(64);
    const failures = [];
    for (const entry of this.entries) {
      if (entry.previous !== previous) {
        failures.push({ sequence: entry.sequence, type: "PREVIOUS_DIGEST_MISMATCH" });
      }
      const { digest, ...candidate } = entry;
      const calculated = await sha256(stable(candidate));
      if (calculated !== digest) {
        failures.push({ sequence: entry.sequence, type: "DIGEST_MISMATCH" });
      }
      previous = digest;
    }
    return {
      schema: "HHS_PROJECTION_JOURNAL_VERIFICATION_V2",
      classification: "NON_AUTHORITATIVE_PRESENTATION_JOURNAL",
      valid: failures.length === 0,
      checked: this.entries.length,
      head: this.head,
      failures
    };
  }

  export() {
    return {
      schema: "HHS_PROJECTION_JOURNAL_V2",
      classification: "NON_AUTHORITATIVE_PRESENTATION_JOURNAL",
      head: this.head,
      count: this.entries.length,
      entries: this.timeline()
    };
  }
}
