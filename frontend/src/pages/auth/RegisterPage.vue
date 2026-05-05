<template>
  <AuthPageDecor>
    <div class="auth-card card">
      <div class="auth-header">
        <div class="brand">
          <AuthBrandIcon />
          <div>
            <h2 class="h4 mb-0">{{ $t('auth.registerTitle') }}</h2>
            <p class="section-subtitle mb-0">{{ $t('auth.registerSubtitle') }}</p>
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
          <label for="email" class="form-label">{{ $t('auth.email') }}</label>
          <div class="input-group">
            <span class="input-group-text"><i class="fas fa-envelope"></i></span>
            <input
              type="email"
              class="form-control"
              id="email"
              v-model="form.email"
              :placeholder="$t('auth.placeholderEmail')"
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

        <div class="mb-3">
          <label for="confirmPassword" class="form-label">{{ $t('auth.confirmPassword') }}</label>
          <div class="input-group">
            <span class="input-group-text"><i class="fas fa-lock"></i></span>
            <input
              type="password"
              class="form-control"
              id="confirmPassword"
              v-model="form.confirmPassword"
              :placeholder="$t('auth.placeholderConfirm')"
              required
            >
          </div>
        </div>

        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          <span>{{ $t('auth.registerSubmit') }}</span>
        </button>

        <div class="text-center">
          <p class="mb-0">{{ $t('auth.hasAccount') }}
            <router-link to="/login" class="text-primary text-decoration-none">
              {{ $t('auth.signInLink') }}
            </router-link>
          </p>
        </div>
      </form>
    </div>
  </AuthPageDecor>
</template>

<script>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import AuthPageDecor from '@/components/auth/AuthPageDecor.vue'
import AuthBrandIcon from '@/components/auth/AuthBrandIcon.vue'

export default {
  name: 'RegisterPage',
  components: { AuthPageDecor, AuthBrandIcon },
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    const toast = useToast()
    const { t } = useI18n()

    const form = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    })

    const loading = ref(false)

    const handleSubmit = async () => {
      if (form.value.password !== form.value.confirmPassword) {
        toast.error(t('auth.passwordsMismatch'))
        return
      }

      try {
        loading.value = true
        await authStore.register({
          username: form.value.username,
          email: form.value.email,
          password: form.value.password
        })
        router.push('/login')
      } catch (error) {
        const data = error?.response?.data
        if (data && typeof data === 'object') {
          const messages = Object.entries(data)
            .flatMap(([, v]) => Array.isArray(v) ? v : [v])
            .join(' ')
          toast.error(messages)
        } else {
          toast.error(t('auth.registerError'))
        }
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
  width: min(560px, 100%);
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
  border-right: 0;
}

.input-group .form-control {
  border-left: 0;
  border-radius: 0 12px 12px 0;
}

.input-group-text {
  border-right: 0;
}

</style>