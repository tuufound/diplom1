<template>
  <div class="profile-page page-shell">
    <div class="page-content-surface">
    <div class="profile-head">
      <div>
        <h2 class="page-title">
          <i class="fas fa-user-circle"></i>
          Профиль
        </h2>
        <p class="section-subtitle">Управляй своим аккаунтом и настройками</p>
      </div>
      <button class="btn btn-outline-danger" @click="logout">
        <i class="fas fa-sign-out-alt me-2"></i> Выйти
      </button>
    </div>

    <div class="row g-4">
      <!-- Left Column - Profile Card & Stats -->
      <div class="col-lg-4">
        <!-- Profile Card -->
        <div class="card profile-card">
          <div class="card-body text-center">
            <div class="profile-avatar mb-3">
              <span v-if="profilePhoto" class="avatar-photo-wrap">
                <img :src="profilePhoto" alt="Фото профиля" class="avatar-photo">
              </span>
              <span v-else class="avatar-placeholder">
                <i class="fas fa-user"></i>
              </span>
            </div>

            <div v-if="isEditingProfile" class="d-flex justify-content-center gap-2 mb-3">
              <input
                ref="avatarInput"
                class="d-none"
                type="file"
                accept="image/png,image/jpeg,image/webp,image/gif"
                @change="onAvatarSelected"
              >
              <button class="btn btn-sm btn-outline-secondary" @click="triggerAvatarSelect">
                <i class="fas fa-image me-1"></i> Сменить
              </button>
              <button v-if="profilePhoto" class="btn btn-sm btn-outline-danger" @click="removeAvatar">
                <i class="fas fa-trash me-1"></i>
              </button>
            </div>

            <h4 class="profile-name mb-1">{{ user?.username }}</h4>
            <p class="profile-email mb-3">{{ user?.email }}</p>

            <div v-if="!isEditingProfile" class="d-flex justify-content-center gap-2">
              <button class="btn btn-primary" @click="startEditing">
                <i class="fas fa-edit me-2"></i> Редактировать
              </button>
            </div>
          </div>
        </div>

        <!-- Stats Card -->
        <div class="card stats-card mt-4">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="fas fa-chart-line me-2"></i>Статистика
            </h5>
          </div>
          <div class="card-body">
            <div class="stat-item">
              <div class="stat-icon stat-icon-total">
                <i class="fas fa-tasks"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.totalTasks }}</span>
                <span class="stat-label">Всего задач</span>
              </div>
            </div>

            <div class="stat-item">
              <div class="stat-icon stat-icon-completed">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.completedTasks }}</span>
                <span class="stat-label">Выполнено</span>
              </div>
            </div>

            <div class="stat-item">
              <div class="stat-icon stat-icon-progress">
                <i class="fas fa-spinner"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.inProgressTasks }}</span>
                <span class="stat-label">В процессе</span>
              </div>
            </div>

            <div class="stat-item">
              <div class="stat-icon stat-icon-time">
                <i class="fas fa-clock"></i>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.totalTime }}</span>
                <span class="stat-label">Общее время</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Activity & Settings -->
      <div class="col-lg-8">
        <!-- Activity Card -->
        <div class="card activity-card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="fas fa-history me-2"></i>Недавняя активность
            </h5>
          </div>
          <div class="card-body">
            <div v-if="recentActivity.length === 0" class="empty-state">
              <i class="fas fa-inbox"></i>
              <p>Нет недавней активности</p>
            </div>
            <div v-else class="activity-list">
              <div v-for="(activity, index) in recentActivity" :key="index" class="activity-item">
                <div class="activity-icon" :class="getActivityIconClass(activity.type)">
                  <i :class="getActivityIcon(activity.type)"></i>
                </div>
                <div class="activity-content">
                  <strong>{{ activity.title }}</strong>
                  <p class="mb-0">{{ activity.description }}</p>
                  <small class="activity-date">{{ formatDate(activity.date) }}</small>
                </div>
                <div class="activity-badge">
                  <span class="chip" :class="getActivityChipClass(activity.type)">
                    {{ getActivityTypeText(activity.type) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Settings Card -->
        <div class="card settings-card mt-4">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="fas fa-cog me-2"></i>
              {{ isEditingProfile ? 'Редактирование профиля' : 'Настройки' }}
            </h5>
          </div>
          <div class="card-body">
            <template v-if="isEditingProfile">
              <div class="mb-4">
                <label for="profileUsername" class="form-label">Имя пользователя</label>
                <input
                  id="profileUsername"
                  class="form-control"
                  v-model.trim="profileForm.username"
                  maxlength="150"
                  placeholder="Введите имя пользователя"
                >
              </div>
              <div class="d-flex gap-3">
                <button class="btn btn-primary" :disabled="savingProfile" @click="saveProfile">
                  <span v-if="savingProfile" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fas fa-check me-2"></i>
                  Сохранить
                </button>
                <button class="btn btn-outline-secondary" :disabled="savingProfile" @click="cancelEditing">
                  <i class="fas fa-times me-2"></i> Отмена
                </button>
              </div>
            </template>
            <template v-else>
              <div class="setting-item">
                <div class="setting-info">
                  <i class="fas fa-moon setting-icon"></i>
                  <div>
                    <label for="theme" class="setting-label mb-0">Тёмный режим</label>
                    <p class="setting-desc mb-0">Переключить на тёмную тему</p>
                  </div>
                </div>
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" id="theme" v-model="darkMode">
                  <label class="form-check-label" for="theme"></label>
                </div>
              </div>

              <div class="setting-item">
                <div class="setting-info">
                  <i class="fas fa-bell setting-icon"></i>
                  <div>
                    <label for="notifications" class="setting-label mb-0">Уведомления</label>
                    <p class="setting-desc mb-0">Получать уведомления о задачах</p>
                  </div>
                </div>
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" id="notifications" v-model="notificationsEnabled">
                  <label class="form-check-label" for="notifications"></label>
                </div>
              </div>

              <div class="setting-item">
                <div class="setting-info">
                  <i class="fas fa-language setting-icon"></i>
                  <div>
                    <label for="language" class="setting-label mb-0">Язык интерфейса</label>
                    <p class="setting-desc mb-0">Выберите язык приложения</p>
                  </div>
                </div>
                <select class="form-select setting-select" id="language" v-model="language">
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
  </div>
</template>

<style scoped lang="scss">
.profile-page {
  max-width: 1320px;
  margin: 0 auto;
}

.profile-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 2rem;
}

// Profile Card Styles
.profile-card .card-body {
  padding: 2rem;
}

.profile-avatar {
  display: inline-block;
  position: relative;
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-gradient);
  color: white;
  font-size: 2.5rem;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35);
}

