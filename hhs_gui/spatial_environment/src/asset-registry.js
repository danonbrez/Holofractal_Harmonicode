const MAX_ASSETS = 512;
const MAX_ASSET_BYTES = 64 * 1024 * 1024;
const clone = (value) => JSON.parse(JSON.stringify(value));

function bytesToHex(buffer) {
  return [...new Uint8Array(buffer)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

export function classifyAsset(name = "", mime = "") {
  const lower = String(name).toLowerCase();
  const type = String(mime).toLowerCase();
  if (type.startsWith("image/") || /\.(png|jpe?g|webp|gif|hdr|exr)$/.test(lower)) return "IMAGE";
  if (type.startsWith("audio/") || /\.(wav|mp3|ogg|flac)$/.test(lower)) return "AUDIO";
  if (/\.(glb|gltf|obj|fbx|stl)$/.test(lower)) return "MODEL";
  if (/\.(wgsl|glsl|vert|frag)$/.test(lower)) return "SHADER_TEXT";
  if (/\.(js|mjs|ts|tsx|py|lua)$/.test(lower)) return "SCRIPT_TEXT";
  if (type.includes("json") || /\.(json|jsonl|csv|xml)$/.test(lower)) return "DATA";
  if (type.startsWith("text/") || /\.(md|txt|html|css)$/.test(lower)) return "DOCUMENT";
  return "BINARY";
}

async function readBytes(source) {
  if (source instanceof Uint8Array) return source;
  if (source instanceof ArrayBuffer) return new Uint8Array(source);
  if (source?.bytes instanceof Uint8Array) return source.bytes;
  if (source?.bytes instanceof ArrayBuffer) return new Uint8Array(source.bytes);
  if (typeof source?.arrayBuffer === "function") return new Uint8Array(await source.arrayBuffer());
  throw new Error("ASSET_BYTES_UNAVAILABLE");
}

export class AssetRegistry extends EventTarget {
  constructor({ maxAssets = MAX_ASSETS, maxAssetBytes = MAX_ASSET_BYTES } = {}) {
    super();
    this.maxAssets = maxAssets;
    this.maxAssetBytes = maxAssetBytes;
    this.assets = new Map();
    this.objectUrls = new Map();
  }

  async ingest(source, metadata = {}) {
    if (this.assets.size >= this.maxAssets) throw new Error("ASSET_LIMIT_REACHED");
    const bytes = await readBytes(source);
    if (bytes.byteLength > this.maxAssetBytes) throw new Error("ASSET_SIZE_LIMIT_REACHED");
    const name = metadata.name ?? source?.name ?? "unnamed.bin";
    const mime = metadata.mime ?? source?.type ?? "application/octet-stream";
    const digest = bytesToHex(await crypto.subtle.digest("SHA-256", bytes));
    const id = `asset-${digest.slice(0, 20)}`;
    if (this.assets.has(id)) return { ...this.get(id), duplicate: true };
    const category = classifyAsset(name, mime);
    const asset = {
      id,
      name: String(name),
      mime: String(mime),
      category,
      size: bytes.byteLength,
      sha256: digest,
      importedAt: new Date().toISOString(),
      executionPolicy: category === "SCRIPT_TEXT" || category === "SHADER_TEXT" ? "INERT_TEXT_UNTIL_VALIDATED" : "NON_EXECUTABLE_ASSET",
      source: metadata.source ?? "local-import",
      bindings: []
    };
    this.assets.set(id, asset);
    if (typeof Blob !== "undefined" && typeof URL?.createObjectURL === "function") {
      try {
        this.objectUrls.set(id, URL.createObjectURL(new Blob([bytes], { type: mime })));
      } catch {}
    }
    this.emit("asset-added", asset);
    this.emit("changed", this.export());
    return clone(asset);
  }

  bind(assetId, entityId) {
    const asset = this.require(assetId);
    if (!asset.bindings.includes(entityId)) asset.bindings.push(entityId);
    this.emit("changed", this.export());
    return clone(asset);
  }

  unbind(assetId, entityId) {
    const asset = this.require(assetId);
    asset.bindings = asset.bindings.filter((id) => id !== entityId);
    this.emit("changed", this.export());
    return clone(asset);
  }

  remove(id) {
    const asset = this.require(id);
    const url = this.objectUrls.get(id);
    if (url) URL.revokeObjectURL?.(url);
    this.objectUrls.delete(id);
    this.assets.delete(id);
    this.emit("asset-removed", asset);
    this.emit("changed", this.export());
    return clone(asset);
  }

  get(id) {
    const asset = this.assets.get(id);
    return asset ? { ...clone(asset), objectUrl: this.objectUrls.get(id) ?? null } : null;
  }

  list() {
    return [...this.assets.values()].map(clone).sort((a, b) => a.name.localeCompare(b.name));
  }

  require(id) {
    const asset = this.assets.get(id);
    if (!asset) throw new Error("ASSET_NOT_FOUND");
    return asset;
  }

  load(payload = {}) {
    this.clear();
    const assets = Array.isArray(payload) ? payload : payload.assets;
    for (const asset of assets ?? []) this.assets.set(asset.id, clone(asset));
    this.emit("changed", this.export());
    return this.export();
  }

  clear() {
    for (const url of this.objectUrls.values()) URL.revokeObjectURL?.(url);
    this.objectUrls.clear();
    this.assets.clear();
  }

  export() {
    return {
      schema: "HHS_SPATIAL_ASSET_MANIFEST_V4",
      classification: "ASSET_METADATA_AND_DIGESTS_ONLY",
      assets: this.list()
    };
  }

  emit(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail: clone(detail) }));
  }
}

export { MAX_ASSETS, MAX_ASSET_BYTES };
