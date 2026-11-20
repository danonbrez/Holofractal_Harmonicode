/** Conventional byte-stream client for the authenticated SQL-stage transport.
 * File.slice() keeps file contents out of whole-file JS buffers. Credentials
 * are ordinary same-origin browser credentials; never accept owner IDs from UI.
 * SQL staging is noncanonical until independent signed VM81 admission.
 */
export async function stageBrowserFile(
  file,
  { fetchImpl = fetch, baseUrl = '/api/runtime/admin-source-stream', signal, capabilityToken, chunkBytes = 256 * 1024 } = {},
) {
  if (!Number.isSafeInteger(chunkBytes) || chunkBytes <= 0) throw new Error('INVALID_TRANSPORT_CHUNK_SIZE');
  const request = async (suffix, options = {}) => {
    const response = await fetchImpl(baseUrl + suffix, {
      credentials: 'same-origin',
      signal,
      ...options,
      ...(capabilityToken ? { headers: { ...(options.headers || {}), Authorization: 'HHS-Capability ' + capabilityToken } } : {}),
    });
    let result;
    try { result = await response.json(); }
    catch { throw new Error('HHS_ADMIN_STREAM_RESPONSE_INVALID'); }
    if (!response.ok) throw new Error(String(result.detail || 'HHS_ADMIN_STREAM_REQUEST_REJECTED'));
    return result;
  };

  const first = await request('/uploads', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source_name: file.name }),
  });
  const uploadId = first.upload_id;
  let offset = first.received_bytes;
  if (!uploadId || !Number.isSafeInteger(offset) || offset !== 0) throw new Error('HHS_ADMIN_STREAM_CREATE_INVALID');

  while (offset < file.size) {
    const chunk = file.slice(offset, Math.min(file.size, offset + chunkBytes));
    const status = await request('/uploads/' + encodeURIComponent(uploadId) + '?offset=' + offset, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/octet-stream' },
      body: chunk,
    });
    if (!Number.isSafeInteger(status.received_bytes) || status.received_bytes <= offset) {
      throw new Error('HHS_ADMIN_STREAM_OFFSET_NOT_ADVANCED');
    }
    if (status.received_bytes > file.size || status.received_bytes > offset + chunk.size) {
      throw new Error('HHS_ADMIN_STREAM_OFFSET_CORRUPT');
    }
    offset = status.received_bytes;
  }
  const staged = await request('/uploads/' + encodeURIComponent(uploadId) + '/finalize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });
  if (staged.state !== 'STAGED' || staged.received_bytes !== file.size ||
      staged.canonical_hash216_admitted !== false || !/^[a-f0-9]{64}$/.test(staged.source_sha256 || '')) {
    throw new Error('HHS_ADMIN_STREAM_STAGED_RECEIPT_INVALID');
  }
  return Object.freeze({
    upload_id: uploadId,
    source_name: file.name,
    received_bytes: staged.received_bytes,
    source_sha256: staged.source_sha256,
    status: 'STAGED_NONCANONICAL',
    canonical_hash216_admitted: false,
  });
}

/** Explicit separate candidate continuation after successful SQL staging.
 * Does not mint VM81/Hash72/Hash216 authority or create a RAG knowledge record.
 */
export async function continueStagedLane5Candidate(
  uploadId,
  { fetchImpl = fetch, baseUrl = '/api/runtime/admin-source-stream', signal, capabilityToken } = {},
) {
  if (typeof uploadId !== 'string' || !/^[0-9a-f-]{36}$/.test(uploadId)) {
    throw new Error('HHS_ADMIN_STREAM_UPLOAD_ID_INVALID');
  }
  const headers = { Accept: 'application/json' };
  if (capabilityToken) headers.Authorization = 'HHS-Capability ' + capabilityToken;
  const response = await fetchImpl(baseUrl + '/uploads/' + encodeURIComponent(uploadId) + '/candidate', {
    method: 'POST', credentials: 'same-origin', signal, headers,
  });
  let payload;
  try { payload = await response.json(); }
  catch { throw new Error('HHS_LANE5_CANDIDATE_RESPONSE_INVALID'); }
  if (!response.ok) throw new Error(String(payload.detail || 'HHS_LANE5_CANDIDATE_REJECTED'));
  if (payload.upload_id !== uploadId || payload.canonical_hash216_admitted !== false ||
      payload.signed_vm81_admission_required !== true ||
      payload.native_candidate_receipt?.candidate_only !== true) {
    throw new Error('HHS_LANE5_CANDIDATE_AUTHORITY_INVALID');
  }
  return payload;
}

/** Stream privately staged original bytes into a caller-supplied WritableStream.
 * It never buffers an entire file or claims canonical Hash216 admission.
 */
export async function readStagedSource(
  uploadId,
  destination,
  { fetchImpl = fetch, baseUrl = '/api/runtime/admin-source-stream', signal, capabilityToken } = {},
) {
  if (typeof uploadId !== 'string' || !/^[0-9a-f-]{36}$/.test(uploadId))
    throw new Error('HHS_ADMIN_STREAM_UPLOAD_ID_INVALID');
  if (!destination || typeof destination.getWriter !== 'function')
    throw new Error('HHS_ADMIN_STREAM_WRITABLE_DESTINATION_REQUIRED');
  const headers = { Accept: 'application/octet-stream' };
  if (capabilityToken) headers.Authorization = 'HHS-Capability ' + capabilityToken;
  const response = await fetchImpl(baseUrl + '/uploads/' + encodeURIComponent(uploadId) + '/source', {
    method: 'GET', credentials: 'same-origin', signal, headers, cache: 'no-store',
  });
  if (!response.ok) throw new Error('HHS_ADMIN_SOURCE_EGRESS_REJECTED:' + response.status);
  const digest = response.headers?.get('X-HHS-Source-SHA256');
  const canonical = response.headers?.get('X-HHS-Canonical-Hash216-Admitted');
  const declaredSize = response.headers?.get('Content-Length');
  if (!/^[a-f0-9]{64}$/.test(digest || '') || canonical !== 'false' ||
      !/^(0|[1-9][0-9]*)$/.test(declaredSize || '') ||
      !Number.isSafeInteger(Number(declaredSize)) ||
      !response.body || typeof response.body.getReader !== 'function') {
    throw new Error('HHS_ADMIN_SOURCE_EGRESS_RECEIPT_INVALID');
  }
  const expected = Number(declaredSize);
  let received = 0;
  const reader = response.body.getReader();
  const writer = destination.getWriter();
  try {
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      if (!(value instanceof Uint8Array)) throw new Error('HHS_ADMIN_SOURCE_EGRESS_BINARY_REQUIRED');
      received += value.byteLength;
      if (received > expected) throw new Error('HHS_ADMIN_SOURCE_EGRESS_LENGTH_OVERFLOW');
      await writer.write(value);
    }
    if (received !== expected) throw new Error('HHS_ADMIN_SOURCE_EGRESS_LENGTH_MISMATCH');
    await writer.close();
    return Object.freeze({
      upload_id: uploadId, received_bytes: received, source_sha256: digest,
      canonical_hash216_admitted: false, status: 'STAGED_NONCANONICAL',
    });
  } catch (error) {
    await writer.abort(error).catch(() => {});
    throw error;
  } finally {
    reader.releaseLock();
    writer.releaseLock();
  }
}
