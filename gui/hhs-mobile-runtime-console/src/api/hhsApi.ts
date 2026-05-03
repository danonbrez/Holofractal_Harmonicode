const BASE = '/api/hhs';

async function request(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${BASE}${path}`, { ...init, headers });
  const contentType = response.headers.get('content-type') ?? '';
  const payload = contentType.includes('application/json') ? await response.json() : await response.text();

  if (!response.ok) {
    throw new Error(typeof payload === 'string' ? payload : JSON.stringify(payload));
  }

  return payload;
}

export type HHSCommand =
  | 'solve'
  | 'branch'
  | 'rejoin'
  | 'trace'
  | 'invariant'
  | 'receipt'
  | 'tensor'
  | 'adaptive'
  | 'reset';

export const hhsApi = {
  solve: (payload: Record<string, unknown>) =>
    request('/solve', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  branch: () => request('/branch', { method: 'POST' }),
  rejoin: () => request('/rejoin', { method: 'POST' }),
  trace: () => request('/trace'),
  invariants: () => request('/invariants'),
  receipt: () => request('/receipt'),
  tensor: () => request('/tensor', { method: 'POST' }),
  adaptive: () => request('/adaptive', { method: 'POST' }),
  reset: () => request('/reset', { method: 'POST' })
};
