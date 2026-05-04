import axios from 'axios'

/**
 * На телефоне по http://192.168.x.x:3000 запросы к localhost:8000 уходят на сам телефон.
 * Если в .env забыли IP ПК, подставляем тот же хост, что у открытой страницы (только dev / LAN).
 */
function resolveApiBaseUrl() {
  const fromEnv = (import.meta.env.VITE_API_BASE_URL || '').trim()
  const hostname =
    typeof window !== 'undefined' ? window.location.hostname : ''
  const isLan =
    hostname &&
    hostname !== 'localhost' &&
    hostname !== '127.0.0.1'
  if (isLan) {
    // localhost / docker service «backend» в браузере телефона не указывают на ваш ПК
    const unusableFromPhone =
      !fromEnv ||
      fromEnv.includes('localhost') ||
      fromEnv.includes('127.0.0.1') ||
      fromEnv.includes('://backend')
    if (unusableFromPhone) {
      return `http://${hostname}:8000/api`
    }
  }
  return fromEnv || 'http://localhost:8000/api'
}

const apiBaseUrl = resolveApiBaseUrl()

// Create axios instance
const api = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Add request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      const reqUrl = String(error.config?.url || '')
      const skipRedirect =
        reqUrl.includes('/auth/login/') ||
        reqUrl.includes('/auth/register/') ||
        reqUrl.includes('/auth/refresh/')
      if (!skipRedirect) {
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default {
  // Auth endpoints
  login(data) {
    return api.post('/auth/login/', data)
  },
  register(data) {
    return api.post('/auth/register/', data)
  },
  resetPassword(data) {
    return api.post('/auth/reset-password/', data)
  },
  getCurrentUser() {
    return api.get('/auth/user/')
  },
  searchUsers(params = {}) {
    return api.get('/users/search/', { params })
  },
  updateCurrentUser(data) {
    return api.patch('/auth/user/', data)
  },

  // Task endpoints
  getTasks(params = {}) {
    return api.get('/tasks/', { params })
  },
  toggleTaskFavorite(id) {
    return api.post(`/tasks/${id}/favorite/`)
  },
  getTask(id) {
    return api.get(`/tasks/${id}/`)
  },
  createTask(data) {
    return api.post('/tasks/', data)
  },
  updateTask(id, data) {
    return api.put(`/tasks/${id}/`, data)
  },
  deleteTask(id) {
    return api.delete(`/tasks/${id}/`)
  },

  // Category endpoints
  getCategories() {
    return api.get('/categories/')
  },
  createCategory(data) {
    return api.post('/categories/', data)
  },

  // Priority endpoints
  getPriorities() {
    return api.get('/priorities/')
  },
  createPriority(data) {
    return api.post('/priorities/', data)
  },

  // Project endpoints
  getProjects() {
    return api.get('/projects/')
  },
  createProject(data) {
    return api.post('/projects/', data)
  },
  updateProject(id, data) {
    return api.put(`/projects/${id}/`, data)
  },
  deleteProject(id) {
    return api.delete(`/projects/${id}/`)
  },
  addProjectMembership(projectId, data) {
    return api.post(`/projects/${projectId}/memberships/`, data)
  },
  removeProjectMembership(projectId, membershipId) {
    return api.delete(`/projects/${projectId}/memberships/${membershipId}/`)
  },

  // Time entry endpoints
  getTimeEntries() {
    return api.get('/time-entries/')
  },
  getTimeEntry(id) {
    return api.get(`/time-entries/${id}/`)
  },
  createTimeEntry(data) {
    return api.post('/time-entries/', data)
  },
  updateTimeEntry(id, data) {
    return api.put(`/time-entries/${id}/`, data)
  },
  deleteTimeEntry(id) {
    return api.delete(`/time-entries/${id}/`)
  },
  startTimeEntry(taskId, data) {
    return api.post(`/tasks/${taskId}/start/`, data)
  },
  stopTimeEntry(timeEntryId) {
    return api.post(`/time-entries/${timeEntryId}/stop/`)
  },

  // Report endpoints
  getReports(params = {}) {
    return api.get('/reports/', { params })
  }
}