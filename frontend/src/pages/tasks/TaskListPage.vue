<template>
  <div class="tasks-page page-shell">
    <div class="tasks-surface">
      <div class="tasks-head">
        <div>
          <h2 class="page-title"><i class="fas fa-list-check me-2"></i>Задачи</h2>
          <p class="section-subtitle">Быстрый список: ищи, фильтруй, открывай детали.</p>
        </div>
        <div class="tasks-actions">
          <router-link to="/kanban" class="btn btn-outline-secondary">
            <i class="fas fa-table-columns me-1"></i> Канбан
          </router-link>
          <router-link to="/tasks/create" class="btn btn-primary">
            <i class="fas fa-plus me-1"></i> Новая задача
          </router-link>
        </div>
      </div>

      <div class="tasks-toolbar card">
        <div class="card-body">
          <div class="toolbar-row">
            <div class="search">
              <i class="fas fa-search"></i>
              <input v-model="query" class="form-control" type="text" placeholder="Поиск по названию и описанию">
            </div>
            <div class="status-filters scope-filters">
              <button type="button" class="filter-pill" :class="{ active: taskScope === 'all' }" @click="setTaskScope('all')">Все задачи</button>
              <button type="button" class="filter-pill" :class="{ active: taskScope === 'collaborative' }" @click="setTaskScope('collaborative')">Совместные</button>
              <button type="button" class="filter-pill" :class="{ active: taskScope === 'favorites' }" @click="setTaskScope('favorites')"><i class="fas fa-star me-1"></i>Избранное</button>
              <select
                id="taskStatusFilter"
                v-model="statusFilter"
                class="form-select status-filter-select"
                aria-label="Фильтр по статусу"
              >
                <option value="all">Все статусы</option>
                <option value="todo">К выполнению</option>
                <option value="in_progress">В процессе</option>
                <option value="done">Выполнено</option>
                <option value="archived">Архив</option>
              </select>
            </div>
          </div>
          <div class="kpis">
            <span class="kpi">Активные: <strong>{{ activeTasksCount }}</strong></span>
            <span class="kpi">Сегодня: <strong>{{ todayTasksCount }}</strong></span>
            <span class="kpi">Просрочено: <strong>{{ overdueTasksCount }}</strong></span>
          </div>
        </div>
      </div>

      <div v-if="visibleTasksFiltered.length === 0" class="empty-state card">
        <div class="card-body">
          <i class="fas fa-inbox"></i>
          <p>Задачи не найдены</p>
        </div>
      </div>

      <div v-else class="task-rows">
        <transition-group name="slide-up" tag="div" class="task-rows">
          <article
            v-for="item in visibleTasksFiltered"
            :key="item.task.id"
            class="task-row"
            :class="[getRowClass(item.task), { 'is-child': item.isChild }]"
            @click="goToTaskDetail(item.task.id)"
          >
            <div class="task-main">
              <div class="title-row">
                <button
                  v-if="hasSubtasks(item.task.id)"
                  class="collapse-btn"
                  type="button"
                  @click.stop="toggleSubtasks(item.task.id)"
                >
                  <i class="fas" :class="isExpanded(item.task.id) ? 'fa-chevron-down' : 'fa-chevron-right'"></i>
                </button>
                <span v-else class="collapse-placeholder"></span>
                <h6 class="task-title">{{ item.task.title }}</h6>
              </div>
              <p v-if="item.task.description" class="task-sub">{{ truncateText(item.task.description, 110) }}</p>
              <div class="chips">
                <span class="chip" :class="getStatusChipClass(item.task.status)">{{ getStatusText(item.task.status) }}</span>
                <span class="chip muted">{{ formatDate(item.task.created_at) }}</span>
                <span v-if="!item.task.project" class="chip chip-personal">Личная</span>
                <span v-if="item.task.project" class="chip chip-collaborative">Совместная</span>
                <span v-if="item.task.project" class="chip" :class="getProjectChipClass(item.task.project?.id)">{{ item.task.project.name }}</span>
                <span v-if="item.task.category" class="chip" :class="getCategoryChipClass(item.task.category?.id)">
                  <span class="me-1">{{ item.task.category.icon || '📁' }}</span>{{ item.task.category.name }}
                </span>
                <span v-if="item.task.priority" class="chip" :class="getPriorityChipClass(item.task.priority)">{{ item.task.priority.name }}</span>
                <span v-if="item.isChild" class="chip child">Подзадача</span>
                <span v-if="item.task.collaborators?.length" class="chip chip-coworkers">
                  <i class="fas fa-users me-1"></i>{{ item.task.collaborators.map((u) => u.username).join(', ') }}
                </span>
                <span v-if="countdownLabelForTask(item.task.id)" class="chip chip-timer-countdown">
                  <i class="fas fa-bell me-1"></i>До сигнала: {{ countdownLabelForTask(item.task.id) }}
                </span>
              </div>
            </div>
            <div class="task-actions">
              <button
                class="icon-btn star-btn"
                :class="{ active: item.task.is_favorited }"
                type="button"
                @click.stop="toggleFavorite(item.task)"
                title="Избранное"
              >
                <i class="fas fa-star"></i>
              </button>
              <button class="icon-btn" @click.stop="toggleTimeTracking(item.task)" :disabled="!item.task.can_edit" title="Таймер">
                <i class="fas" :class="getTimeTrackingIcon(item.task)"></i>
              </button>
              <button class="icon-btn" @click.stop="editTask(item.task.id)" :disabled="!item.task.can_edit" title="Редактировать">
                <i class="fas fa-pen"></i>
              </button>
              <button class="icon-btn danger" @click.stop="deleteTask(item.task.id)" :disabled="!item.task.can_delete" title="Удалить">
                <i class="fas fa-trash"></i>
              </button>
              <router-link class="icon-btn" :to="`/tasks/create?parent=${item.task.id}`" title="Подзадача">
                <i class="fas fa-code-branch"></i>
              </router-link>
            </div>
          </article>
        </transition-group>
      </div>

      <div v-if="timerModalOpen" class="timer-modal-backdrop" @click.self="timerModalOpen = false">
        <div class="timer-modal card shadow" @click.stop>
          <div class="card-body">
            <h5 class="card-title mb-2">
              <i class="fas fa-clock me-2 text-primary"></i>Таймер
            </h5>
            <p v-if="timerModalTask" class="text-muted small mb-3">
              Задача: <strong>{{ timerModalTask.title }}</strong>
            </p>
            <div class="mb-3">
              <label class="form-label">Лимит времени (минуты)</label>
              <input
                v-model.number="timerModalMinutes"
                type="number"
                class="form-control"
                min="0"
                max="720"
                placeholder="0 — без сигнала"
              >
              <small class="form-text text-muted">0 — только учёт времени без обратного отсчёта и звука.</small>
            </div>
            <div class="form-check mb-2">
              <input id="tm-sound" v-model="timerModalSound" class="form-check-input" type="checkbox">
              <label class="form-check-label" for="tm-sound">Звуковой сигнал по окончании</label>
            </div>
            <div class="form-check mb-3">
              <input id="tm-stop" v-model="timerModalAutoStop" class="form-check-input" type="checkbox">
              <label class="form-check-label" for="tm-stop">Остановить учёт времени, когда время выйдет</label>
            </div>
            <div class="d-flex flex-wrap gap-2 justify-content-between">
              <button type="button" class="btn btn-outline-secondary btn-sm" @click="playTimerPreview">
                <i class="fas fa-volume-high me-1"></i>Проверить звук
              </button>
              <div class="d-flex gap-2">
                <button type="button" class="btn btn-outline-secondary" @click="timerModalOpen = false">Отмена</button>
                <button type="button" class="btn btn-primary" @click="confirmStartTimer">Старт</button>
              </div>
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
import { useTaskTimerCountdown } from '@/composables/useTaskTimerCountdown'
import { playTimerExpirySound } from '@/utils/timerAlertSound'
import { format, startOfMonth, endOfMonth, startOfWeek, addDays, isSameMonth, isSameDay } from 'date-fns'
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
    const currentDate = ref(new Date())
    const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    const expandedParents = ref({})
    const query = ref('')
    const statusFilter = ref('all')
    const taskScope = ref('all')

    const timerModalOpen = ref(false)
    const timerModalTask = ref(null)
    const timerModalMinutes = ref(25)
    const timerModalSound = ref(true)
    const timerModalAutoStop = ref(false)

    const fetchTasks = async () => {
      try {
        loading.value = true
        const params = {}
        if (taskScope.value === 'collaborative') params.collaborative = 1
        if (taskScope.value === 'favorites') params.favorites = 1
        const response = await api.getTasks(params)
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

    const filteredTasks = computed(() => tasks.value)
    const tasksByParent = computed(() => {
      const map = {}
      for (const task of tasks.value) {
        const parentId = task.parent_task?.id || null
        if (!map[parentId]) {
          map[parentId] = []
        }
        map[parentId].push(task)
      }
      return map
    })
    const visibleTasks = computed(() => {
      const result = []
      const knownIds = new Set(tasks.value.map(task => task.id))
      const parents = [
        ...(tasksByParent.value[null] || []),
        ...tasks.value.filter(task => task.parent_task?.id && !knownIds.has(task.parent_task.id))
      ]
      for (const parent of parents) {
        result.push({ task: parent, isChild: false })
        if (expandedParents.value[parent.id]) {
          const subtasks = tasksByParent.value[parent.id] || []
          for (const subtask of subtasks) {
            result.push({ task: subtask, isChild: true })
          }
        }
      }
      return result
    })
    const visibleTasksFiltered = computed(() => {
      const q = query.value.trim().toLowerCase()
      return visibleTasks.value.filter(item => {
        const task = item.task
        if (statusFilter.value !== 'all' && task.status !== statusFilter.value) return false
        if (!q) return true
        const hay = `${task.title || ''} ${task.description || ''}`.toLowerCase()
        return hay.includes(q)
      })
    })
    const monthLabel = computed(() => format(currentDate.value, 'LLLL yyyy', { locale: ru }))
    const calendarDays = computed(() => {
      const startMonth = startOfMonth(currentDate.value)
      const endMonth = endOfMonth(currentDate.value)
      const startDate = startOfWeek(startMonth, { weekStartsOn: 1 })
      const days = []
      let day = startDate
      while (days.length < 42) {
        days.push(day)
        if (day > endMonth && days.length >= 35) break
        day = addDays(day, 1)
      }
      return days
    })
    const activeTasksCount = computed(() => tasks.value.filter(t => t.status === 'in_progress' || t.status === 'todo').length)
    const todayTasksCount = computed(() => tasks.value.filter(t => t.due_date && isSameDay(new Date(t.due_date), new Date())).length)
    const overdueTasksCount = computed(() => tasks.value.filter(t => t.due_date && new Date(t.due_date) < new Date() && t.status !== 'done').length)

    const fetchTimeEntries = async () => {
      try {
        const response = await api.getTimeEntries()
        timeEntries.value = response.data
      } catch (error) {
        console.error('Error fetching time entries:', error)
      }
    }

    const {
      tick,
      scheduleCountdown,
      clearStoredCountdown,
      remainingSecondsForEntry,
      formatCountdown,
      loadCountdown
    } = useTaskTimerCountdown(timeEntries, {
      stopEntry: async (entryId) => {
        await api.stopTimeEntry(entryId)
        toast.success('Таймер остановлен по лимиту')
        await fetchTimeEntries()
      }
    })

    const goToTaskDetail = (taskId) => {
      router.push(`/tasks/${taskId}/edit`)
    }

    const editTask = (taskId) => {
      const task = tasks.value.find(item => item.id === taskId)
      if (task && !task.can_edit) {
        toast.error('Режим просмотра: редактирование недоступно')
        return
      }
      router.push(`/tasks/${taskId}/edit`)
    }

    const deleteTask = async (taskId) => {
      if (confirm('Вы уверены, что хотите удалить эту задачу?')) {
        const task = tasks.value.find(item => item.id === taskId)
        if (task && !task.can_delete) {
          toast.error('Удаление недоступно')
          return
        }
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

    const stopTimeTracking = async (entryId) => {
      try {
        const cfg = loadCountdown()
        if (cfg && cfg.entryId === entryId) {
          clearStoredCountdown()
        }
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

    const countdownLabelForTask = (taskId) => {
      void tick.value
      const entry = getActiveEntry(taskId)
      if (!entry) return ''
      const sec = remainingSecondsForEntry(entry.id)
      if (sec == null) return ''
      return formatCountdown(sec)
    }

    const confirmStartTimer = async () => {
      const task = timerModalTask.value
      if (!task?.can_edit) return
      const mins = Number(timerModalMinutes.value)
      if (!Number.isFinite(mins) || mins < 0) {
        toast.error('Укажите неотрицательное число минут')
        return
      }
      try {
        const { data } = await api.startTimeEntry(task.id, { description: 'Таймер' })
        toast.success('Таймер запущен')
        if (mins > 0) {
          scheduleCountdown(data.id, mins, timerModalSound.value, timerModalAutoStop.value)
        } else {
          clearStoredCountdown()
        }
        timerModalOpen.value = false
        await fetchTimeEntries()
      } catch (error) {
        toast.error('Ошибка запуска таймера')
        console.error('Error starting time tracking:', error)
      }
    }

    const playTimerPreview = () => {
      playTimerExpirySound()
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
        'todo': 'soft-blue',
        'in_progress': 'soft-purple',
        'done': 'soft-green',
        'archived': 'soft-gray'
      }
      return statusMap[status] || 'soft-blue'
    }

    const getStatusChipClass = (status) => {
      const statusMap = {
        todo: 'chip-status-todo',
        in_progress: 'chip-status-progress',
        done: 'chip-status-done',
        archived: 'chip-status-archived'
      }
      return statusMap[status] || 'chip-status-todo'
    }

    const getPriorityChipClass = (priority) => {
      if (!priority || typeof priority.level !== 'number') return 'chip-priority-default'
      if (priority.level >= 4) return 'chip-priority-critical'
      if (priority.level === 3) return 'chip-priority-high'
      if (priority.level === 2) return 'chip-priority-medium'
      return 'chip-priority-low'
    }

    const getProjectChipClass = (projectId) => {
      const palette = ['chip-project-a', 'chip-project-b', 'chip-project-c', 'chip-project-d']
      if (!projectId) return palette[0]
      return palette[Math.abs(Number(projectId)) % palette.length]
    }

    const getCategoryChipClass = (categoryId) => {
      const palette = ['chip-category-a', 'chip-category-b', 'chip-category-c', 'chip-category-d']
      if (!categoryId) return palette[0]
      return palette[Math.abs(Number(categoryId)) % palette.length]
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return format(new Date(dateString), 'dd MMM yyyy, HH:mm', { locale: ru })
    }

    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    const getTimeTrackingIcon = (task) => {
      return getActiveEntry(task.id) ? 'fa-stop' : 'fa-play'
    }

    const hasSubtasks = (taskId) => {
      return (tasksByParent.value[taskId] || []).length > 0
    }

    const isExpanded = (taskId) => {
      return !!expandedParents.value[taskId]
    }

    const toggleSubtasks = (taskId) => {
      expandedParents.value = {
        ...expandedParents.value,
        [taskId]: !expandedParents.value[taskId]
      }
    }

    const getRowClass = (task) => {
      const map = {
        todo: 'row-todo',
        in_progress: 'row-progress',
        done: 'row-done',
        archived: 'row-archived'
      }
      return map[task.status] || 'row-todo'
    }

    const toggleTimeTracking = (task) => {
      const activeEntry = getActiveEntry(task.id)
      if (activeEntry) {
        stopTimeTracking(activeEntry.id)
        return
      }
      if (!task.can_edit) {
        toast.error('Режим просмотра: запуск таймера недоступен')
        return
      }
      timerModalTask.value = task
      timerModalMinutes.value = 25
      timerModalSound.value = true
      timerModalAutoStop.value = false
      timerModalOpen.value = true
    }

    const setTaskScope = (scope) => {
      taskScope.value = scope
      fetchTasks()
    }

    const toggleFavorite = async (task) => {
      try {
        const { data } = await api.toggleTaskFavorite(task.id)
        if (taskScope.value === 'favorites' && !data.is_favorited) {
          await fetchTasks()
          return
        }
        task.is_favorited = data.is_favorited
      } catch (error) {
        toast.error('Не удалось обновить избранное')
        console.error('toggleFavorite', error)
      }
    }

    const isCurrentMonth = (day) => isSameMonth(day, currentDate.value)
    const isToday = (day) => isSameDay(day, new Date())

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
      filteredTasks,
      visibleTasks,
      visibleTasksFiltered,
      monthLabel,
      weekDays,
      calendarDays,
      activeTasksCount,
      todayTasksCount,
      overdueTasksCount,
      query,
      statusFilter,
      taskScope,
      setTaskScope,
      toggleFavorite,
      goToTaskDetail,
      editTask,
      deleteTask,
      timerModalOpen,
      timerModalTask,
      timerModalMinutes,
      timerModalSound,
      timerModalAutoStop,
      confirmStartTimer,
      playTimerPreview,
      countdownLabelForTask,
      getStatusText,
      getStatusChipClass,
      getPriorityChipClass,
      getProjectChipClass,
      getCategoryChipClass,
      getStatusBadgeClass,
      formatDate,
      truncateText,
      getTimeTrackingIcon,
      toggleTimeTracking,
      getRowClass,
      hasSubtasks,
      isExpanded,
      toggleSubtasks,
      isCurrentMonth,
      isToday,
      format
    }
  }
}
</script>

<style scoped>
.tasks-page {
  max-width: 1260px;
  margin: 0 auto;
}

.tasks-surface {
  position: relative;
  border-radius: 24px;
  padding: 16px;
  border: 1px solid rgba(224, 206, 232, 0.7);
  background:
    radial-gradient(circle at 12% 15%, rgba(245, 195, 210, 0.25), transparent 42%),
    radial-gradient(circle at 92% 10%, rgba(213, 193, 246, 0.22), transparent 46%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.72), rgba(252, 241, 248, 0.68));
  box-shadow: 0 16px 36px rgba(136, 110, 149, 0.12);
  backdrop-filter: blur(10px);
}

.tasks-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.tasks-actions {
  display: inline-flex;
  gap: 8px;
}

.tasks-toolbar .card-body {
  padding: 14px;
}

.toolbar-row {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}

.search {
  flex: 1;
  min-width: 240px;
  position: relative;
}

.search i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #8b7697;
}

