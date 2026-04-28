import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'

const toast = useToast()

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const router = useRouter()

  const isAuthenticated = computed(() => !!token.value)

  const setAuth = (userData, authToken) => {
    user.value = userData
    token.value = authToken
    localStorage.setItem('token', authToken)
    axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`
  }

  const clearAuth = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  const login = async (credentials) => {
    try {
      const response = await axios.post('/api/auth/login/', credentials)
      setAuth(response.data.user, response.data.access)
      toast.success('Вход выполнен успешно!')
      router.push('/tasks')
      return response.data
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Ошибка входа')
      throw error
    }
  }

  const register = async (userData) => {
    try {
      const response = await axios.post('/api/auth/register/', userData)
      toast.success('Регистрация успешна! Пожалуйста, войдите.')
      router.push('/login')
      return response.data
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Ошибка регистрации')
      throw error
    }
  }

  const logout = () => {
    clearAuth()
    toast.success('Вы успешно вышли')
    router.push('/login')
  }

  const checkAuth = async () => {
    if (token.value) {
      try {
        const response = await axios.get('/api/auth/user/')
        user.value = response.data
      } catch (error) {
        clearAuth()
      }
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth
  }
})