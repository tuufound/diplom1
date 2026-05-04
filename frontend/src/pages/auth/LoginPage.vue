<template>
  <AuthPageDecor>
    <div class="auth-card card">
      <div class="auth-header">
        <div class="brand">
          <AuthBrandIcon />
          <div>
            <h2 class="h4 mb-0">{{ $t('auth.loginTitle') }}</h2>
            <p class="section-subtitle mb-0">{{ $t('auth.loginSubtitle') }}</p>
          </div>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="mb-3">
          <label for="username" class="form-label">{{ $t('auth.username') }}</label>
          <div class="input-group">
            <span class="input-group-text"><i class="fas fa-user"></i></span>
            <input
              type="text"
              class="form-control"
              id="username"
              v-model="form.username"
              :placeholder="$t('auth.placeholderUser')"
              required
            >
          </div>
        </div>

        <div class="mb-3">
          <label for="password" class="form-label">{{ $t('auth.password') }}</label>
          <div class="input-group">
            <span class="input-group-text"><i class="fas fa-lock"></i></span>
            <input
              type="password"
              class="form-control"
              id="password"
              v-model="form.password"
              :placeholder="$t('auth.placeholderPass')"
              required
            >
          </div>
        </div>

        <div class="mb-3 form-check">
          <input type="checkbox" class="form-check-input" id="remember" v-model="form.remember">
          <label class="form-check-label" for="remember">{{ $t('auth.remember') }}</label>
        </div>

        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          <span>{{ $t('auth.signIn') }}</span>
        </button>

        <div class="text-center">
          <p class="mb-0">{{ $t('auth.noAccount') }}
            <router-link to="/register" class="text-primary text-decoration-none">
              {{ $t('auth.register') }}
            </router-link>
          </p>
          <p class="mb-0 mt-2">
            <router-link to="/forgot-password" class="text-decoration-none">
              {{ $t('auth.forgot') }}
            </router-link>
          </p>
        </div>
      </form>
    </div>
  </AuthPageDecor>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import AuthPageDecor from '@/components/auth/AuthPageDecor.vue'
import AuthBrandIcon from '@/components/auth/AuthBrandIcon.vue'

export default {
  name: 'LoginPage',
  components: { AuthPageDecor, AuthBrandIcon },
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
.auth-card {
  width: min(520px, 100%);
}

.auth-card.card {
  border-radius: 18px;
  overflow: hidden;
}

.auth-header {
  padding: 16px 16px 8px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.auth-form {
  padding: 12px 16px 16px;
}

.input-group-text {
  border-radius: 12px 0 0 12px;
  border-color: rgba(219, 199, 230, 0.85);
  background: rgba(255, 255, 255, 0.92);
  color: #6f5d88;
}

.input-group .form-control {
  border-left: 0;
  border-radius: 0 12px 12px 0;
}

.input-group-text {
  border-right: 0;
}

</style>