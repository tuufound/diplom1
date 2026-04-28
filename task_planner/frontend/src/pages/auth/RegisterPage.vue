<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header text-center mb-4">
        <i class="fas fa-user-plus fa-3x text-primary mb-3"></i>
        <h2 class="h4">Регистрация</h2>
        <p class="text-muted">Создайте новый аккаунт</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="mb-3">
          <label for="username" class="form-label">Имя пользователя</label>
          <div class="input-group">
            <span class="input-group-text"><i class="fas fa-user"></i></span>
            <input
              type="text"
              class="form-control"
              id="username"
              v-model="form.username"
              placeholder="Введите имя пользователя"
              required
            >
          </div>
        </div>

        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <div class="input-group">
            <span class="input-group-text"><i class="fas fa-envelope"></i></span>
            <input
              type="email"
              class="form-control"
              id="email"
              v-model="form.email"
              placeholder="Введите email"
              required
            >
          </div>
        </div>

        <div class="mb-3">
          <label for="password" class="form-label">Пароль</label>
          <div class="input-group">
            <span class="input-group-text"><i class="fas fa-lock"></i></span>
            <input
              type="password"
              class="form-control"
              id="password"
              v-model="form.password"
              placeholder="Введите пароль"
              required
            >
          </div>
        </div>

        <div class="mb-3">
          <label for="confirmPassword" class="form-label">Подтвердите пароль</label>
          <div class="input-group">
            <span class="input-group-text"><i class="fas fa-lock"></i></span>
            <input
              type="password"
              class="form-control"
              id="confirmPassword"
              v-model="form.confirmPassword"
              placeholder="Подтвердите пароль"
              required
            >
          </div>
        </div>

        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          <span>Зарегистрироваться</span>
        </button>

        <div class="text-center">
          <p class="mb-0">Уже есть аккаунт?
            <router-link to="/login" class="text-primary text-decoration-none">
              Войти
            </router-link>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'

export default {
  name: 'RegisterPage',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    const toast = useToast()

    const form = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    })

    const loading = ref(false)

    const handleSubmit = async () => {
      if (form.value.password !== form.value.confirmPassword) {
        toast.error('Пароли не совпадают')
        return
      }

      try {
        loading.value = true
        await authStore.register({
          username: form.value.username,
          email: form.value.email,
          password: form.value.password
        })
      } catch (error) {
        console.error('Registration error:', error)
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      loading,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 500px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 40px;
  transition: all 0.3s ease;
}

.auth-card:hover {
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.auth-header {
  color: #333;
}

.auth-header i {
  color: #42b983;
}

.form-control:focus {
  border-color: #42b983;
  box-shadow: 0 0 0 0.25rem rgba(66, 185, 131, 0.25);
}

.btn-primary {
  background-color: #42b983;
  border-color: #42b983;
  padding: 10px;
  font-weight: 500;
}

.btn-primary:hover {
  background-color: #3aa876;
  border-color: #3aa876;
}

.input-group-text {
  background-color: #f8f9fa;
  border-right: 0;
}

@media (max-width: 576px) {
  .auth-card {
    padding: 30px 20px;
  }
}
</style>