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
      ...(capabilityToken ? { headers: { Authorization: 'HHS-Capability ' + capabilityToken, ...(options.headers || {}) } } : {}),
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
