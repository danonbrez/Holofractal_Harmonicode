import test from 'node:test';
import assert from 'node:assert/strict';
import { installPass196ProjectionRefresh } from '../src/pass196-projection-refresh.mjs';

class FakeRegistry {
  constructor() { this.objects = new Map(); }
  has(id) { return this.objects.has(id); }
  async register(object) {
    if (this.objects.has(object.object_id)) throw new Error('DUPLICATE_OBJECT_ID');
    const value = structuredClone({
      relationships: [], history: [], receipts: [], face_registry: [], spatial_projection: null,
      shader_bindings: [], sprite_bindings: [], capabilities: [], actions: [], dependencies: [],
      diagnostics: [], metadata: {}, ...object,
    });
    this.objects.set(value.object_id, value);
    return structuredClone(value);
  }
  lookup(id) {
    if (!this.objects.has(id)) throw new Error('OBJECT_NOT_FOUND');
    return structuredClone(this.objects.get(id));
  }
  list(filter = {}) {
    return [...this.objects.values()]
      .filter((object) => (!filter.object_type || object.object_type === filter.object_type)
        && (!filter.lifecycle_state || object.lifecycle_state === filter.lifecycle_state))
      .map((object) => structuredClone(object));
  }
  search(query) {
    const normalized = String(query || '').toLowerCase();
    return this.list().filter((object) => JSON.stringify(object).toLowerCase().includes(normalized));
  }
}

function fakeRuntime() {
  let sequence = 0;
  return {
    registry: new FakeRegistry(),
    ledger: {
      async append(receiptClass, payload, context) {
        assert.equal(receiptClass, 'P161_REPLAY');
        assert.equal(context.authority_state, 'VALIDATED_PROJECTION');
        sequence += 1;
        return { receipt_sha256: String(sequence).padStart(64, '0'), payload, context };
      },
    },
  };
}

const projection = (lifecycle, manifest) => ({
  object_id: 'hhs:runtime:pass196-integrated-environment',
  object_type: 'RUNTIME',
  canonical_name: 'HHS_PASS196_SERIALIZED_PARALLEL_INTEGRATED_ENVIRONMENT',
  display_name: 'Pass 196 Integrated Environment',
  description: 'projection',
  lifecycle_state: lifecycle,
  authority_state: 'VALIDATED_PROJECTION',
  validation_state: lifecycle === 'ACTIVE' ? 'PASS_LAYER_CLOSURE_VERIFIED' : 'PASS_LAYER_GAPS_EXPLICIT',
  metadata: { manifest_hash72: manifest, frontend_is_authority: false },
});

test('Pass196 projection refresh updates registry reads instead of leaving stale registration', async () => {
  const runtime = fakeRuntime();
  installPass196ProjectionRefresh(runtime);
  await runtime.registry.refreshValidatedProjection(projection('INITIALIZING', null));
  assert.equal(runtime.registry.lookup(projection().object_id).lifecycle_state, 'INITIALIZING');

  await runtime.registry.refreshValidatedProjection(projection('ACTIVE', 'a'.repeat(72)));
  const current = runtime.registry.lookup(projection().object_id);
  assert.equal(current.lifecycle_state, 'ACTIVE');
  assert.equal(current.validation_state, 'PASS_LAYER_CLOSURE_VERIFIED');
  assert.equal(current.metadata.manifest_hash72, 'a'.repeat(72));
  assert.equal(current.metadata.frontend_is_authority, false);
  assert.equal(current.receipts.length, 1);
  assert.equal(runtime.registry.list({ lifecycle_state: 'ACTIVE' }).length, 1);
  assert.equal(runtime.registry.search('PASS_LAYER_CLOSURE_VERIFIED').length, 1);
});

test('Pass196 projection refresh rejects authority and identity escalation', async () => {
  const runtime = fakeRuntime();
  installPass196ProjectionRefresh(runtime);
  await runtime.registry.refreshValidatedProjection(projection('INITIALIZING', null));

  await assert.rejects(
    runtime.registry.refreshValidatedProjection({ ...projection('ACTIVE', 'b'.repeat(72)), authority_state: 'AUTHORITATIVE' }),
    /P196_PROJECTION_AUTHORITY_ESCALATION_REJECTED/,
  );
  await assert.rejects(
    runtime.registry.refreshValidatedProjection({ ...projection('ACTIVE', 'b'.repeat(72)), object_type: 'AUTHORITY' }),
    /P196_PROJECTION_OBJECT_TYPE_DRIFT/,
  );
});
