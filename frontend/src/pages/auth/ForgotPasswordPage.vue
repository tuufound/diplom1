<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header text-center mb-4">
        <i class="fas fa-key fa-3x text-primary mb-3"></i>
        <h2 class="h4">Восстановление пароля</h2>
        <p class="text-muted">Введите данные аккаунта и новый пароль</p>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="mb-3">
          <label class="form-label" for="username">Имя пользователя</label>
          <input id="username" v-model="form.username" class="form-control" required>
        </div>

        <div class="mb-3">
          <label class="form-label" for="email">Email</label>
          <input id="email" v-model="form.email" type="email" class="form-control" required>
        </div>

        <div class="mb-3">
          <label class="form-label" for="password">Новый пароль</label>
          <input id="password" v-model="form.newPassword" type="password" class="form-control" required>
        </div>

        <div class="mb-3">
          <label class="form-label" for="confirmPassword">Подтверждение пароля</label>
          <input id="confirmPassword" v-model="form.confirmPassword" type="password" class="form-control" required>
        </div>

        <button class="btn btn-primary w-100" :disabled="loading" type="submit">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          Обновить пароль
        </button>

        <div class="text-center mt-3">
          <router-link to="/login" class="text-decoration-none">Вернуться ко входу</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/utils/api'

export default {
  name: 'ForgotPasswordPage',
  setup() {
    const router = useRouter()
    const toast = useToast()
    const loading = ref(false)
    const form = ref({
      username: '',
      email: '',
      newPassword: '',
      confirmPassword: ''
    })

    const handleSubmit = async () => {
      if (form.value.newPassword !== form.value.confirmPassword) {
        toast.error('Пароли не совпадают')
        return
      }

      try {
        loading.value = true
        await api.resetPassword({
          username: form.value.username,
          email: form.value.email,
          new_password: form.value.newPassword
        })
        toast.success('Пароль обновлен, теперь можно войти')
        router.push('/login')
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Не удалось обновить пароль')
      } finally {
        loading.value = false
      }
    }

    return { form, loading, handleSubmit }
  }
}
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
.auth-card { width: 100%; max-width: 460px; background: #fff; border-radius: 12px; padding: 32px; box-shadow: 0 10px 24px rgba(0,0,0,.1); }
</style>
