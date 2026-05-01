<template>
  <div class="focus-layout page-shell">
    <aside class="focus-sidebar">
      <div class="calendar-card">
        <div class="calendar-head">
          <button class="icon-btn" type="button"><i class="fas fa-chevron-left"></i></button>
          <strong>{{ monthLabel }}</strong>
          <button class="icon-btn" type="button"><i class="fas fa-chevron-right"></i></button>
        </div>
        <div class="weekdays">
          <span v-for="wd in weekDays" :key="wd">{{ wd }}</span>
        </div>
        <div class="days-grid">
          <button
            v-for="day in calendarDays"
            :key="day.toISOString()"
            class="day-cell"
            :class="{ muted: !isCurrentMonth(day), today: isToday(day) }"
            type="button"
          >
            {{ format(day, 'd') }}
          </button>
        </div>
      </div>

      <nav class="sections-card">
        <button class="section-item active"><i class="fas fa-bookmark"></i> В фокусе</button>
        <button class="section-item"><i class="fas fa-play"></i> В работе <span>{{ activeTasksCount }}</span></button>
        <button class="section-item"><i class="fas fa-calendar-day"></i> Сегодня <span>{{ todayTasksCount }}</span></button>
        <button class="section-item"><i class="fas fa-clock"></i> Просрочено <span>{{ overdueTasksCount }}</span></button>
      </nav>
    </aside>

    <section class="focus-content">
      <div class="content-head">
        <h2 class="page-title"><i class="fas fa-list me-2"></i>В фокусе</h2>
      </div>

      <router-link to="/tasks/create" class="add-task-row">
        <i class="fas fa-plus"></i>
        Добавить задачу
      </router-link>

      <div v-if="visibleTasks.length === 0" class="empty-state">
        <i class="fas fa-inbox"></i>
        <p>Задачи не найдены</p>
      </div>

      <div v-else class="task-rows">
        <article
          v-for="item in visibleTasks"
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
            <p class="task-sub">{{ truncateText(item.task.description, 90) }}</p>
            <div class="chips">
              <span class="chip muted"><i class="far fa-calendar-alt"></i> {{ formatDate(item.task.created_at) }}</span>
              <span v-if="item.task.project" class="chip"><i class="fas fa-briefcase"></i> {{ item.task.project.name }}</span>
              <span v-if="item.task.category" class="chip"><i class="far fa-folder"></i> {{ item.task.category.name }}</span>
              <span v-if="item.task.priority" class="chip danger"><i class="fas fa-flag"></i> {{ item.task.priority.name }}</span>
              <span v-if="item.isChild" class="chip child"><i class="fas fa-level-down-alt"></i> Подзадача</span>
            </div>
          </div>
          <div class="task-actions">
            <button class="icon-btn" @click.stop="toggleTimeTracking(item.task)" :disabled="!item.task.can_edit">
              <i class="fas" :class="getTimeTrackingIcon(item.task)"></i>
            </button>
            <button class="icon-btn" @click.stop="editTask(item.task.id)" :disabled="!item.task.can_edit">
              <i class="fas fa-pen"></i>
            </button>
            <button class="icon-btn danger" @click.stop="deleteTask(item.task.id)" :disabled="!item.task.can_edit">
              <i class="fas fa-trash"></i>
            </button>
            <router-link class="icon-btn" :to="`/tasks/create?parent=${item.task.id}`" title="Создать подзадачу">
              <i class="fas fa-code-branch"></i>
            </router-link>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'
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
        if (task && !task.can_edit) {
          toast.error('Режим просмотра: удаление недоступно')
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

    const startTimeTracking = async (taskId) => {
      const task = tasks.value.find(item => item.id === taskId)
      if (task && !task.can_edit) {
        toast.error('Режим просмотра: запуск таймера недоступен')
        return
      }
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
        'todo': 'soft-blue',
        'in_progress': 'soft-purple',
        'done': 'soft-green',
        'archived': 'soft-gray'
      }
      return statusMap[status] || 'soft-blue'
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
      } else {
        startTimeTracking(task.id)
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
      monthLabel,
      weekDays,
      calendarDays,
      activeTasksCount,
      todayTasksCount,
      overdueTasksCount,
      goToTaskDetail,
      editTask,
      deleteTask,
      startTimeTracking,
      getStatusText,
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
.focus-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 16px;
  min-height: calc(100vh - 170px);
}

.focus-sidebar,
.focus-content {
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(188, 204, 233, 0.9);
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(35, 63, 123, 0.1);
  padding: 14px;
}

.calendar-card {
  padding: 4px;
}

.calendar-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.weekdays,
.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.weekdays {
  font-size: 0.75rem;
  color: #7b8cab;
  margin-bottom: 4px;
}

.weekdays span {
  text-align: center;
}

.day-cell {
  border: none;
  background: transparent;
  height: 30px;
  border-radius: 8px;
  color: #2b3c5c;
}

.day-cell.muted {
  opacity: 0.5;
}

.day-cell.today {
  background: #f0f5ff;
  border: 1px solid #b9c9ea;
}

.sections-card {
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-item {
  border: none;
  background: transparent;
  text-align: left;
  color: #334968;
  border-radius: 10px;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-item.active,
.section-item:hover {
  background: #eef3ff;
}

.content-head {
  margin-bottom: 12px;
}

.add-task-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px dashed #b9c8e8;
  color: #556c90;
  background: rgba(255, 255, 255, 0.8);
  margin-bottom: 12px;
}

.task-rows {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-row {
  border-radius: 12px;
  padding: 10px 12px;
  border: 1px solid #cedaf1;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
}

.row-todo { background: #ecf2ff; }
.row-progress { background: #efeaff; }
.row-done { background: #eaf7ea; }
.row-archived { background: #f5f6f8; }

.task-title {
  margin: 0 0 2px 0;
  color: #1e2f4b;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.collapse-btn {
  width: 24px;
  height: 24px;
  border: 1px solid #c3d1eb;
  border-radius: 8px;
  background: #fff;
  color: #36507b;
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
  color: #5f7193;
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
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(177, 195, 227, 0.9);
  padding: 2px 8px;
  color: #43597d;
}

.chip.danger {
  background: #ffe8ea;
  border-color: #ffb8c0;
  color: #a33745;
}

.chip.muted {
  color: #6a7c9f;
}

.chip.child {
  background: #edf6ff;
  border-color: #b9daf9;
  color: #2d5982;
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.task-row.is-child {
  margin-left: 28px;
  border-style: dashed;
}

.icon-btn {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  border: 1px solid #c3d1eb;
  background: #fff;
  color: #36507b;
}

.icon-btn.danger {
  color: #b4364a;
}

.empty-state {
  padding: 30px 0;
  text-align: center;
  color: #768ab0;
}

.soft-blue { background: #dce8ff; color: #244981; }
.soft-purple { background: #e9ddff; color: #4f3b82; }
.soft-green { background: #dff4df; color: #2f6d3a; }
.soft-gray { background: #eceff4; color: #4f5e77; }

@media (max-width: 992px) {
  .focus-layout {
    grid-template-columns: 1fr;
  }
}

</style>