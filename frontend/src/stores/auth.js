import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  const toast = useToast()
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isAuthenticated = computed(() => !!token.value)

  const setAuth = (userData, authToken) => {
    user.value = userData
    token.value = authToken
    localStorage.setItem('token', authToken)
    // На всякий случай: "гостевой" аватар не должен тянуться в аккаунты
    localStorage.removeItem('profile_photo_guest')
  }

  const clearAuth = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  const login = async (credentials) => {
    try {
      const response = await api.login(credentials)
      setAuth(response.data.user, response.data.access)
      toast.success('Вход выполнен успешно!')
      return response.data
    } catch (error) {
      const detail = error.response?.data?.detail
      const network =
        error.code === 'ERR_NETWORK' ||
        error.message === 'Network Error' ||
        !error.response
      toast.error(
        detail ||
          (network
            ? 'Нет связи с сервером. Откройте сайт по IP ПК (например http://192.168.0.106:3000) и проверьте, что Django запущен на 0.0.0.0:8000.'
            : 'Ошибка входа')
      )
      throw error
    }
  }

  const register = async (userData) => {
    try {
      const response = await api.register(userData)
      toast.success('Регистрация успешна')
      return response.data
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Ошибка регистрации')
      throw error
    }
  }

  const logout = () => {
    clearAuth()
    toast.success('Вы успешно вышли')
  }

  const checkAuth = async () => {
    if (token.value) {
      try {
        const response = await api.getCurrentUser()
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