import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── Ingredientes ──────────────────────────────────────────
export const ingredientsAPI = {
  list: () => api.get('/ingredients/'),
  add: (data) => api.post('/ingredients/', data),
  addBulk: (items) => api.post('/ingredients/bulk', items),
  update: (id, data) => api.patch(`/ingredients/${id}`, data),
  remove: (id) => api.delete(`/ingredients/${id}`),
  clear: () => api.delete('/ingredients/'),
}

// ── Recetas ───────────────────────────────────────────────
export const recipesAPI = {
  generate: (preferences) => api.post('/recipes/generate', { preferences }),
  history: (params) => api.get('/recipes/history', { params }),
  toggleFavorite: (id, is_favorite) =>
    api.patch(`/recipes/history/${id}/favorite`, { is_favorite }),
  deleteHistory: (id) => api.delete(`/recipes/history/${id}`),
}
