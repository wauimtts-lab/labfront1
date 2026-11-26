// Пустой VITE_API_URL = запросы идут на тот же адрес, а Vite проксирует /api на бэкенд (см. vite.config.js)
const API_URL = import.meta.env.VITE_API_URL || '';

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

// Список экспонатов; необязательные фильтры: { author, epoch, style, theme, museum }
export const fetchExhibits = (filters = {}) => {
  const qs = new URLSearchParams(
    Object.entries(filters).filter(([, v]) => v)
  ).toString();
  return request('/api/exhibits' + (qs ? `?${qs}` : ''));
};

export const fetchExhibitById = (id) =>
  request(`/api/exhibits/${encodeURIComponent(id)}`);

// Похожие экспонаты (по связям в графе знаний)
export const fetchRelated = (id) =>
  request(`/api/exhibits/${encodeURIComponent(id)}/related`);

export const askQuestion = async (query) => {
  const data = await request('/api/ask', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });
  return data.answer;
};
