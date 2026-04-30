import axios from 'axios'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

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
      // Handle unauthorized access
      localStorage.removeItem('token')
      window.location.href = '/login'
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

  // Task endpoints
  getTasks() {
    return api.get('/tasks/')
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