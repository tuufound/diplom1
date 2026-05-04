<template>
  <AuthPageDecor>
    <div class="auth-card card">
      <div class="auth-header">
        <div class="brand">
          <AuthBrandIcon />
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
  </AuthPageDecor>
</template>

<script>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/utils/api'
import AuthPageDecor from '@/components/auth/AuthPageDecor.vue'
import AuthBrandIcon from '@/components/auth/AuthBrandIcon.vue'

export default {
  name: 'ForgotPasswordPage',
  components: { AuthPageDecor, AuthBrandIcon },
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

form {
  padding: 12px 16px 16px;
}
</style>
