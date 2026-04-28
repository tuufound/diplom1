<template>
  <div class="tasks-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">
        <i class="fas fa-tasks me-2"></i>Мои задачи
      </h2>
      <router-link to="/tasks/create" class="btn btn-primary">
        <i class="fas fa-plus me-1"></i> Создать задачу
      </router-link>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <div class="d-flex flex-wrap gap-3 mb-3">
          <select v-model="filterStatus" class="form-select" style="width: 200px;">
            <option value="">Все статусы</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
            <option value="archived">Archived</option>
          </select>

          <select v-model="filterPriority" class="form-select" style="width: 200px;">
            <option value="">Все приоритеты</option>
            <option v-for="priority in priorities" :key="priority.id" :value="priority.id">
              {{ priority.name }}
            </option>
          </select>

          <select v-model="filterCategory" class="form-select" style="width: 200px;">
            <option value="">Все категории</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>

          <button class="btn btn-outline-secondary" @click="resetFilters">
            <i class="fas fa-redo me-1"></i> Сбросить
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>

    <div v-else>
      <div v-if="filteredTasks.length === 0" class="text-center py-5">
        <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
        <h4>Задач не найдено</h4>
        <p class="text-muted">Создайте новую задачу, нажав кнопку выше</p>
      </div>

      <div v-else class="row g-3">
        <div v-for="task in filteredTasks" :key="task.id" class="col-md-6 col-lg-4">
          <div class="card task-card h-100" @click="goToTaskDetail(task.id)">
            <div class="card-header d-flex justify-content-between align-items-center">
              <span class="badge" :class="getStatusBadgeClass(task.status)">
                {{ getStatusText(task.status) }}
              </span>
              <div class="dropdown">
                <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="dropdown">
                  <i class="fas fa-ellipsis-v"></i>
                </button>
                <ul class="dropdown-menu">
                  <li><a class="dropdown-item" href="#" @click.stop="startTimeTracking(task.id)">Запустить таймер</a></li>
                  <li><a class="dropdown-item" href="#" @click.stop="editTask(task.id)">Редактировать</a></li>
                  <li><hr class="dropdown-divider"></li>
                  <li><a class="dropdown-item text-danger" href="#" @click.stop="deleteTask(task.id)">Удалить</a></li>
                </ul>
              </div>
            </div>
            <div class="card-body">
              <h5 class="card-title">{{ task.title }}</h5>
              <p class="card-text text-muted mb-3">{{ truncateText(task.description, 100) }}</p>
              <div class="d-flex flex-wrap gap-2 mb-3">
                <span v-if="task.priority" class="badge bg-warning text-dark">
                  <i class="fas fa-exclamation-circle me-1"></i> {{ task.priority.name }}
                </span>
                <span v-if="task.category" class="badge bg-info">
                  <i class="fas fa-folder me-1"></i> {{ task.category.name }}
                </span>
                <span v-if="task.due_date" class="badge bg-secondary">
                  <i class="fas fa-calendar me-1"></i> {{ formatDate(task.due_date) }}
                </span>
              </div>
            </div>
            <div class="card-footer d-flex justify-content-between align-items-center">
              <small class="text-muted">
                <i class="fas fa-clock me-1"></i> {{ formatDate(task.created_at) }}
              </small>
              <button class="btn btn-sm" :class="getTimeTrackingButtonClass(task)" @click.stop="toggleTimeTracking(task)">
                <i class="fas" :class="getTimeTrackingIcon(task)"></i>
                {{ getTimeTrackingText(task) }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

export default {
  name: 'TaskListPage',
  setup() {
    const router = useRouter()
    const toast = useToast()

    const tasks = ref([])
    const categories = ref([])
    const priorities = ref([])
    const timeEntries = ref([])
    const loading = ref(false)

    const filterStatus = ref('')
    const filterPriority = ref('')
    const filterCategory = ref('')

    const fetchTasks = async () => {
      try {
        loading.value = true
        const response = await api.getTasks()
        tasks.value = response.data
      } catch (error) {
        toast.error('Ошибка загрузки задач')
        console.error('Error fetching tasks:', error)
      } finally {
        loading.value = false
      }
    }

    const fetchCategories = async () => {
      try {
        const response = await api.getCategories()
        categories.value = response.data
      } catch (error) {
        console.error('Error fetching categories:', error)
      }
    }

    const fetchPriorities = async () => {
      try {
        const response = await api.getPriorities()
        priorities.value = response.data
      } catch (error) {
        console.error('Error fetching priorities:', error)
      }
    }

    const filteredTasks = computed(() => {
      return tasks.value.filter(task => {
        const statusMatch = !filterStatus.value || task.status === filterStatus.value
        const priorityMatch = !filterPriority.value || task.priority?.id === Number(filterPriority.value)
        const categoryMatch = !filterCategory.value || task.category?.id === Number(filterCategory.value)
        return statusMatch && priorityMatch && categoryMatch
      })
    })

    const fetchTimeEntries = async () => {
      try {
        const response = await api.getTimeEntries()
        timeEntries.value = response.data
      } catch (error) {
        console.error('Error fetching time entries:', error)
      }
    }

    const resetFilters = () => {
      filterStatus.value = ''
      filterPriority.value = ''
      filterCategory.value = ''
    }

    const goToTaskDetail = (taskId) => {
      router.push(`/tasks/${taskId}/edit`)
    }

    const editTask = (taskId) => {
      router.push(`/tasks/${taskId}/edit`)
    }

    const deleteTask = async (taskId) => {
      if (confirm('Вы уверены, что хотите удалить эту задачу?')) {
        try {
          await api.deleteTask(taskId)
          toast.success('Задача успешно удалена')
          await fetchTasks()
        } catch (error) {
          toast.error('Ошибка удаления задачи')
          console.error('Error deleting task:', error)
        }
      }
    }

    const startTimeTracking = async (taskId) => {
      try {
        await api.startTimeEntry(taskId, { description: 'Автоматический запуск' })
        toast.success('Таймер запущен')
        await fetchTimeEntries()
      } catch (error) {
        toast.error('Ошибка запуска таймера')
        console.error('Error starting time tracking:', error)
      }
    }

    const stopTimeTracking = async (entryId) => {
      try {
        await api.stopTimeEntry(entryId)
        toast.success('Таймер остановлен')
        await fetchTimeEntries()
      } catch (error) {
        toast.error('Ошибка остановки таймера')
        console.error('Error stopping time tracking:', error)
      }
    }

    const getActiveEntry = (taskId) => {
      return timeEntries.value.find(entry => entry.task?.id === taskId && !entry.end_time)
    }

    const getStatusText = (status) => {
      const statusMap = {
        'todo': 'К выполнению',
        'in_progress': 'В процессе',
        'done': 'Выполнено',
        'archived': 'В архиве'
      }
      return statusMap[status] || status
    }

    const getStatusBadgeClass = (status) => {
      const statusMap = {
        'todo': 'bg-secondary',
        'in_progress': 'bg-primary',
        'done': 'bg-success',
        'archived': 'bg-dark'
      }
      return statusMap[status] || 'bg-secondary'
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return format(new Date(dateString), 'dd MMM yyyy, HH:mm', { locale: ru })
    }

    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    const getTimeTrackingButtonClass = (task) => {
      return getActiveEntry(task.id) ? 'btn-danger' : 'btn-outline-primary'
    }

    const getTimeTrackingIcon = (task) => {
      return getActiveEntry(task.id) ? 'fa-stop' : 'fa-play'
    }

    const getTimeTrackingText = (task) => {
      return getActiveEntry(task.id) ? 'Остановить' : 'Запустить'
    }

    const toggleTimeTracking = (task) => {
      const activeEntry = getActiveEntry(task.id)
      if (activeEntry) {
        stopTimeTracking(activeEntry.id)
      } else {
        startTimeTracking(task.id)
      }
    }

    onMounted(() => {
      fetchTasks()
      fetchCategories()
      fetchPriorities()
      fetchTimeEntries()
    })

    return {
      tasks,
      categories,
      priorities,
      timeEntries,
      loading,
      filterStatus,
      filterPriority,
      filterCategory,
      filteredTasks,
      resetFilters,
      goToTaskDetail,
      editTask,
      deleteTask,
      startTimeTracking,
      getStatusText,
      getStatusBadgeClass,
      formatDate,
      truncateText,
      getTimeTrackingButtonClass,
      getTimeTrackingIcon,
      getTimeTrackingText,
      toggleTimeTracking
    }
  }
}
</script>

<style scoped>
.tasks-container {
  max-width: 1400px;
  margin: 0 auto;
}

.task-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.task-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-color: rgba(0, 0, 0, 0.15);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.card-footer {
  background-color: #f8f9fa;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.badge {
  font-size: 0.85em;
}

.dropdown-menu {
  min-width: 120px;
}

.form-select {
  flex: 1;
  min-width: 150px;
}

@media (max-width: 768px) {
  .d-flex.flex-wrap.gap-3 {
    flex-direction: column;
  }

  .form-select {
    width: 100% !important;
  }
}
</style>