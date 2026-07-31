(() => {
  'use strict';
  const api = '/api/v1/pass184';
  const form = document.getElementById('packageForm');
  const badge = document.getElementById('authorityBadge');
  const statePill = document.getElementById('statePill');
  const summary = document.getElementById('summary');
  const facts = document.getElementById('facts');
  const components = document.getElementById('components');
  const raw = document.getElementById('rawResult');
  const buttons = [...document.querySelectorAll('[data-action]')];

  const payload = () => ({
    profile: document.getElementById('profile').value,
    install_name: document.getElementById('installName').value.trim(),
    host: document.getElementById('host').value.trim(),
    port: Number(document.getElementById('port').value),
  });

  function setBusy(value) {
    buttons.forEach((button) => { button.disabled = value; });
  }

  function addFact(label, value) {
    if (value === undefined || value === null || value === '') return;
    const dt = document.createElement('dt');
    const dd = document.createElement('dd');
    dt.textContent = label;
    dd.textContent = String(value);
    facts.append(dt, dd);
  }

  function render(result, failed = false) {
    const classification = result.classification || result.status || result.detail?.status || 'HHS_PASS_184_RESULT';
    const detail = result.detail && typeof result.detail === 'object' ? result.detail : result;
    const isReady = result.ready === true || /VERIFIED|READY|AVAILABLE|BUILT_AND_VERIFIED/.test(classification);
    const isError = failed || /REJECT|ERROR|TIMEOUT|NO_LISTENER|NOT_READY/.test(classification);
    statePill.className = `state ${isError ? 'error' : isReady ? 'ready' : 'neutral'}`;
    statePill.textContent = isError ? 'ACTION REQUIRED' : isReady ? 'VERIFIED' : 'OBSERVED';
    summary.textContent = detail.message || classification.replaceAll('_', ' ');
    facts.replaceChildren();
    addFact('Classification', classification);
    addFact('Profile', result.profile || result.plan?.profile);
    addFact('Install root', result.install_root || result.plan?.install_root);
    addFact('Plan identity', result.plan_identity || result.plan?.plan_identity);
    addFact('Manifest identity', result.manifest_identity || result.verification?.manifest_identity);
    addFact('Host', result.host || result.plan?.host);
    addFact('Port', result.port || result.plan?.port);
    addFact('TCP listener', result.tcp_listener);
    addFact('HTTP health', result.http_health);
    addFact('Verified files', result.verified_file_count || result.verification?.verified_file_count);

    const list = result.components || result.plan?.components || result.profiles?.full;
    components.replaceChildren();
    (Array.isArray(list) && list.length ? list : ['No component closure returned']).forEach((item) => {
      const li = document.createElement('li');
      li.textContent = String(item);
      components.appendChild(li);
    });
    raw.textContent = JSON.stringify(result, null, 2);
  }

  async function request(path, body) {
    const response = await fetch(`${api}${path}`, {
      method: body ? 'POST' : 'GET',
      headers: body ? {'Content-Type': 'application/json'} : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
    const result = await response.json();
    if (!response.ok) {
      const error = new Error(result.detail?.message || `Request failed with ${response.status}`);
      error.result = result;
      throw error;
    }
    return result;
  }

  async function run(action) {
    setBusy(true);
    try {
      const base = payload();
      let result;
      if (action === 'plan') result = await request('/plan', base);
      else if (action === 'build') result = await request('/package', {...base, clean: true});
      else if (action === 'verify') result = await request('/verify', {install_name: base.install_name});
      else result = await request('/probe', {host: base.host, port: base.port, health_path: '/health', timeout: 2});
      render(result);
    } catch (error) {
      render(error.result || {classification: 'HHS_PASS_184_STUDIO_REQUEST_FAILED', message: error.message}, true);
    } finally {
      setBusy(false);
    }
  }

  form.addEventListener('click', (event) => {
    const button = event.target.closest('[data-action]');
    if (button) run(button.dataset.action);
  });

  request('/status')
    .then((result) => {
      badge.className = 'badge ready';
      badge.textContent = 'VM81 package authority available';
      render(result);
    })
    .catch((error) => {
      badge.className = 'badge pending';
      badge.textContent = 'Authority unavailable';
      render(error.result || {classification: 'HHS_PASS_184_STATUS_UNAVAILABLE', message: error.message}, true);
    });
})();
