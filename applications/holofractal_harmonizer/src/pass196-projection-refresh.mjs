const INSTALL_MARKER = Symbol.for('hhs.pass196.validatedProjectionRefresh');
const clone = (value) => structuredClone(value);

function requireProjection(condition, code) {
  if (!condition) throw new Error(code);
}

export function installPass196ProjectionRefresh(runtime) {
  const registry = runtime?.registry;
  const ledger = runtime?.ledger;
  requireProjection(registry && ledger, 'P196_PROJECTION_RUNTIME_UNAVAILABLE');
  if (registry[INSTALL_MARKER]) return registry.refreshValidatedProjection;

  const overlays = new Map();
  const originalHas = registry.has.bind(registry);
  const originalLookup = registry.lookup.bind(registry);
  const originalList = registry.list.bind(registry);
  const originalRegister = registry.register.bind(registry);

  const materialize = (objectId) => {
    const base = originalLookup(objectId);
    const overlay = overlays.get(objectId);
    if (!overlay) return base;
    return {
      ...base,
      ...clone(overlay),
      relationships: clone(base.relationships || []),
      history: clone(base.history || []),
      face_registry: clone(base.face_registry || []),
      spatial_projection: clone(base.spatial_projection || null),
      shader_bindings: clone(base.shader_bindings || []),
      sprite_bindings: clone(base.sprite_bindings || []),
      receipts: clone(overlay.receipts || base.receipts || []),
    };
  };

  registry.lookup = (objectId) => clone(materialize(objectId));
  registry.list = (filter = {}) => originalList({})
    .map((object) => materialize(object.object_id))
    .filter((object) => (!filter.object_type || object.object_type === filter.object_type)
      && (!filter.lifecycle_state || object.lifecycle_state === filter.lifecycle_state))
    .map(clone);
  registry.search = (query) => {
    const normalized = String(query ?? '').trim().toLowerCase();
    const objects = registry.list();
    if (!normalized) return objects;
    return objects.filter((object) => JSON.stringify(object).toLowerCase().includes(normalized));
  };

  registry.refreshValidatedProjection = async (projection, actor = 'system:pass196-integration-projection') => {
    requireProjection(projection && typeof projection === 'object' && !Array.isArray(projection), 'P196_PROJECTION_SCHEMA_INVALID');
    requireProjection(typeof projection.object_id === 'string' && projection.object_id, 'P196_PROJECTION_OBJECT_ID_REQUIRED');
    if (!originalHas(projection.object_id)) return originalRegister(projection, actor);

    const current = materialize(projection.object_id);
    requireProjection(current.object_type === projection.object_type, 'P196_PROJECTION_OBJECT_TYPE_DRIFT');
    requireProjection(current.canonical_name === projection.canonical_name, 'P196_PROJECTION_CANONICAL_NAME_DRIFT');
    requireProjection(current.authority_state === 'VALIDATED_PROJECTION', 'P196_PROJECTION_EXISTING_AUTHORITY_DRIFT');
    requireProjection(projection.authority_state === 'VALIDATED_PROJECTION', 'P196_PROJECTION_AUTHORITY_ESCALATION_REJECTED');

    const next = {
      ...current,
      display_name: projection.display_name ?? current.display_name,
      description: projection.description ?? current.description,
      modality_classes: clone(projection.modality_classes ?? current.modality_classes),
      lifecycle_state: projection.lifecycle_state ?? current.lifecycle_state,
      authority_state: 'VALIDATED_PROJECTION',
      validation_state: projection.validation_state ?? current.validation_state,
      metadata: clone(projection.metadata ?? current.metadata),
      capabilities: clone(projection.capabilities ?? current.capabilities),
      actions: clone(projection.actions ?? current.actions),
      dependencies: clone(projection.dependencies ?? current.dependencies),
      diagnostics: clone(projection.diagnostics ?? current.diagnostics),
      receipts: clone(current.receipts || []),
    };
    const receipt = await ledger.append(
      'P161_REPLAY',
      {
        classification: 'HHS_PASS196_VALIDATED_PROJECTION_REFRESH_V1',
        object_id: next.object_id,
        previous_lifecycle_state: current.lifecycle_state,
        lifecycle_state: next.lifecycle_state,
        previous_validation_state: current.validation_state,
        validation_state: next.validation_state,
        manifest_hash72: next.metadata?.manifest_hash72 ?? null,
        frontend_is_authority: false,
      },
      { object_id: next.object_id, actor_id: actor, authority_state: 'VALIDATED_PROJECTION' },
    );
    next.receipts.push(receipt.receipt_sha256);
    overlays.set(next.object_id, clone(next));
    return clone(next);
  };

  Object.defineProperty(registry, INSTALL_MARKER, { value: true, enumerable: false });
  return registry.refreshValidatedProjection;
}
