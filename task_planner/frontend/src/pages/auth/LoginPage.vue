<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header text-center mb-4">
        <i class="fas fa-sign-in-alt fa-3x text-primary mb-3"></i>
        <h2 class="h4">Вход в систему</h2>
        <p class="text-muted">Войдите в свой аккаунт</p>
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

        <div class="mb-3 form-check">
          <input type="checkbox" class="form-check-input" id="remember" v-model="form.remember">
          <label class="form-check-label" for="remember">Запомнить меня</label>
        </div>

        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          <span>Войти</span>
        </button>

        <div class="text-center">
          <p class="mb-0">Еще нет аккаунта?
            <router-link to="/register" class="text-primary text-decoration-none">
              Зарегистрироваться
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

export default {
  name: 'LoginPage',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    const form = ref({
      username: '',
      password: '',
      remember: false
    })

    const loading = ref(false)

    const handleSubmit = async () => {
      try {
        loading.value = true
        await authStore.login({
          username: form.value.username,
          password: form.value.password
        })
        router.push('/tasks')
      } catch (error) {
        console.error('Login error:', error)
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
  max-width: 450px;
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