async function check(endpoint, elementId) {
  const element = document.getElementById(elementId);
  element.textContent = 'Checking...';
  element.dataset.state = '';
  try {
    const response = await fetch(endpoint, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();
    element.textContent = result.status === 'ok' ? 'Healthy' : 'Connected';
    element.dataset.state = 'ok';
  } catch (error) {
    element.textContent = 'Unavailable';
    element.dataset.state = 'error';
  }
}

function refresh() {
  void Promise.all([check('/health', 'api-status'), check('/ready', 'db-status')]);
}

document.getElementById('refresh').addEventListener('click', refresh);
refresh();
