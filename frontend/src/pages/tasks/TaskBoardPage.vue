<template>
  <div class="kanban-page page-shell">
    <div class="kanban-surface">
      <div class="kanban-head">
        <div>
          <h2 class="page-title"><i class="fas fa-table-columns me-2"></i>Канбан</h2>
          <p class="section-subtitle">Перетаскивай задачи между статусами или сдвигай стрелками.</p>
        </div>
        <div class="head-actions">
          <router-link to="/tasks" class="btn btn-outline-secondary">
            <i class="fas fa-list-check me-1"></i> Список
          </router-link>
          <router-link to="/tasks/create" class="btn btn-primary">
            <i class="fas fa-plus me-1"></i> Новая
          </router-link>
        </div>
      </div>

      <div class="kanban-toolbar card mb-3">
        <div class="card-body py-2 px-3">
          <div class="scope-filters">
            <button type="button" class="filter-pill" :class="{ active: taskScope === 'all' }" @click="setTaskScope('all')">Все</button>
            <button type="button" class="filter-pill" :class="{ active: taskScope === 'collaborative' }" @click="setTaskScope('collaborative')">Совместные</button>
            <button type="button" class="filter-pill" :class="{ active: taskScope === 'favorites' }" @click="setTaskScope('favorites')"><i class="fas fa-star me-1"></i>Избранное</button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="empty-state card">
        <div class="card-body">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Загружаю задачи...</p>
        </div>
      </div>

      <div v-else class="kanban-grid">
        <section
          v-for="column in columns"
          :key="column.status"
          class="kanban-column"
          :class="[getColumnClass(column.status), { 'drop-target': dropTargetStatus === column.status }]"
          @dragover.prevent
          @dragenter.prevent="onDragEnter(column.status)"
          @dragleave="onDragLeave"
          @drop="onDrop(column.status)"
        >
          <header class="column-head">
            <h5>{{ column.title }}</h5>
            <span class="count">{{ tasksByStatus(column.status).length }}</span>
          </header>

        <div v-if="tasksByStatus(column.status).length === 0" class="column-empty">
          Перетащи задачу сюда
        </div>

        <article
          v-for="task in tasksByStatus(column.status)"
          :key="task.id"
          class="task-card"
          :class="[getTaskCardClass(task), { dragging: draggingTaskId === task.id }]"
          draggable="true"
          @dragstart="onDragStart(task.id)"
          @dragend="onDragEnd"
        >
          <div class="task-title-row">
            <h6 class="task-title">{{ task.title }}</h6>
            <span v-if="task.parent_task" class="badge subtask">Подзадача</span>
          </div>
          <p v-if="task.description" class="task-desc">{{ truncateText(task.description, 120) }}</p>

          <div class="chips">
            <span class="chip" :class="getStatusChipClass(task.status)">{{ getStatusText(task.status) }}</span>
            <span v-if="!task.project" class="chip chip-personal">Личная</span>
            <span v-if="task.project" class="chip chip-collaborative">Совместная</span>
            <span v-if="task.project" class="chip" :class="getProjectChipClass(task.project?.id)">{{ task.project.name }}</span>
            <span v-if="task.category" class="chip" :class="getCategoryChipClass(task.category?.id)">
              <span class="me-1">{{ task.category.icon || '📁' }}</span>{{ task.category.name }}
            </span>
            <span v-if="task.priority" class="chip" :class="getPriorityChipClass(task.priority)">{{ task.priority.name }}</span>
          </div>

          <div class="task-actions">
            <button
              type="button"
              class="icon-btn star-btn"
              :class="{ active: task.is_favorited }"
              @click.stop="toggleFavorite(task)"
              title="Избранное"
            >
              <i class="fas fa-star"></i>
            </button>
            <button class="icon-btn" :disabled="!task.can_edit" @click="shiftStatus(task, -1)" title="Влево">
              <i class="fas fa-arrow-left"></i>
            </button>
            <button class="icon-btn" :disabled="!task.can_edit" @click="shiftStatus(task, 1)" title="Вправо">
              <i class="fas fa-arrow-right"></i>
            </button>
            <router-link class="icon-btn" :to="`/tasks/${task.id}/edit`" title="Редактировать">
              <i class="fas fa-pen"></i>
            </router-link>
          </div>
        </article>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'

