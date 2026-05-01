<template>
  <div class="kanban-page page-shell">
    <div class="kanban-head">
      <h2 class="page-title"><i class="fas fa-table-columns me-2"></i>Канбан-доска</h2>
      <router-link to="/tasks/create" class="btn btn-primary">
        <i class="fas fa-plus me-1"></i> Новая задача
      </router-link>
    </div>

    <div v-if="loading" class="empty-state">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Загружаю задачи...</p>
    </div>

    <div v-else class="kanban-grid">
      <section
        v-for="column in columns"
        :key="column.status"
        class="kanban-column"
        @dragover.prevent
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
          :class="{ dragging: draggingTaskId === task.id }"
          draggable="true"
          @dragstart="onDragStart(task.id)"
          @dragend="onDragEnd"
        >
          <div class="task-title-row">
            <h6 class="task-title">{{ task.title }}</h6>
            <span v-if="task.parent_task" class="badge subtask">Подзадача</span>
          </div>
          <p class="task-desc">{{ truncateText(task.description, 100) }}</p>

          <div class="chips">
            <span v-if="task.project" class="chip"><i class="fas fa-briefcase"></i> {{ task.project.name }}</span>
            <span v-if="task.priority" class="chip danger"><i class="fas fa-flag"></i> {{ task.priority.name }}</span>
          </div>

          <div class="task-actions">
            <button class="icon-btn" :disabled="!task.can_edit" @click="shiftStatus(task, -1)">
              <i class="fas fa-arrow-left"></i>
            </button>
            <button class="icon-btn" :disabled="!task.can_edit" @click="shiftStatus(task, 1)">
              <i class="fas fa-arrow-right"></i>
            </button>
            <router-link class="icon-btn" :to="`/tasks/${task.id}/edit`">
              <i class="fas fa-pen"></i>
            </router-link>
          </div>
        </article>
      </section>
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
    const columns = [
      { status: 'todo', title: 'К выполнению' },
      { status: 'in_progress', title: 'В процессе' },
      { status: 'done', title: 'Выполнено' },
      { status: 'archived', title: 'Архив' }
    ]

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
    }

    const onDrop = async (status) => {
      const task = tasks.value.find(item => item.id === draggingTaskId.value)
      if (!task) return
      await setTaskStatus(task, status)
      draggingTaskId.value = null
    }

    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? `${text.substring(0, length)}...` : text
    }

    onMounted(fetchTasks)

    return {
      loading,
      tasks,
      columns,
      draggingTaskId,
      tasksByStatus,
      onDragStart,
      onDragEnd,
      onDrop,
      shiftStatus,
      truncateText
    }
  }
}
</script>

<style scoped>
.kanban-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.kanban-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.kanban-column {
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(188, 204, 233, 0.9);
  border-radius: 14px;
  padding: 10px;
  min-height: 360px;
}

.column-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.count {
  background: #edf2ff;
  border: 1px solid #bfd0f1;
  border-radius: 999px;
  padding: 2px 8px;
  color: #375184;
  font-size: 0.8rem;
}

.column-empty {
  color: #8092b2;
  font-size: 0.9rem;
  padding: 10px;
  border: 1px dashed #c7d6ef;
  border-radius: 10px;
}

.task-card {
  border: 1px solid #c7d4ed;
  border-radius: 12px;
  padding: 10px;
  margin-bottom: 8px;
  background: #fff;
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
  color: #1f3050;
}

.task-desc {
  margin: 6px 0 8px;
  color: #60749a;
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
  background: rgba(239, 245, 255, 0.95);
  border: 1px solid rgba(188, 204, 233, 0.95);
  padding: 2px 8px;
  color: #43597d;
}

.chip.danger {
  background: #ffe8ea;
  border-color: #ffb8c0;
  color: #a33745;
}

.task-actions {
  margin-top: 8px;
  display: flex;
  gap: 6px;
}

.icon-btn {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  border: 1px solid #c3d1eb;
  background: #fff;
  color: #36507b;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.badge.subtask {
  background: #edf6ff;
  border: 1px solid #b9daf9;
  color: #2d5982;
  font-weight: 500;
}

.empty-state {
  padding: 24px;
  text-align: center;
  color: #7288ad;
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