.search .form-control {
  padding-left: 36px;
}

.status-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-pill {
  border: 1px solid rgba(216, 196, 226, 0.8);
  background: rgba(255, 255, 255, 0.92);
  border-radius: 999px;
  color: #65567d;
  padding: 7px 12px;
  font-size: 0.82rem;
}

.filter-pill.active {
  background: linear-gradient(135deg, rgba(246, 232, 245, 0.96), rgba(241, 226, 247, 0.96));
  color: #3a4c78;
  border-color: rgba(194, 170, 211, 0.9);
}

.status-filter-select {
  flex-shrink: 0;
  min-width: 188px;
  max-width: 100%;
  border: 1px solid rgba(216, 196, 226, 0.8);
  border-radius: 999px;
  color: #65567d;
  background-color: rgba(255, 255, 255, 0.92);
  font-size: 0.82rem;
  line-height: 1.25;
  padding: 7px 2.25rem 7px 12px;
  height: auto;
  min-height: 0;
  box-shadow: none;
}

.status-filter-select:focus {
  border-color: rgba(194, 170, 211, 0.95);
  box-shadow: 0 0 0 0.2rem rgba(176, 131, 200, 0.2);
  color: #3a4c78;
}

.kpis {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #7a6991;
  font-size: 0.88rem;
}