.avatar-photo-wrap {
  width: 100px;
  height: 100px;
  border-radius: 28px;
  overflow: hidden;
  background: var(--surface-2);
  border: 3px solid var(--glass-border);
}

.avatar-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.profile-email {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin: 0;
}

// Stats Card Styles
.stats-card .card-header {
  display: flex;
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--glass-border);
}

.stat-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.stat-icon-total {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
  color: var(--accent-primary);
}

.stat-icon-completed {
  background: rgba(72, 187, 120, 0.2);
  color: var(--success-color);
}

.stat-icon-progress {
  background: rgba(118, 75, 162, 0.2);
  color: var(--accent-secondary);
}

.stat-icon-time {
  background: rgba(99, 179, 237, 0.2);
  color: var(--info-color);
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

// Activity Card Styles
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: var(--surface-1);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: var(--surface-2);
  transform: translateX(4px);
}

.activity-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon-create {
  background: rgba(72, 187, 120, 0.15);
  color: var(--success-color);
}

.activity-icon-update {
  background: rgba(99, 179, 237, 0.15);
  color: var(--info-color);
}

.activity-icon-complete {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
  color: var(--accent-primary);
}

.activity-icon-timer {
  background: rgba(237, 137, 54, 0.15);
  color: var(--warning-color);
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-content strong {
  color: var(--text-primary);
  font-weight: 600;
}

.activity-content p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0.25rem 0 0;
}

.activity-date {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.activity-badge {
  flex-shrink: 0;
}

// Settings Card Styles
.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 0;
  border-bottom: 1px solid var(--glass-border);
}

.setting-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.setting-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.setting-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-primary);
  font-size: 1.1rem;
}

.setting-label {
  font-weight: 600;
  color: var(--text-primary);
}

.setting-desc {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.setting-select {
  width: auto;
  min-width: 140px;
}

// Form Switch Styling
.form-switch .form-check-input {
  width: 52px;
  height: 28px;
  border-radius: 14px;
  background-color: var(--surface-1);
  border: 2px solid var(--glass-border);
  cursor: pointer;
  transition: all 0.3s ease;
}

.form-switch .form-check-input:checked {
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
}

.form-switch .form-check-input:focus {
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
}

// Responsive
@media (max-width: 992px) {
  .profile-head {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (max-width: 768px) {
  .profile-page {
    padding: 0;
  }

  .stat-item {
    padding: 0.75rem 0;
  }

  .activity-item {
    flex-wrap: wrap;
  }
}
</style>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { format, parseISO } from 'date-fns'
import { ru } from 'date-fns/locale'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/utils/api'

export default {
  name: 'ProfilePage',
  setup() {
    const authStore = useAuthStore()
    const themeStore = useThemeStore()
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

    // Dark mode from theme store
    const darkMode = computed({
      get: () => themeStore.isDark,
      set: (val) => { themeStore.isDark = val }
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

    const getActivityIcon = (type) => {
      const iconMap = {
        'task_created': 'fas fa-plus-circle',
        'task_updated': 'fas fa-edit',
        'task_completed': 'fas fa-check-circle',
        'time_started': 'fas fa-play-circle',
        'time_stopped': 'fas fa-stop-circle'
      }
      return iconMap[type] || 'fas fa-circle'
    }

    const getActivityIconClass = (type) => {
      const classMap = {
        'task_created': 'activity-icon-create',
        'task_updated': 'activity-icon-update',
        'task_completed': 'activity-icon-complete',
        'time_started': 'activity-icon-timer',
        'time_stopped': 'activity-icon-timer'
      }
      return classMap[type] || 'activity-icon-update'
    }

    const getActivityChipClass = (type) => {
      const classMap = {
        'task_created': 'chip-status-done',
        'task_updated': 'chip-status-progress',
        'task_completed': 'chip-status-done',
        'time_started': 'chip-status-todo',
        'time_stopped': 'chip-status-archived'
      }
      return classMap[type] || 'chip-status-todo'
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
      getActivityIcon,
      getActivityIconClass,
      getActivityChipClass,
      formatDate
    }
  }
}
</script>