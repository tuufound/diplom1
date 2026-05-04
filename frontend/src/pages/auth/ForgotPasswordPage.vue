<template>
  <div class="auth-shell page-shell">
    <div class="auth-card card">
      <div class="auth-header">
        <div class="brand">
          <span class="brand-icon"><i class="fas fa-key"></i></span>
          <div>
            <h2 class="h4 mb-0">{{ $t('auth.forgotPageTitle') }}</h2>
            <p class="section-subtitle mb-0">{{ $t('auth.forgotPageSubtitle') }}</p>
          </div>
        </div>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="mb-3">
          <label class="form-label" for="username">{{ $t('auth.username') }}</label>
          <input id="username" v-model="form.username" class="form-control" required>
        </div>

        <div class="mb-3">
          <label class="form-label" for="email">{{ $t('auth.email') }}</label>
          <input id="email" v-model="form.email" type="email" class="form-control" required>
        </div>

        <div class="mb-3">
          <label class="form-label" for="password">{{ $t('auth.newPassword') }}</label>
          <input id="password" v-model="form.newPassword" type="password" class="form-control" required>
        </div>

        <div class="mb-3">
          <label class="form-label" for="confirmPassword">{{ $t('auth.confirmPasswordLabel') }}</label>
          <input id="confirmPassword" v-model="form.confirmPassword" type="password" class="form-control" required>
        </div>

        <button class="btn btn-primary w-100" :disabled="loading" type="submit">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          {{ $t('auth.updatePassword') }}
        </button>

        <div class="text-center mt-3">
          <router-link to="/login" class="text-decoration-none">{{ $t('auth.backLogin') }}</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/utils/api'

export default {
  name: 'ForgotPasswordPage',
  setup() {
    const router = useRouter()
    const toast = useToast()
    const { t } = useI18n()
    const loading = ref(false)
    const form = ref({
      username: '',
      email: '',
      newPassword: '',
      confirmPassword: ''
    })

    const handleSubmit = async () => {
      if (form.value.newPassword !== form.value.confirmPassword) {
        toast.error(t('auth.passwordsMismatch'))
        return
      }

      try {
        loading.value = true
        await api.resetPassword({
          username: form.value.username,
          email: form.value.email,
          new_password: form.value.newPassword
        })
        toast.success(t('auth.passwordUpdated'))
        router.push('/login')
      } catch (error) {
        toast.error(error.response?.data?.detail || t('auth.passwordUpdateFailed'))
      } finally {
        loading.value = false
      }
    }

    return { form, loading, handleSubmit }
  }
}
</script>

<style scoped>
.auth-shell {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 170px);
  padding: 18px;
}

.auth-card {
  width: min(540px, 100%);
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

.brand-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  background: linear-gradient(135deg, var(--brand-a), var(--brand-b));
  box-shadow: 0 12px 22px rgba(136, 110, 149, 0.22);
}

form {
  padding: 12px 16px 16px;
}
</style>
