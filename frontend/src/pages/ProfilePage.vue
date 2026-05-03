<template>
  <div class="profile-page page-shell">
    <div class="profile-head">
      <div>
        <h2 class="page-title"><i class="fas fa-user me-2"></i>Профиль</h2>
        <p class="section-subtitle">Аккаунт, статистика и настройки — в одном месте.</p>
      </div>
      <button class="btn btn-outline-danger" @click="logout">
        <i class="fas fa-sign-out-alt me-1"></i> Выйти
      </button>
    </div>

    <div class="row g-4">
      <div class="col-lg-4">
        <div class="card mb-4">
          <div class="card-body text-center">
            <div class="profile-avatar mb-3">
              <span v-if="profilePhoto" class="avatar avatar-photo-wrap">
                <img :src="profilePhoto" alt="Фото профиля" class="avatar-photo">
              </span>
              <span v-else class="avatar">
                <i class="fas fa-user"></i>
              </span>
            </div>
            <div class="d-flex justify-content-center gap-2 mb-3">
              <input
                ref="avatarInput"
                class="d-none"
                type="file"
                accept="image/png,image/jpeg,image/webp,image/gif"
                @change="onAvatarSelected"
              >
              <button class="btn btn-outline-secondary btn-sm" @click="triggerAvatarSelect">
                <i class="fas fa-image me-1"></i> Сменить фото
              </button>
              <button v-if="profilePhoto" class="btn btn-outline-danger btn-sm" @click="removeAvatar">
                <i class="fas fa-trash me-1"></i> Убрать
              </button>
            </div>
            <h4 class="mb-1">{{ user?.username }}</h4>
            <p class="text-muted mb-3">{{ user?.email }}</p>
            <div class="d-flex justify-content-center gap-2">
              <button class="btn btn-outline-primary btn-sm" @click="startEditing">
                <i class="fas fa-edit me-1"></i> Редактировать профиль
              </button>
              <router-link class="btn btn-primary btn-sm" to="/tasks">
                <i class="fas fa-list-check me-1"></i> К задачам
              </router-link>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Статистика</h5>
          </div>
          <div class="card-body">
            <div class="d-flex justify-content-between mb-3">
              <span>Всего задач</span>
              <span class="badge bg-primary">{{ stats.totalTasks }}</span>
            </div>
            <div class="d-flex justify-content-between mb-3">
              <span>Выполнено</span>
              <span class="badge bg-success">{{ stats.completedTasks }}</span>
            </div>
            <div class="d-flex justify-content-between mb-3">
              <span>В процессе</span>
              <span class="badge bg-warning text-dark">{{ stats.inProgressTasks }}</span>
            </div>
            <div class="d-flex justify-content-between">
              <span>Общее время</span>
              <span class="badge bg-info">{{ stats.totalTime }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-8">
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Недавняя активность</h5>
          </div>
          <div class="card-body">
            <div v-if="recentActivity.length === 0" class="text-center py-4">
              <i class="fas fa-history fa-3x text-muted mb-3"></i>
              <p class="mb-0">Нет недавней активности</p>
            </div>
            <div v-else class="activity-list">
              <div v-for="(activity, index) in recentActivity" :key="index" class="activity-item mb-3 pb-3 border-bottom">
                <div class="d-flex justify-content-between">
                  <div>
                    <strong>{{ activity.title }}</strong>
                    <p class="mb-1 text-muted">{{ activity.description }}</p>
                    <small class="text-muted">{{ formatDate(activity.date) }}</small>
                  </div>
                  <div class="text-end">
                    <span class="badge" :class="getActivityBadgeClass(activity.type)">
                      {{ getActivityTypeText(activity.type) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">{{ isEditingProfile ? 'Редактирование профиля' : 'Настройки' }}</h5>
          </div>
          <div class="card-body">
            <template v-if="isEditingProfile">
              <div class="mb-3">
                <label for="profileUsername" class="form-label">Имя пользователя</label>
                <input id="profileUsername" class="form-control" v-model.trim="profileForm.username" maxlength="150">
              </div>
              <div class="d-flex gap-2">
                <button class="btn btn-primary" :disabled="savingProfile" @click="saveProfile">
                  <span v-if="savingProfile" class="spinner-border spinner-border-sm me-2"></span>
                  Сохранить
                </button>
                <button class="btn btn-outline-secondary" :disabled="savingProfile" @click="cancelEditing">
                  Отмена
                </button>
              </div>
            </template>
            <template v-else>
              <div class="mb-3">
                <label for="theme" class="form-label">Темный режим</label>
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" id="theme" v-model="darkMode">
                  <label class="form-check-label" for="theme">Включить темный режим</label>
                </div>
              </div>
              <div class="mb-3">
                <label for="notifications" class="form-label">Уведомления</label>
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" id="notifications" v-model="notificationsEnabled">
                  <label class="form-check-label" for="notifications">Включить уведомления</label>
                </div>
              </div>
              <div class="mb-3">
                <label for="language" class="form-label">Язык</label>
                <select class="form-select" id="language" v-model="language">
                  <option value="ru">Русский</option>
                  <option value="en">English</option>
                </select>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  max-width: 1320px;
  margin: 0 auto;
}

.profile-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.avatar {
  width: 84px;
  height: 84px;
  border-radius: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  background: linear-gradient(135deg, var(--brand-a), var(--brand-b));
  box-shadow: 0 16px 28px rgba(136, 110, 149, 0.22);
  font-size: 1.6rem;
}

.avatar-photo-wrap {
  padding: 0;
  overflow: hidden;
  background: #fff;
}

.avatar-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@media (max-width: 768px) {
  .profile-head {
    flex-direction: column;
  }
}
</style>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { format, parseISO } from 'date-fns'
import { ru } from 'date-fns/locale'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/utils/api'

export default {
  name: 'ProfilePage',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    const toast = useToast()

    const user = computed(() => authStore.user)

    const stats = ref({
      totalTasks: 0,
      completedTasks: 0,
      inProgressTasks: 0,
      totalTime: '0м'
    })

    const recentActivity = ref([])

    const darkMode = ref(false)
    const notificationsEnabled = ref(true)
    const language = ref('ru')
    const isEditingProfile = ref(false)
    const savingProfile = ref(false)
    const avatarInput = ref(null)
    const profilePhoto = ref('')
    const profileForm = ref({
      username: ''
    })
    const avatarStorageKey = computed(() => {
      const key = user.value?.id || user.value?.username || 'guest'
      return `profile_photo_${key}`
    })

    const getActivityTypeText = (type) => {
      const typeMap = {
        'task_created': 'Создание',
        'task_updated': 'Обновление',
        'task_completed': 'Завершение',
        'time_started': 'Таймер',
        'time_stopped': 'Остановка'
      }
      return typeMap[type] || type
    }

    const getActivityBadgeClass = (type) => {
      const typeMap = {
        'task_created': 'bg-success',
        'task_updated': 'bg-info',
        'task_completed': 'bg-primary',
        'time_started': 'bg-warning text-dark',
        'time_stopped': 'bg-secondary'
      }
      return typeMap[type] || 'bg-secondary'
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return format(parseISO(dateString), 'dd MMM yyyy, HH:mm', { locale: ru })
    }

    const logout = () => {
      authStore.logout()
      router.push('/login')
    }

    const syncProfileForm = () => {
      profileForm.value.username = user.value?.username || ''
    }

    const startEditing = () => {
      syncProfileForm()
      isEditingProfile.value = true
    }

    const cancelEditing = () => {
      isEditingProfile.value = false
      syncProfileForm()
    }

    const saveProfile = async () => {
      const username = profileForm.value.username.trim()
      if (!username) {
        toast.error('Имя пользователя не может быть пустым')
        return
      }
      try {
        savingProfile.value = true
        await api.updateCurrentUser({ username })
        await authStore.checkAuth()
        isEditingProfile.value = false
        toast.success('Профиль обновлен')
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Ошибка обновления профиля')
      } finally {
        savingProfile.value = false
      }
    }

    const loadAvatar = () => {
      profilePhoto.value = localStorage.getItem(avatarStorageKey.value) || ''
    }

    const triggerAvatarSelect = () => {
      avatarInput.value?.click()
    }

    const onAvatarSelected = (event) => {
      const file = event.target.files?.[0]
      if (!file) return
      if (!file.type.startsWith('image/')) {
        toast.error('Выберите файл изображения')
        return
      }
      if (file.size > 2 * 1024 * 1024) {
        toast.error('Максимальный размер изображения: 2MB')
        return
      }
      const reader = new FileReader()
      reader.onload = () => {
        profilePhoto.value = String(reader.result || '')
        localStorage.setItem(avatarStorageKey.value, profilePhoto.value)
        toast.success('Фото профиля обновлено')
      }
      reader.readAsDataURL(file)
      event.target.value = ''
    }

    const removeAvatar = () => {
      profilePhoto.value = ''
      localStorage.removeItem(avatarStorageKey.value)
      toast.success('Фото профиля удалено')
    }

    const parseDurationToSeconds = (durationString) => {
      if (!durationString) return 0
      const parts = durationString.split(':')
      if (parts.length !== 3) return 0
      return Number(parts[0]) * 3600 + Number(parts[1]) * 60 + Number(parts[2])
    }

    const formatTotalTime = (seconds) => {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      if (hours > 0) return `${hours}ч ${minutes}м`
      return `${minutes}м`
    }

    const loadProfileData = async () => {
      try {
        const [tasksRes, timeRes] = await Promise.all([api.getTasks(), api.getTimeEntries()])
        const tasks = tasksRes.data
        const timeEntries = timeRes.data

        const totalSeconds = timeEntries.reduce((sum, entry) => {
          return sum + parseDurationToSeconds(entry.duration)
        }, 0)

        stats.value = {
          totalTasks: tasks.length,
          completedTasks: tasks.filter(task => task.status === 'done').length,
          inProgressTasks: tasks.filter(task => task.status === 'in_progress').length,
          totalTime: formatTotalTime(totalSeconds)
        }

        const taskActivity = tasks.slice(0, 5).map(task => ({
          title: `Задача "${task.title}"`,
          description: `Статус: ${getStatusText(task.status)}`,
          date: task.updated_at || task.created_at,
          type: task.status === 'done' ? 'task_completed' : 'task_updated'
        }))

        recentActivity.value = taskActivity
      } catch (error) {
        console.error('Error loading profile data:', error)
      }
    }

    const getStatusText = (status) => {
      const map = {
        todo: 'К выполнению',
        in_progress: 'В процессе',
        done: 'Выполнено',
        archived: 'В архиве'
      }
      return map[status] || status
    }

    onMounted(() => {
      loadProfileData()
      syncProfileForm()
      loadAvatar()
    })

    watch(avatarStorageKey, () => {
      loadAvatar()
    })

    return {
      user,
      stats,
      recentActivity,
      darkMode,
      notificationsEnabled,
      language,
      isEditingProfile,
      savingProfile,
      avatarInput,
      profilePhoto,
      profileForm,
      logout,
      startEditing,
      cancelEditing,
      saveProfile,
      triggerAvatarSelect,
      onAvatarSelected,
      removeAvatar,
      getActivityTypeText,
      getActivityBadgeClass,
      formatDate
    }
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
}

.profile-avatar i {
  font-size: 3rem;
}

.activity-item {
  padding-bottom: 1rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.activity-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.badge {
  font-size: 0.85em;
}

@media (max-width: 992px) {
  .profile-container {
    padding: 0 15px;
  }
}
</style>