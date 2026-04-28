<template>
  <div class="profile-container">
    <div class="row">
      <div class="col-lg-4">
        <div class="card mb-4">
          <div class="card-body text-center">
            <div class="profile-avatar mb-3">
              <i class="fas fa-user-circle fa-5x text-primary"></i>
            </div>
            <h4 class="mb-1">{{ user?.username }}</h4>
            <p class="text-muted mb-3">{{ user?.email }}</p>
            <div class="d-flex justify-content-center gap-2">
              <button class="btn btn-outline-primary btn-sm">
                <i class="fas fa-edit me-1"></i> Редактировать профиль
              </button>
              <button class="btn btn-outline-danger btn-sm">
                <i class="fas fa-sign-out-alt me-1"></i> Выйти
              </button>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-header bg-primary text-white">
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
          <div class="card-header bg-primary text-white">
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
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Настройки</h5>
          </div>
          <div class="card-body">
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { format, parseISO } from 'date-fns'
import { ru } from 'date-fns/locale'

export default {
  name: 'ProfilePage',
  setup() {
    const authStore = useAuthStore()

    const user = computed(() => authStore.user)

    const stats = ref({
      totalTasks: 15,
      completedTasks: 8,
      inProgressTasks: 4,
      totalTime: '25ч 30м'
    })

    const recentActivity = ref([
      {
        title: 'Задача "Проект X" выполнена',
        description: 'Вы завершили работу над проектом X',
        date: new Date().toISOString(),
        type: 'task_completed'
      },
      {
        title: 'Новая задача создана',
        description: 'Вы создали новую задачу "Исследование"',
        date: subDays(new Date(), 1).toISOString(),
        type: 'task_created'
      },
      {
        title: 'Таймер запущен',
        description: 'Вы начали отслеживание времени для задачи "Дизайн"',
        date: subDays(new Date(), 2).toISOString(),
        type: 'time_started'
      }
    ])

    const darkMode = ref(false)
    const notificationsEnabled = ref(true)
    const language = ref('ru')

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

    // Mock function to subtract days
    const subDays = (date, days) => {
      const result = new Date(date)
      result.setDate(result.getDate() - days)
      return result
    }

    onMounted(() => {
      // Fetch real user stats and activity
      console.log('Fetching user profile data...')
    })

    return {
      user,
      stats,
      recentActivity,
      darkMode,
      notificationsEnabled,
      language,
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