export default {
  name: 'TaskBoardPage',
  setup() {
    const toast = useToast()
    const loading = ref(false)
    const tasks = ref([])
    const draggingTaskId = ref(null)
    const dropTargetStatus = ref(null)
    const columns = [
      { status: 'todo', title: 'К выполнению' },
      { status: 'in_progress', title: 'В процессе' },
      { status: 'done', title: 'Выполнено' },
      { status: 'archived', title: 'Архив' }
    ]

    const taskScope = ref('all')

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

    const tasksByStatus = (status) => tasks.value.filter(task => task.status === status)

    const toUpdatePayload = (task, nextStatus) => ({
      title: task.title,
      description: task.description,
      status: nextStatus,
      priority: task.priority?.id || null,
      project: task.project?.id || null,
      category: task.category?.id || null,
      parent_task: task.parent_task?.id || null,
      due_date: task.due_date || null,
      is_active: task.is_active
    })

    const setTaskStatus = async (task, nextStatus) => {
      if (!task.can_edit || task.status === nextStatus) return
      try {
        await api.updateTask(task.id, toUpdatePayload(task, nextStatus))
        task.status = nextStatus
      } catch (error) {
        toast.error('Не удалось обновить статус')
        console.error('Error updating task status:', error)
      }
    }

    const shiftStatus = async (task, direction) => {
      const idx = columns.findIndex(col => col.status === task.status)
      const next = columns[idx + direction]
      if (!next) return
      await setTaskStatus(task, next.status)
    }

    const onDragStart = (taskId) => {
      draggingTaskId.value = taskId
    }

    const onDragEnd = () => {
      draggingTaskId.value = null
      dropTargetStatus.value = null
    }

    const onDragEnter = (status) => {
      if (draggingTaskId.value) {
        dropTargetStatus.value = status
      }
    }

    const onDragLeave = () => {
      dropTargetStatus.value = null
    }

    const onDrop = async (status) => {
      const task = tasks.value.find(item => item.id === draggingTaskId.value)
      if (!task) return
      await setTaskStatus(task, status)
      draggingTaskId.value = null
      dropTargetStatus.value = null
    }

    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? `${text.substring(0, length)}...` : text
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

    const getStatusText = (status) => {
      const statusMap = {
        todo: 'К выполнению',
        in_progress: 'В процессе',
        done: 'Выполнено',
        archived: 'В архиве'
      }
      return statusMap[status] || status
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

    const getTaskCardClass = (task) => {
      const map = {
        todo: 'card-todo',
        in_progress: 'card-progress',
        done: 'card-done',
        archived: 'card-archived'
      }
      return map[task.status] || 'card-todo'
    }

    const getColumnClass = (status) => {
      const map = {
        todo: 'column-todo',
        in_progress: 'column-progress',
        done: 'column-done',
        archived: 'column-archived'
      }
      return map[status] || 'column-todo'
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

    onMounted(fetchTasks)

    return {
      loading,
      tasks,
      taskScope,
      setTaskScope,
      toggleFavorite,
      columns,
      draggingTaskId,
      dropTargetStatus,
      tasksByStatus,
      onDragStart,
      onDragEnd,
      onDragEnter,
      onDragLeave,
      onDrop,
      shiftStatus,
      truncateText,
      getPriorityChipClass,
      getTaskCardClass,
      getProjectChipClass,
      getCategoryChipClass,
      getStatusText,
      getStatusChipClass,
      getColumnClass
    }
  }
}
</script>

<style scoped>
.kanban-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.page-title {
  color: #1f2f57;
}

.head-actions {
  display: inline-flex;
  gap: 8px;
}

.kanban-page {
  max-width: 1320px;
  margin: 0 auto;
}

.kanban-surface {
  position: relative;
  border-radius: 24px;
  padding: 16px;
  border: 1px solid rgba(224, 206, 232, 0.7);
  background:
    radial-gradient(circle at 10% 16%, rgba(245, 195, 210, 0.25), transparent 42%),
    radial-gradient(circle at 94% 10%, rgba(213, 193, 246, 0.22), transparent 46%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.72), rgba(244, 236, 254, 0.66));
  box-shadow: 0 16px 36px rgba(136, 110, 149, 0.12);
  backdrop-filter: blur(10px);
}

.kanban-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.kanban-column {
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(218, 202, 229, 0.78);
  border-radius: 20px;
  padding: 10px;
  min-height: 360px;
  backdrop-filter: blur(8px);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.kanban-column.column-todo { background: linear-gradient(180deg, rgba(252, 241, 248, 0.94), rgba(255, 255, 255, 0.9)); }
.kanban-column.column-progress { background: linear-gradient(180deg, rgba(244, 236, 254, 0.94), rgba(255, 255, 255, 0.9)); }
.kanban-column.column-done { background: linear-gradient(180deg, rgba(233, 248, 240, 0.94), rgba(255, 255, 255, 0.9)); }
.kanban-column.column-archived { background: linear-gradient(180deg, rgba(245, 239, 250, 0.94), rgba(255, 255, 255, 0.9)); }

.kanban-column.drop-target {
  border-color: #d9a8d0;
  box-shadow: inset 0 0 0 2px rgba(217, 168, 208, 0.35);
  background: rgba(255, 243, 251, 0.92);
}

.column-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.column-head h5 {
  margin: 0;
  font-size: 1rem;
  color: #2a2f4d;
}

.count {
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(218, 201, 229, 0.82);
  border-radius: 999px;
  padding: 2px 8px;
  color: #5b4d80;
  font-size: 0.8rem;
}

.column-empty {
  color: #826f98;
  font-size: 0.9rem;
  padding: 10px;
  border: 1px dashed rgba(220, 181, 214, 0.85);
  border-radius: 10px;
}

.task-card {
  border: 1px solid rgba(226, 209, 236, 0.88);
  border-left: 4px solid #ff6db8;
  border-radius: 12px;
  padding: 10px;
  margin-bottom: 8px;
  background: #ffffff;
  backdrop-filter: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.task-card.card-todo {
  background: linear-gradient(180deg, #fff3fb 0%, #ffffff 100%);
  border-left-color: #ff6db8;
}

.task-card.card-progress {
  background: linear-gradient(180deg, #f5efff 0%, #ffffff 100%);
  border-left-color: #9b7bff;
}

.task-card.card-done {
  background: linear-gradient(180deg, #eaf9f1 0%, #ffffff 100%);
  border-left-color: #63c799;
}

.task-card.card-archived {
  background: linear-gradient(180deg, #f7f1fb 0%, #ffffff 100%);
  border-left-color: #bca8c9;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 22px rgba(136, 110, 149, 0.18);
}

.task-card.dragging {
  opacity: 0.5;
}

.task-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.task-title {
  margin: 0;
  color: #2a2d4f;
}

.task-desc {
  margin: 6px 0 8px;
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
  border: 1px solid rgba(221, 205, 231, 0.86);
  padding: 2px 8px;
  color: #5b4e7f;
}

.chip.danger {
  background: #ffe8ea;
  border-color: #ffb8c0;
  color: #a33745;
}

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

.chip-status-todo { background: #ffe8f6; border-color: #ffc4e6; color: #9f3f7d; }
.chip-status-progress { background: #efe7ff; border-color: #d4c1ff; color: #6846a8; }
.chip-status-done { background: #e9f9ef; border-color: #bcebcf; color: #2c8059; }
.chip-status-archived { background: #f3eef8; border-color: #dbcee6; color: #705d86; }

.chip-project-a { background: #e8f1ff; border-color: #bbd4ff; color: #315f9d; }
.chip-project-b { background: #eafbf4; border-color: #bcecd4; color: #2f7a5d; }
.chip-project-c { background: #fff2e8; border-color: #f4cfb4; color: #9b6438; }
.chip-project-d { background: #f2ecff; border-color: #d7c6ff; color: #6146a8; }

.chip-category-a { background: #fff6de; border-color: #f3e1a8; color: #8d6a13; }
.chip-category-b { background: #ffecec; border-color: #ffc8c8; color: #a14444; }
.chip-category-c { background: #e8f7ff; border-color: #b8e5fa; color: #2f6f93; }
.chip-category-d { background: #eef7ea; border-color: #cfe7c1; color: #4e7a3f; }

.task-actions {
  margin-top: 8px;
  display: flex;
  gap: 6px;
}

.icon-btn {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  border: 1px solid rgba(219, 201, 229, 0.88);
  background: #ffffff;
  color: #5f4b84;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.badge.subtask {
  background: rgba(220, 238, 255, 0.72);
  border: 1px solid rgba(172, 206, 239, 0.84);
  color: #2f648f;
  font-weight: 500;
}

.kanban-toolbar .card-body {
  padding: 10px 12px;
}

.scope-filters {
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

.icon-btn.star-btn.active {
  color: #c9a227;
  border-color: rgba(212, 175, 55, 0.75);
  background: rgba(255, 248, 220, 0.95);
}

.empty-state {
  text-align: center;
  color: #7f6a8e;
}

@media (max-width: 1200px) {
  .kanban-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .kanban-grid {
    grid-template-columns: 1fr;
  }
}
</style>