.kpi strong {
  color: #2f3f6d;
}

.task-rows {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-row {
  border-radius: 12px;
  padding: 10px 12px;
  border: 1px solid rgba(227, 211, 236, 0.88);
  display: flex;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background: #ffffff;
  backdrop-filter: none;
}

.task-row:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 22px rgba(136, 110, 149, 0.18);
}

.task-row:hover .task-actions {
  opacity: 1;
}

.row-todo { background: #fff9fd; border-left: 4px solid #ff6db8; }
.row-progress { background: #f9f4ff; border-left: 4px solid #9b7bff; }
.row-done { background: #f1fbf6; border-left: 4px solid #63c799; }
.row-archived { background: #f7f4fb; border-left: 4px solid #bca8c9; }

.task-title {
  margin: 0 0 2px 0;
  color: #2a2d4f;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.collapse-btn {
  width: 24px;
  height: 24px;
  border: 1px solid rgba(193, 209, 238, 0.82);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.78);
  color: #35527c;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.collapse-placeholder {
  width: 24px;
  height: 24px;
  display: inline-block;
}

.task-sub {
  margin: 0 0 7px 0;
  color: #7d7696;
  font-size: 0.9rem;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  font-size: 0.74rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(220, 206, 230, 0.85);
  padding: 2px 8px;
  color: #5b4e7f;
}

.chip.danger {
  background: #ffe8ea;
  border-color: #ffb8c0;
  color: #a33745;
}

.chip-status-todo {
  background: #ffe8f6;
  border-color: #ffc4e6;
  color: #9f3f7d;
}

.chip-status-progress {
  background: #efe7ff;
  border-color: #d4c1ff;
  color: #6846a8;
}

.chip-status-done {
  background: #e9f9ef;
  border-color: #bcebcf;
  color: #2c8059;
}

.chip-status-archived {
  background: #f3eef8;
  border-color: #dbcee6;
  color: #705d86;
}

.chip-project-a { background: #e8f1ff; border-color: #bbd4ff; color: #315f9d; }
.chip-project-b { background: #eafbf4; border-color: #bcecd4; color: #2f7a5d; }
.chip-project-c { background: #fff2e8; border-color: #f4cfb4; color: #9b6438; }
.chip-project-d { background: #f2ecff; border-color: #d7c6ff; color: #6146a8; }

.chip-category-a { background: #fff6de; border-color: #f3e1a8; color: #8d6a13; }
.chip-category-b { background: #ffecec; border-color: #ffc8c8; color: #a14444; }
.chip-category-c { background: #e8f7ff; border-color: #b8e5fa; color: #2f6f93; }
.chip-category-d { background: #eef7ea; border-color: #cfe7c1; color: #4e7a3f; }

.chip-priority-low {
  background: #e8f7ff;
  border-color: #bfe7ff;
  color: #256e99;
}

.chip-priority-medium {
  background: #fff5e1;
  border-color: #ffe0a9;
  color: #9a6b12;
}

.chip-priority-high {
  background: #ffe9d9;
  border-color: #ffc7a3;
  color: #b05b17;
}

.chip-priority-critical {
  background: #ffe5ea;
  border-color: #ffb8c8;
  color: #ab2748;
}

.chip-priority-default {
  background: #f3f0ff;
  border-color: #ddd4ff;
  color: #5f4da5;
}

.chip.muted {
  color: #5f7398;
}

.chip.child {
  background: rgba(220, 238, 255, 0.72);
  border-color: rgba(172, 206, 239, 0.82);
  color: #2f648f;
}

.chip-personal {
  background: rgba(243, 240, 255, 0.95);
  border-color: rgba(190, 180, 230, 0.75);
  color: #5a4a8a;
}

.chip-collaborative {
  background: linear-gradient(135deg, #e8f4ff, #f0f8ff);
  border-color: rgba(120, 170, 220, 0.55);
  color: #1d5a8a;
}

.chip-coworkers {
  background: rgba(232, 245, 255, 0.92);
  border-color: rgba(140, 190, 230, 0.65);
  color: #2d5f87;
  max-width: 100%;
}

.chip-timer-countdown {
  background: rgba(255, 248, 230, 0.95);
  border-color: rgba(220, 180, 90, 0.55);
  color: #8a5f12;
}

.timer-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: rgba(40, 28, 52, 0.38);
  backdrop-filter: blur(4px);
}

.timer-modal {
  width: 100%;
  max-width: 420px;
  border-radius: 18px;
  border: 1px solid rgba(219, 199, 230, 0.85);
}

.scope-filters {
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px dashed rgba(224, 206, 232, 0.65);
}

.icon-btn.star-btn.active {
  color: #c9a227;
  border-color: rgba(212, 175, 55, 0.75);
  background: rgba(255, 248, 220, 0.95);
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  opacity: 0.55;
  transition: opacity 0.18s ease;
}

.task-row.is-child {
  margin-left: 28px;
  border-style: dashed;
  background-image: linear-gradient(90deg, rgba(106, 137, 211, 0.12), transparent 35%);
}

.icon-btn {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  border: 1px solid rgba(216, 198, 229, 0.9);
  background: #ffffff;
  color: #5f4b84;
}

.icon-btn.danger {
  color: #b4364a;
}

.empty-state {
  text-align: center;
  color: #7f6a8e;
}

.soft-blue { background: #dce8ff; color: #244981; }
.soft-purple { background: #e9ddff; color: #4f3b82; }
.soft-green { background: #dff4df; color: #2f6d3a; }
.soft-gray { background: #eceff4; color: #4f5e77; }

@media (max-width: 992px) {
  .tasks-head {
    flex-direction: column;
  }
}

</style>