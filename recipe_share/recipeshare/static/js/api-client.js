class ApiClient {
  constructor() { this.csrfToken = document.querySelector('meta[name="csrf-token"]')?.content; }
  async request(path, options = {}) {
    const headers = { Accept: 'application/json', ...(options.headers || {}) };
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes((options.method || 'GET').toUpperCase()) && this.csrfToken) headers['X-CSRFToken'] = this.csrfToken;
    const response = await fetch(path, { ...options, headers, credentials: 'same-origin' });
    if (!response.ok) throw new Error(`Request failed (${response.status})`);
    return response.status === 204 ? null : response.json();
  }
}
window.recipeShareApi = new ApiClient();
